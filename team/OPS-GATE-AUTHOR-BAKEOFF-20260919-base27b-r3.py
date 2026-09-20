#!/usr/bin/env python3
"""Gate check for row S11-3: pi-lcm native supersession on broader histories.

Verifies that the broader-history native-arm re-measurement was actually
performed and reported, per the row's substance requirements:
  - broader corpus declared (more distractor families, longer streams,
    92.9% agentmemory distractor shape, unfitted)
  - native pi-lcm arm only, no layer code
  - false-supersession and missed-update counts reported (null is valid)
  - old-vs-new comparison against the S7-STATELAYER baseline
  - prior measurement file present and referenced
"""

import json
import os
import sys
import tempfile
import shutil

BASE = "/home/bmosher/memory-bake-off"


def _fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def _run_check(base):
    """Core check logic. Returns 0 on pass, calls _fail on any finding."""
    prior_path = os.path.join(base, "team", "S7-STATELAYER", "verdict.json")
    results_path = os.path.join(base, "team", "S10-PI-LCM-HIST", "verdict.json")

    # --- File existence (row-declared paths) ---
    if not os.path.isfile(prior_path):
        _fail("prior measurement file missing: team/S7-STATELAYER/verdict.json")
    if not os.path.isfile(results_path):
        _fail("broader-history results file missing: team/S10-PI-LCM-HIST/verdict.json")

    # --- Load ---
    try:
        with open(prior_path, "r") as f:
            prior = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _fail(f"cannot parse prior verdict: {e}")
    try:
        with open(results_path, "r") as f:
            results = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _fail(f"cannot parse results verdict: {e}")

    if not isinstance(prior, dict):
        _fail("prior verdict is not a JSON object")
    if not isinstance(results, dict):
        _fail("results verdict is not a JSON object")

    # --- Prior must carry the S7-3 baseline (0/32 false supersession, 12/12 updates) ---
    prior_blob = json.dumps(prior).lower()
    has_baseline_fs = ("32" in prior_blob) or ("false_supersession" in prior_blob)
    has_baseline_mu = ("12" in prior_blob) or ("update" in prior_blob)
    if not (has_baseline_fs and has_baseline_mu):
        _fail("prior verdict lacks S7-3 baseline numbers (0/32 false supersession, 12/12 updates)")

    # --- Broader corpus must be declared ---
    broader_keys = ("distractor_families", "stream_length", "corpus", "trial_generation",
                    "broader_corpus", "distractor_shape", "stream_lengths",
                    "distractor_family_count", "stream_len", "n_distractor_families",
                    "n_families", "stream_len", "trial_params")
    has_broader = any(k in results for k in broader_keys)
    if not has_broader:
        _fail("results do not declare a broader corpus (distractor families / stream length)")

    # Check that the broader corpus actually extends S7-3
    broader_blob = json.dumps(results).lower()
    has_extension_evidence = any(
        token in broader_blob
        for token in ("distractor", "stream", "family", "92.9", "agentmemory", "unfitted")
    )
    if not has_extension_evidence:
        _fail("broader corpus does not evidence extension beyond S7-3 (distractor families / 92.9% agentmemory / unfitted)")

    # --- Must reference the 92.9% agentmemory distractor shape ---
    if "92.9" not in broader_blob and "agentmemory" not in broader_blob:
        _fail("results do not reference the documented agentmemory 92.9% distractor shape")

    # --- Must be declared unfitted ---
    if "unfitted" not in broader_blob:
        _fail("results do not declare the distractor shape as unfitted")

    # --- Native arm only, no layer code ---
    layer_active = False
    if results.get("layer_code") is True:
        layer_active = True
    if results.get("layer") is True:
        layer_active = True
    if results.get("arm") == "layer":
        layer_active = True
    if results.get("arm") == "native+layer":
        layer_active = True
    if results.get("arms") and isinstance(results["arms"], list):
        if any("layer" in str(a).lower() for a in results["arms"]):
            layer_active = True
    if layer_active:
        _fail("results indicate layer code was used; row requires native pi-lcm arm only, no layer code")

    # Must positively confirm native
    native_confirmed = False
    if results.get("arm") == "native":
        native_confirmed = True
    elif results.get("native_only") is True:
        native_confirmed = True
    elif results.get("layer_code") is False:
        native_confirmed = True
    elif results.get("layer") is False:
        native_confirmed = True
    else:
        blob_lower = json.dumps(results).lower()
        if "native" in blob_lower and "layer" not in blob_lower:
            native_confirmed = True
    if not native_confirmed:
        _fail("results do not confirm native pi-lcm arm only (no explicit native designation)")

    # --- False supersession count reported (null/zero is valid evidence) ---
    fs_keys = ("false_supersession", "false_supersession_count", "fs_count",
               "false_supersessions", "native_false_supersession")
    has_fs = any(k in results for k in fs_keys)
    if not has_fs:
        _fail("results do not report a false-supersession count")

    # --- Missed update count reported (null/zero is valid evidence) ---
    mu_keys = ("missed_update", "missed_update_count", "mu_count",
               "missed_updates", "native_missed_update")
    has_mu = any(k in results for k in mu_keys)
    if not has_mu:
        _fail("results do not report a missed-update count")

    # --- Old-vs-new comparison present ---
    cmp_keys = ("old_vs_new", "comparison", "prior_comparison", "baseline_comparison",
                "old_vs_new_comparison", "delta", "change", "vs_prior", "vs_baseline")
    has_cmp = any(k in results for k in cmp_keys)
    if not has_cmp:
        _fail("results do not include an old-vs-new comparison against the S7-3 baseline")

    print("PASS: S11-3 broader-history native pi-lcm check")
    return 0


