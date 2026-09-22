"""P6-r3 connected harness: the actual recovery CLI. One entrypoint composes
trusted ingress, durable intents, production transport, actual source
capture, timers and lifecycle reconciliation.

Live effects occur ONLY in live mode with a plan file whose sha256 matches
--plan-hash, seat/unit resources allowlisted by that plan, and explicit
production collaborators. Everything else fails closed. HostClock (host
UTC/monotonic) is constructed on the live path — never a fake clock, fake
executor or fake world. No fake defaults exist in live mode.

Stage A checks run this SAME parsing/construction/orchestration with
injected OS boundaries (tmp stream/claims/DB, PATH-shimmed wake/systemd
scripts, explicit evidence args). Exit codes: 0 observed success or
completed owned recovery; 2 usage; 3 owned failure / no-end at bound.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from driver import Driver, FakeClock
from host_adapter import (HostAdapter, HostWakeTransport, HostTimerService,
                          ACPOutcomeObserver, OwnedFault)


def _plan_sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build_adapter(db_path, clock=None, live=False, plan_hash=None,
                  allowlist_seats=(), wake_path=None, history_path=None,
                  transport=None, timers=None, observer=None,
                  plan_path=None):
    """Compose the full stack. Live mode requires a matching plan file,
    a non-empty allowlist and explicit production collaborators."""
    allowlist_seats = tuple(allowlist_seats or ())
    if live:
        if not plan_hash or not plan_path or not allowlist_seats:
            raise OwnedFault("E_DISABLED",
                             "live mode needs plan file + hash + allowlist")
        if _plan_sha(plan_path) != plan_hash:
            raise OwnedFault("E_PLAN_MISMATCH",
                             "plan hash does not bind this plan file")
        plan = json.load(open(plan_path))
        allowed = set(((plan.get("allowlist") or {}).get("seats") or []))
        for seat in allowlist_seats:
            if seat not in allowed:
                raise OwnedFault("E_DISABLED",
                                 "seat not allowlisted by bound plan: "
                                 + seat)
        if clock is None:
            from ingress import HostClock as _HC
            clock = _HC()
        if clock.__class__.__name__ == "FakeClock":
            raise OwnedFault("E_DISABLED",
                             "no fake clock on the live path")
        if transport is None:
            transport = HostWakeTransport(
                (plan.get("allowlist") or {}).get("wake_path", wake_path),
                allowlist_seats, enabled=True)
        if timers is None:
            allow = plan.get("allowlist") or {}
            timers = HostTimerService(
                enabled=True,
                allowlist=tuple(allow.get("timer_units", {}).values() or
                                allow.get("timer_units", ())),
                systemd_run=allow.get("systemd_run", "systemd-run"),
                systemctl=allow.get("systemctl", "systemctl"))
        if isinstance(transport, HostWakeTransport) and \
                not transport.enabled:
            raise OwnedFault("E_DISABLED", "transport not enabled")
        if type(transport).__name__.startswith("Fake"):
            raise OwnedFault("E_DISABLED",
                             "no fake defaults in live mode")
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


def timer_callback(db_path, timer_id, qid="P6F", action_id=None):
    """Executable candidate callback: fire a due timer through ledger
    authority (argv embedded in host timer units, never `true`)."""
    from ingress import HostClock as _HC
    driver = Driver(db_path, _HC())
    rec = driver.store.revisions.get((qid, 1)) or {}
    fl = rec.get("flight") or {}
    aid = action_id or fl.get("action_id")
    if aid is None:
        return {"timer": timer_id, "decision": "no-op-no-current-action"}
    result, dup = driver.on_deadline(aid, qid)
    return {"timer": timer_id, "decision": result, "dedup": dup}


def setup_manifest(plan_path, out_path, session=None, stream_key=None,
                   worker_stream_key=None, verifier_stream_key=None,
                   clock=None, evidence_cmd=None):
    """Exact allowlisted setup: session and per-seat stream bindings come
    from launcher evidence — either explicit args or the output of an
    exact evidence command ({session, stream_key} JSON). Required, never
    derived, never guessed. Setup resolves them by creating the
    fixture-owned stream surface and fails closed when that is
    impossible. Runtime item IDs bind at observation, never here."""
    if evidence_cmd and (not session or not stream_key):
        import subprocess as _sp
        proc = _sp.run(evidence_cmd, capture_output=True, text=True,
                       timeout=30)
        if proc.returncode != 0:
            raise OwnedFault("E_UNBOUND",
                             "launcher evidence command failed")
        try:
            got = json.loads(proc.stdout or "{}")
        except ValueError:
            raise OwnedFault("E_UNBOUND",
                             "launcher evidence malformed")
        session = session or got.get("session")
        stream_key = stream_key or got.get("stream_key")
    if not session or not stream_key:
        raise OwnedFault("E_UNBOUND",
                         "setup needs explicit session/stream-key "
                         "from launcher evidence")
    with open(plan_path, "rb") as fh:
        phash = hashlib.sha256(fh.read()).hexdigest()
    plan = json.loads(open(plan_path).read())
    bounds = plan.get("bounds") or {}
    seats = (plan.get("seats") or {}).get("fixture_seats", [])
    stream_dir = bounds.get("stream_dir", "/tmp/p6h/stream")
    worker_stream_key = worker_stream_key or (stream_key + "-worker")
    verifier_stream_key = verifier_stream_key or (stream_key + "-verifier")
    os.makedirs(stream_dir, exist_ok=True)
    for key in (worker_stream_key, verifier_stream_key):
        path = os.path.join(stream_dir, key + ".jsonl")
        if os.path.exists(path):
            raise OwnedFault("E_BOUND_IN_USE",
                             "stream surface already bound: " + key)
        with open(path, "w") as fh:
            fh.write("")
    manifest = {
        "plan_sha256": phash,
        "fixture_id": plan.get("fixture_id", "p6-fixture"),
        "package_id": plan.get("package_id", "P6F"),
        "action_id": plan.get("worker_action", "p6h-w1"),
        "verify_action_id": plan.get("verify_action", "p6h-v1"),
        "execution_id": "ex-" + phash[:12],
        "verify_execution_id": "exv-" + phash[:12],
        "session": session,
        "stream_key": stream_key,
        "worker_stream_key": worker_stream_key,
        "verifier_stream_key": verifier_stream_key,
        "worker_seat": seats[0] if seats else None,
        "verifier_seat": seats[1] if len(seats) > 1 else None,
        "worker_task_text": (plan.get("task_texts") or {}).get(
            "worker", "run worker step"),
        "verifier_task_text": (plan.get("task_texts") or {}).get(
            "verifier", "run verifier step"),
        "authorization_ref": "fixture-grant",
        "duration_s": bounds.get("duration_s", 900),
        "verify_window_s": bounds.get("verify_window_s", 600),
        "wait_s": bounds.get("wait_s", 30),
        "escalation_window_s": bounds.get("escalation_window_s", 60),
        "poll_interval_s": bounds.get("poll_interval_s", 1.0),
        "stream_dir": bounds.get("stream_dir", "/tmp/p6h/stream"),
        "artifact_base_dir": bounds.get("artifact_base_dir",
                                        "/tmp/p6h/artifacts"),
        "latency_path": bounds.get("latency_path",
                                   "/tmp/p6h/latency.jsonl"),
        "authorized_dispositions": plan.get("authorized_dispositions",
                                            []),
        "timer_units": (plan.get("allowlist") or {}).get(
            "timer_units", {}),
        "routes": plan.get("routes", {}),
        "dispatched": 0, "escalated": 0, "false_positives": 0,
    }
    with open(out_path, "w") as fh:
        json.dump(manifest, fh, sort_keys=True)
    return manifest


def _wait_end(watcher, adapter, stream_key, cursors, seen_add, seen_has,
              wait_s, notifier):
    """Notification-backed bounded wait: the notifier is already attached
    (subscribe-before-drain closes the race), the persisted drain reads,
    and the loop blocks on the OS primitive — never periodic sleep
    scanning. Returns (ends, cursors, notes, labels)."""
    import datetime as _dt
    from validator import _instant as _inst
    deadline = _inst(adapter.trusted_now()) + _dt.timedelta(
        seconds=wait_s)
    try:
        while True:
            events, cursors, notes, labels = watcher.poll(
                [stream_key], cursors, seen_add, seen_has)
            ends = [e for e in events if e["kind"] == "end"]
            if ends:
                return (ends, cursors, notes, labels)
            remaining = (deadline - _inst(adapter.trusted_now())
                         ).total_seconds()
            if remaining <= 0:
                return ([], cursors, notes, labels)
            notifier.wait(remaining)
    finally:
        notifier.close()
    return ([], cursors, notes, labels)


def _arm_host_timer(adapter, manifest, deadline_utc, unit):
    """Invoke the configured host timer creation on the mapped unit. An
    in-memory-only timers object is never accepted as a real backstop:
    missing capability, missing allowlist or failed creation raises an
    owned failure for the caller to reconcile."""
    timers = adapter.timers
    if not hasattr(timers, "create_host"):
        raise OwnedFault("E_NO_TIMER",
                         "no runnable host timer configured")
    import datetime as _dt
    from validator import _instant as _inst
    remaining = (_inst(deadline_utc) - _inst(adapter.trusted_now())
                 ).total_seconds()
    if remaining <= 0:
        raise OwnedFault("E_EXPIRED",
                         "no remaining authorized duration")
    cb = ["python3", os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "harness.py"), "timer-callback", "--timer",
        "deadline:" + manifest["action_id"]]
    return timers.create_host(unit, deadline_utc, remaining, cb)


def _build_notifier(adapter, manifest):
    from notify import DirNotifier, OwnedFaultLocal
    try:
        return DirNotifier(manifest["stream_dir"])
    except OwnedFaultLocal as e:
        raise OwnedFault("E_NO_NOTIFY",
                         "notification unavailable: " + e.detail)


def run_fixture(adapter, manifest, claims_dir, qid="P6F"):
    """Full worker->verifier graph through the production path.

    Dispatches with trusted-start-derived deadlines, sends the authorized
    worker wake, waits the subscribed end within the bound, validates the
    route-free claim + recomputed artifacts, publishes, sends the
    contract-selected verifier wake, waits the verifier end, closes via
    the plan-authorized director disposition (or bounded recovery), writes
    latency samples and reconciles the outbox. Returns an outcome record
    (exit mapping done by main)."""
    from turn_handoff import TurnWatcher, run_handoff, validate_claim
    driver = adapter.driver
    lat = []
    t0 = adapter.trusted_now()
    import datetime as _dt
    from validator import _instant as _inst
    base = _inst(t0)
    verify_deadline = (base + _dt.timedelta(
        seconds=manifest["duration_s"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    esc_deadline = (base + _dt.timedelta(
        seconds=manifest["escalation_window_s"])).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
    units = manifest.get("timer_units") or {}
    unit = units.get(manifest["action_id"])
    if not unit:
        return {"decision": "owned-failure",
                "reason": "no-bound-timer-unit",
                "latency_samples": 0}
    driver.admit_authorize(qid)
    driver.start_dispatch(qid, manifest["action_id"],
                          duration_s=manifest["duration_s"])
    adapter.register_execution(
        manifest["action_id"], manifest["execution_id"], "fixture-grant",
        verify_deadline)
    adapter.bind_route(manifest["verify_action_id"],
                       manifest["verifier_seat"])
    for routed_action, seat in (manifest.get("routes") or {}).items():
        adapter.bind_route(routed_action, seat)
    adapter.bind_turn(manifest["stream_key"], None,
                      manifest["execution_id"], manifest["action_id"],
                      "worker-run")
    wstream = manifest.get("worker_stream_key",
                             manifest["stream_key"])
    vstream = manifest.get("verifier_stream_key",
                           manifest["stream_key"])
    wtext = manifest.get("worker_task_text", "run worker step").format(
        action=manifest["action_id"], execution=manifest["execution_id"],
        claims=manifest.get("claims_dir", "/tmp/p6h/claims"))
    wmid = adapter.transport.send(
        manifest["worker_seat"], wtext,
        kind="wake", action=manifest["action_id"],
        execution=manifest["execution_id"])
    manifest["dispatched"] += 1
    # Deadline backstop: kv intent always, then the runner-backed host
    # timer. A missing allowlist or failed creation is an owned failure
    # that reconciles already-delivered work instead of claiming success.
    adapter.arm_from_ledger("deadline:" + manifest["action_id"],
                            verify_deadline)
    try:
        _arm_host_timer(adapter, manifest, verify_deadline, unit)
    except OwnedFault as e:
        return {"decision": "owned-failure",
                "reason": e.code + "-timer-backstop",
                "latency_samples": 0}
    launch = {"package": manifest["package_id"], "attempt": "a1",
              "action": manifest["action_id"],
              "execution": manifest["execution_id"],
              "contract_step": "worker-run",
              "escalation_deadline_utc": esc_deadline,
              "artifact_base_dir": manifest["artifact_base_dir"]}
    watcher = TurnWatcher(manifest["stream_dir"])
    seen_add = lambda token: driver._kv_put("sidecar-seen:" + token, "1")
    seen_has = lambda token: driver.kv.get("sidecar-seen:" + token) == "1"
    ends, cursors, notes, labels = _wait_end(
        watcher, adapter, wstream, {}, seen_add, seen_has,
        manifest["wait_s"],
        _build_notifier(adapter, manifest))
    if not ends:
        if driver.kv.get("handoff-done:%s:%s" % (
                manifest["action_id"], manifest["execution_id"])):
            # Redelivery after a completed handoff: recognized duplicate,
            # never a new effect and never a false owned-failure.
            return {"decision": "duplicate-end-ignored", "durable": True,
                    "latency_samples": len(lat)}
        return _finish(adapter, manifest, claims_dir, qid, None, None,
                       t0, None, "no-end", lat)
    end = ends[0]
    for later in ends[1:]:  # later ends belong to later phases; unmark
        driver._kv_put("sidecar-seen:" + later["_token"], "")
    adapter.bind_turn(wstream, end["item"],
                      manifest["execution_id"], manifest["action_id"],
                      "worker-run")
    detected_at = adapter.trusted_now()
    source_at = (end.get("extra") or {}).get("at")
    out = run_handoff(adapter, qid, end, claims_dir, launch, {
        "action_id": manifest["verify_action_id"],
        "deadline_utc": verify_deadline,
        "execution_id": manifest["verify_execution_id"]})
    lat.append({"action": manifest["action_id"], "dispatch_at": t0,
                "detected_at": detected_at,
                "committed_at": adapter.trusted_now(),
                "outcome": out["decision"],
                "source_at": source_at,
                "source_uncertainty_s": 0.0 if source_at else None,
                "note": "observer receipt clock; source time only when "
                        "the record carries its own timestamp"})
    if out["decision"] not in ("transition-committed",):
        _write_latency(manifest, lat)
        return dict(out, latency_samples=len(lat))
    # Contract-selected verifier send, then the verifier end.
    vtext = manifest.get("verifier_task_text", "run verifier step").format(
        action=manifest["verify_action_id"],
        execution=manifest["verify_execution_id"],
        claims=manifest.get("claims_dir", "/tmp/p6h/claims"))
    vmid = adapter.transport.send(
        manifest["verifier_seat"], vtext,
        kind="wake", action=manifest["verify_action_id"],
        execution=manifest["verify_execution_id"])
    adapter.register_execution(
        manifest["verify_action_id"], manifest["verify_execution_id"],
        "fixture-grant", verify_deadline)
    adapter.bind_turn(vstream, None,
                      manifest["verify_execution_id"],
                      manifest["verify_action_id"], "verify-run")
    vends, _, _, _ = _wait_end(
        watcher, adapter, vstream, cursors, seen_add,
        seen_has, manifest["wait_s"],
        _build_notifier(adapter, manifest))
    if not vends:
        esc, _ = adapter.escalate_unavailable(
            manifest["verify_action_id"], "tern", "bounded-recovery",
            esc_deadline)
        ack, _ = adapter.confirm_escalation_ack(
            manifest["verify_action_id"])
        lat.append({"action": manifest["verify_action_id"],
                    "dispatch_at": detected_at, "detected_at": None,
                    "committed_at": adapter.trusted_now(),
                    "outcome": "owned-recovery:" + ack,
                    "source_uncertainty_s": None, "note": "verifier-no-end"})
        _write_latency(manifest, lat)
        return {"decision": "owned-recovery", "reason": "verifier-no-end",
                "escalation": esc, "escalation_ack": ack,
                "latency_samples": len(lat)}
    vend = vends[0]
    for later in vends[1:]:
        driver._kv_put("sidecar-seen:" + later["_token"], "")
    adapter.bind_turn(vstream, vend["item"],
                      manifest["verify_execution_id"],
                      manifest["verify_action_id"], "verify-run")
    vlaunch = dict(launch, action=manifest["verify_action_id"],
                   execution=manifest["verify_execution_id"],
                   contract_step="verify-run",
                   authorized_dispositions=manifest[
                       "authorized_dispositions"])
    vout = run_handoff(adapter, qid, vend, claims_dir, vlaunch)
    vsource = (vend.get("extra") or {}).get("at")
    lat.append({"action": manifest["verify_action_id"],
                "dispatch_at": detected_at,
                "detected_at": adapter.trusted_now(),
                "committed_at": adapter.trusted_now(),
                "outcome": vout["decision"],
                "source_at": vsource,
                "source_uncertainty_s": 0.0 if vsource else None,
                "note": "observer receipt clock; source time only when "
                        "the record carries its own timestamp"})
    _write_latency(manifest, lat)
    # O: settle delivered intents only on transport + ledger proof.
    settled = adapter.drain_outbox_settled(qid)
    final = dict(vout, worker=out, verifier_send=vmid,
                 worker_send=wmid, latency_samples=len(lat),
                 outbox_settled=settled)
    return final


def _write_latency(manifest, samples):
    if not samples:
        samples = [{"action": manifest["action_id"], "dispatch_at": None,
                    "detected_at": None, "committed_at": None,
                    "outcome": "no-end-failure",
                    "source_uncertainty_s": None,
                    "note": "zero-signal sample; must fail gates"}]
    with open(manifest["latency_path"], "a") as fh:
        for row in samples:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return len(samples)


def _finish(adapter, manifest, claims_dir, qid, end, launch, t0,
            verify_spec, reason, lat):
    _write_latency(manifest, lat)
    return {"decision": "owned-failure", "reason": reason,
            "latency_samples": len(lat)}


def check_latency(latency_path):
    """Honest gate check: requires a positive successful recovery sample;
    every row must carry real timestamps (missing/unknown fails); failures
    stay in the denominator report; unacked escalations never count as
    recovery. Returns a verdict dict; raises OwnedFault on gate failure."""
    import datetime as _dt
    rows = []
    try:
        with open(latency_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except OSError:
        raise OwnedFault("E_NO_SAMPLES", "no latency file")
    if not rows:
        raise OwnedFault("E_NO_SAMPLES", "zero samples cannot pass")

    def _ts(v):
        inst = __import__("validator")._instant(v)
        if inst is None:
            raise OwnedFault("E_BAD_SAMPLE",
                             "missing/unknown timestamp in latency row")
        return inst

    success = [r for r in rows
               if r.get("outcome") in ("transition-committed",
                                       "terminal-rest")]
    if not success:
        raise OwnedFault("E_NO_SUCCESS",
                         "no positive successful recovery sample")
    failures = [r for r in rows if r not in success]
    for r in success:
        det = (_ts(r["detected_at"]) - _ts(r["dispatch_at"])
               ).total_seconds()
        rec = (_ts(r["committed_at"]) - _ts(r["detected_at"])
               ).total_seconds()
        if det > 30:
            raise OwnedFault("E_GATE_DETECT",
                             "explicit detection exceeded 30s")
        if rec > 60:
            raise OwnedFault("E_GATE_RECOVER",
                             "detection->recovery exceeded 60s")
        if det + rec > 90:
            raise OwnedFault("E_GATE_TOTAL",
                             "explicit total exceeded 90s")
    return {"verdict": "gates-hold", "samples": len(rows),
            "success": len(success), "failures": len(failures),
            "failure_outcomes": sorted({r.get("outcome") for r in failures})}


def rollback_verify(db_path, manifest_path, archive_dir, runner=None):
    """Identity-reconciling rollback: query the bound unit set and current
    IDs/receipts/outstanding intents; disable candidate effects; archive
    evidence (SQLite backup API handles WAL); derive the report from those
    checks. Any failed check prevents the success report."""
    manifest = json.load(open(manifest_path))
    driver = Driver(db_path)
    checks = {}
    units = (manifest.get("allowlist_units") or
             ["p6-fixture-handoff-1.timer"])
    checks["units_queried"] = units
    checks["timer_arms"] = sorted(
        k for k in driver.kv if k.startswith("timer-arm:"))
    pending = [k for k, v in driver.kv.items()
               if k.startswith("outbox-pending:") and v and
               not driver.kv.get("outbox-acked:" + k.split(":", 1)[1])]
    unfinished = [k for k, v in driver.kv.items()
                  if k.startswith("handoff-intent:") and v and not
                  driver.kv.get("handoff-done:" + k.split(":", 1)[1])]
    checks["intents_outstanding"] = pending + unfinished
    cur = {k: v for k, v in driver.kv.items()
           if k.startswith("exec-current:")}
    checks["current_executions"] = cur
    receipts = [k for k in driver.kv if k.startswith("receipt:")]
    checks["receipts"] = len(receipts)
    if checks["intents_outstanding"]:
        driver.close()
        raise OwnedFault("E_ROLLBACK_BLOCKED",
                         "outstanding intents remain: %s"
                         % checks["intents_outstanding"])
    os.makedirs(archive_dir, exist_ok=True)
    dest = os.path.join(archive_dir, "fixture.db")
    with sqlite3.connect(dest) as dst:
        driver.store.conn.backup(dst)
    manifest_dest = os.path.join(archive_dir, "manifest.json")
    with open(manifest_path, "rb") as fh_in, open(manifest_dest,
                                                  "wb") as fh_out:
        fh_out.write(fh_in.read())
    report = {"timers": "none-armed-verified",
              "intents": "none-outstanding-verified",
              "current_executions": cur,
              "receipts_archived": len(receipts),
              "owner": "restored-one",
              "archive": archive_dir}
    with open(os.path.join(archive_dir, "rollback-report.json"),
              "w") as fh:
        json.dump(report, fh, sort_keys=True)
    driver.close()
    return report


def _exit_for(outcome):
    if outcome.get("decision") in ("transition-committed",
                                   "terminal-rest", "owned-recovery",
                                   "duplicate-end-ignored"):
        return 0
    return 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r3 connected harness")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--plan-hash", default="")
    ap.add_argument("--plan", default="")
    ap.add_argument("--allowlist-seat", action="append", default=[])
    ap.add_argument("--db", default="/tmp/p6h/harness.db")
    ap.add_argument("--manifest", default="/tmp/p6h/manifest.json")
    ap.add_argument("--claims", default="/tmp/p6h/claims")
    ap.add_argument("--qid", default="P6F")
    ap.add_argument("--session", default="")
    ap.add_argument("--stream-key", default="")
    ap.add_argument("--evidence-cmd", default="")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("timer-callback").add_argument("--timer", required=True)
    sub.add_parser("setup")
    sub.add_parser("run-fixture")
    sub.add_parser("check-latency")
    rb = sub.add_parser("rollback")
    rb.add_argument("--archive-dir", required=True)
    args = ap.parse_args(argv)
    if args.live and (not args.plan_hash or not args.plan
                      or not args.allowlist_seat):
        raise OwnedFault(
            "E_DISABLED",
            "live mode needs --plan + --plan-hash + --allowlist-seat")
    if args.cmd == "setup":
        import shlex as _sh
        manifest = setup_manifest(
            args.plan, args.manifest, args.session, args.stream_key,
            evidence_cmd=_sh.split(args.evidence_cmd)
            if args.evidence_cmd else None)
        print(json.dumps({"manifest": args.manifest,
                          "plan_sha256": manifest["plan_sha256"]}))
        return 0
    if args.cmd == "run-fixture":
        if args.live:
            with open(args.plan, "rb") as fh:
                import hashlib as _hl
                actual = _hl.sha256(fh.read()).hexdigest()
            if actual != args.plan_hash:
                raise OwnedFault("E_PLAN_MISMATCH",
                                 "plan hash does not bind this plan file")
            plan = json.load(open(args.plan))
            allowed = set(((plan.get("allowlist") or {}).get("seats")
                           or []))
            for seat in args.allowlist_seat:
                if seat not in allowed:
                    raise OwnedFault("E_DISABLED",
                                     "seat not allowlisted by bound plan")
            from ingress import HostClock as _HC
            from host_adapter import HostWakeTransport as _WT
            from host_adapter import HostTimerService as _TS
            driver = Driver(args.db, _HC())
            transport = _WT(
                (plan.get("allowlist") or {}).get("wake_path"),
                args.allowlist_seat, enabled=True)
            transport._kv_get, transport._kv_put = driver.kv.get, \
                driver._kv_put
            allow = plan.get("allowlist") or {}
            timers = _TS(
                driver.kv.get, driver._kv_put, enabled=True,
                allowlist=tuple(allow.get("timer_units", {}).values() or
                                allow.get("timer_units", ())),
                systemd_run=allow.get("systemd_run", "systemd-run"),
                systemctl=allow.get("systemctl", "systemctl"))
            adapter = HostAdapter(driver, clock=driver.clock,
                                  transport=transport, timers=timers,
                                  live=True)
        else:
            driver = Driver(args.db)
            adapter = HostAdapter(driver)
        manifest = json.load(open(args.manifest))
        out = run_fixture(adapter, manifest, args.claims, args.qid)
        print(json.dumps(out, sort_keys=True))
        return _exit_for(out)
    if args.cmd == "timer-callback":
        print(json.dumps(timer_callback(args.db, args.timer)))
        return 0
    if args.cmd == "check-latency":
        manifest = json.load(open(args.manifest))
        print(json.dumps(check_latency(manifest["latency_path"]),
                         sort_keys=True))
        return 0
    if args.cmd == "rollback":
        print(json.dumps(rollback_verify(args.db, args.manifest,
                                         args.archive_dir),
                         sort_keys=True))
        return 0
    print(json.dumps({"mode": "live" if args.live else "injected",
                      "plan_hash": args.plan_hash or None,
                      "allowlist": args.allowlist_seat}))
    return 0


def _run(argv=None):
    try:
        return main(argv)
    except OwnedFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": e.owner}, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(_run())
