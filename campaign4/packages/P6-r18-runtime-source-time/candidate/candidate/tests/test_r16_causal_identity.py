"""P6-r16 causal identity: onset joined to ITS detection via verified
item->action bindings, never filename order (new core bytes).

Old gap (R15): sorted-first onset file (verifier item) paired with worker
detection -> false E_CAUSAL. Covers reorder both ways, unbound
earlier-sorting files, negatives, and one exact-CLI run-case composition.
Injected effects only.
"""
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
SRC = os.path.join(PKG, "src")
sys.path.insert(0, SRC)
import case_entry as CE

R15 = ("/home/bmosher/memory-bake-off/campaign4/packages/"
       "P6-r15-live-failure-rest/live-failed-1/failed-verification")
PARENT_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
              "P6-r14-host-timing/candidate/src")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_module_is_new_candidate():
    assert os.path.realpath(CE.__file__) == os.path.realpath(
        os.path.join(SRC, "case_entry.py")), CE.__file__
    assert os.path.realpath(CE.__file__) != os.path.realpath(
        os.path.join(PARENT_SRC, "case_entry.py"))
    print("case_entry=%s" % sha(CE.__file__)[:12])


def r15_copies(tmp):
    """Copies (never edits) of R15 onset evidence + detections."""
    odir = os.path.join(tmp, "onsets")
    os.makedirs(odir)
    for f in ("id492c9c28b64.json", "i42e65da2879b.json"):
        shutil.copy(os.path.join(R15, "onsets", f), odir)
    det = {}
    for r in (json.loads(l) for l in open(
            os.path.join(R15, "latency.jsonl")) if l.strip()):
        det[r["action"]] = r["detected_at"]
    return odir, det


WA = "p6r15-f1-failed-verification-w"
VA = "p6r15-f1-failed-verification-v"
ITEMS = {"w-item": "id492c9c28b64", "v-item": "i42e65da2879b"}
INTERVENTION = {"armed_at": "2026-09-23T00:50:00Z"}


def join(odir_items=None):
    return {WA: ITEMS["w-item"], VA: ITEMS["v-item"]}


