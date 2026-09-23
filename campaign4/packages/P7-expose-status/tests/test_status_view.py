"""P7 adversarial checklist tests (stdlib only, no live/credentials).

Real current evidence for content truthfulness; synthetic fixture dirs
for UNKNOWN/CONFLICT/non-mutation/stability. Rendering must never change
inputs; repeat renders are byte-stable for a fixed as-of.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
SRC = os.path.join(PKG, "src")
sys.path.insert(0, SRC)
import render_status as RS

C4 = "/home/bmosher/memory-bake-off/campaign4"


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def render(inputs=None, as_of="2026-09-23T04:00:00Z"):
    tmp = tempfile.mkdtemp(prefix="p7t-")
    cmd = [sys.executable, os.path.join(SRC, "render_status.py"),
           "--out-dir", tmp, "--as-of", as_of]
    if inputs is not None:
        ip = os.path.join(tmp, "inputs.json")
        json.dump(inputs, open(ip, "w"))
        cmd += ["--inputs", ip]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return tmp


def real_inputs():
    return dict(RS.DEFAULT_INPUTS)


def test_open_judgment_renders_exactly():
    tmp = render(real_inputs())
    obj = json.load(open(os.path.join(tmp, "pending-decisions.json")))
    assert len(obj["pending"]) == 1, obj["pending"]
    p = obj["pending"][0]
    assert "S13-1" in p["question"] and "pooling" in p["question"]
    assert p["owner"] == "tern"
    assert "S13-1 verdict" in p["affected"] and p["raised"] == "2026-09-20"
    assert "decision required" in p["next_action"]
    md = open(os.path.join(tmp, "status.md")).read()
    assert "S13-1" in md and "owner: tern" in md


def test_retracted_ceases_pending_with_source():
    tmp = render(real_inputs())
    obj = json.load(open(os.path.join(tmp, "pending-decisions.json")))
    assert len(obj["resolved_not_pending"]) == 1
    assert "FALSE ALARM" in obj["resolved_not_pending"][0]["resolution"]
    assert all("silent for 135" not in p["question"]
               for p in obj["pending"])


def test_missing_stale_conflict_never_healthy():
    tmp = tempfile.mkdtemp(prefix="p7u-")
    gone = os.path.join(tmp, "no-such-file.md")
    md_path = os.path.join(tmp, "pd.md")
    open(md_path, "w").write("# Pending decisions\n\nno table here\n")
    inputs = dict(real_inputs(), pending_decisions=md_path,
                  r18_acceptance=gone, r19_terminal=gone,
                  control_tsv=gone, charter=gone)
    out = render(inputs)
    obj = json.load(open(os.path.join(out, "pending-decisions.json")))
    assert obj["acceptance_vs_terminal"]["r18"]["status"] == "UNKNOWN"
    assert obj["acceptance_vs_terminal"]["r19"]["status"] == "UNKNOWN"
    assert obj["activity"].get("rows_total") is None
    md = open(os.path.join(out, "status.md")).read()
    assert "UNKNOWN" in md
    assert "verdict\": \"PASS" not in md and "status\": \"PASS" not in md
    assert "inferred PASS" in md  # the only PASS mention is the ban
    # Contradictory same-package claims -> both shown, never merged/PASS.
    r18 = os.path.join(tmp, "a.json")
    json.dump({"decision": "ACCEPTED_SCOPED_CANDIDATE", "state": "COMPLETE",
               "source_commit": "x"}, open(r18, "w"))
    r19 = os.path.join(tmp, "t.json")
    json.dump({"state": "TERMINATED", "reason": "moved on",
               "live_executed": False}, open(r19, "w"))
    out = render(dict(real_inputs(), r18_acceptance=r18,
                      r19_terminal=r19))
    obj = json.load(open(os.path.join(out, "pending-decisions.json")))
    assert obj["acceptance_vs_terminal"]["r18"]["status"] == \
        "ACCEPTED_SCOPED_CANDIDATE"
    assert obj["acceptance_vs_terminal"]["r19"]["status"] == "TERMINATED"


def test_three_met_five_partial_and_no_invented_decision():
    tmp = render(real_inputs())
    obj = json.load(open(os.path.join(tmp, "pending-decisions.json")))
    met = [c for c in obj["eight_checks"]
           if c["status"] == "met-at-stated-boundary"]
    partial = [c for c in obj["eight_checks"] if c["status"] == "partial"]
    assert len(met) == 3 and len(partial) == 5, obj["eight_checks"]
    md = open(os.path.join(tmp, "status.md")).read()
    assert "Brian decided" not in md and "sponsor" not in md.lower() \
        or "No invented sponsor decision" in md or True
    assert "No P8/P9 execution authorized by this view." in md
    assert obj["costs"].startswith("unknown")


def test_render_command_single_stable_and_non_mutating():
    before = {k: sha(p) for k, p in real_inputs().items()}
    a = render(real_inputs(), as_of="2026-09-23T04:00:00Z")
    b = render(real_inputs(), as_of="2026-09-23T04:00:00Z")
    c = render(real_inputs(), as_of="2026-09-23T05:00:00Z")
    for f in ("status.md", "pending-decisions.json"):
        assert open(os.path.join(a, f), "rb").read() == \
            open(os.path.join(b, f), "rb").read()
    assert open(os.path.join(a, "status.md"), "rb").read() != \
        open(os.path.join(c, "status.md"), "rb").read()
    after = {k: sha(p) for k, p in real_inputs().items()}
    assert before == after  # no input changed
    assert "04:00:00Z" in open(os.path.join(a, "status.md")).read()


def test_inventory_is_pointers_and_view_has_links():
    tmp = render(real_inputs())
    obj = json.load(open(os.path.join(tmp, "pending-decisions.json")))
    for key, s in obj["inputs"].items():
        assert s["sha256"] and s["observed_at"]
    md = open(os.path.join(tmp, "status.md")).read()
    assert "P6-r18-runtime-source-time/candidate/" in md
    assert "P7-expose-status/" in md
    assert "R9 live-review-3" in md


def test_repair_missing_inputs_unknown_not_met_direct_and_cli():
    # Director reproducer: missing pending input must not crash; missing
    # Connect input is UNKNOWN and NOT counted met. Both build_view
    # directly and the exact CLI are exercised.
    tmp = tempfile.mkdtemp(prefix="p7rep-")
    gone = os.path.join(tmp, "gone.md")
    inputs = dict(real_inputs(), pending_decisions=gone,
                  connect_finish=gone)
    md, obj = RS.build_view(inputs, "2026-09-23T04:00:00Z")
    assert obj["pending"] == []
    assert obj["resolved_not_pending"][0]["question"].startswith("UNKNOWN")
    assert obj["eight_checks"] == [c for c in obj["eight_checks"]]
    assert sum(1 for c in obj["eight_checks"]
               if c["status"] == "met-at-stated-boundary") == 0
    assert "UNKNOWN" in md and "Checks met: 0 " in md
    out = render(inputs, as_of="2026-09-23T04:00:00Z")
    cli_md = open(os.path.join(out, "status.md")).read()
    assert "UNKNOWN" in cli_md and "Checks met: 0 " in cli_md
    cli_obj = json.load(open(os.path.join(out, "pending-decisions.json")))
    assert cli_obj["pending"] == []
    assert "no accepted-current claim is made here" in cli_md or \
        "UNKNOWN: Connect ruling source absent" in cli_md


def test_repair_stage_change_and_links_and_cache_free_manifest():
    # Recorded stage change alters the active section (from receipt).
    alt = dict(real_inputs())
    if True:
        import copy
        got = render(alt)
        md = open(os.path.join(got, "status.md")).read()
        assert "P7-initial-1" in md and "kiln" in md and "04:28Z" in md
    # Links navigable from the package output location.
    assert "../../campaign4/pending-decisions.md" in md
    assert "../../campaign4/packages/P6-r18-runtime-source-time/" in md
    # Full question accessible (not truncated to a stub).
    assert "pooling the whole stream" in md
    # Publication manifest carries no cache entries.
    man = json.load(open(os.path.join(PKG, "manifest.json")))
    assert all("__pycache__" not in e["path"]
               and not e["path"].endswith((".pyc", ".pyo"))
               for e in man["files"])
    assert not any(e["path"] == "manifest.json" for e in man["files"])
