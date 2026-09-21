"""Candidate supervision: authoritative ledger + versioned snapshot.

Wraps accepted validator with owned-fault handling: missing/unreadable/stale
snapshot or ledger failure returns explicit owned fault, never silent success.
Enforces: REST suppresses generic silence escalation (incl. successor chains
ending in rest); INVALID never masked by file activity or busy seats;
ACTION_DUE owned/durable/deduplicated across restart; ACTIVE uses actual
current action deadline (stale worker timers cannot expire a verifier).
"""
from __future__ import annotations

import json
import os

import validator as V


def load_snapshot(path):
    try:
        with open(path) as fh:
            return json.load(fh), None
    except (OSError, ValueError) as e:
        return None, "E_ABSENT_STATE: snapshot unreadable (%s)" % e


def supervise(snapshot, ledger, now, triggers_fired=None, file_activity=None,
              busy_seats=None):
    """Supervise one tick. file_activity/busy_seats are informational only and
    must never mask INVALID."""
    if not isinstance(ledger, dict) or "packages" not in ledger:
        return {"verdict": "INVALID", "code": "E_LEDGER",
                "detail": "ledger unavailable",
                "action": {"type": "owner-reconcile", "owner": "cairn"}}
    if snapshot is None:
        return {"verdict": "INVALID", "code": "E_ABSENT_STATE",
                "detail": "missing snapshot; ledger authoritative",
                "action": {"type": "owner-reconcile", "owner": "cairn"}}
    if isinstance(snapshot, dict) and "ledger_revision" in snapshot and \
            "revision" in ledger and \
            snapshot["ledger_revision"] != ledger["revision"]:
        return {"verdict": "INVALID", "code": "E_LEDGER_INCOMPLETE",
                "detail": "stale snapshot revision",
                "action": {"type": "owner-reconcile", "owner": "cairn"}}
    verdict = V.validate(snapshot, ledger, now, triggers_fired)
    # file_activity / busy_seats deliberately ignored for verdict.
    if verdict.get("verdict") == "INVALID":
        owner = (verdict.get("action") or {}).get("owner", "tern")
        verdict.setdefault("code", "E_INVALID")
        return verdict
    return verdict


def dedupe_action_due(seen_trigger_ids, verdict):
    """ACTION_DUE deduplicated across restart via durable trigger ids."""
    if verdict.get("verdict") != "ACTION_DUE":
        return verdict, False
    tid = (verdict.get("action") or {}).get("trigger_id")
    if tid in seen_trigger_ids:
        return {"verdict": "ACTIVE", "detail": "deduplicated; trigger %s already owned" % tid}, True
    seen_trigger_ids.add(tid)
    return verdict, False
