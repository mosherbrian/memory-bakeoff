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

ALL_PHASES = ("DRAFT", "ADMITTED", "REGISTERED", "RUNNING", "CHECKING",
              "REPAIR_ALLOWED", "BLOCKED") + TERMINALS


def _invalid(code, detail, owner="tern"):
    return {"verdict": "INVALID", "code": code, "detail": detail,
            "action": {"type": "owner-reconcile", "owner": owner}}


def _instant(value):
    """Strict UTC instant. Returns aware datetime or None (never raises).

    Accepts `Z` or numeric offsets; offsets are range-checked and all
    arithmetic is guarded, so minimum-date offsets and out-of-range fields
    fault as malformed instead of raising OverflowError/ValueError.
    """
    if not isinstance(value, str):
        return None
    try:
        m = _UTC_RE.match(value.strip())
        if not m:
            return None
        base = datetime.datetime(int(m.group(1)), int(m.group(2)),
                                 int(m.group(3)), int(m.group(4)),
                                 int(m.group(5)), int(m.group(6)))
        zone = m.group(7)
        if not zone or zone == "Z":
            return base.replace(tzinfo=datetime.timezone.utc)
        digits = zone[1:].replace(":", "")
        if len(digits) != 4:
            return None
        oh, om = int(digits[:2]), int(digits[2:])
        if oh > 23 or om > 59:
            return None
        off = datetime.timedelta(hours=oh, minutes=om)
        if zone[0] == "+":
            result = base - off
        elif zone[0] == "-":
            result = base + off
        else:
            return None
        return result.replace(tzinfo=datetime.timezone.utc)
    except (ValueError, OverflowError, ArithmeticError):
        return None


def _is_str(value):
    return isinstance(value, str)


def _is_opt_str(value):
    return value is None or isinstance(value, str)


def validate(snapshot, ledger, now, triggers_fired=None):
    """Validate snapshot against the authoritative ledger.

    ``snapshot``: parsed derived projection (None if absent/unreadable).
    ``ledger``: {"revision": int, "packages": {pid: {"phase", "verdict",
      "disposition", "decision_task", "blocked", "flight", "handoff",
      "receipt"}}}.
    ``now``: timestamp (any UTC offset formatting accepted; compared as an
    instant). ``triggers_fired``: already-returned trigger ids.
    """
    try:
        triggers_fired = set(triggers_fired or ())
    except TypeError:
        return _invalid("E_MALFORMED", "triggers_fired not a set of ids")
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
        if not _is_str(pid) or not pid:
            return _invalid("E_MALFORMED", "ledger package id shape")
        if not isinstance(rec, dict) or rec.get("phase") not in ALL_PHASES:
            return _invalid("E_MALFORMED", "ledger package %s shape" % pid)
        for key in ("flight", "handoff", "decision_task"):
            if rec.get(key) is not None and not isinstance(rec[key], dict):
                return _invalid("E_MALFORMED",
                                "ledger package %s %s shape" % (pid, key))

    # Structural shape enforcement on projection content, BEFORE any use:
    # ids are non-empty strings, metadata is str-or-None, duplicates are
    # rejected. Malformed values fault; they never crash and never pass.
    seen_pids = set()
    for item in snap_flight:
        if not isinstance(item, dict):
            return _invalid("E_MALFORMED", "in_flight entry shape")
        pid = item.get("package_id")
        if not _is_str(pid) or not pid:
            return _invalid("E_MALFORMED", "in_flight package_id shape")
        if pid in seen_pids:
            return _invalid("E_DUPLICATE",
                            "in-flight %s projected twice" % pid)
        seen_pids.add(pid)
        if not _is_str(item.get("phase")) or not item.get("phase"):
            return _invalid("E_MALFORMED",
                            "in_flight %s phase shape" % pid)
        for field in FLIGHT_FIELDS:
            if field not in item or not _is_opt_str(item[field]):
                return _invalid("E_MALFORMED",
                                "in_flight %s field %s shape" % (pid, field))
        dl = _instant(item.get("deadline")) if item.get("deadline") \
            is not None else None
        if item.get("deadline") is not None and dl is None:
            return _invalid("E_MALFORMED",
                            "in_flight %s deadline not a UTC instant"
                            % item.get("package_id"))
        if dl is not None and dl < tnow:
            return _invalid("E_OVERDUE_ACTION",
                            "in-flight %s past deadline" % item["package_id"])

    for pid in snap_terms:
        if not _is_str(pid) or not pid:
            return _invalid("E_MALFORMED", "terminal package id shape")

    # Terminal structural checks: faults only. A due trigger is STASHED,
    # never emitted, until ledger authority confirms a clean record.
    pending_due = None
    for pid, entry in snap_terms.items():
        if not isinstance(entry, dict):
            return _invalid("E_MALFORMED", "terminal entry %s" % pid)
        if not _is_str(entry.get("state")) or not entry.get("state"):
            return _invalid("E_MALFORMED", "terminal %s state shape" % pid)
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
        if entry.get("decided_by") != "tern" or \
                not _is_str(entry.get("decision_ref")) or \
                not entry.get("decision_ref"):
            return _invalid("E_OWNERSHIP",
                            "terminal %s needs attributed director decision"
                            % pid)
        kind = disp["kind"]
        if kind == "successor_opened":
            sid = disp.get("successor_id")
            if not sid:
                return _invalid("E_DANGLING_SUCCESSOR",
                                "%s names no successor" % pid)
            if not _is_str(sid):
                return _invalid("E_MALFORMED",
                                "terminal %s successor_id shape" % pid)
            bad = _check_successor(pid, disp, snap_terms, snap_flight,
                                   pkgs, tnow)
            if bad:
                return bad
        elif kind == "question_answered":
            if not isinstance(disp.get("evidence_refs"), list) or \
                    not disp.get("evidence_refs") or \
                    not _is_str(disp.get("reason")) or not disp.get("reason"):
                return _invalid("E_INCOMPLETE_REST",
                                "%s needs evidence + reason" % pid)
        elif kind == "budget_spent":
            if not _is_str(disp.get("allocation_ref")) or \
                    not disp.get("allocation_ref") or \
                    not _is_str(disp.get("reason")) or not disp.get("reason"):
                return _invalid("E_INCOMPLETE_REST",
                                "%s needs allocation ref + decision" % pid)
        elif kind == "blocked":
            bad = _blocked_shape(pid, disp)
            if bad:
                return bad
            due = _check_blocked(pid, disp, tnow, triggers_fired)
            if due is not None and pending_due is None:
                pending_due = due  # emitted only after authority passes

    for pid, entry in snap_terms.items():
        disp = entry.get("disposition") or {}
        if disp.get("kind") == "successor_opened":
            bad = _follow_chain(pid, snap_terms, snap_flight, set())
            if bad:
                return bad

    # Ledger authority: no valid outcome (ACTIVE/REST/ACTION_DUE) may be
    # produced while any projection claim contradicts the ledger — even a
    # genuine due trigger alongside another inconsistent package.
    bad = _authority_check(snap_terms, snap_flight, pkgs, tnow)
    if bad:
        return bad
    if pending_due is not None:
        return pending_due

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
        if entry.get("decided_by") != "tern":
            return _invalid("E_MISMATCH",
                            "terminal %s decision attribution changed" % pid)
        for field in ("decision_ref", "reason"):
            stated = ldisp.get(field, "")
            claimed = entry.get(field, "")
            if stated:
                if claimed != stated:
                    return _invalid("E_MISMATCH",
                                    "terminal %s decision %s changed"
                                    % (pid, field))
            elif not _is_str(claimed) or not claimed:
                return _invalid("E_MISMATCH",
                                "terminal %s decision %s unattributed"
                                % (pid, field))

    # Flight agreement: phase, action, owner, deadline, receipt per facts.
    for pid, item in flight_by_pid.items():
        rec = pkgs[pid]
        if item.get("phase") != rec["phase"]:
            return _invalid("E_MISMATCH",
                            "in-flight %s phase forged" % pid)
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


