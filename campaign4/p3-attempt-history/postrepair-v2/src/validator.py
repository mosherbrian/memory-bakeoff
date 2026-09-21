"""Versioned terminal-boundary validator (P2 r2.1 boundary-schema).

Compares a derived snapshot against the authoritative ledger view and emits
one structured verdict: ACTIVE (in-flight work outstanding), REST
(legitimate rest, no alarm), INVALID (state fault + owned action), or a due
owned owner-reconciliation action. Never wakes/stops/signals anything; it
only returns data. Unknown versions, malformed/absent data, missing
dispositions, cycles, dangling/unrelated successors and overdue actions can
never produce REST.
"""
from __future__ import annotations

KINDS = ("successor_opened", "question_answered", "budget_spent", "blocked")
SCHEMA_VERSION = 1
TERMINALS = ("COMPLETE", "EXHAUSTED", "TERMINATED", "SUPERSEDED")


def _invalid(code, detail, owner="tern"):
    return {"verdict": "INVALID", "code": code, "detail": detail,
            "action": {"type": "owner-reconcile", "owner": owner}}


def validate(snapshot, ledger, now, triggers_fired=None):
    """Validate snapshot against authoritative ledger.

    ``snapshot``: parsed derived projection (or None if absent/unreadable).
    ``ledger``: {"revision": int, "packages": {pid: {"phase", "verdict",
      "disposition", "decision_task", "blocked"}}}.
    ``now``: ISO timestamp string. ``triggers_fired``: set of trigger ids
    already returned (exactly-once per trigger id enforced by caller store;
    this pure function reports due triggers and the caller dedups).
    """
    triggers_fired = triggers_fired or set()
    if snapshot is None:
        return _invalid("E_ABSENT_STATE", "no snapshot; ledger authoritative")
    if not isinstance(snapshot, dict):
        return _invalid("E_MALFORMED", "snapshot not an object")
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        return _invalid("E_VERSION", "unsupported schema_version")
    if snapshot.get("ledger_revision") != ledger.get("revision"):
        return _invalid("E_LEDGER_INCOMPLETE",
                        "snapshot revision != authoritative ledger revision")
    snap_terms = snapshot.get("terminal")
    snap_flight = snapshot.get("in_flight")
    if not isinstance(snap_terms, dict) or not isinstance(snap_flight, list):
        return _invalid("E_MALFORMED", "terminal/in_flight shapes")

    pkgs = ledger.get("packages", {})
    # Ledger completeness: every known ledger terminal must appear; an empty
    # declaration cannot hide known terminal packages.
    for pid, rec in pkgs.items():
        if rec["phase"] in TERMINALS and pid not in snap_terms:
            return _invalid("E_LEDGER_INCOMPLETE",
                            "ledger terminal %s missing from snapshot" % pid)

    # Overdue in-flight actions are faults even if files are fresh.
    # D2/D3: entries carry the full action identity; presence is enforced.
    for item in snap_flight:
        if not isinstance(item, dict) or "package_id" not in item:
            return _invalid("E_MALFORMED", "in_flight entry shape")
        for field in ("action_id", "owner", "deadline", "dispatch_receipt"):
            if field not in item:
                return _invalid("E_MALFORMED",
                                "in_flight %s missing %s"
                                % (item.get("package_id"), field))
        if item.get("deadline") and item["deadline"] < now:
            return _invalid("E_OVERDUE_ACTION",
                            "in-flight %s past deadline" % item["package_id"])

    # Validate each terminal entry and follow successor chains.
    for pid, entry in snap_terms.items():
        if not isinstance(entry, dict):
            return _invalid("E_MALFORMED", "terminal entry %s" % pid)
        disp = entry.get("disposition")
        if disp is None:
            # Row-17 held state: verdict without disposition but with an
            # open bounded director-decision task in the LEDGER (not merely
            # claimed by the snapshot) is pending, not omitted — provided
            # the task is carried in flight and unexpired.
            task = (pkgs.get(pid) or {}).get("decision_task")
            if task and task.get("deadline", "") >= now and \
                    entry.get("held") is True and \
                    any(isinstance(i, dict) and
                        i.get("package_id") == pid and
                        i.get("phase") == "DECISION" for i in snap_flight):
                continue
            # Missing disposition is a state fault, never rest — even with
            # fresh activity elsewhere (the Tern-omission shape).
            return _invalid("E_MISSING_DISPOSITION",
                            "terminal %s has no disposition" % pid)
        if not isinstance(disp, dict) or disp.get("kind") not in KINDS:
            return _invalid("E_MISSING_DISPOSITION",
                            "terminal %s kind not enumerable" % pid)
        if entry.get("decided_by") != "tern" or not entry.get("decision_ref"):
            return _invalid("E_OWNERSHIP",
                            "terminal %s needs attributed director decision"
                            % pid)
        kind = disp["kind"]
        if kind == "successor_opened":
            bad = _check_successor(pid, disp, snap_terms, snap_flight,
                                   pkgs, now)
            if bad:
                return bad
        elif kind == "question_answered":
            if not disp.get("evidence_refs") or not disp.get("reason"):
                return _invalid("E_INCOMPLETE_REST",
                                "%s needs evidence + reason" % pid)
        elif kind == "budget_spent":
            if not disp.get("allocation_ref") or not disp.get("reason"):
                return _invalid("E_INCOMPLETE_REST",
                                "%s needs allocation ref + decision" % pid)
        elif kind == "blocked":
            bad = _check_blocked(pid, disp, now, triggers_fired)
            if bad:
                return bad  # INVALID or a due owned action

    # Chains from every successor_opened must terminate at in-flight work or
    # a rest leaf; completed chains rest without permanent alarms.
    for pid, entry in snap_terms.items():
        disp = entry.get("disposition") or {}
        if disp.get("kind") == "successor_opened":
            bad = _follow_chain(pid, snap_terms, snap_flight, set())
            if bad:
                return bad

    if snap_flight:
        return {"verdict": "ACTIVE",
                "detail": "%d acknowledged bounded action(s) in flight"
                          % len(snap_flight)}
    return {"verdict": "REST", "detail": "all chains end in legitimate rest"}


