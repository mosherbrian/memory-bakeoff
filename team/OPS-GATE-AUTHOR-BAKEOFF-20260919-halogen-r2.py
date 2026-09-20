#!/usr/bin/env python3
"""Gate check for row S11-3: pi-lcm native supersession on broader histories.

Verifies that the native pi-lcm arm was run on a declared-broader corpus
(more distractor families, longer streams) with NO layer code, and that
results report false_supersession, missed_update, and an old-vs-new
comparison against the prior S7-STATELAYER measurement.
"""

import json
import os
import sys

PROJECT_ROOT = "/home/bmosher/memory-bake-off"

PRIOR_VERDICT = os.path.join(PROJECT_ROOT, "team/S7-STATELAYER/verdict.json")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "team/S10-PI-LCM-HIST/results.json")
TRIAL_CONFIG_PATH = os.path.join(PROJECT_ROOT, "team/S10-PI-LCM-HIST/trial_config.json")

PRIOR_FALSE_SUPERS = 0
PRIOR_TOTAL_TRIALS = 32
PRIOR_UPDATES = 12
PRIOR_TOTAL_UPDATES = 12


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def check_prior_verdict():
    """Verify the prior measurement file exists and matches declared values."""
    if not os.path.isfile(PRIOR_VERDICT):
        return "FINDING: prior measurement file missing: " + PRIOR_VERDICT
    try:
        data = _load_json(PRIOR_VERDICT)
    except (json.JSONDecodeError, OSError) as e:
        return "FINDING: prior measurement unreadable: " + str(e)
    native = data.get("native") or data.get("native_arm") or data
    if isinstance(native, dict):
        fs = native.get("false_supersession")
        upd = native.get("updates")
        if fs is not None:
            if isinstance(fs, dict):
                val = fs.get("count", fs.get("false_supersession"))
            else:
                val = fs
            if val != PRIOR_FALSE_SUPERS:
                return "FINDING: prior native false_supersession != " + str(PRIOR_FALSE_SUPERS)
        if upd is not None:
            if isinstance(upd, dict):
                val = upd.get("count", upd.get("updates"))
            else:
                val = upd
            if val != PRIOR_UPDATES:
                return "FINDING: prior native updates != " + str(PRIOR_UPDATES)
    return None


def check_trial_config():
    """Verify the trial config declares a BROADER corpus: more distractor
    families and longer streams than the S7-3 baseline. Must be unfitted,
    native-only."""
    if not os.path.isfile(TRIAL_CONFIG_PATH):
        return "FINDING: trial config missing: " + TRIAL_CONFIG_PATH
    try:
        cfg = _load_json(TRIAL_CONFIG_PATH)
    except (json.JSONDecodeError, OSError) as e:
        return "FINDING: trial config unreadable: " + str(e)

    df = cfg.get("distractor_families") or cfg.get("num_distractor_families")
    if df is None:
        return "FINDING: trial_config missing distractor_families count"
    if not isinstance(df, int) or df < 2:
        return "FINDING: distractor_families must be int >= 2, got " + repr(df)

    sl = cfg.get("stream_length") or cfg.get("num_trials") or cfg.get("total_trials")
    if sl is None:
        return "FINDING: trial_config missing stream_length / num_trials"
    if not isinstance(sl, int) or sl < 32:
        return "FINDING: stream_length must be int >= 32 (broader than baseline), got " + repr(sl)

    fitted = cfg.get("fitted", False)
    if fitted:
        return "FINDING: trial_config declares fitted=True; row requires unfitted"

    arm = cfg.get("arm", cfg.get("arm_type", ""))
    if isinstance(arm, str) and "layer" in arm.lower():
        return "FINDING: trial_config arm mentions 'layer': " + repr(arm) + "; must be native only"

    return None


