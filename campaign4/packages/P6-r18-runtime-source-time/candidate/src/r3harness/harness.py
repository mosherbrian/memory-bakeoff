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


def timer_callback(db_path, timer_id, qid=None, action_id=None,
                   execution=None):
    """Executable candidate callback: fire a due timer through ledger
    authority (argv embedded in host timer units, never `true`).

    T1: every callback carries the ledger-selected DB, qid, action and
    execution. Omitted identity fails closed (no silent P6F default);
    identity is bound to the persisted action/execution, never to
    callback self-assertion: unknown package, action mismatch and
    execution mismatch are owned failures before any deadline handling.
    """
    from ingress import HostClock as _HC
    if not qid or not action_id or not execution:
        raise OwnedFault("E_NO_IDENTITY",
                         "callback needs --db, --timer, --qid-cb, --action "
                         "and --execution; omitted identity fails closed")
    driver = Driver(db_path, _HC())
    rec = driver.store.revisions.get((qid, 1)) or {}
    if not rec:
        raise OwnedFault("E_UNKNOWN_PACKAGE",
                         "no persisted ledger package for qid " + str(qid))
    fl = rec.get("flight") or {}
    if action_id != fl.get("action_id"):
        raise OwnedFault("E_ACTION_MISMATCH",
                         "callback action %s is not the persisted current "
                         "action %s" % (action_id, fl.get("action_id")))
    current_exec = driver.kv.get("exec-current:" + action_id)
    # T1 completion: persisted execution authority is required, never
    # callback self-assertion. Missing/null/empty/malformed/superseded
    # identity deterministically rejects here: the guard never recovers
    # authority from argv alone and never creates a registration.
    if not isinstance(current_exec, str) or not current_exec.strip():
        raise OwnedFault("E_NO_EXECUTION_AUTHORITY",
                         "no persisted current execution for action "
                         + str(action_id))
    if current_exec.startswith("SUPERSEDED->"):
        raise OwnedFault("E_SUPERSEDED_ACTION",
                         "action %s is superseded; callback refused"
                         % action_id)
    if current_exec != execution:
        raise OwnedFault("E_EXECUTION_MISMATCH",
                         "callback execution %s is not the persisted "
                         "current execution %s"
                         % (execution, current_exec))
    result, dup = driver.on_deadline(action_id, qid)
    return {"timer": timer_id, "decision": result, "dedup": dup}


def _validate_stream_records(path):
    """Read-only format check: every complete line must be an actual-format
    record (JSON object with t+item). Partial trailing bytes are allowed
    (producer mid-write); corrupt complete lines fail the binding."""
    with open(path, "rb") as fh:
        data = fh.read()
    text = data.decode("utf-8", "replace")
    lines = text.split("\n")
    body = lines[:-1] if text.endswith("\n") or text == "" else lines
    # A torn tail (no trailing newline) is held, not judged.
    complete = body if (text.endswith("\n") or not text) else body[:-1]
    for line in complete:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise OwnedFault("E_CORRUPT_STREAM",
                             "non-record bytes in " + path)
        if not isinstance(row, dict) or "t" not in row \
                or "item" not in row:
            raise OwnedFault("E_CORRUPT_STREAM",
                             "non-record row in " + path)
    return True


def discover_runtime(state_root):
    """Read-only discovery of the runtime surface: stream keys, observed
    items, producer root. Never modifies, creates or truncates anything."""
    if not os.path.isdir(state_root):
        raise OwnedFault("E_UNBOUND",
                         "runtime state root absent: " + state_root)
    streams, items = {}, {}
    for fn in sorted(os.listdir(state_root)):
        if not fn.endswith(".jsonl"):
            continue
        key = fn[:-len(".jsonl")]
        path = os.path.join(state_root, fn)
        seen_items = []
        try:
            with open(path, "rb") as fh:
                for line in fh.read().decode(
                        "utf-8", "replace").split("\n"):
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(row, dict) and "item" in row:
                        seen_items.append(row["item"])
        except OSError:
            continue
        streams[key] = path
        items[key] = sorted(set(seen_items))
    return {"producer_root": state_root, "streams": streams,
            "items": items}


