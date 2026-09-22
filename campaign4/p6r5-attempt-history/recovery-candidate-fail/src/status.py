"""Compact status report: package, owner/action/deadline, receipt, evidence,
next permitted action. Simulated observations are labeled SIMULATED; real
campaign history is never claimed."""
from __future__ import annotations


def status_report(package_id, ledger_packages, snapshot, verdict):
    rec = (ledger_packages or {}).get(package_id, {})
    fl = rec.get("flight") or {}
    ho = rec.get("handoff") or {}
    inflight = [i for i in (snapshot or {}).get("in_flight", [])
                if isinstance(i, dict) and i.get("package_id") == package_id]
    return {
        "package": package_id,
        "simulated": True,
        "owner": fl.get("owner") or ho.get("owner"),
        "action": fl.get("action_id"),
        "deadline": fl.get("deadline") or ho.get("deadline"),
        "receipt": rec.get("receipt"),
        "evidence": rec.get("verdict") or (inflight[0].get("phase") if inflight else rec.get("phase")),
        "phase": rec.get("phase"),
        "next_permitted_action": _next(rec, verdict),
        "supervision": verdict,
        "duty": "cairn",
        "escalation": "tern",
    }


def _next(rec, verdict):
    phase = rec.get("phase")
    if verdict.get("verdict") == "ACTION_DUE":
        return "owner-reconcile %s" % (verdict.get("action") or {}).get("owner")
    if verdict.get("verdict") == "INVALID":
        return "owner-reconcile %s" % (verdict.get("action") or {}).get("owner", "cairn")
    table = {"REGISTERED": "duty start", "RUNNING": "worker publish",
             "CHECKING": "verifier verify", "BLOCKED": "duty resolve/defer/terminate",
             "COMPLETE": "director decide (terminal pause proposal: fake output only)"}
    return table.get(phase, "none")