def check_results():
    """Verify results report native false_supersession, missed_update,
    and an old-vs-new comparison. No layer code present."""
    if not os.path.isfile(RESULTS_PATH):
        return "FINDING: results file missing: " + RESULTS_PATH
    try:
        res = _load_json(RESULTS_PATH)
    except (json.JSONDecodeError, OSError) as e:
        return "FINDING: results unreadable: " + str(e)

    findings = []

    # Must report false_supersession (native) - handle zero correctly
    has_fs = ("false_supersession" in res) or ("native_false_supersession" in res)
    if not has_fs:
        findings.append("FINDING: results missing false_supersession metric")

    # Must report missed_update - handle zero correctly
    has_mu = ("missed_update" in res) or ("native_missed_update" in res) or ("missed_updates" in res)
    if not has_mu:
        findings.append("FINDING: results missing missed_update metric")

    # Must report old-vs-new comparison
    has_ovs = ("old_vs_new" in res) or ("comparison" in res) or ("vs_prior" in res)
    if not has_ovs:
        findings.append("FINDING: results missing old_vs_new comparison")
    else:
        ovs = res.get("old_vs_new") or res.get("comparison") or res.get("vs_prior")
        if isinstance(ovs, dict):
            old = ovs.get("old") or ovs.get("prior")
            new = ovs.get("new") or ovs.get("current")
            if old is None or new is None:
                findings.append("FINDING: old_vs_new must contain both 'old' and 'new' keys")
        elif not isinstance(ovs, str):
            findings.append("FINDING: old_vs_new must be dict or string")

    # Must be native-only: no layer results
    if "layer" in res and res["layer"] is not None:
        findings.append("FINDING: results contain 'layer' key; row requires native arm only")
    if "layer_false_supersession" in res:
        findings.append("FINDING: results contain layer_false_supersession; native only")

    # Check for any layer code references in the results metadata
    meta = res.get("metadata", res.get("run_info", {}))
    if isinstance(meta, dict):
        code_files = meta.get("code_files", meta.get("imports", []))
        if isinstance(code_files, list):
            for cf in code_files:
                if isinstance(cf, str) and "layer" in cf.lower():
                    findings.append("FINDING: results reference layer code file: " + cf)

    if findings:
        return "\n".join(findings)
    return None


def run_checks():
    """Run all substance checks. Return list of findings (empty = clean)."""
    findings = []
    for fn in (check_prior_verdict, check_trial_config, check_results):
        r = fn()
        if r:
            findings.append(r)
    return findings


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f)


