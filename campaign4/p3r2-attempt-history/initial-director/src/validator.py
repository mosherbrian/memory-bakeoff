"""Versioned terminal-boundary validator (P2 r2.1 boundary-schema, r2 ledger
authority).

The LEDGER determines package inventory, current phase, terminal
disposition/decision, current action, owner, deadline and acknowledged
receipt. The snapshot is compared against these authoritative facts before
any ACTIVE/REST/ACTION_DUE verdict; equal revision counters are necessary
but not sufficient. Omissions, fabrications, hidden/changed dispositions and
forged phase/decision/action/owner/ack/deadline claims fault deterministically.
Timestamps are validated as UTC instants; comparisons never depend on string
formatting. The function only returns data — it never wakes/stops/signals.
"""
from __future__ import annotations

import datetime
import re

KINDS = ("successor_opened", "question_answered", "budget_spent", "blocked")
SCHEMA_VERSION = 1
TERMINALS = ("COMPLETE", "EXHAUSTED", "TERMINATED", "SUPERSEDED")
FLIGHT_FIELDS = ("action_id", "owner", "deadline", "dispatch_receipt")

_UTC_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})"
    r"(Z|[+-]\d{2}:?\d{2})?$")


def _invalid(code, detail, owner="tern"):
    return {"verdict": "INVALID", "code": code, "detail": detail,
            "action": {"type": "owner-reconcile", "owner": owner}}


def _instant(value):
    """Strict UTC instant. Returns aware datetime or None (never raises)."""
    if not isinstance(value, str):
        return None
    m = _UTC_RE.match(value.strip())
    if not m:
        return None
    try:
        base = datetime.datetime(int(m.group(1)), int(m.group(2)),
                                 int(m.group(3)), int(m.group(4)),
                                 int(m.group(5)), int(m.group(6)))
    except ValueError:
        return None
    zone = m.group(7)
    if not zone or zone == "Z":
        return base.replace(tzinfo=datetime.timezone.utc)
    sign = 1 if zone[0] == "+" else -1
    digits = zone[1:].replace(":", "")
    if len(digits) != 4:
        return None
    off = datetime.timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
    return (base - sign * off).replace(tzinfo=datetime.timezone.utc)


def validate(snapshot, ledger, now, triggers_fired=None):
    """Validate snapshot against the authoritative ledger.

    ``snapshot``: parsed derived projection (None if absent/unreadable).
    ``ledger``: {"revision": int, "packages": {pid: {"phase", "verdict",
      "disposition", "decision_task", "blocked", "flight", "handoff",
      "receipt"}}}.
    ``now``: timestamp (any UTC offset formatting accepted; compared as an
    instant). ``triggers_fired``: already-returned trigger ids.
    """
    triggers_fired = triggers_fired or set()
    tnow = _instant(now)
    if tnow is None:
        return _invalid("E_MALFORMED", "now is not a UTC instant")
    if snapshot is None:
        return _invalid("E_ABSENT_STATE", "no snapshot; ledger authoritative")
    if not isinstance(snapshot, dict):
        return _invalid("E_MALFORMED", "snapshot not an object")
    if not isinstance(ledger, dict) or \
            not isinstance(ledger.get("packages"), dict):
        return _invalid("E_MALFORMED", "ledger packages not an object")
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        return _invalid("E_VERSION", "unsupported schema_version")
    if snapshot.get("ledger_revision") != ledger.get("revision"):
        return _invalid("E_LEDGER_INCOMPLETE",
                        "snapshot revision != authoritative ledger revision")
    snap_terms = snapshot.get("terminal")
    snap_flight = snapshot.get("in_flight")
    if not isinstance(snap_terms, dict) or not isinstance(snap_flight, list):
        return _invalid("E_MALFORMED", "terminal/in_flight shapes")

    pkgs = ledger["packages"]
    for pid, rec in pkgs.items():
        if not isinstance(rec, dict) or "phase" not in rec:
            return _invalid("E_MALFORMED", "ledger package %s shape" % pid)

    # Structural checks on projection content (deterministic order).
    for item in snap_flight:
        if not isinstance(item, dict) or "package_id" not in item:
            return _invalid("E_MALFORMED", "in_flight entry shape")
        for field in FLIGHT_FIELDS:
            if field not in item:
                return _invalid("E_MALFORMED",
                                "in_flight %s missing %s"
                                % (item.get("package_id"), field))
        dl = _instant(item.get("deadline")) if item.get("deadline") \
            is not None else None
        if item.get("deadline") is not None and dl is None:
            return _invalid("E_MALFORMED",
                            "in_flight %s deadline not a UTC instant"
                            % item.get("package_id"))
        if dl is not None and dl < tnow:
            return _invalid("E_OVERDUE_ACTION",
                            "in-flight %s past deadline" % item["package_id"])

    for pid, entry in snap_terms.items():
        if not isinstance(entry, dict):
            return _invalid("E_MALFORMED", "terminal entry %s" % pid)
        disp = entry.get("disposition")
        if disp is None:
            task = (pkgs.get(pid) or {}).get("decision_task")
            tdl = (task or {}).get("deadline")
            if task and _instant(tdl) is not None and \
                    _instant(tdl) >= tnow and entry.get("held") is True and \
                    any(isinstance(i, dict) and
                        i.get("package_id") == pid and
                        i.get("phase") == "DECISION" for i in snap_flight):
                continue
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
                                   pkgs, tnow)
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
            bad = _check_blocked(pid, disp, tnow, triggers_fired)
            if bad:
                return bad

    for pid, entry in snap_terms.items():
        disp = entry.get("disposition") or {}
        if disp.get("kind") == "successor_opened":
            bad = _follow_chain(pid, snap_terms, snap_flight, set())
            if bad:
                return bad

    # Ledger authority: compare every projection claim against ledger facts.
    bad = _authority_check(snap_terms, snap_flight, pkgs, tnow)
    if bad:
        return bad

    if snap_flight:
        return {"verdict": "ACTIVE",
                "detail": "%d acknowledged bounded action(s) in flight"
                          % len(snap_flight)}
    return {"verdict": "REST", "detail": "all chains end in legitimate rest"}