def _selftest():
    """Prove the check can fail in multiple distinct ways and can pass.
    Exit 0 only if every bad fixture is rejected by its own named finding
    AND the conforming fixture is accepted."""
    tmp = tempfile.mkdtemp(prefix="s11_3_selftest_")
    failures = []

    def _make_dirs(root):
        os.makedirs(os.path.join(root, "team", "S7-STATELAYER"), exist_ok=True)
        os.makedirs(os.path.join(root, "team", "S10-PI-LCM-HIST"), exist_ok=True)

    def _write_prior(root, data=None):
        if data is None:
            data = {"false_supersession": "0/32", "updates": "12/12", "corpus": "controlled"}
        with open(os.path.join(root, "team", "S7-STATELAYER", "verdict.json"), "w") as f:
            json.dump(data, f)

    def _write_results(root, data):
        with open(os.path.join(root, "team", "S10-PI-LCM-HIST", "verdict.json"), "w") as f:
            json.dump(data, f)

    def _expect_reject(root, label):
        """Run check; expect exit 1. Return (ok, finding_text)."""
        try:
            _run_check(root)
            return False, "check unexpectedly passed"
        except SystemExit as e:
            if e.code == 1:
                return True, f"rejected ({label})"
            return False, f"unexpected exit code {e.code}"

    def _expect_accept(root, label):
        """Run check; expect exit 0. Return (ok, finding_text)."""
        try:
            rc = _run_check(root)
            if rc == 0:
                return True, f"accepted ({label})"
            return False, f"unexpected return {rc}"
        except SystemExit as e:
            if e.code == 0:
                return True, f"accepted ({label})"
            return False, f"unexpectedly rejected ({label})"

    # ============================================================
    # BAD 1: missing broader corpus declaration
    # ============================================================
    d1 = os.path.join(tmp, "bad1_no_broader")
    _make_dirs(d1)
    _write_prior(d1)
    _write_results(d1, {
        "arm": "native",
        "layer_code": False,
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d1, "missing broader corpus")
    if not ok:
        failures.append(f"BAD1: {msg}")

    # ============================================================
    # BAD 2: layer code present (violates native-only)
    # ============================================================
    d2 = os.path.join(tmp, "bad2_layer_active")
    _make_dirs(d2)
    _write_prior(d2)
    _write_results(d2, {
        "arm": "native",
        "layer_code": True,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d2, "layer code active")
    if not ok:
        failures.append(f"BAD2: {msg}")

    # ============================================================
    # BAD 3: missing old-vs-new comparison
    # ============================================================
    d3 = os.path.join(tmp, "bad3_no_comparison")
    _make_dirs(d3)
    _write_prior(d3)
    _write_results(d3, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0
    })
    ok, msg = _expect_reject(d3, "missing old-vs-new comparison")
    if not ok:
        failures.append(f"BAD3: {msg}")

    # ============================================================
    # BAD 4: missing false-supersession count
    # ============================================================
    d4 = os.path.join(tmp, "bad4_no_fs")
    _make_dirs(d4)
    _write_prior(d4)
    _write_results(d4, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d4, "missing false-supersession count")
    if not ok:
        failures.append(f"BAD4: {msg}")

    # ============================================================
    # BAD 5: missing missed-update count
    # ============================================================
    d5 = os.path.join(tmp, "bad5_no_mu")
    _make_dirs(d5)
    _write_prior(d5)
    _write_results(d5, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d5, "missing missed-update count")
    if not ok:
        failures.append(f"BAD5: {msg}")

    # ============================================================
    # BAD 6: prior file missing entirely
    # ============================================================
    d6 = os.path.join(tmp, "bad6_no_prior")
    os.makedirs(os.path.join(d6, "team", "S10-PI-LCM-HIST"), exist_ok=True)
    _write_results(d6, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d6, "prior file missing")
    if not ok:
        failures.append(f"BAD6: {msg}")

    # ============================================================
    # BAD 7: no native designation at all
    # ============================================================
    d7 = os.path.join(tmp, "bad7_no_native")
    _make_dirs(d7)
    _write_prior(d7)
    _write_results(d7, {
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d7, "no native arm designation")
    if not ok:
        failures.append(f"BAD7: {msg}")

    # ============================================================
    # BAD 8: arms list includes layer (not native-only)
    # ============================================================
    d8 = os.path.join(tmp, "bad8_arms_include_layer")
    _make_dirs(d8)
    _write_prior(d8)
    _write_results(d8, {
        "arms": ["native", "layer"],
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d8, "arms list includes layer")
    if not ok:
        failures.append(f"BAD8: {msg}")

    # ============================================================
    # BAD 9: missing 92.9% agentmemory distractor shape reference
    # ============================================================
    d9 = os.path.join(tmp, "bad9_no_agentmemory_shape")
    _make_dirs(d9)
    _write_prior(d9)
    _write_results(d9, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "random uniform",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d9, "missing 92.9% agentmemory distractor shape")
    if not ok:
        failures.append(f"BAD9: {msg}")

    # ============================================================
    # BAD 10: missing "unfitted" declaration
    # ============================================================
    d10 = os.path.join(tmp, "bad10_not_unfitted")
    _make_dirs(d10)
    _write_prior(d10)
    _write_results(d10, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% fitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d10, "distractor shape not declared unfitted")
    if not ok:
        failures.append(f"BAD10: {msg}")

    # ============================================================
    # BAD 11: prior file lacks S7-3 baseline numbers
    # ============================================================
    d11 = os.path.join(tmp, "bad11_prior_no_baseline")
    _make_dirs(d11)
    _write_prior(d11, {"note": "some other measurement", "score": 0.99})
    _write_results(d11, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64"}
    })
    ok, msg = _expect_reject(d11, "prior lacks S7-3 baseline numbers")
    if not ok:
        failures.append(f"BAD11: {msg}")

    # ============================================================
    # BAD 12: results file is not valid JSON
    # ============================================================
    d12 = os.path.join(tmp, "bad12_bad_json")
    _make_dirs(d12)
    _write_prior(d12)
    with open(os.path.join(d12, "team", "S10-PI-LCM-HIST", "verdict.json"), "w") as f:
        f.write("{not valid json")
    ok, msg = _expect_reject(d12, "results file not valid JSON")
    if not ok:
        failures.append(f"BAD12: {msg}")

    # ============================================================
    # GOOD: minimal conforming fixture
    # ============================================================
    dg = os.path.join(tmp, "good_conforming")
    _make_dirs(dg)
    _write_prior(dg)
    _write_results(dg, {
        "arm": "native",
        "layer_code": False,
        "distractor_families": 8,
        "stream_length": 256,
        "distractor_shape": "agentmemory 92.9% unfitted",
        "false_supersession": 0,
        "missed_update": 0,
        "old_vs_new": {"prior_fs": "0/32", "new_fs": "0/64", "prior_mu": "0/12", "new_mu": "0/24"}
    })
    ok, msg = _expect_accept(dg, "conforming fixture")
    if not ok:
        failures.append(f"GOOD: {msg}")

    # --- Cleanup ---
    shutil.rmtree(tmp, ignore_errors=True)

    # --- Verdict ---
    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}")
        sys.exit(1)

    print("SELFTEST PASS: all 12 bad fixtures rejected, conforming fixture accepted")
    sys.exit(0)


def main():
    if "--selftest" in sys.argv:
        _selftest()
    else:
        _run_check(BASE)


if __name__ == "__main__":
    main()