def setup_manifest(plan_path, out_path, session=None, stream_key=None,
                   worker_stream_key=None, verifier_stream_key=None,
                   clock=None, evidence_cmd=None):
    """Exact allowlisted setup: session and per-seat stream bindings come
    from launcher evidence — either explicit args or the output of an
    exact evidence command ({session, stream_key} JSON). Required, never
    derived, never guessed. Setup resolves them by creating the
    fixture-owned stream surface and fails closed when that is
    impossible. Runtime item IDs bind at observation, never here."""
    launcher_source = worker_socket = None
    incarnation_mtime = None
    if evidence_cmd and (not session or not stream_key
                         or not worker_stream_key
                         or not verifier_stream_key
                         or launcher_source is None):
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
        if isinstance(got, dict) and got.get("error"):
            raise OwnedFault("E_UNBOUND",
                             "launcher evidence reports: "
                             + str(got.get("error")))
        session = session or got.get("session")
        stream_key = stream_key or got.get("stream_key")
        worker_stream_key = worker_stream_key or got.get(
            "worker_stream_key")
        verifier_stream_key = verifier_stream_key or got.get(
            "verifier_stream_key")
        launcher_source = got.get("launcher_source")
        worker_socket = got.get("worker_socket")
        incarnation_mtime = got.get("incarnation_mtime")
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
    if not worker_stream_key or not verifier_stream_key:
        raise OwnedFault("E_UNBOUND",
                         "setup needs explicit --worker-stream-key and "
                         "--verifier-stream-key; suffix inference is "
                         "forbidden")
    if not os.path.isdir(stream_dir):
        raise OwnedFault("E_UNBOUND",
                         "stream directory absent: " + stream_dir)
    for key in (worker_stream_key, verifier_stream_key):
        path = os.path.join(stream_dir, key + ".jsonl")
        if os.path.exists(path):
            _validate_stream_records(path)
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
        "launcher_source": launcher_source,
        "worker_socket": worker_socket,
        "incarnation_mtime": incarnation_mtime,
        "worker_seat": seats[0] if seats else None,
        "verifier_seat": seats[1] if len(seats) > 1 else None,
        "worker_task_text": (plan.get("task_texts") or {}).get(
            "worker", "run worker step"),
        "verifier_task_text": (plan.get("task_texts") or {}).get(
            "verifier", "run verifier step"),
        "authorization_ref": "fixture-grant",
        "artifact_task": bounds.get("artifact_task", "write-out-bin"),
        "pinned_input": bounds.get("pinned_input", "fixture-bytes"),
        "incarnations": {},
        "duration_s": bounds.get("duration_s", 900),
        "verify_window_s": bounds.get("verify_window_s", 600),
        "wait_s": bounds.get("wait_s", 30),
        "live_stop_utc": plan.get("live_stop_utc"),
        "escalation_window_s": bounds.get("escalation_window_s", 60),
        "poll_interval_s": bounds.get("poll_interval_s", 1.0),
        "stream_dir": bounds.get("stream_dir", "/tmp/p6h/stream"),
        "artifact_base_dir": bounds.get("artifact_base_dir",
                                        "/tmp/p6h/artifacts"),
        "latency_path": bounds.get("latency_path",
                                   "/tmp/p6h/latency.jsonl"),
        "onset_dir": bounds.get("onset_dir",
                                os.path.join(os.path.dirname(
                                    bounds.get("stream_dir",
                                               "/tmp/p6h/stream")),
                                    "onsets")),
        "authorized_dispositions": plan.get("authorized_dispositions",
                                            []),
        "timer_units": (plan.get("allowlist") or {}).get(
            "timer_units", {}),
        "routes": plan.get("routes", {}),
        "dispatched": 0, "escalated": 0, "false_positives": 0,
        "source_mode": bounds.get("source_mode", "sidecar"),
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


def _canonical_timer_base(timer_id):
    if timer_id.endswith(".timer"):
        return timer_id[:-len(".timer")]
    return timer_id


def _canonical_unit(timer_id):
    return _canonical_timer_base(timer_id) + ".timer"


def _arm_host_timer(adapter, manifest, deadline_utc, unit, qid):
    """Invoke the configured host timer creation on the mapped unit. An
    in-memory-only timers object is never accepted as a real backstop:
    missing capability, missing allowlist or failed creation raises an
    owned failure for the caller to reconcile. T1: the callback argv
    carries the full ledger-selected identity (DB, qid, action,
    execution); qid/execution are required, never defaulted."""
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
    try:
        db_path = adapter.driver.store.path
    except AttributeError:
        db_path = "/tmp/p6h/harness.db"
    canon = _canonical_timer_base(unit)
    if not manifest.get("execution_id"):
        raise OwnedFault("E_NO_IDENTITY",
                         "arming needs a manifest execution_id for the "
                         "callback identity")
    cb = ["python3", os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "harness.py"), "--db", db_path, "timer-callback",
        "--timer", canon, "--qid-cb", qid, "--action",
        manifest["action_id"], "--execution", manifest["execution_id"]]
    return timers.create_host(canon, deadline_utc, remaining, cb)


def _build_notifier(adapter, manifest):
    from notify import DirNotifier, OwnedFaultLocal
    try:
        return DirNotifier(manifest["stream_dir"])
    except OwnedFaultLocal as e:
        raise OwnedFault("E_NO_NOTIFY",
                         "notification unavailable: " + e.detail)


def _interval_s(earlier_utc, later_utc):
    """Receipt-side interval in seconds, or None when unmeasurable."""
    from validator import _instant as _inst
    earlier, later = _inst(earlier_utc), _inst(later_utc)
    if earlier is None or later is None:
        return None
    return (later - earlier).total_seconds()


