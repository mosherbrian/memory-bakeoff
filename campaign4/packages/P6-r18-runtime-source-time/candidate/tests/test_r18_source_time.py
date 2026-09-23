"""P6-r18 runtime source time: emit/write + consumer join + negatives.

Tests exercise the actual candidate runtime hook (runtime/srcemit.py,
used by the local runtime/acp-worker copy) in isolated tmp streams with
injected clocks and no model calls; the consumer reads those SAME
emitted bytes through production code/CLI. No parallel fake emitter, no
model-authored timestamp. Injected effects only.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
SRC = os.path.join(PKG, "src")
RUNTIME = os.path.join(PKG, "runtime")
sys.path.insert(0, SRC)
sys.path.insert(0, RUNTIME)
import srcemit
from srcemit import SourceWriteError
import case_entry as CE

R17 = ("/home/bmosher/memory-bake-off/campaign4/packages/"
       "P6-r17-live-failure-rest/live-failed-1")
R17_STREAMS = [os.path.join(R17, f) for f in
               ("576b7ed5-1790129305.jsonl", "a94e7711-1790129305.jsonl")]
R17_ONSETS = os.path.join(R17, "failed-verification", "onsets")
INPUTS = ("/home/bmosher/memory-bake-off/campaign4/packages/"
          "P6-r18-runtime-source-time/inputs")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_modules_are_new_candidate():
    import harness as H
    assert os.path.realpath(H.__file__) == os.path.realpath(
        os.path.join(SRC, "r3harness", "harness.py"))
    assert os.path.realpath(srcemit.__file__) == os.path.realpath(
        os.path.join(RUNTIME, "srcemit.py"))
    print("srcemit=%s" % sha(srcemit.__file__)[:12])


def test_R17_missing_instrumentation_reproduced():
    # R17: onset dir empty; end records carry no source receipt.
    assert os.listdir(R17_ONSETS) == []
    from harness import _source_receipt
    for stream in R17_STREAMS:
        for line in open(stream):
            row = json.loads(line)
            if row.get("t") == "end":
                rec, reason = _source_receipt(row)
                assert rec is None and reason == "missing-src-version", \
                    (row, reason)
                break
        else:
            raise AssertionError("no end in %s" % stream)


def test_pinned_emit_schema_has_no_time_and_swallows():
    raw = open(os.path.join(INPUTS, "acp-worker")).read()
    assert sha(os.path.join(INPUTS, "acp-worker")).startswith("6871ceb1")
    i = raw.index("def emit(self, kind")
    block = raw[i:i + 600]
    assert '"t": kind' in block and "src_at" not in block
    assert "except Exception:" in block and "pass" in block


def test_local_copy_confined_and_shared_untouched():
    assert sha(os.path.join(INPUTS, "acp-worker")).startswith("6871ceb1")
    local = open(os.path.join(RUNTIME, "acp-worker")).read()
    assert "src_v" in local and "interface.md" in local
    assert local.count("_runtime_source_fields") == 2


def test_emit_format_and_injected_clock():
    import harness as H
    tmp = tempfile.mkdtemp(prefix="p6r18-emit-")
    stream = os.path.join(tmp, "s.jsonl")
    rec = srcemit.emit_end(stream, "sess-1", "i-1", now=1790125205.0)
    assert rec["src_v"] == 1 and rec["src_clock"] == "ok"
    assert rec["src_at"] == "2026-09-23T01:00:05Z", rec
    assert rec["src_session"] == "sess-1"
    assert rec["src_provenance"] == "runtime-end-append"
    assert rec["src_uncertainty_s"] == 1 and rec["src_status"] == "ok"
    same = json.loads(open(stream).read())
    assert same == rec  # consumer reads these SAME bytes
    got, reason = H._source_receipt(same)
    assert reason == "ok" and got["src_at"] == rec["src_at"]
    for bad in ("", None, 123):
        try:
            srcemit.source_fields(bad, "i")
            raise AssertionError("bad session accepted: %r" % (bad,))
        except (ValueError, TypeError):
            pass
    try:
        srcemit.source_fields("s", "")
        raise AssertionError("empty item accepted")
    except ValueError:
        pass


def test_hook_subprocess_producer_to_consumer():
    # Actual producer->consumer subprocess test of the shipped hook.
    tmp = tempfile.mkdtemp(prefix="p6r18-hook-")
    stream = os.path.join(tmp, "s.jsonl")
    env = dict(os.environ, ACP_SOURCE_TEST_NOW="2026-09-23T02:00:05Z")
    r = subprocess.run(
        [sys.executable, os.path.join(RUNTIME, "srcemit.py"), "emit-end",
         "--stream", stream, "--session", "sess-p", "--item", "i-p"],
        capture_output=True, text=True, timeout=30, env=env)
    assert r.returncode == 0, r.stderr
    rec = json.loads(r.stdout)
    assert rec["src_clock"] == "test" and rec["src_session"] == "sess-p"
    from harness import _source_receipt
    ondisk = json.loads(open(stream).read())
    assert ondisk == rec
    got, reason = _source_receipt(ondisk)
    assert reason == "ok" and got["src_item"] == "i-p"


def test_discontinuity_flagged_not_backfilled():
    srcemit._last.update({"wall": None, "mono": None})
    srcemit.source_fields("s", "i-1")
    wall, mono = srcemit._last["wall"], srcemit._last["mono"]
    srcemit._last.update({"wall": wall - 900.0, "mono": mono})
    f = srcemit.source_fields("s", "i-2")
    assert f["src_clock"] == "discontinuous", f
    assert f["src_at"] is not None  # stamp kept, flagged unusable
    from harness import _source_receipt
    rec, reason = _source_receipt({"t": "end", "item": "i-2", **f})
    assert rec is None and reason == "clock-discontinuous"
    srcemit._last.update({"wall": None, "mono": None})


def test_write_failure_raises_and_consumer_incomplete():
    import harness as H
    tmp = tempfile.mkdtemp(prefix="p6r18-write-")
    sub = os.path.join(tmp, "sub")
    os.makedirs(sub)
    stream = os.path.join(sub, "s.jsonl")
    os.chmod(sub, 0o500)
    try:
        srcemit.emit_end(stream, "s", "i")
        raise AssertionError("write failure swallowed")
    except SourceWriteError:
        pass
    finally:
        os.chmod(sub, 0o700)
    # No receipt bytes exist -> consumer INCOMPLETE, never PASS.
    rec, reason = H._source_receipt({"t": "end", "item": "i"})
    assert rec is None


def _causal_runtime(odir_end=None, src=None, det=None, arm=None,
                    mapping=None):
    det = det or {}
    arm = arm or {"armed_at": "2026-09-23T01:00:00Z"}
    mapping = mapping if mapping is not None else {}
    return CE._check_causal(dict(arm), "/nonexistent-onsets", det, "a-W",
                            dict(mapping), source_mode="runtime",
                            source_by_action=dict(src or {}))


def _src(item, at="2026-09-23T01:00:05Z", session="sess-1", **kw):
    d = {"src_mode": "runtime", "src_at": at, "src_session": session,
         "src_item": item, "src_provenance": "runtime-end-append",
         "src_uncertainty_s": 1, "src_clock": "ok", "src_status": "ok"}
    d.update(kw)
    return d


def test_runtime_join_and_negative_matrix():
    det = {"a-W": "2026-09-23T01:00:06Z", "a-V": "2026-09-23T01:00:10Z"}
    mapping = {"a-W": "i-w", "a-V": "i-v"}
    src = {"a-W": _src("i-w"),
           "a-V": _src("i-v", at="2026-09-23T01:00:09Z")}
    out = _causal_runtime(src=src, det=det, mapping=mapping)
    assert out["pairs"]["worker"]["onset_at"] == "2026-09-23T01:00:05Z"
    assert out["pairs"]["a-V"]["onset_at"] == "2026-09-23T01:00:09Z"
    # Missing receipt -> INCOMPLETE.
    for bad_src in ({}, {"a-W": _src("i-w")},
                    {"a-W": {"src_status": "missing"}}):
        try:
            _causal_runtime(src=bad_src, det=det, mapping=mapping)
            raise AssertionError("missing source accepted: %r" % bad_src)
        except CE.StageCFault as e:
            assert e.code == "E_NO_SOURCE", e.code
    # Empty/wrong item/session, previous-execution item, discontinuous.
    for bad in (_src("", session="s"), _src("i-1", session=""),
                _src("i-OTHER"), _src("i-w", session=""),
                _src("i-old-exec"), _src("i-w", src_clock="discontinuous"),
                _src("i-w", src_clock="unknown")):
        try:
            _causal_runtime(src={"a-W": bad, "a-V": src["a-V"]}, det=det,
                            mapping=mapping)
            raise AssertionError("bad source accepted: %r" % bad)
        except CE.StageCFault as e:
            assert e.code in ("E_NO_SOURCE", "E_SOURCE_MISMATCH"), e.code
    # Malformed/partial source; nonfinite uncertainty.
    for bad in (_src("i-w", src_at=None),
                {"src_mode": "runtime", "src_status": "ok"},
                _src("i-w", src_uncertainty_s=float("nan")),
                _src("i-w", src_uncertainty_s=float("inf")),
                _src("i-w", src_uncertainty_s=-1)):
        try:
            _causal_runtime(src={"a-W": bad, "a-V": src["a-V"]}, det=det,
                            mapping=mapping)
            raise AssertionError("malformed source accepted: %r" % bad)
        except CE.StageCFault as e:
            assert e.code == "E_NO_SOURCE", e.code
    # Genuine source-after-own-detection and arm-after-source rejected.
    try:
        _causal_runtime(
            src={"a-W": _src("i-w", at="2026-09-23T01:00:09Z")}, det=det,
            mapping={"a-W": "i-w"})
        raise AssertionError("late source accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CAUSAL", e.code
    try:
        _causal_runtime(src=src, det=det, mapping=mapping,
                        arm={"armed_at": "2026-09-23T01:00:06Z"})
        raise AssertionError("arm-after-source accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CAUSAL", e.code
    # Conflicting duplicate records for one action.
    try:
        CE._detect_source_conflict(
            [{"action": "a-W", "src_at": "2026-09-23T01:00:05Z"}],
            {"a-W": _src("i-w", at="2026-09-23T01:00:07Z")})
        raise AssertionError("conflict accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CONFLICT", e.code
    CE._detect_source_conflict(
        [{"action": "a-W", "src_at": "2026-09-23T01:00:05Z"}],
        {"a-W": _src("i-w", at="2026-09-23T01:00:05Z")})  # agreement ok


def test_delayed_observer_keeps_append_time_and_restart_stable():
    import harness as H
    from driver import Driver
    from ingress import HostClock
    tmp = tempfile.mkdtemp(prefix="p6r18-delay-")
    db = os.path.join(tmp, "fx.db")
    stream = os.path.join(tmp, "s.jsonl")
    srcemit.emit_end(stream, "sess-d", "i-d", now=1790125205.0)
    d = Driver(db, HostClock())
    a = H  # module ref for helper access
    end = json.loads(open(stream).read())
    rec, reason = H._source_receipt(end)
    assert reason == "ok"
    H._persist_source_receipt(d, "a-W", "ex-1", rec)
    d.close()
    # Delayed observer: detection much later; source stays append time.
    assert rec["src_at"] == "2026-09-23T01:00:05Z"
    assert rec["src_at"] < "2026-09-23T02:00:00Z"  # never relabelled
    # Restart re-reads the same bytes: no fresh stamp.
    d2 = Driver(db, HostClock())
    raw = d2.kv.get("src-receipt:a-W:ex-1")
    d2.close()
    assert json.loads(raw)["src_at"] == "2026-09-23T01:00:05Z"


def test_fixture_plan_is_local_only_with_hashes():
    plan = json.load(open(os.path.join(PKG, "fixture-launch-plan.json")))
    assert plan["runtime"]["local_sha256"] == sha(
        os.path.join(RUNTIME, "acp-worker"))[:64]
    assert plan["runtime"]["parent_sha256"].startswith("6871ceb1")
    assert ".config/agent-deck" in plan["runtime"]["shared_path"]
    assert plan["runtime"]["local_copy"].startswith("candidate/")
    assert plan["adopted"] is False
    assert "runtime" in plan["task_contracts"]["worker"].lower() \
        or "source time" in plan["task_contracts"]["worker"]


R3H = os.path.join(SRC, "r3harness", "harness.py")
P5_FIXTURE = ("/home/bmosher/memory-bake-off/campaign4/packages/"
              "P6-r5-launch-binding/src/fixture_worker.py")


def _r3cli(*args, timeout=120):
    return subprocess.run(
        [sys.executable, R3H] + list(args),
        capture_output=True, text=True, timeout=timeout, cwd=PKG)


def _write_plan(tmp, **over):
    bounds = {"duration_s": 900, "verify_window_s": 60,
              "wait_s": 2, "escalation_window_s": 30,
              "source_mode": "runtime",
              "stream_dir": os.path.join(tmp, "stream"),
              "onset_dir": os.path.join(tmp, "onsets"),
              "artifact_base_dir": os.path.join(tmp, "art"),
              "latency_path": os.path.join(tmp, "latency.jsonl")}
    bounds.update(over.get("bounds", {}))
    plan = {"fixture_id": "p6-r18", "package_id": "P6R",
            "worker_action": "p6r-w1", "verify_action": "p6r-v1",
            "seats": {"fixture_seats": ["s-w", "s-v"]},
            "allowlist": {"seats": ["s-w", "s-v"],
                          "timer_units": {"p6r-w1": "u-r18.timer"},
                          "wake_path": "/bin/true",
                          "systemd_run": "/bin/true",
                          "systemctl": "/bin/true"},
            "bounds": bounds,
            "task_texts": {
                "worker": "action: {action}\nexecution: {execution}\n"
                          "attempt: {attempt}\nstep: {step}\n"
                          "claim: {claims}/{execution}.json\n"
                          "artifacts: {artifacts}\nartifact: out.bin\n"
                          "pinned_input: {pinned_input}\n"
                          "package: P6R\nitem: iR18\n"
                          "source time is recorded by the runtime, "
                          "not by this task text\n",
                "verifier": "action: {action}\nexecution: {execution}\n"
                            "attempt: {attempt}\nstep: {step}\n"
                            "claim: {claims}/{execution}.json\n"
                            "artifacts: {artifacts}\n"
                            "worker_claim: {claims}/"
                            "{worker_claim_execution}.json\n"
                            "check: recompute-sha256\n"
                            "package: P6R\nitem: iR18\n"},
            "authorized_dispositions": [{"kind": "question_answered",
                                         "decision_ref": "d1",
                                         "reason": "verified"}],
            "routes": {"p6r-v1": "s-v", "p6r-w1": "s-w"}}
    path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(path, "w"), sort_keys=True)
    return path


def _setup(tmp, plan):
    manifest = os.path.join(tmp, "manifest.json")
    r = _r3cli("--plan", plan, "--manifest", manifest, "--session", "s",
               "--stream-key", "sk", "--worker-stream-key", "wsk",
               "--verifier-stream-key", "vsk", "setup")
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.load(open(manifest))["source_mode"] == "runtime"
    return manifest


def _run(tmp, plan, manifest, cmd):
    return _r3cli("--live", "--plan", plan, "--plan-hash", sha(plan),
                  "--allowlist-seat", "s-w", "--allowlist-seat", "s-v",
                  "--db", os.path.join(tmp, "fx.db"), "--manifest",
                  manifest, "--claims", os.path.join(tmp, "claims"),
                  "--qid", "P6R", cmd)


def _produce(step, tmp, manifest, item, session, outcome="completed",
             at=None):
    """Producer via the SHIPPED hook (subprocess) + bound claim/artifact,
    mirroring the fixture claim shape. Same bytes the consumer reads."""
    import hashlib as _hl
    m = json.load(open(manifest))
    is_worker = (step == "worker-run")
    action = m["action_id"] if is_worker else m["verify_action_id"]
    execution = m["execution_id"] if is_worker \
        else m["verify_execution_id"]
    skey = m["worker_stream_key"] if is_worker \
        else m["verifier_stream_key"]
    stream = os.path.join(tmp, "stream", skey + ".jsonl")
    art = os.path.join(tmp, "art", "out.bin")
    os.makedirs(os.path.join(tmp, "art"), exist_ok=True)
    with open(art, "wb") as fh:
        fh.write(b"fixture-artifact-bytes")
    digest = _hl.sha256(b"fixture-artifact-bytes").hexdigest()
    claim = {"package": "P6R", "attempt": "a1", "action": action,
             "execution": execution,
             "contract_step": step, "outcome": outcome,
             "artifacts": {"out.bin": {"path": "out.bin",
                                       "sha256": digest}}}
    if not is_worker:
        claim["check"] = "recompute-sha256"
    os.makedirs(os.path.join(tmp, "claims"), exist_ok=True)
    with open(os.path.join(tmp, "claims", execution + ".json"),
              "w") as fh:
        json.dump(claim, fh, sort_keys=True)
    env = dict(os.environ)
    if at is not None:
        env["ACP_SOURCE_TEST_NOW"] = at
    r = subprocess.run(
        [sys.executable, os.path.join(RUNTIME, "srcemit.py"), "emit-end",
         "--stream", stream, "--session", session, "--item", item],
        capture_output=True, text=True, timeout=30, env=env)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _utc_plus(seconds):
    import datetime as _dt
    return (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(
        seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_cli_runtime_success_and_rejection_with_matched_source():
    for outcome,imesh in (("completed", "ok"), ("failed", "rej")):
        w_at = _utc_plus(-5)
        v_at = _utc_plus(0)
        tmp = tempfile.mkdtemp(prefix="p6r18-cli-")
        for d in ("stream", "claims", "art", "onsets"):
            os.makedirs(os.path.join(tmp, d))
        plan = _write_plan(tmp)
        manifest = _setup(tmp, plan)
        latpath = os.path.join(tmp, "latency.jsonl")
        wrec = _produce("worker-run", tmp, manifest, "iR18W",
                        "sess-w-%s" % imesh, "completed", at=w_at)
        assert wrec["src_clock"] in ("ok", "test")
        outs = []
        bg = threading.Thread(
            target=lambda: outs.append(_run(tmp, plan, manifest,
                                           "run-fixture")))
        bg.start()  # worker observed at once; verifier dispatched ~now
        _produce("verify-run", tmp, manifest, "iR18V",
                 "sess-v-%s" % imesh, outcome, at=v_at)
        bg.join(timeout=110)
        assert outs, "run-fixture thread did not return"
        out = json.loads(outs[0].stdout)
        if outcome == "completed":
            assert out.get("decision") in ("transition-committed",
                                           "terminal-rest",
                                           "duplicate-end-ignored"), out
        else:
            # Failed verifier claim: honest bounded recovery, never a
            # manufactured success — but the source records still match.
            assert out.get("decision") == "owned-recovery", out
        rows = [json.loads(l) for l in open(latpath) if l.strip()]
        wrows = [x for x in rows if x["action"] == "p6r-w1"]
        assert wrows, rows
        assert wrows[0]["src_at"] == w_at, wrows[0]
        assert wrows[0]["src_session"] == "sess-w-%s" % imesh
        assert wrows[0]["src_known"] is True
        # Detection is later; source stays append time (never relabelled).
        assert wrows[0]["src_at"] <= wrows[0]["detected_at"]
        r = _r3cli("--manifest", manifest, "check-latency")
        if outcome == "completed":
            assert r.returncode == 0, r.stdout
            assert json.loads(r.stdout)["verdict"] == "gates-hold", r.stdout
        else:
            # Worker success counts; the verifier rejection stays in the
            # denominator (failures reported, never truncated/rewritten).
            assert r.returncode == 0, r.stdout
            verdict = json.loads(r.stdout)
            assert verdict["verdict"] == "gates-hold", r.stdout
            assert "owned-recovery" in verdict["failure_outcomes"], r.stdout