def _authority_check(snap_terms, snap_flight, pkgs, tnow):
    """The ledger decides inventory, phase, disposition, action, owner,
    deadline and receipt. Returns an INVALID verdict or None."""
    flight_by_pid = {}
    for item in snap_flight:
        if item.get("phase") == "DECISION":
            continue
        flight_by_pid.setdefault(item["package_id"], item)

    # Active inventory: ledger non-terminals must be projected in flight.
    for pid, rec in pkgs.items():
        if rec["phase"] not in TERMINALS and pid not in flight_by_pid and \
                not _has_decision_entry(snap_flight, pid):
            return _invalid("E_LEDGER_INCOMPLETE",
                            "ledger-active %s missing from projection" % pid)
    # Fabricated flight: projection-only or terminal pids in flight.
    for pid in flight_by_pid:
        if pid not in pkgs or pkgs[pid]["phase"] in TERMINALS:
            return _invalid("E_FABRICATED",
                            "in-flight %s unknown to the ledger" % pid)

    # Terminal agreement: state, disposition, decision.
    for pid, rec in pkgs.items():
        if rec["phase"] in TERMINALS and pid not in snap_terms:
            return _invalid("E_LEDGER_INCOMPLETE",
                            "ledger terminal %s missing from projection" % pid)
    for pid, entry in snap_terms.items():
        if pid not in pkgs or pkgs[pid]["phase"] not in TERMINALS:
            return _invalid("E_FABRICATED",
                            "terminal %s unknown to the ledger" % pid)
        rec = pkgs[pid]
        if entry.get("state") != rec["phase"]:
            return _invalid("E_MISMATCH",
                            "terminal %s state contradicts ledger" % pid)
        ldisp = rec.get("disposition")
        sdisp = entry.get("disposition")
        if ldisp is None and sdisp is None:
            continue  # held state already vetted above
        if ldisp is None:
            return _invalid("E_FABRICATED",
                            "terminal %s disposition invented" % pid)
        if sdisp is None:
            return _invalid("E_MISSING_DISPOSITION",
                            "terminal %s hides its disposition" % pid)
        if not isinstance(sdisp, dict) or sdisp.get("kind") != ldisp.get("kind"):
            return _invalid("E_MISMATCH",
                            "terminal %s disposition kind changed" % pid)
        for key, val in ldisp.items():
            if sdisp.get(key) != val:
                return _invalid("E_MISMATCH",
                                "terminal %s disposition.%s changed"
                                % (pid, key))
        if entry.get("decided_by") != "tern" or \
                entry.get("decision_ref") != ldisp.get("decision_ref", "") or \
                entry.get("reason") != ldisp.get("reason", ""):
            return _invalid("E_MISMATCH",
                            "terminal %s decision attribution changed" % pid)

    # Flight agreement: action, owner, deadline, receipt per ledger facts.
    for pid, item in flight_by_pid.items():
        rec = pkgs[pid]
        lf = rec.get("flight") or {}
        ho = rec.get("handoff") or {}
        if lf.get("action_id"):
            for field in ("action_id", "owner"):
                if item.get(field) != lf.get(field):
                    return _invalid("E_MISMATCH",
                                    "in-flight %s %s forged" % (pid, field))
            bad = _deadline_equal(item.get("deadline"), lf.get("deadline"),
                                  pid)
            if bad:
                return bad
            lrec = rec.get("receipt")
            if lrec is not None:
                if item.get("dispatch_receipt") != lrec:
                    return _invalid("E_MISMATCH",
                                    "in-flight %s ack forged" % pid)
            elif item.get("dispatch_receipt") == "acknowledged":
                return _invalid("E_MISMATCH",
                                "in-flight %s ack unrecorded" % pid)
        elif ho:
            if item.get("action_id") is not None:
                return _invalid("E_MISMATCH",
                                "in-flight %s action invented" % pid)
            if item.get("owner") != ho.get("owner"):
                return _invalid("E_MISMATCH",
                                "in-flight %s owner forged" % pid)
            bad = _deadline_equal(item.get("deadline"), ho.get("deadline"),
                                  pid)
            if bad:
                return bad
        elif item.get("action_id") is not None:
            return _invalid("E_FABRICATED",
                            "in-flight %s action never dispatched" % pid)

    # Decision tasks: ledger-open tasks need matching DECISION entries.
    for pid, rec in pkgs.items():
        task = rec.get("decision_task")
        if task and rec.get("disposition") is None:
            tdl = _instant(task.get("deadline"))
            if tdl is None:
                return _invalid("E_MALFORMED",
                                "ledger decision task %s deadline" % pid)
            match = [i for i in snap_flight
                     if isinstance(i, dict) and i.get("phase") == "DECISION"
                     and i.get("package_id") == pid
                     and i.get("action_id") == task.get("task_id")
                     and i.get("owner") == "tern"
                     and _instant(i.get("deadline")) == tdl]
            if not match:
                return _invalid("E_LEDGER_INCOMPLETE",
                                "ledger decision task %s unprojected" % pid)
    for item in snap_flight:
        if item.get("phase") == "DECISION":
            pid = item.get("package_id")
            task = (pkgs.get(pid) or {}).get("decision_task")
            if not task or (pkgs.get(pid) or {}).get("disposition") \
                    is not None:
                return _invalid("E_FABRICATED",
                                "decision entry %s unrecorded" % pid)
    return None