def _latency_row(action, dispatch_at, detected_at, committed_at, outcome,
                 source_at, onset_at=None, onset_provenance=None,
                 onset_uncertainty_s=None, src=None):
    """One acceptance sample. onset_at is the independently recorded
    event/fault onset (producer-side record with provenance); detection is
    onset->detected. dispatch->detected is normal worker duration, reported
    separately and never gated: long normal work then prompt detection must
    not fail merely because dispatch was long ago. Missing onset/source is
    unmeasurable, never zero, and can never pass the campaign criterion.
    P6-r18: optional runtime source receipt (src dict) rides along with
    declared mode/provenance; legacy rows carry src None."""
    row = {"action": action, "dispatch_at": dispatch_at,
           "detected_at": detected_at, "committed_at": committed_at,
           "outcome": outcome, "source_at": source_at,
           "source_time_known": source_at is not None,
           "onset_at": onset_at, "onset_provenance": onset_provenance,
           "onset_uncertainty_s": onset_uncertainty_s,
           "onset_known": onset_at is not None,
           "detection_latency_s": _interval_s(onset_at, detected_at),
           "worker_duration_s": _interval_s(dispatch_at, detected_at),
           "recovery_latency_s": _interval_s(detected_at, committed_at),
           "note": "detection is onset->detected; dispatch->detected is "
                   "worker duration only; missing onset is unmeasurable"}
    if src is not None:
        row["src_mode"] = src.get("src_mode", "runtime")
        for key in ("src_at", "src_session", "src_provenance",
                    "src_uncertainty_s", "src_clock", "src_status"):
            row[key] = src.get(key)
        row["src_known"] = bool(src.get("src_at")) and \
            src.get("src_status") == "ok"
    return row


def _source_receipt(end, mode="runtime"):
    """P6-r18: parse the trusted runtime source receipt from an observed
    end record. Returns (receipt_dict_or_None, reason). Anything missing,
    partial, malformed or version-mismatched yields (None, reason) —
    never a fabricated timestamp. The receipt is the end record's own
    versioned fields, bound to its item. Accepts both raw stream records
    and watcher events (fields under ``extra``)."""
    if not isinstance(end, dict):
        return None, "no-end-record"
    rec_in = dict(end)
    if isinstance(end.get("extra"), dict):
        rec_in.update(end["extra"])
    if rec_in.get("src_v") != 1:
        return None, "missing-src-version"
    rec = {"src_mode": mode}
    for key in ("src_at", "src_session", "src_provenance",
                "src_uncertainty_s", "src_clock", "src_status"):
        rec[key] = rec_in.get(key)
    if not rec["src_at"] or not rec["src_session"] or not rec_in.get("item"):
        return None, "partial-source"
    if rec["src_status"] != "ok":
        return None, "source-%s" % (rec["src_status"],)
    if rec["src_clock"] not in ("ok", "test"):
        return None, "clock-%s" % (rec["src_clock"],)
    unc = rec["src_uncertainty_s"]
    if not isinstance(unc, (int, float)) or isinstance(unc, bool):
        return None, "bad-uncertainty"
    rec["src_item"] = rec_in["item"]
    return rec, "ok"


def _persist_source_receipt(driver, action, execution, receipt):
    """Durably persist the observed source receipt (kv). Reopen/replay
    re-reads these bytes: a fresh source time is never stamped."""
    driver._kv_put("src-receipt:%s:%s" % (action, execution),
                   json.dumps(receipt or {"src_status": "missing"},
                              sort_keys=True))


def _onset_for(manifest, item):
    """Independently recorded event onset for a bound item: the producer
    seat writes its own append-time sidecar (see fixture_worker
    --onset-dir) with provenance and uncertainty. Returns
    (onset_at, provenance, uncertainty_s); missing file means unmeasurable,
    never zero. Never fabricated by the harness."""
    onset_dir = (manifest or {}).get("onset_dir")
    if not onset_dir or not item:
        return (None, None, None)
    try:
        rec = json.load(open(os.path.join(onset_dir, item + ".json")))
    except (OSError, ValueError):
        return (None, None, None)
    if not isinstance(rec, dict):
        return (None, None, None)
    return (rec.get("onset_at"), rec.get("provenance"),
            rec.get("uncertainty_s"))


