#!/usr/bin/env python3
"""Gate check for row S11-3: pi-lcm native supersession on broader histories.

The row declares, from its own text:
  - A PRIOR MEASUREMENT at team/S7-STATELAYER/verdict.json whose substance is
    "native and layer both 0/32 false supersession, 12/12 updates — controlled
    corpus only".
  - A re-measurement of the NATIVE arm only (no layer code) on a declared-broader
    corpus: mechanically extended S7-3 trial generation (more distractor
    families, longer streams — the documented agentmemory 92.9% distractor shape,
    unfitted), reporting any native false supersession or missed update, and an
    old-vs-new comparison.

This check requires both declared files by their declared paths and checks the
row's SUBSTANCE (extension, native-only, failure report, old-vs-new), not a file
count. --selftest builds many distinct deliberately-wrong fixtures, each wrong
in a different way the row's text makes possible, and rejects each by its own
named finding; it accepts a minimal conforming one; it exits 0 only if every
one of those holds.
"""

import json
import os
import sys
import tempfile

BASE = "/home/bmosher/memory-bake-off"
PRIOR_REL = os.path.join("team", "S7-STATELAYER", "verdict.json")
RESULT_REL = os.path.join("team", "S10-PI-LCM-HIST", "verdict.json")

OLD_KEYS = ("old", "prior", "s7", "previous", "baseline")
NEW_KEYS = ("new", "current", "this_run", "extended")


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _check(base):
    """Run all substance checks against *base*. Returns list of (name, msg)."""
    findings = []

    prior_path = os.path.join(base, PRIOR_REL)
    result_path = os.path.join(base, RESULT_REL)

    # --- 1. Declared prior measurement ---
    if not os.path.isfile(prior_path):
        findings.append(("prior-missing",
                         "Declared prior measurement not found: " + PRIOR_REL))
    else:
        try:
            prior = _load(prior_path)
            ptext = json.dumps(prior).lower()
            if "supersession" not in ptext:
                findings.append(("prior-no-supersession",
                                 "Prior measurement lacks supersession data "
                                 "(row declares 0/32 false supersession)"))
            if "update" not in ptext:
                findings.append(("prior-no-update",
                                 "Prior measurement lacks update data "
                                 "(row declares 12/12 updates)"))
            if "0/32" not in ptext or "12/12" not in ptext:
                findings.append(("prior-no-declared-numbers",
                                 "Prior measurement lacks the declared numbers "
                                 "0/32 and 12/12"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            findings.append(("prior-unreadable",
                             "Prior measurement unreadable or invalid JSON: %s" % exc))

    # --- 2. This run's result ---
    if not os.path.isfile(result_path):
        findings.append(("result-missing",
                         "Result file not found: " + RESULT_REL))
    else:
        try:
            result = _load(result_path)
            rtext = json.dumps(result).lower()

            # 2a. Extended trial generation: more distractor families, longer streams
            if "distractor" not in rtext:
                findings.append(("no-distractor-extension",
                                 "Result lacks evidence of extended distractor families"))
            if "stream" not in rtext and "length" not in rtext:
                findings.append(("no-stream-extension",
                                 "Result lacks evidence of longer streams"))

            # 2b. Native arm only, no layer code
            if "native" not in rtext:
                findings.append(("no-native-arm",
                                 "Result does not indicate the native pi-lcm arm was run"))
            arm = result.get("arm")
            if isinstance(arm, str) and "layer" in arm.lower() and "native" not in arm.lower():
                findings.append(("layer-arm-present",
                                 "Result ran the layer arm; row requires the NATIVE arm only"))
            layer = result.get("layer")
            if isinstance(layer, dict) and any(
                    k in layer for k in ("false_supersession", "missed_updates", "updates")):
                findings.append(("layer-arm-present",
                                 "Result reports layer-arm results; row requires the NATIVE arm only"))

            # 2c. False supersession or missed update reported
            if not any(k in rtext for k in ("supersession", "false_sup", "missed", "update")):
                findings.append(("no-failure-report",
                                 "Result lacks a false-supersession or missed-update report"))

            # 2d. Old-vs-new comparison
            if not any(k in rtext for k in OLD_KEYS):
                findings.append(("no-old-reference",
                                 "Result lacks a reference to the prior (old) measurement"))
            if not any(k in rtext for k in NEW_KEYS):
                findings.append(("no-new-reference",
                                 "Result lacks a reference to the new (this-run) measurement"))

        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            findings.append(("result-unreadable",
                             "Result file unreadable or invalid JSON: %s" % exc))

    return findings


def _build(base, prior, result):
    """Materialize a fixture.

    prior/result may be:
      - None: file absent
      - dict: written as JSON
      - str: written raw (for invalid-JSON fixtures)
    """
    if prior is not None:
        pdir = os.path.join(base, "team", "S7-STATELAYER")
        os.makedirs(pdir, exist_ok=True)
        ppath = os.path.join(pdir, "verdict.json")
        with open(ppath, "w", encoding="utf-8") as fh:
            if isinstance(prior, str):
                fh.write(prior)
            else:
                json.dump(prior, fh)
    if result is not None:
        rdir = os.path.join(base, "team", "S10-PI-LCM-HIST")
        os.makedirs(rdir, exist_ok=True)
        rpath = os.path.join(rdir, "verdict.json")
        with open(rpath, "w", encoding="utf-8") as fh:
            if isinstance(result, str):
                fh.write(result)
            else:
                json.dump(result, fh)


def _names(findings):
    return {n for n, _ in findings}


def _selftest():
    """Prove the check can fail in many distinct ways and can pass.

    Exit 0 only if every wrong fixture is rejected by its own named finding and
    the conforming fixture is accepted.
    """
    conforming_prior = {
        "native": {"false_supersession": "0/32", "updates": "12/12"},
        "layer": {"false_supersession": "0/32", "updates": "12/12"},
        "corpus": "controlled",
    }
    conforming_result = {
        "arm": "native",
        "trial_generation": {
            "distractor_families": 8,
            "stream_length": 200,
            "shape": "agentmemory 92.9%",
            "fitted": False,
        },
        "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
        "comparison": {
            "old": "0/32 false supersession, 12/12 updates (controlled corpus)",
            "new": "0/64 false supersession, 0/24 missed updates (broader corpus)",
        },
    }

    # Each wrong fixture: (label, prior, result, expected named finding(s))
    wrong = [
        ("A: prior file missing entirely",
         None, {"note": "placeholder"},
         {"prior-missing"}),

        ("B: no extended trial generation (no distractor, no stream)",
         conforming_prior,
         {"arm": "native",
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "comparison": {"old": "0/32", "new": "0/64"}},
         {"no-distractor-extension", "no-stream-extension"}),

        ("C: layer arm results present (row requires native only)",
         conforming_prior,
         {"arm": "native",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "layer": {"false_supersession": "1/64", "missed_updates": "2/24"},
          "comparison": {"old": "0/32", "new": "0/64"}},
         {"layer-arm-present"}),

        ("D: no old-vs-new comparison (missing old reference)",
         conforming_prior,
         {"arm": "native",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "comparison": {"new": "0/64"}},
         {"no-old-reference"}),

        ("E: prior lacks the declared numbers 0/32 and 12/12",
         {"native": {"false_supersession": "zero of thirty-two",
                     "updates": "all twelve"}},
         conforming_result,
         {"prior-no-declared-numbers"}),

        ("F: no failure report in result (no supersession/missed/update)",
         conforming_prior,
         {"arm": "native",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "comparison": {"old": "0/32", "new": "0/64"}},
         {"no-failure-report"}),

        ("G: prior file is invalid JSON",
         "{not valid json at all",
         conforming_result,
         {"prior-unreadable"}),

        ("H: result file is invalid JSON",
         conforming_prior,
         "this is not json {{{",
         {"result-unreadable"}),

        ("I: result does not indicate native arm",
         conforming_prior,
         {"arm": "pi-lcm",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "comparison": {"old": "0/32", "new": "0/64"}},
         {"no-native-arm"}),

        ("J: prior lacks supersession data specifically",
         {"native": {"false_sup": "0/32", "updates": "12/12"}},
         conforming_result,
         {"prior-no-supersession"}),

        ("K: prior lacks update data specifically",
         {"native": {"false_supersession": "0/32", "supersession_rate": "12/12"}},
         conforming_result,
         {"prior-no-update"}),

        ("L: result lacks new (this-run) reference",
         conforming_prior,
         {"arm": "native",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "comparison": {"old": "0/32 false supersession"}},
         {"no-new-reference"}),

        ("M: result file missing entirely",
         conforming_prior,
         None,
         {"result-missing"}),

        ("N: arm field explicitly says layer (not native)",
         conforming_prior,
         {"arm": "layer",
          "trial_generation": {"distractor_families": 8, "stream_length": 200},
          "results": {"false_supersession": "0/64", "missed_updates": "0/24"},
          "comparison": {"old": "0/32", "new": "0/64"}},
         {"layer-arm-present", "no-native-arm"}),
    ]

    for label, prior, result, expected in wrong:
        with tempfile.TemporaryDirectory() as tmp:
            _build(tmp, prior, result)
            findings = _check(tmp)
            got = _names(findings)
            if not findings:
                print("SELFTEST-FAIL: %s was ACCEPTED (check cannot fail)" % label)
                return 1
            missing = expected - got
            if missing:
                print("SELFTEST-FAIL: %s rejected but not by expected finding(s) %s "
                      "(got %s)" % (label, sorted(missing), sorted(got)))
                return 1
            print("SELFTEST-OK: %s rejected by %s" % (label, sorted(expected)))

    # Conforming fixture must be accepted.
    with tempfile.TemporaryDirectory() as tmp:
        _build(tmp, conforming_prior, conforming_result)
        findings = _check(tmp)
        if findings:
            print("SELFTEST-FAIL: conforming fixture was REJECTED: %s" % findings)
            return 1
        print("SELFTEST-OK: conforming fixture accepted")

    return 0


def main():
    try:
        if "--selftest" in sys.argv:
            sys.exit(_selftest())

        findings = _check(BASE)
        if findings:
            for name, msg in findings:
                print("FINDING [%s]: %s" % (name, msg))
            sys.exit(1)
        print("CLEAN: all S11-3 checks passed")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:  # never a traceback
        print("FINDING [internal-error]: unexpected exception: %s" % exc)
        sys.exit(1)


if __name__ == "__main__":
    main()