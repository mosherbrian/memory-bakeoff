import json
import os
import sys
import tempfile
import shutil

BASE = "/home/bmosher/memory-bake-off"


def _finding(name, msg):
    print("FINDING [{}]: {}".format(name, msg))
    return 1


def _search_numeric(obj, key_pred):
    """Recursively search for a dict key matching key_pred with a numeric value."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if key_pred(k) and isinstance(v, (int, float)) and not isinstance(v, bool):
                return True
            if _search_numeric(v, key_pred):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _search_numeric(item, key_pred):
                return True
    return False


def _all_text(paths):
    """Concatenate text content of all given files."""
    chunks = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                chunks.append(f.read())
        except OSError:
            pass
    return "\n".join(chunks)


def run_checks(base):
    """Run all substance checks. Returns 0 on clean, 1 on first finding."""
    s7_verdict = os.path.join(base, "team", "S7-STATELAYER", "verdict.json")
    s10_dir = os.path.join(base, "team", "S10-PI-LCM-HIST")

    # --- 1. Require declared file: team/S7-STATELAYER/verdict.json ---
    if not os.path.isfile(s7_verdict):
        return _finding(
            "missing-prior-measurement",
            "Row declares team/S7-STATELAYER/verdict.json as PRIOR MEASUREMENT; "
            "file not found at {}".format(s7_verdict),
        )

    # --- 2. Prior measurement must be valid JSON with false-supersession substance ---
    try:
        with open(s7_verdict, "r", encoding="utf-8") as f:
            prior = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return _finding(
            "prior-measurement-unreadable",
            "team/S7-STATELAYER/verdict.json is not valid JSON: {}".format(e),
        )

    prior_text = json.dumps(prior).lower()
    if "false" not in prior_text or "supersession" not in prior_text:
        return _finding(
            "prior-measurement-substance",
            "Prior measurement must contain false-supersession data "
            "(row: 'native and layer both 0/32 false supersession, 12/12 updates').",
        )

    # --- 3. S10-PI-LCM-HIST directory must exist ---
    if not os.path.isdir(s10_dir):
        return _finding(
            "missing-results-dir",
            "Results directory {} does not exist.".format(s10_dir),
        )

    # --- 4. Find results files (json or txt, excluding check.py) ---
    results_files = []
    for fn in sorted(os.listdir(s10_dir)):
        if fn == "check.py":
            continue
        if fn.endswith(".json") or fn.endswith(".txt"):
            results_files.append(os.path.join(s10_dir, fn))

    if not results_files:
        return _finding(
            "missing-results",
            "No .json or .txt results file in {}. "
            "Row requires reporting native false supersession / missed update "
            "on a broader corpus.".format(s10_dir),
        )

    # --- 5. Parse JSON results (if any) for structured checks ---
    results_obj = None
    for rf in results_files:
        if rf.endswith(".json"):
            try:
                with open(rf, "r", encoding="utf-8") as f:
                    results_obj = json.load(f)
                break
            except (json.JSONDecodeError, OSError):
                continue

    combined_text = _all_text(results_files).lower()

    # --- 6. Must report a numeric native false-supersession count ---
    fs_found = False
    if results_obj is not None:
        fs_found = _search_numeric(
            results_obj,
            lambda k: "false" in k.lower() and "supersession" in k.lower(),
        )
    if not fs_found:
        # Fallback: look for a pattern like "false_supersession": N or "false supersession: N"
        import re
        if re.search(r"false[\s_-]*supersession[\s]*[:=]\s*\d+", combined_text):
            fs_found = True
    if not fs_found:
        return _finding(
            "no-false-supersession-count",
            "Results must report a numeric native false-supersession count. "
            "Row: 'report any native false supersession or missed update'.",
        )

    # --- 7. Must report a numeric missed/failed update count ---
    mu_found = False
    if results_obj is not None:
        mu_found = _search_numeric(
            results_obj,
            lambda k: ("miss" in k.lower() or "update" in k.lower() or "fail" in k.lower()),
        )
    if not mu_found:
        import re
        if re.search(r"(miss|fail|update)[\s_-]*\w*[\s]*[:=]\s*\d+", combined_text):
            mu_found = True
    if not mu_found:
        return _finding(
            "no-missed-update-count",
            "Results must report a numeric missed-update (or failed-update) count. "
            "Row: 'report any native false supersession or missed update'.",
        )

    # --- 8. Must indicate NATIVE arm only (no layer execution) ---
    if "native" not in combined_text:
        return _finding(
            "not-native-arm",
            "Results must indicate the NATIVE pi-lcm arm was run. "
            "Row: 'run the NATIVE pi-lcm arm only, no layer code'.",
        )

    # --- 9. Must indicate broader corpus (extended beyond S7-3) ---
    broader_terms = [
        "broader", "distractor", "stream", "extended", "92.9",
        "agentmemory", "longer", "more",
    ]
    if not any(t in combined_text for t in broader_terms):
        return _finding(
            "not-broader-corpus",
            "Results must indicate a broader corpus than S7-3 "
            "(more distractor families, longer streams, agentmemory 92.9% shape). "
            "Row: 'Mechanically extend the S7-3 trial generation'.",
        )

    # --- 10. Must report old-vs-new comparison to prior measurement ---
    comparison_terms = [
        "old", "new", "prior", "previous", "s7", "comparison",
        "delta", "change", "re-measure", "remeasure",
    ]
    if not any(t in combined_text for t in comparison_terms):
        return _finding(
            "no-old-vs-new",
            "Results must report old-vs-new comparison to the prior measurement "
            "(team/S7-STATELAYER/verdict.json). Row: 'must report old-vs-new'.",
        )

    return 0


def selftest():
    """Prove the check can fail and can pass. Exit 0 only if both hold."""
    tmp = tempfile.mkdtemp(prefix="s11_3_selftest_")
    try:
        # --- Non-conforming fixture: missing old-vs-new comparison ---
        bad_base = os.path.join(tmp, "bad")
        os.makedirs(os.path.join(bad_base, "team", "S7-STATELAYER"))
        os.makedirs(os.path.join(bad_base, "team", "S10-PI-LCM-HIST"))

        with open(os.path.join(bad_base, "team", "S7-STATELAYER", "verdict.json"), "w") as f:
            json.dump({
                "native": {"false_supersession": 0, "total": 32, "updates": 12, "total_updates": 12},
                "layer": {"false_supersession": 0, "total": 32, "updates": 12, "total_updates": 12},
            }, f)

        # Results that lack old-vs-new comparison
        with open(os.path.join(bad_base, "team", "S10-PI-LCM-HIST", "results.json"), "w") as f:
            json.dump({
                "arm": "native",
                "corpus": "broader",
                "distractor_families": 6,
                "false_supersession": 0,
                "missed_updates": 0,
            }, f)

        rc_bad = run_checks(bad_base)
        if rc_bad != 1:
            print("SELFTEST FAIL: non-conforming fixture was not rejected (rc={})".format(rc_bad))
            return 1

        # --- Conforming fixture: all substance present ---
        good_base = os.path.join(tmp, "good")
        os.makedirs(os.path.join(good_base, "team", "S7-STATELAYER"))
        os.makedirs(os.path.join(good_base, "team", "S10-PI-LCM-HIST"))

        with open(os.path.join(good_base, "team", "S7-STATELAYER", "verdict.json"), "w") as f:
            json.dump({
                "native": {"false_supersession": 0, "total": 32, "updates": 12, "total_updates": 12},
                "layer": {"false_supersession": 0, "total": 32, "updates": 12, "total_updates": 12},
            }, f)

        with open(os.path.join(good_base, "team", "S10-PI-LCM-HIST", "results.json"), "w") as f:
            json.dump({
                "arm": "native",
                "corpus": "broader",
                "distractor_families": 6,
                "stream_length": 200,
                "shape": "agentmemory 92.9%",
                "false_supersession": 0,
                "missed_updates": 0,
                "old_vs_new": {
                    "prior_false_supersession": 0,
                    "new_false_supersession": 0,
                    "prior_updates": 12,
                    "new_updates": 12,
                    "delta": "null",
                },
            }, f)

        rc_good = run_checks(good_base)
        if rc_good != 0:
            print("SELFTEST FAIL: conforming fixture was rejected (rc={})".format(rc_good))
            return 1

        print("SELFTEST PASS: non-conforming rejected, conforming accepted.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    try:
        rc = run_checks(BASE)
    except Exception as e:
        print("FINDING [internal-error]: {}".format(e))
        rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