def _observe_until(manifest, grant_deadline_utc):
    """Observation bound for one wait: the signed grant deadline for the
    awaited step, capped by a stricter signed outer live stop bound when
    present. An observation slice (wait_s) is never itself the bound: the
    observer stays alive while the grant remains valid. Returns None only
    when no bound can be established (caller keeps the wait_s slice)."""
    from validator import _instant as _inst
    cands = [grant_deadline_utc, manifest.get("live_stop_utc")]
    insts = [d for d in (_inst(c) for c in cands if c) if d is not None]
    if not insts:
        return None
    return min(insts).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wait_bound_end(watcher, adapter, manifest, stream_key, cursors,
                    seen_add, seen_has, accept, until_utc=None):
    """Wait one acceptable end on the bound stream. Ends whose item is
    already bound to a different execution are skipped (never adopted
    merely for being observed first); redelivery dedups via the durable
    seen set. Later authority checks (execution, claim, artifacts) still
    apply. The wait lasts until until_utc (a signed grant/outer-stop
    bound supplied by the caller); only when no bound is established
    does the legacy wait_s slice apply. Returns
    (end, cursors, detected_at, source_at)."""
    import os as _os
    path = _os.path.join(manifest["stream_dir"], stream_key + ".jsonl")
    try:
        start_size = _os.path.getsize(path)
    except OSError:
        start_size = 0
    notifier = _build_notifier(adapter, manifest)
    import datetime as _dt
    import time as _time
    from validator import _instant as _inst
    bound = _inst(until_utc) if until_utc else None
    if bound is None:
        bound = _inst(adapter.trusted_now()) + _dt.timedelta(
            seconds=manifest["wait_s"])
    # Wall backstop only bounds loop iterations (frozen test clocks);
    # the trusted deadline always governs the owned decision.
    wall_stop = _time.monotonic() + max(0.0, (bound - _inst(
        adapter.trusted_now())).total_seconds()) + 5.0
    try:
        while True:
            events, cursors, notes, labels = watcher.poll(
                [stream_key], cursors, seen_add, seen_has)
            for end in [e for e in events if e["kind"] == "end"]:
                if accept(end):
                    for later in [e for e in events if e is not end]:
                        driver = adapter.driver
                        driver._kv_put("sidecar-seen:" + later["_token"],
                                       "")
                    return (end, cursors, adapter.trusted_now(),
                            (end.get("extra") or {}).get("at"))
            if _inst(adapter.trusted_now()) >= bound or \
                    _time.monotonic() >= wall_stop:
                return (None, cursors, None, None)
            remaining = (bound - _inst(adapter.trusted_now())
                         ).total_seconds()
            notifier.wait(max(0.0, min(remaining, 1.0)))
    finally:
        notifier.close()


def _send_once(adapter, manifest, target_action, payload, execution):
    """R3 resume seam (sole behavioral delta vs pinned parent): the outbox
    identity is deterministic in the payload, so a reattach that finds the
    intent already sent reuses it WITHOUT a second transport send. First
    runs behave exactly as parent outbox_send (no outbox-sent record yet).
    Returns (outbox_id, resumed_bool)."""
    import hashlib as _hl
    driver = adapter.driver
    oid = "ob-%s" % _hl.sha256(json.dumps(
        payload, sort_keys=True).encode()).hexdigest()[:16]
    if driver.kv.get("outbox-sent:" + oid):
        return oid, True
    return adapter.outbox_send(target_action, payload,
                               execution=execution), False


def _r3_keep_first(driver, pairs):
    """Persist resume facts exactly once: first-run dispatch time and both
    grant deadlines. Never overwrites — a resume can never silently extend
    the grant it reconciles under."""
    for key, value in pairs:
        if driver.kv.get(key) is None:
            driver._kv_put(key, value)


def _r3_resume_facts(driver, manifest):
    base = "r3:%s:%s:" % (manifest["action_id"],
                          manifest["execution_id"])
    got = {k: driver.kv.get(base + k)
           for k in ("dispatch_at", "verify_deadline", "esc_deadline")}
    if any(v is None for v in got.values()):
        from host_adapter import OwnedFault as _OF
        raise _OF("E_NOT_RESUMABLE",
                  "no first-run dispatch facts; reattach needs a prior run")
    return got


