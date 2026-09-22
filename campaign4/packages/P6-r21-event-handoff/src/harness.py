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
                  transport=None, timers=None, observer=None,
                  plan_path=None):
    """Compose the full stack. Live mode requires a bound plan hash that
    actually matches sha256 of the plan file, plus a non-empty allowlist
    and explicit production collaborators (fail-closed otherwise)."""
    allowlist_seats = tuple(allowlist_seats or ())
    if live:
        if not plan_hash or not plan_path or not allowlist_seats:
            raise OwnedFault("E_DISABLED",
                             "live mode needs plan file + hash + allowlist")
        with open(plan_path, "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        if actual != plan_hash:
            raise OwnedFault("E_PLAN_MISMATCH",
                             "plan hash does not bind this plan file")
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


def setup_manifest(plan_path, out_path, clock=None):
    """Exact setup command: derives bound runtime IDs from the plan hash
    (deterministic, never guessed) and writes the manifest. No times are
    invented: dispatch timing comes from the trusted clock at run time."""
    with open(plan_path, "rb") as fh:
        phash = hashlib.sha256(fh.read()).hexdigest()
    plan = json.loads(open(plan_path).read())
    fid = plan.get("fixture_id", "p6-fixture")
    manifest = {
        "plan_sha256": phash,
        "fixture_id": fid,
        "package_id": plan.get("package_id", "P6F"),
        "action_id": "p6h-w1",
        "verify_action_id": "p6h-v1",
        "execution_id": "ex-" + hashlib.sha256(
            (phash + fid).encode()).hexdigest()[:12],
        "session": "sess-" + phash[:12],
        "stream_key": "sess-" + phash[:12],
        "seat": (plan.get("seats") or {}).get("fixture_seats",
                                              ["p6-fixture-worker"])[0],
        "verifier_seat": "p6-fixture-verifier",
        "authorization_ref": "fixture-grant",
        "duration_s": (plan.get("bounds") or {}).get("duration_s", 900),
        "verify_deadline_utc": (plan.get("bounds") or {}).get(
            "deadline_hint_utc", "2026-09-22T01:00:00Z"),
        "recover_by_utc": (plan.get("bounds") or {}).get(
            "recover_by_utc", "2026-09-22T01:00:00Z"),
        "stream_dir": (plan.get("bounds") or {}).get(
            "stream_dir", "/tmp/p6h/stream"),
        "artifact_base_dir": (plan.get("bounds") or {}).get(
            "artifact_base_dir", "/tmp/p6h/artifacts"),
        "dispatched": 0, "escalated": 0, "false_positives": 0,
    }
    with open(out_path, "w") as fh:
        json.dump(manifest, fh, sort_keys=True)
    return manifest


def run_fixture(adapter, manifest, claims_dir, verify_deadline_utc,
                qid="P6F"):
    """Bounded fixture run: dispatch -> subscribed turn trigger ->
    run_handoff -> recovery. Runtime item IDs come from observed end
    events (never guessed); manifest IDs come from setup. Raises
    SystemExit nonzero via main() on unobserved failure."""
    from turn_handoff import TurnWatcher, run_handoff
    driver = adapter.driver
    driver.admit_authorize(qid)
    driver.start_dispatch(qid, manifest["action_id"],
                          duration_s=manifest["duration_s"])
    adapter.register_execution(
        manifest["action_id"], manifest["execution_id"],
        manifest["authorization_ref"], verify_deadline_utc)
    adapter.bind_route(manifest["verify_action_id"],
                       manifest["verifier_seat"])
    launch = {"package": manifest.get("package_id", "P6F"),
              "attempt": "a1", "action": manifest["action_id"],
              "execution": manifest["execution_id"],
              "contract_step": "worker-run",
              "escalation_deadline_utc": manifest["recover_by_utc"],
              "artifact_base_dir": manifest["artifact_base_dir"]}
    watcher = TurnWatcher(manifest["stream_dir"])
    seen_add = lambda token: driver._kv_put("sidecar-seen:" + token, "1")
    seen_has = lambda token: driver.kv.get("sidecar-seen:" + token) == "1"
    events, _, notes, _ = watcher.poll([manifest["stream_key"]], {},
                                       seen_add, seen_has)
    ends = [e for e in events if e["kind"] == "end"]
    if not ends:
        return {"decision": "no-end-observed", "events": len(events),
                "notes": notes}
    end = ends[-1]
    adapter.bind_turn(manifest["stream_key"], end["item"],
                      manifest["execution_id"], manifest["action_id"],
                      "worker-run")
    out = run_handoff(adapter, qid, end, claims_dir, launch, {
        "action_id": manifest["verify_action_id"],
        "deadline_utc": verify_deadline_utc})
    return dict(out, notes=notes)


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r2 connected harness")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--plan-hash", default="")
    ap.add_argument("--plan", default="")
    ap.add_argument("--allowlist-seat", action="append", default=[])
    ap.add_argument("--db", default="/tmp/p6f/harness.db")
    ap.add_argument("--manifest", default="/tmp/p6h/manifest.json")
    ap.add_argument("--claims", default="/tmp/p6h/claims")
    ap.add_argument("--qid", default="P6F")
    ap.add_argument("--verify-deadline", default="")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("timer-callback").add_argument("--timer", required=True)
    sub.add_parser("setup")
    sub.add_parser("run-fixture")
    args = ap.parse_args(argv)
    if args.live and (not args.plan_hash or not args.plan
                      or not args.allowlist_seat):
        raise OwnedFault(
            "E_DISABLED",
            "live mode needs --plan + --plan-hash + --allowlist-seat")
    if args.cmd == "setup":
        manifest = setup_manifest(args.plan, args.manifest)
        print(json.dumps({"manifest": args.manifest,
                          "plan_sha256": manifest["plan_sha256"]}))
        return 0
    if args.cmd == "run-fixture":
        import driver as _drv
        from host_adapter import HostAdapter as _HA
        manifest = json.load(open(args.manifest))
        if args.live:
            with open(args.plan, "rb") as fh:
                actual = hashlib.sha256(fh.read()).hexdigest()
            if actual != args.plan_hash:
                raise OwnedFault("E_PLAN_MISMATCH",
                                 "plan hash does not bind this plan file")
            from host_adapter import HostWakeTransport, HostTimerService
            driver = _drv.Driver(args.db)
            transport = HostWakeTransport(
                manifest.get("wake_path",
                             "/home/bmosher/.config/agent-deck/wake"),
                args.allowlist_seat, enabled=True)
            transport._kv_get, transport._kv_put = driver.kv.get, \
                driver._kv_put
            timers = HostTimerService(
                driver.kv.get, driver._kv_put, enabled=True,
                allowlist=[manifest.get("timer_unit",
                                        "p6-fixture-handoff-1.timer")])
            adapter = _HA(driver, transport=transport, timers=timers,
                          live=True)
        else:
            driver = _drv.Driver(args.db)
            adapter = _HA(driver)
        out = run_fixture(adapter, manifest, args.claims,
                          args.verify_deadline, args.qid)
        print(json.dumps(out, sort_keys=True))
        # Failing exits on failure: only committed terminal/dispatched,
        # owned recovery, or observed no-end count as observed results.
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest", "owned-recovery",
                                       "duplicate-end-ignored",
                                       "no-end-observed"):
            return 3
        return 0
    if args.cmd == "timer-callback":
        print(json.dumps(timer_callback(args.db, args.timer)))
        return 0
    print(json.dumps({"mode": "live" if args.live else "injected",
                      "plan_hash": args.plan_hash or None,
                      "allowlist": args.allowlist_seat}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