def _deadline_equal(snap_dl, ledger_dl, pid):
    a, b = _instant(snap_dl), _instant(ledger_dl)
    if a is None or b is None:
        return _invalid("E_MALFORMED",
                        "in-flight %s deadline not a UTC instant" % pid)
    if a != b:
        return _invalid("E_MISMATCH",
                        "in-flight %s deadline extended" % pid)
    return None


def _has_decision_entry(snap_flight, pid):
    return any(isinstance(i, dict) and i.get("package_id") == pid and
               i.get("phase") == "DECISION" for i in snap_flight)


def _live_ids(snap_flight):
    """D3 liveness: acknowledged dispatch AND a finite deadline."""
    return {i.get("package_id") for i in snap_flight
            if isinstance(i, dict) and
            i.get("dispatch_receipt") == "acknowledged" and i.get("deadline")}


def _check_successor(pid, disp, snap_terms, snap_flight, pkgs, tnow):
    sid = disp.get("successor_id")
    if not sid:
        return _invalid("E_DANGLING_SUCCESSOR",
                        "%s names no successor" % pid)
    if sid in _live_ids(snap_flight):
        return None  # acknowledged bounded work in flight
    if sid in snap_terms:
        return None  # terminal successor: chain-following decides
    if sid in pkgs:
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


def _check_blocked(pid, disp, tnow, triggers_fired):
    blk = disp.get("blocker") or {}
    trig = blk.get("wake_trigger") or {}
    if not blk.get("id") or not blk.get("owner") or not blk.get("resumption"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs id/owner/resumption" % pid)
    if not trig.get("event_id") and not trig.get("revisit_at"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs a machine trigger" % pid)
    tid = trig.get("event_id") or ("revisit:" + trig.get("revisit_at"))
    revisit = _instant(trig.get("revisit_at")) \
        if trig.get("revisit_at") else None
    if trig.get("revisit_at") and revisit is None:
        return _invalid("E_MALFORMED",
                        "%s trigger revisit_at not a UTC instant" % pid)
    if revisit is not None and revisit <= tnow and tid not in triggers_fired:
        return {"verdict": "ACTION_DUE",
                "action": {"type": "owner-reconcile", "owner": blk["owner"],
                           "trigger_id": tid, "package_id": pid,
                           "bounded": True},
                "detail": "blocker trigger due for %s" % pid}
    return None