def selftest():
    """Prove the check CAN fail: reject several distinct non-conforming
    fixtures, accept a minimal conforming one. Exit 0 only if all hold."""
    import tempfile
    import shutil

    base = tempfile.mkdtemp(prefix="s11_3_selftest_")
    global PRIOR_VERDICT, RESULTS_PATH, TRIAL_CONFIG_PATH
    orig = (PRIOR_VERDICT, RESULTS_PATH, TRIAL_CONFIG_PATH)

    try:
        # --- CONFORMING FIXTURE ---
        conf = os.path.join(base, "conf")
        _write_json(os.path.join(conf, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(conf, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "native"})
        _write_json(os.path.join(conf, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {"false_supersession": 0, "updates": 12},
                                    "new": {"false_supersession": 0, "updates": 12}},
                     "metadata": {"code_files": ["pi_lcm_native.py"]}})

        PRIOR_VERDICT = os.path.join(conf, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(conf, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(conf, "team/S10-PI-LCM-HIST/trial_config.json")
        findings_good = run_checks()
        if findings_good:
            print("SELFTEST FAIL: conforming fixture was rejected:")
            for f in findings_good:
                print("  " + f)
            return 1

        # --- NON-CONFORMING FIXTURE 1: prior verdict has wrong values ---
        nc1 = os.path.join(base, "nc1")
        _write_json(os.path.join(nc1, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 5, "updates": 3}})
        _write_json(os.path.join(nc1, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "native"})
        _write_json(os.path.join(nc1, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}}})
        PRIOR_VERDICT = os.path.join(nc1, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc1, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc1, "team/S10-PI-LCM-HIST/trial_config.json")
        f1 = run_checks()
        if not f1:
            print("SELFTEST FAIL: nc1 (wrong prior values) was NOT rejected")
            return 1
        if "prior native false_supersession" not in f1[0]:
            print("SELFTEST FAIL: nc1 rejected but not for the expected reason: " + f1[0])
            return 1

        # --- NON-CONFORMING FIXTURE 2: trial config not broader (1 family, short stream) ---
        nc2 = os.path.join(base, "nc2")
        _write_json(os.path.join(nc2, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc2, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 1, "stream_length": 10, "fitted": False, "arm": "native"})
        _write_json(os.path.join(nc2, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}}})
        PRIOR_VERDICT = os.path.join(nc2, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc2, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc2, "team/S10-PI-LCM-HIST/trial_config.json")
        f2 = run_checks()
        if not f2:
            print("SELFTEST FAIL: nc2 (not broader corpus) was NOT rejected")
            return 1
        if "distractor_families" not in f2[0]:
            print("SELFTEST FAIL: nc2 rejected but not for expected reason: " + f2[0])
            return 1

        # --- NON-CONFORMING FIXTURE 3: trial config declares fitted=True ---
        nc3 = os.path.join(base, "nc3")
        _write_json(os.path.join(nc3, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc3, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": True, "arm": "native"})
        _write_json(os.path.join(nc3, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}}})
        PRIOR_VERDICT = os.path.join(nc3, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc3, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc3, "team/S10-PI-LCM-HIST/trial_config.json")
        f3 = run_checks()
        if not f3:
            print("SELFTEST FAIL: nc3 (fitted=True) was NOT rejected")
            return 1
        if "fitted" not in f3[0]:
            print("SELFTEST FAIL: nc3 rejected but not for expected reason: " + f3[0])
            return 1

        # --- NON-CONFORMING FIXTURE 4: results contain layer key (native only) ---
        nc4 = os.path.join(base, "nc4")
        _write_json(os.path.join(nc4, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc4, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "native"})
        _write_json(os.path.join(nc4, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}},
                     "layer": {"false_supersession": 1}})
        PRIOR_VERDICT = os.path.join(nc4, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc4, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc4, "team/S10-PI-LCM-HIST/trial_config.json")
        f4 = run_checks()
        if not f4:
            print("SELFTEST FAIL: nc4 (layer in results) was NOT rejected")
            return 1
        if "layer" not in f4[0]:
            print("SELFTEST FAIL: nc4 rejected but not for expected reason: " + f4[0])
            return 1

        # --- NON-CONFORMING FIXTURE 5: results missing old_vs_new ---
        nc5 = os.path.join(base, "nc5")
        _write_json(os.path.join(nc5, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc5, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "native"})
        _write_json(os.path.join(nc5, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0})
        PRIOR_VERDICT = os.path.join(nc5, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc5, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc5, "team/S10-PI-LCM-HIST/trial_config.json")
        f5 = run_checks()
        if not f5:
            print("SELFTEST FAIL: nc5 (missing old_vs_new) was NOT rejected")
            return 1
        if "old_vs_new" not in f5[0]:
            print("SELFTEST FAIL: nc5 rejected but not for expected reason: " + f5[0])
            return 1

        # --- NON-CONFORMING FIXTURE 6: trial config arm mentions layer ---
        nc6 = os.path.join(base, "nc6")
        _write_json(os.path.join(nc6, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc6, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "layer_augmented"})
        _write_json(os.path.join(nc6, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}}})
        PRIOR_VERDICT = os.path.join(nc6, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc6, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc6, "team/S10-PI-LCM-HIST/trial_config.json")
        f6 = run_checks()
        if not f6:
            print("SELFTEST FAIL: nc6 (arm=layer_augmented) was NOT rejected")
            return 1
        if "layer" not in f6[0]:
            print("SELFTEST FAIL: nc6 rejected but not for expected reason: " + f6[0])
            return 1

        # --- NON-CONFORMING FIXTURE 7: results reference layer code file ---
        nc7 = os.path.join(base, "nc7")
        _write_json(os.path.join(nc7, "team/S7-STATELAYER/verdict.json"),
                    {"native": {"false_supersession": 0, "updates": 12}})
        _write_json(os.path.join(nc7, "team/S10-PI-LCM-HIST/trial_config.json"),
                    {"distractor_families": 5, "stream_length": 64, "fitted": False, "arm": "native"})
        _write_json(os.path.join(nc7, "team/S10-PI-LCM-HIST/results.json"),
                    {"false_supersession": 0, "missed_update": 0,
                     "old_vs_new": {"old": {}, "new": {}},
                     "metadata": {"code_files": ["state_layer.py"]}})
        PRIOR_VERDICT = os.path.join(nc7, "team/S7-STATELAYER/verdict.json")
        RESULTS_PATH = os.path.join(nc7, "team/S10-PI-LCM-HIST/results.json")
        TRIAL_CONFIG_PATH = os.path.join(nc7, "team/S10-PI-LCM-HIST/trial_config.json")
        f7 = run_checks()
        if not f7:
            print("SELFTEST FAIL: nc7 (layer code file in metadata) was NOT rejected")
            return 1
        if "layer code file" not in f7[0]:
            print("SELFTEST FAIL: nc7 rejected but not for expected reason: " + f7[0])
            return 1

        print("SELFTEST PASS: conforming accepted; 7 non-conforming fixtures each rejected by named finding")
        return 0

    finally:
        PRIOR_VERDICT, RESULTS_PATH, TRIAL_CONFIG_PATH = orig
        shutil.rmtree(base, ignore_errors=True)


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())

    findings = run_checks()
    if findings:
        for f in findings:
            print(f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()