def run_fixture(adapter, manifest, claims_dir, qid="P6F", resume=False):
    """Full worker->verifier graph through the production path.

    ONE durable sender: worker and verifier dispatches go out ONLY via
    the outbox (stable identity, ack-after-delivery); no direct harness
    sends exist on this path. A redelivery finding a completed handoff
    returns before any dispatch or send. Unbound/foreign ends are
    skipped (never adopted) while the bound waits. Latency rows carry
    receipt-side detection/recovery intervals plus explicit source-time
    knowledge flags; missing source time is unmeasurable, never zero."""
    from turn_handoff import TurnWatcher, run_handoff
    driver = adapter.driver
    if driver.kv.get("handoff-done:%s:%s" % (
            manifest["action_id"], manifest["execution_id"])):
    # Redelivery after a completed handoff: recognized duplicate
    # before any dispatch or send: never a fresh message identity.
        return {"decision": "duplicate-end-ignored", "durable": True,
                "latency_samples": 0}
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
    if resume:
        # Reattach under the ORIGINAL grant: stored dispatch facts govern;
        # nothing here extends any deadline. Expired grants escalate
        # boundedly below instead of waiting or extending.
        facts = _r3_resume_facts(driver, manifest)
        t0 = facts["dispatch_at"]
        verify_deadline = facts["verify_deadline"]
        esc_deadline = facts["esc_deadline"]
        remaining = (_inst(verify_deadline) - _inst(
            adapter.trusted_now())).total_seconds()
        if remaining <= 0:
            esc, _ = adapter.escalate_unavailable(
                manifest["action_id"], "tern", "bounded-recovery",
                esc_deadline)
            ack, _ = adapter.confirm_escalation_ack(
                manifest["action_id"])
            lat.append({"action": manifest["action_id"],
                        "dispatch_at": t0, "detected_at": None,
                        "committed_at": adapter.trusted_now(),
                        "outcome": "owned-recovery:" + ack,
                        "source_at": None, "source_time_known": False,
                        "onset_at": None, "onset_provenance": None,
                        "onset_uncertainty_s": None, "onset_known": False,
                        "detection_latency_s": None,
                        "worker_duration_s": None,
                        "recovery_latency_s": None,
                        "note": "grant-expired-at-reattach"})
            _write_latency(manifest, lat)
            return {"decision": "owned-recovery",
                    "reason": "grant-expired",
                    "escalation": esc, "escalation_ack": ack,
                    "latency_samples": len(lat), "resumed": True,
                    "resent": False}
    else:
        _r3_keep_first(driver, [
            ("r3:%s:%s:dispatch_at" % (manifest["action_id"],
                                       manifest["execution_id"]), t0),
            ("r3:%s:%s:verify_deadline" % (manifest["action_id"],
                                            manifest["execution_id"]),
             verify_deadline),
            ("r3:%s:%s:esc_deadline" % (manifest["action_id"],
                                        manifest["execution_id"]),
             esc_deadline)])
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
    adapter.bind_route(manifest["action_id"], manifest["worker_seat"])
    for routed_action, seat in (manifest.get("routes") or {}).items():
        adapter.bind_route(routed_action, seat)
    # Turn/item bindings are created at observation time (first sight of
    # each end), never pre-declared with placeholder items.
    wstream = manifest.get("worker_stream_key",
                           manifest["stream_key"])
    vstream = manifest.get("verifier_stream_key",
                           manifest["stream_key"])
    fields = {"action": manifest["action_id"],
              "execution": manifest["execution_id"], "attempt": "a1",
              "step": "worker-run", "claims": claims_dir,
              "claim_path": os.path.join(
                  claims_dir, manifest["execution_id"] + ".json"),
              "artifacts": manifest["artifact_base_dir"],
              "artifact_task": manifest.get("artifact_task", ""),
              "pinned_input": manifest.get("pinned_input", "")}
    launch = {"package": manifest["package_id"], "attempt": "a1",
              "action": manifest["action_id"],
              "execution": manifest["execution_id"],
              "contract_step": "worker-run",
              "escalation_deadline_utc": esc_deadline,
              "artifact_base_dir": manifest["artifact_base_dir"],
              "stream_dir": manifest["stream_dir"],
              "defer_verifier_send": True}
    wtext = manifest.get("worker_task_text",
                         "run worker step").format(**fields)
    woid, wresumed = _send_once(
        adapter, manifest, manifest["action_id"],
        {"kind": "wake", "seat": manifest["worker_seat"], "text": wtext,
         "action": manifest["action_id"],
         "execution": manifest["execution_id"]},
        execution=manifest["execution_id"])
    manifest["dispatched"] += 0 if (wresumed or resume) else 1
    # Deadline backstop: kv intent always, then the runner-backed host
    # timer. A missing allowlist or failed creation is an owned failure
    # that reconciles already-delivered work instead of claiming success.
    # R3: never re-arm an already-armed host timer on reattach (the
    # persisted timer-arm record proves the backstop already exists).
    adapter.arm_from_ledger("deadline:" + manifest["action_id"],
                            verify_deadline)
    _canon = _canonical_timer_base(unit)
    _canon_key = "timer-arm:" + _canon
    _existing = adapter.driver.kv.get(_canon_key) or None
    _need_arm = _existing is None
    if _existing is not None:
        # Reopen reconciles ACTUAL host facts, never kv presence alone:
        # conflicting persisted deadline/unit for this canonical identity
        # is an owned failure, never a hijack or silent extension.
        try:
            _rec = json.loads(_existing)
        except ValueError:
            _rec = {}
        if _rec.get("deadline") != verify_deadline or \
                _rec.get("unit", _canonical_unit(unit)) != \
                _canonical_unit(unit):
            return {"decision": "owned-failure",
                    "reason": "E_TIMER_CONFLICT-timer-backstop",
                    "latency_samples": 0}
        if hasattr(adapter.timers, "query_host"):
            try:
                _props = adapter.timers.query_host(_canon)
            except OwnedFault as e:
                # A failed query is never swallowed: owned failure.
                return {"decision": "owned-failure",
                        "reason": e.code + "-timer-backstop",
                        "latency_samples": 0}
            _state = (_props or {}).get("ActiveState")
            if _state == "active":
                _need_arm = False  # matching host timer exists: reuse
            elif _state in ("inactive", "failed", "dead"):
                # Host lost the timer: reconstruct ONLY the remaining
                # original grant (never a fresh interval); overdue work
                # gets bounded disposition via E_EXPIRED below.
                adapter.driver._kv_put(_canon_key, "")
                _need_arm = True
            elif _props:
                # Host answered but state is unknown: owned failure,
                # never blind reuse or blind recreate.
                return {"decision": "owned-failure",
                        "reason": "E_TIMER_UNKNOWN-timer-backstop",
                        "latency_samples": 0}
            else:
                _need_arm = False  # uninformative host: legacy kv reuse
    if _need_arm:
        try:
            _arm_host_timer(adapter, manifest, verify_deadline, unit, qid)
        except OwnedFault as e:
            return {"decision": "owned-failure",
                    "reason": e.code + "-timer-backstop",
                    "latency_samples": 0}
    launch["stream_dir"] = manifest["stream_dir"]
    watcher = TurnWatcher(manifest["stream_dir"])
    seen_add = lambda token: driver._kv_put("sidecar-seen:" + token, "1")
    seen_has = lambda token: driver.kv.get("sidecar-seen:" + token) == "1"
    notifier = _build_notifier(adapter, manifest)
    def _accept_work(end):
        binding = adapter.turn_binding(wstream, end["item"])
        if binding is None:
            return True  # first observation binds below
        return (binding.get("execution") == manifest["execution_id"]
                and binding.get("action") == manifest["action_id"]
                and binding.get("step") == "worker-run")
    end, cursors, detected_at, source_at = _wait_bound_end(
        watcher, adapter, manifest, wstream, {}, seen_add, seen_has,
        _accept_work,
        # First run keeps the bounded slice (the abnormal-delay drill
        # must be able to miss it); a same-execution reattach waits the
        # REMAINDER of the original signed grant, never a fresh slice.
        until_utc=_observe_until(manifest, verify_deadline)
        if resume else None)
    if end is None:
        if driver.kv.get("handoff-done:%s:%s" % (
                manifest["action_id"], manifest["execution_id"])):
            return {"decision": "duplicate-end-ignored", "durable": True,
                    "latency_samples": len(lat)}
        # T3: the slice missed but the signed grant is still open: this
        # is an explicit NONTERMINAL owned continuation, never a terminal
        # no-end failure. No latency row is written for an unconcluded
        # execution (T4: one execution yields rows only when it concludes).
        # The continuation carries the resume facts; reattach waits the
        # remainder of the ORIGINAL grant with zero new sends.
        _remaining = (_inst(verify_deadline) - _inst(
            adapter.trusted_now())).total_seconds()
        if _remaining > 0:
            return {"decision": "nonterminal-continuation",
                    "reason": "grant-open-continue",
                    "action_id": manifest["action_id"],
                    "execution_id": manifest["execution_id"],
                    "grant_deadline": verify_deadline,
                    "latency_samples": 0, "resent": False}
        return _finish(adapter, manifest, claims_dir, qid, None, None,
                       t0, None, "no-end", lat)
    adapter.bind_turn(wstream, end["item"],
                      manifest["execution_id"], manifest["action_id"],
                      "worker-run")
    # P6-r18: capture the trusted runtime source receipt from the SAME
    # observed bytes and persist it (kv). Reopen/replay re-reads these
    # bytes: a fresh source time is never stamped, grants never extend.
    _wsrc, _wsrc_reason = _source_receipt(
        end, manifest.get("source_mode", "sidecar"))
    _persist_source_receipt(driver, manifest["action_id"],
                            manifest["execution_id"], _wsrc)
    # T2: the verifier window starts at the contract-authorized verifier
    # dispatch (worker-end detection), never at worker dispatch: worker
    # elapsed time cannot consume it. Persisted once (keep-first), so
    # reattach/reopen can never restart or extend it. escalation_window_s
    # is recovery allowance only, never a substitute verification budget.
    # The effective bound is min(verifier deadline, outer live stop);
    # inadequate time yields a truthful bounded result, never extra budget.
    _vbase = "r3v:%s:%s:" % (manifest["verify_action_id"],
                             manifest["verify_execution_id"])
    _vstart = detected_at
    _vdeadline = (_inst(_vstart) + _dt.timedelta(
        seconds=manifest["verify_window_s"])).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
    _vesc = (_inst(_vstart) + _dt.timedelta(
        seconds=manifest["verify_window_s"]
        + manifest["escalation_window_s"])).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
    _r3_keep_first(driver, [
        (_vbase + "dispatch_at", _vstart),
        (_vbase + "verify_deadline", _vdeadline),
        (_vbase + "esc_deadline", _vesc)])
    _vstart = driver.kv.get(_vbase + "dispatch_at")
    _vdeadline = driver.kv.get(_vbase + "verify_deadline")
    _vesc = driver.kv.get(_vbase + "esc_deadline")
    _veff = _observe_until(manifest, _vdeadline)
    driver._kv_put(_vbase + "effective_deadline", _veff)
    verifier_window = {"dispatch_at": _vstart,
                       "verify_deadline": _vdeadline,
                       "esc_deadline": _vesc,
                       "effective_deadline": _veff}
    out = run_handoff(adapter, qid, end, claims_dir, launch, {
        "action_id": manifest["verify_action_id"],
        "deadline_utc": verify_deadline,
        "execution_id": manifest["verify_execution_id"]})
    lat.append(_latency_row(manifest["action_id"], t0, detected_at,
                            adapter.trusted_now(), out["decision"],
                            source_at, *_onset_for(manifest,
                                                   end["item"]),
                            src=_wsrc))
    if out["decision"] not in ("transition-committed",):
        _write_latency(manifest, lat)
        return dict(out, latency_samples=len(lat))
    # Contract-selected verifier dispatch through the same single sender.
    vfields = dict(fields, action=manifest["verify_action_id"],
                   execution=manifest["verify_execution_id"],
                   step="verify-run",
                   worker_claim_execution=manifest["execution_id"])
    vtext = manifest.get("verifier_task_text",
                         "run verifier step").format(**vfields)
    vout_oid, _vresumed = _send_once(
        adapter, manifest, manifest["verify_action_id"],
        {"kind": "wake", "seat": manifest["verifier_seat"],
         "text": vtext, "action": manifest["verify_action_id"],
         "execution": manifest["verify_execution_id"]},
        execution=manifest["verify_execution_id"])
    adapter.register_execution(
        manifest["verify_action_id"], manifest["verify_execution_id"],
        "fixture-grant", _veff)
    def _accept_verify(end):
        binding = adapter.turn_binding(vstream, end["item"])
        if binding is None:
            return True
        return (binding.get("execution") == manifest["verify_execution_id"]
                and binding.get("action") == manifest["verify_action_id"]
                and binding.get("step") == "verify-run")
    vend, cursors, vdetected, vsource = _wait_bound_end(
        watcher, adapter, manifest, vstream, cursors, seen_add, seen_has,
        _accept_verify,
        until_utc=_veff)
    if vend is None:
        # The verifier window itself is exhausted here (the wait ran to
        # the persisted window bound): honest bounded owned-recovery with
        # the recorded window as evidence, never extra budget.
        esc, _ = adapter.escalate_unavailable(
            manifest["verify_action_id"], "tern", "bounded-recovery",
            _vesc)
        ack, _ = adapter.confirm_escalation_ack(
            manifest["verify_action_id"])
        lat.append({"action": manifest["verify_action_id"],
                    "dispatch_at": detected_at, "detected_at": None,
                    "committed_at": adapter.trusted_now(),
                    "outcome": "owned-recovery:" + ack,
                    "source_at": None, "source_time_known": False,
                    "onset_at": None, "onset_provenance": None,
                    "onset_uncertainty_s": None, "onset_known": False,
                    "detection_latency_s": None,
                    "worker_duration_s": None,
                    "recovery_latency_s": None,
                    "note": "verifier-no-end"})
        _write_latency(manifest, lat)
        return {"decision": "owned-recovery", "reason": "verifier-no-end",
                "escalation": esc, "escalation_ack": ack,
                "latency_samples": len(lat),
                "verifier_window": verifier_window}
    adapter.bind_turn(vstream, vend["item"],
                      manifest["verify_execution_id"],
                      manifest["verify_action_id"], "verify-run")
    _vsrc, _vsrc_reason = _source_receipt(
        vend, manifest.get("source_mode", "sidecar"))
    _persist_source_receipt(driver, manifest["verify_action_id"],
                            manifest["verify_execution_id"], _vsrc)
    vlaunch = dict(launch, action=manifest["verify_action_id"],
                   execution=manifest["verify_execution_id"],
                   contract_step="verify-run",
                   stream_dir=manifest["stream_dir"],
                   authorized_dispositions=manifest[
                       "authorized_dispositions"])
    vout = run_handoff(adapter, qid, vend, claims_dir, vlaunch)
    vdetected_at = adapter.trusted_now()
    vonset, vonset_prov, vonset_unc = _onset_for(manifest, vend["item"])
    vrow = _latency_row(manifest["verify_action_id"], detected_at,
                        vdetected_at, adapter.trusted_now(),
                        vout["decision"], vsource, vonset, vonset_prov,
                        vonset_unc, src=_vsrc)
    vrow["worker_duration_s"] = _interval_s(detected_at, vdetected_at)
    vrow["recovery_latency_s"] = _interval_s(vdetected_at,
                                             adapter.trusted_now())
    vrow["note"] = "detection is onset->detected; dispatch->detected " \
                   "is worker duration only"
    lat.append(vrow)
    _write_latency(manifest, lat)
    # O: settle delivered intents only on transport + ledger proof.
    settled = adapter.drain_outbox_settled(qid)
    final = dict(vout, worker=out, worker_outbox=woid,
                 verifier_outbox=vout_oid, latency_samples=len(lat),
                 outbox_settled=settled, verifier_window=verifier_window)
    return final