def _live_ids(snap_flight):
    """D3 liveness: acknowledged dispatch AND a finite deadline.

    Any in-flight entry with a matching package_id is not enough: without
    an acknowledged dispatch receipt or a finite deadline it is an unrelated
    busy seat, a never-dispatched intention, or a broken reference — none of
    which satisfies a successor link.
    """
    return {i.get("package_id") for i in snap_flight
            if isinstance(i, dict) and
            i.get("dispatch_receipt") == "acknowledged" and i.get("deadline")}


def _check_successor(pid, disp, snap_terms, snap_flight, pkgs, now):
    sid = disp.get("successor_id")
    if not sid:
        return _invalid("E_DANGLING_SUCCESSOR",
                        "%s names no successor" % pid)
    if sid in _live_ids(snap_flight):
        return None  # acknowledged bounded work in flight
    if sid in snap_terms:
        return None  # terminal successor: chain-following decides
    if sid in pkgs:
        # Known to the ledger but neither in flight nor terminal here:
        # claimed-but-absent successor.
        return _invalid("E_DANGLING_SUCCESSOR",
                        "%s -> %s has no acknowledged work" % (pid, sid))
    return _invalid("E_DANGLING_SUCCESSOR",
                    "%s -> unknown %s" % (pid, sid))


def _follow_chain(pid, snap_terms, snap_flight, seen):
    """Follow successor links; None = ends at work or rest leaf."""
    if pid in seen:
        return _invalid("E_CYCLE", "successor cycle at %s" % pid)
    seen = seen | {pid}
    entry = snap_terms.get(pid, {})
    disp = entry.get("disposition") or {}
    if disp.get("kind") != "successor_opened":
        return None  # rest leaf
    sid = disp.get("successor_id")
    if sid in _live_ids(snap_flight):
        return None  # real in-flight work
    if sid not in snap_terms:
        return _invalid("E_DANGLING_SUCCESSOR",
                        "chain %s -> %s dangling" % (pid, sid))
    return _follow_chain(sid, snap_terms, snap_flight, seen)


def _check_blocked(pid, disp, now, triggers_fired):
    blk = disp.get("blocker") or {}
    trig = blk.get("wake_trigger") or {}
    if not blk.get("id") or not blk.get("owner") or not blk.get("resumption"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs id/owner/resumption" % pid)
    if not trig.get("event_id") and not trig.get("revisit_at"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs a machine trigger" % pid)
    tid = trig.get("event_id") or ("revisit:" + trig.get("revisit_at"))
    due = (trig.get("revisit_at") and trig["revisit_at"] <= now)
    if due and tid not in triggers_fired:
        # Due trigger: bounded owner-reconciliation action, exactly once per
        # trigger id. It cannot suppress alarms as parked rest, invent a
        # successor, or restart the terminal package.
        return {"verdict": "ACTION_DUE",
                "action": {"type": "owner-reconcile", "owner": blk["owner"],
                           "trigger_id": tid, "package_id": pid,
                           "bounded": True},
                "detail": "blocker trigger due for %s" % pid}
    return None