def _parent_ce():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "parent_case_entry",
        os.path.join(PARENT_SRC, "case_entry.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_old_wrong_pair_reproduces_on_parent_new_code_joins():
    tmp = tempfile.mkdtemp(prefix="p6r16-old-")
    odir, det = r15_copies(tmp)
    # Real immutable-parent function on R15 evidence copies: false E_CAUSAL.
    parent = _parent_ce()
    try:
        parent._check_causal(dict(INTERVENTION), odir, det, WA)
        raise AssertionError("parent did not reproduce E_CAUSAL")
    except parent.StageCFault as e:
        assert e.code == "E_CAUSAL", e.code
    # New code joins each onset to its own detection: accepts.
    out = CE._check_causal(dict(INTERVENTION), odir, det, WA, join())
    assert out["pairs"]["worker"]["item"] == "id492c9c28b64"
    assert out["pairs"]["worker"]["onset_at"] == "2026-09-23T00:51:11Z"
    assert out["pairs"][VA]["item"] == "i42e65da2879b"
    assert out["pairs"][VA]["onset_at"] == "2026-09-23T00:52:37Z"
    assert out["onset_at"] == "2026-09-23T00:51:11Z"  # worker pair kept


def _synth_dir(tmp, worker_name, verifier_name):
    odir = os.path.join(tmp, "onsets")
    os.makedirs(odir, exist_ok=True)
    w = {"item": worker_name, "onset_at": "2026-09-23T10:00:05Z",
         "provenance": "p", "uncertainty_s": 1}
    v = {"item": verifier_name, "onset_at": "2026-09-23T10:00:09Z",
         "provenance": "p", "uncertainty_s": 1}
    json.dump(w, open(os.path.join(odir, worker_name + ".json"), "w"))
    json.dump(v, open(os.path.join(odir, verifier_name + ".json"), "w"))
    det = {WA: "2026-09-23T10:00:06Z", VA: "2026-09-23T10:00:10Z"}
    return odir, det, w, v


def test_filename_order_both_ways_and_unbound_earlier_file():
    for wname, vname in (("zz-worker", "aa-verifier"),
                         ("aa-worker", "zz-verifier")):
        tmp = tempfile.mkdtemp(prefix="p6r16-reorder-")
        odir, det, w, v = _synth_dir(tmp, wname, vname)
        # Unrelated earlier-sorting unbound onset: must not change result.
        json.dump({"item": "000-intruder",
                   "onset_at": "2020-01-01T00:00:00Z",
                   "provenance": "x", "uncertainty_s": 1},
                  open(os.path.join(odir, "000-intruder.json"), "w"))
        mapping = {WA: wname, VA: vname}
        out = CE._check_causal(dict(INTERVENTION,
                                    armed_at="2026-09-23T10:00:00Z"),
                               odir, det, WA, mapping)
        assert out["pairs"]["worker"]["onset_at"] == w["onset_at"], wname
        assert out["pairs"][VA]["onset_at"] == v["onset_at"], vname


def test_genuine_violations_still_rejected():
    tmp = tempfile.mkdtemp(prefix="p6r16-neg-")
    odir, det, w, v = _synth_dir(tmp, "w1", "v1")
    mapping = {WA: "w1", VA: "v1"}
    arm = {"armed_at": "2026-09-23T10:00:00Z"}
    # Genuine onset-after-own-detection (worker onset 10:00:05, det
    # 10:00:03: beyond the 1s uncertainty; exact-boundary equality passes).
    bad = dict(det, **{WA: "2026-09-23T10:00:03Z"})
    try:
        CE._check_causal(dict(arm), odir, bad, WA, mapping)
        raise AssertionError("late worker onset accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CAUSAL", e.code
    # Arm-after-source stays rejected.
    try:
        CE._check_causal({"armed_at": "2026-09-23T10:00:06Z"}, odir, det,
                         WA, mapping)
        raise AssertionError("arm-after-onset accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CAUSAL", e.code
    # Swapped sidecar content (file asserts another identity) rejected.
    shutil.copy(os.path.join(odir, "v1.json"),
                os.path.join(odir, "w1.json"))
    try:
        CE._check_causal(dict(arm), odir, det, WA, mapping)
        raise AssertionError("swapped sidecar accepted")
    except CE.StageCFault as e:
        assert e.code == "E_NO_ONSET", e.code


def test_missing_ambiguous_uncertainty_rejected():
    tmp = tempfile.mkdtemp(prefix="p6r16-neg2-")
    odir, det, w, v = _synth_dir(tmp, "w1", "v1")
    arm = {"armed_at": "2026-09-23T10:00:00Z"}
    mapping = {WA: "w1", VA: "v1"}
    # Missing worker source file.
    os.remove(os.path.join(odir, "w1.json"))
    try:
        CE._check_causal(dict(arm), odir, det, WA, mapping)
        raise AssertionError("missing worker source accepted")
    except CE.StageCFault as e:
        assert e.code == "E_NO_ONSET", e.code
    # Missing bound mapping for the required action.
    odir2, _, _, _ = _synth_dir(tmp + "b", "w1", "v1")
    try:
        CE._check_causal(dict(arm), odir2, det, WA, {VA: "v1"})
        raise AssertionError("missing worker mapping accepted")
    except CE.StageCFault as e:
        assert e.code == "E_NO_ONSET", e.code
    # Nonfinite / negative / bool uncertainty.
    for bad_unc in (float("nan"), float("inf"), -1, True, "1", None):
        d = tempfile.mkdtemp(prefix="p6r16-unc-")
        o, dt, _, _ = _synth_dir(d, "w1", "v1")
        rec = json.load(open(os.path.join(o, "w1.json")))
        rec["uncertainty_s"] = bad_unc
        json.dump(rec, open(os.path.join(o, "w1.json"), "w"))
        try:
            CE._check_causal(dict(arm), o, dt, WA, mapping)
            raise AssertionError("bad uncertainty accepted: %r" % bad_unc)
        except CE.StageCFault as e:
            assert e.code == "E_NO_ONSET", (bad_unc, e.code)
    # Conflicting duplicate bound items for the same identity.
    manifest = {"action_id": WA, "execution_id": "ex1",
                "verify_action_id": VA, "verify_execution_id": "exv1"}
    carried = [{"action": WA, "execution": "ex1", "item": "w1"},
               {"action": WA, "execution": "ex1", "item": "w1-dup"}]
    try:
        CE._resolve_causal_items(manifest, {"ws": "w1", "vs": "v1"},
                                 "ws", "vs", carried)
        raise AssertionError("conflicting duplicates accepted")
    except CE.StageCFault as e:
        assert e.code == "E_CONFLICT", e.code
    # Observed item disagreeing with bound runtime item.
    carried = [{"action": WA, "execution": "ex1", "item": "w-bound"}]
    try:
        CE._resolve_causal_items(manifest, {"ws": "w-other", "vs": "v1"},
                                 "ws", "vs", carried)
        raise AssertionError("disagreeing item accepted")
    except CE.StageCFault as e:
        assert e.code == "E_ITEM_MISMATCH", e.code
    # Wrong execution mapping.
    try:
        CE._resolve_causal_items(manifest, {"ws": "w1", "vs": "v1"},
                                 "ws", "vs",
                                 [{"action": WA, "execution": "ex-OTHER",
                                   "item": "w1"}])
        raise AssertionError("wrong execution accepted")
    except CE.StageCFault as e:
        assert e.code == "E_ITEM_MISMATCH", e.code


def _tce():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tce_helpers", os.path.join(HERE, "test_case_execution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_failed_verification_causal_pairs_joined():
    # Exact production CLI composition (simulated branch, signed test
    # executables, injected collaborators): the fault case's receipt
    # causal block joins each onset to its own detection.
    tce = _tce()
    env = tce.make_suite()
    try:
        r = tce.cli("fault", "arm", "--case", "failed-verification",
                    "--run-root", env["tmp"], "--control",
                    "corrupt-after-worker", "--actor", "cairn")
        assert r.returncode == 0, r.stdout
        r = tce.run_case_cli(env, "failed-verification")
        assert r.returncode == 0, r.stdout[-2000:]
        rec = json.load(open(os.path.join(
            env["tmp"], "failed-verification", "receipt.json")))
        causal = rec.get("causal")
        assert causal, rec.keys()
        pairs = causal["pairs"]
        assert pairs["worker"]["item"] == rec["worker_item"]
        assert pairs[rec["verify_action"]]["item"] == \
            rec["verifier_item"]
        wfile = os.path.join(env["tmp"], "failed-verification", "onsets",
                             rec["worker_item"] + ".json")
        assert json.load(open(wfile))["onset_at"] == \
            pairs["worker"]["onset_at"]
        assert causal["onset_at"] == pairs["worker"]["onset_at"]
    finally:
        for s in env["socks"]:
            try:
                s.close()
            except Exception:
                pass


def _parent_ce():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "parent_case_entry_d1",
        os.path.join(PARENT_SRC, "case_entry.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _d1_dir(tmp, rec):
    odir = os.path.join(tmp, "onsets")
    os.makedirs(odir, exist_ok=True)
    json.dump(rec, open(os.path.join(odir, "w1.json"), "w"))
    return odir


def test_D1_missing_item_old_accepts_new_rejects():
    # Sidecar WITHOUT any item field: old defaults to the filename and
    # accepts; new requires explicit matching identity.
    for rec in ({"onset_at": "2026-09-23T10:00:05Z", "provenance": "p",
                 "uncertainty_s": 1},
                {"item": None, "onset_at": "2026-09-23T10:00:05Z",
                 "provenance": "p", "uncertainty_s": 1},
                {"item": "", "onset_at": "2026-09-23T10:00:05Z",
                 "provenance": "p", "uncertainty_s": 1},
                {"item": "other", "onset_at": "2026-09-23T10:00:05Z",
                 "provenance": "p", "uncertainty_s": 1}):
        tmp = tempfile.mkdtemp(prefix="p6r16-d1-")
        odir = _d1_dir(tmp, rec)
        det = {WA: "2026-09-23T10:00:06Z"}
        arm = {"armed_at": "2026-09-23T10:00:00Z"}
        parent = _parent_ce()
        old_out = parent._check_causal(dict(arm), odir, det, WA)
        assert old_out["onset_at"] == "2026-09-23T10:00:05Z"  # old accepts
        try:
            CE._check_causal(dict(arm), odir, det, WA, {WA: "w1"})
            raise AssertionError("missing-item sidecar accepted: %r"
                                 % (rec.get("item"),))
        except CE.StageCFault as e:
            assert e.code == "E_NO_ONSET", e.code
    # Genuine explicit matching item still passes on new code.
    tmp = tempfile.mkdtemp(prefix="p6r16-d1-ok-")
    odir = _d1_dir(tmp, {"item": "w1", "onset_at": "2026-09-23T10:00:05Z",
                         "provenance": "p", "uncertainty_s": 1})
    out = CE._check_causal(dict(arm), odir, det, WA, {WA: "w1"})
    assert out["pairs"]["worker"]["onset_at"] == "2026-09-23T10:00:05Z"


def test_D2_adversarial_plant_with_plausible_sidecar_rejected_cli():
    # Exact CLI: pre-planted verifier end + plausible EXPLICIT-item
    # sidecar on the same stream, verifier text held so only the plant
    # is present. E_UNDELIVERED dominates: the plant can never become
    # current-action causal evidence, even well-formed. (Complements the
    # inherited r1f probe, whose forged sidecar lacks explicit item.)
    import time as _t
    tce = _tce()
    env = tce.make_suite()
    try:
        r = tce.cli("fault", "arm", "--case", "positive-handoff",
                    "--run-root", env["tmp"], "--control",
                    "hold-verifier-texts", "--actor", "cairn")
        assert r.returncode == 0, r.stdout
        os.makedirs(os.path.join(env["tmp"], "sim", "stream"),
                    exist_ok=True)
        os.makedirs(os.path.join(env["tmp"], "positive-handoff", "onsets"),
                    exist_ok=True)
        with open(os.path.join(env["tmp"], "sim", "stream",
                               env["vsid"] + ".jsonl"), "w") as fh:
            fh.write('{"t":"end","item":"z9-old-1"}\n')
        json.dump({"item": "z9-old-1",
                   "onset_at": _t.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           _t.gmtime()),
                   "provenance": "plausible-adversarial",
                   "uncertainty_s": 1},
                  open(os.path.join(env["tmp"], "positive-handoff",
                                    "onsets", "z9-old-1.json"), "w"))
        procs = tce.emulators(env, "positive-handoff")
        try:
            r = tce.cli("run-case", "--config", env["cfg"], "--plan",
                        env["plan"], "--signatures", env["sig"], "--case",
                        "positive-handoff", "--suite-root", env["tmp"],
                        "--simulated", "--registry-file", env["reg"],
                        "--out", os.path.join(
                            env["tmp"], "positive-handoff", "receipt.json"),
                        env_extra={"FAULT_CASE": "positive-handoff",
                                   "FAULT_ROOT": os.path.join(
                                       env["tmp"], "faults")})
        finally:
            for p in procs:
                try:
                    p.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    p.kill()
        assert r.returncode == 3 and "E_UNDELIVERED" in r.stdout, r.stdout
    finally:
        for s in env["socks"]:
            try:
                s.close()
            except Exception:
                pass