def _write_latency(manifest, samples):
    if not samples:
        # T4: an unconcluded execution writes no fabricated row. Only a
        # genuinely concluded-unknown signal is recorded, labelled
        # INCOMPLETE (never a manufactured zero-latency recovery and
        # never a no-end-failure row).
        samples = [{"action": manifest["action_id"], "dispatch_at": None,
                    "detected_at": None, "committed_at": None,
                    "outcome": "incomplete-unmeasured",
                    "source_uncertainty_s": None,
                    "note": "zero-signal sample; unmeasurable, must fail "
                            "gates as INCOMPLETE"}]
    with open(manifest["latency_path"], "a") as fh:
        for row in samples:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return len(samples)


def _finish(adapter, manifest, claims_dir, qid, end, launch, t0,
            verify_spec, reason, lat):
    _write_latency(manifest, lat)
    return {"decision": "owned-failure", "reason": reason,
            "latency_samples": len(lat)}


def check_latency(latency_path, source_mode="sidecar"):
    """Honest gate check: requires a positive successful recovery sample;
    every row must carry real timestamps (missing/unknown fails); failures
    stay in the denominator report; unacked escalations never count as
    recovery. Returns a verdict dict; raises OwnedFault on gate failure.
    P6-r18: in runtime source mode the event instant is the runtime
    source receipt (src_at) instead of the sidecar onset; rows without a
    usable source stay unmeasurable. Source, detection and recovery
    clocks remain distinct."""
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
    if any(r.get("outcome") == "no-end-failure" for r in rows):
        raise OwnedFault("E_BAD_SAMPLE",
                         "fabricated no-end-failure row; normal "
                         "slice/continuation/success is ONE execution")
    if not success:
        raise OwnedFault("E_NO_SUCCESS",
                         "no positive successful recovery sample")
    failures = [r for r in rows if r not in success]
    # Event instant per declared source mode: runtime receipts use the
    # trusted end-append time; sidecar mode uses the producer onset.
    # Missing onset/source can never pass the campaign criterion: report
    # receipt-to-recovery separately and return UNMEASURABLE/INCOMPLETE.
    def _event_at(r):
        if source_mode == "runtime" and r.get("src_known"):
            return r.get("src_at")
        return r.get("onset_at")

    unknown = [r for r in success if not _event_at(r)]
    for r in success:
        if r.get("source_time_known") and r.get("source_at") is None:
            raise OwnedFault("E_BAD_SAMPLE",
                             "source time claimed but absent")
        rec = (_ts(r["committed_at"]) - _ts(r["detected_at"])
               ).total_seconds()
        if rec > 60:
            raise OwnedFault("E_GATE_RECOVER",
                             "detection->recovery exceeded 60s")
    if unknown:
        rec_max = max((_ts(r["committed_at"]) - _ts(r["detected_at"])
                       ).total_seconds() for r in success)
        return {"verdict": "unmeasurable-incomplete",
                "reason": "onset/source evidence missing for %d of %d "
                          "success rows; event-to-detection unmeasurable; "
                          "receipt-to-recovery max %.1fs reported separately"
                          % (len(unknown), len(success), rec_max),
                "samples": len(rows), "success": len(success),
                "failures": len(failures),
                "unmeasured": len(unknown),
                "failure_outcomes": sorted(
                    {r.get("outcome") for r in failures})}
    for r in success:
        det = (_ts(r["detected_at"]) - _ts(_event_at(r))).total_seconds()
        rec = (_ts(r["committed_at"]) - _ts(r["detected_at"])
               ).total_seconds()
        if det < 0:
            raise OwnedFault("E_BAD_SAMPLE",
                             "detection precedes recorded source event")
        if det > 30:
            raise OwnedFault("E_GATE_DETECT",
                             "onset-to-detection exceeded 30s")
        if det + rec > 90:
            raise OwnedFault("E_GATE_TOTAL",
                             "onset-to-recovery total exceeded 90s")
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
    ap.add_argument("--worker-stream-key", default="")
    ap.add_argument("--verifier-stream-key", default="")
    ap.add_argument("--evidence-cmd", default="")
    sub = ap.add_subparsers(dest="cmd")
    _tcb = sub.add_parser("timer-callback")
    _tcb.add_argument("--timer", required=True)
    _tcb.add_argument("--action", default=None)
    _tcb.add_argument("--qid-cb", default=None)
    _tcb.add_argument("--execution", default=None)
    sub.add_parser("setup")
    sub.add_parser("run-fixture")
    # R3: reattach consumes late completion under the same action/execution
    # without a second send (see run_fixture resume seam). Same adapter
    # construction as run-fixture; no new authority.
    sub.add_parser("reattach")
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
            args.worker_stream_key or None,
            args.verifier_stream_key or None,
            evidence_cmd=_sh.split(args.evidence_cmd)
            if args.evidence_cmd else None)
        print(json.dumps({"manifest": args.manifest,
                          "plan_sha256": manifest["plan_sha256"]}))
        return 0
    if args.cmd in ("run-fixture", "reattach"):
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
                systemctl=allow.get("systemctl", "systemctl"),
                runner=None)
            adapter = HostAdapter(driver, clock=driver.clock,
                                  transport=transport, timers=timers,
                                  live=True)
        else:
            driver = Driver(args.db)
            adapter = HostAdapter(driver)
        manifest = json.load(open(args.manifest))
        out = run_fixture(adapter, manifest, args.claims, args.qid,
                          resume=(args.cmd == "reattach"))
        print(json.dumps(out, sort_keys=True))
        return _exit_for(out)
    if args.cmd == "timer-callback":
        print(json.dumps(timer_callback(
            args.db, args.timer, qid=args.qid_cb,
            action_id=args.action, execution=args.execution)))
        return 0
    if args.cmd == "check-latency":
        manifest = json.load(open(args.manifest))
        verdict = check_latency(manifest["latency_path"],
                                manifest.get("source_mode", "sidecar"))
        print(json.dumps(verdict, sort_keys=True))
        return 0 if verdict.get("verdict") == "gates-hold" else 3
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