def _blocked_shape(pid, disp):
    """Nested blocker/trigger/decision shapes, before any use. Returns an
    INVALID verdict or None. Malformed nested data faults; it never crashes
    and never passes as a valid outcome."""
    blk = disp.get("blocker")
    if not isinstance(blk, dict):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs a blocker object" % pid)
    trig = blk.get("wake_trigger")
    if trig is not None and not isinstance(trig, dict):
        return _invalid("E_MALFORMED",
                        "%s wake_trigger shape" % pid)
    trig = trig or {}
    for field in ("id", "owner", "resumption"):
        if blk.get(field) is not None and not _is_str(blk[field]):
            return _invalid("E_MALFORMED",
                            "%s blocker.%s shape" % (pid, field))
    for field in ("event_id", "revisit_at"):
        if trig.get(field) is not None and not _is_str(trig[field]):
            return _invalid("E_MALFORMED",
                            "%s trigger.%s shape" % (pid, field))
    if not blk.get("id") or not blk.get("owner") or not blk.get("resumption"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs id/owner/resumption" % pid)
    if not trig.get("event_id") and not trig.get("revisit_at"):
        return _invalid("E_INCOMPLETE_REST",
                        "%s blocked needs a machine trigger" % pid)
    if trig.get("revisit_at") and \
            _instant(trig["revisit_at"]) is None:
        return _invalid("E_MALFORMED",
                        "%s trigger revisit_at not a UTC instant" % pid)
    return None


def _check_blocked(pid, disp, tnow, triggers_fired):
    """Due-trigger computation; shapes are guaranteed by _blocked_shape."""
    blk = disp["blocker"]
    trig = blk.get("wake_trigger") or {}
    tid = trig.get("event_id") or ("revisit:" + trig.get("revisit_at"))
    revisit = _instant(trig.get("revisit_at")) \
        if trig.get("revisit_at") else None
    if revisit is not None and revisit <= tnow and tid not in triggers_fired:
        return {"verdict": "ACTION_DUE",
                "action": {"type": "owner-reconcile", "owner": blk["owner"],
                           "trigger_id": tid, "package_id": pid,
                           "bounded": True},
                "detail": "blocker trigger due for %s" % pid}
    return None
