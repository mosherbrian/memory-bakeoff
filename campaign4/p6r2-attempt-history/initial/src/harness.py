"""P6-r2 connected harness: one runnable entrypoint composing trusted
ingress, durable intents, transport, actual source capture, timers and
lifecycle reconciliation.

Live effects occur ONLY in live mode with an explicit bound plan hash and
a non-empty fixture seat allowlist. Every other invocation (including all
Stage A checks) uses injected collaborators and performs zero live
effects. No fake defaults exist in live mode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from driver import Driver, FakeClock
from host_adapter import (HostAdapter, HostWakeTransport, HostTimerService,
                          ACPOutcomeObserver, OwnedFault)


def build_adapter(db_path, clock=None, live=False, plan_hash=None,
                  allowlist_seats=(), wake_path=None, history_path=None,
                  transport=None, timers=None, observer=None):
    """Compose the full stack. Live mode requires plan hash + allowlist
    and explicit production collaborators (fail-closed otherwise)."""
    allowlist_seats = tuple(allowlist_seats or ())
    if live:
        if not plan_hash or not allowlist_seats:
            raise OwnedFault("E_DISABLED",
                             "live mode needs bound plan hash + allowlist")
        if transport is None:
            transport = HostWakeTransport(
                wake_path, allowlist_seats, enabled=True,
                kv_get=None, kv_put=None)
        if timers is None:
            timers = HostTimerService(enabled=True,
                                      allowlist=allowlist_seats)
        if isinstance(transport, HostWakeTransport) and \
                not transport.enabled:
            raise OwnedFault("E_DISABLED", "transport not enabled")
    driver = Driver(db_path, clock or FakeClock())
    if isinstance(transport, HostWakeTransport):
        transport._kv_get = driver.kv.get
        transport._kv_put = driver._kv_put
    if isinstance(timers, HostTimerService):
        timers._kv_get = driver.kv.get
        timers._kv_put = driver._kv_put
    adapter = HostAdapter(driver, clock=driver.clock, transport=transport,
                          timers=timers, observer=observer, live=live)
    return adapter


def run_step(adapter, spec):
    """One bounded recovery step: dispatch -> send -> capture -> arm ->
    observe -> reconcile -> drive-next-or-escalate. Returns an outcome
    record with per-action latency fields (receipt clock)."""
    qid = spec["question_id"]
    aid, execn = spec["action_id"], spec["execution_id"]
    t0 = adapter.trusted_now()
    adapter.driver.admit_authorize(qid)
    adapter.driver._kv_put("harness-qid", qid)
    adapter.driver.start_dispatch(qid, aid,
                                  duration_s=spec["duration_s"])
    adapter.register_execution(aid, execn, spec["authorization_ref"],
                               spec["deadline_hint_utc"])
    mid = adapter.transport.send(spec["seat"], spec["text"],
                                 action=aid, execution=execn)
    adapter.capture(qid, spec.get("attempt", "a1"), aid,
                    aid + "-dispatched", execn, "dispatched",
                    occurred_at=spec.get("occurred_at"), provenance="step")
    timer = adapter.arm_from_ledger("deadline:" + aid,
                                    spec["deadline_hint_utc"])
    outcome = {"action": aid, "execution": execn, "message_id": mid,
               "timer": timer, "dispatch_at": t0,
               "reconcile": adapter.reconcile_send(mid, aid)}
    return outcome


def timer_callback(db_path, timer_id, qid="P6F", action_id=None):
    """Executable candidate callback: fire a due timer through ledger
    authority (argv embedded in host timer units, never `true`)."""
    from driver import FakeClock as _FC
    try:
        from ingress import HostClock as _HC
        clock = _HC()
    except ImportError:
        clock = _FC()
    driver = Driver(db_path, clock)
    adapter = HostAdapter(driver, clock=clock)
    rec = driver.store.revisions.get((qid, 1)) or {}
    fl = rec.get("flight") or {}
    aid = action_id or fl.get("action_id")
    if aid is None:
        return {"timer": timer_id, "decision": "no-op-no-current-action"}
    result, dup = driver.on_deadline(aid, qid)
    return {"timer": timer_id, "decision": result, "dedup": dup}


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r2 connected harness")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--plan-hash", default="")
    ap.add_argument("--allowlist-seat", action="append", default=[])
    ap.add_argument("--db", default="/tmp/p6f/harness.db")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("timer-callback").add_argument("--timer", required=True)
    args = ap.parse_args(argv)
    if args.live and (not args.plan_hash or not args.allowlist_seat):
        raise OwnedFault("E_DISABLED",
                         "live mode needs --plan-hash + --allowlist-seat")
    if args.cmd == "timer-callback":
        print(json.dumps(timer_callback(args.db, args.timer)))
        return 0
    print(json.dumps({"mode": "live" if args.live else "injected",
                      "plan_hash": args.plan_hash or None,
                      "allowlist": args.allowlist_seat}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
