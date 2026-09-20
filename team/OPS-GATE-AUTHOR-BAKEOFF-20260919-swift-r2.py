#!/usr/bin/env python3
"""Gate check for row S11-3: pi-lcm native supersession on broader histories."""

import json
import os
import sys
import tempfile
import shutil

BASE = "/home/bmosher/memory-bake-off"
PRIOR_REL = os.path.join("team", "S7-STATELAYER", "verdict.json")
NEW_REL = os.path.join("team", "S10-PI-LCM-HIST", "verdict.json")


def _fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def _run_check(base):
    """Core check logic. Returns None on pass, raises SystemExit(1) on fail."""
    prior_path = os.path.join(base, PRIOR_REL)
    new_path = os.path.join(base, NEW_REL)

    # --- Require declared files ---
    if not os.path.isfile(prior_path):
        _fail(f"missing prior measurement file: {PRIOR_REL}")
    if not os.path.isfile(new_path):
        _fail(f"missing new measurement file: {NEW_REL}")

    with open(prior_path, "r") as f:
        prior = json.load(f)
    with open(new_path, "r") as f:
        new = json.load(f)

    # --- Prior measurement substance ---
    if "native" not in prior:
        _fail("prior measurement missing 'native' arm")
    if "layer" not in prior:
        _fail("prior measurement missing 'layer' arm")

    prior_native = prior["native"]
    if "false_supersession" not in prior_native:
        _fail("prior native arm missing 'false_supersession'")
    if "updates" not in prior_native:
        _fail("prior native arm missing 'updates'")

    # --- New measurement substance ---
    # Must be NATIVE arm only (no layer code)
    if "native" not in new:
        _fail("new measurement missing 'native' arm")
    if "layer" in new:
        _fail("new measurement must be native arm only; found 'layer' key")

    new_native = new["native"]
    if "false_supersession" not in new_native:
        _fail("new native arm missing 'false_supersession' count")
    if "missed_update" not in new_native and "updates" not in new_native:
        _fail("new native arm missing 'missed_update' or 'updates' count")

    # --- Broader corpus declaration ---
    if "corpus" not in new:
        _fail("new measurement missing 'corpus' declaration")
    corpus = new["corpus"]

    if "distractor_families" not in corpus:
        _fail("corpus missing 'distractor_families'")
    if "stream_length" not in corpus:
        _fail("corpus missing 'stream_length'")

    # Distractor shape must reference the 92.9% agentmemory shape, unfitted
    if "distractor_shape" not in corpus:
        _fail("corpus missing 'distractor_shape'")
    shape = corpus["distractor_shape"]
    shape_str = json.dumps(shape).lower()
    if "92.9" not in shape_str and "0.929" not in shape_str:
        _fail("distractor_shape must reference the 92.9% agentmemory distractor shape")
    if "unfitted" not in shape_str:
        _fail("distractor_shape must be declared unfitted")

    # Broader than prior: more distractor families
    prior_corpus = prior.get("corpus", {})
    prior_families = prior_corpus.get("distractor_families", 0)
    if corpus["distractor_families"] <= prior_families:
        _fail(
            f"corpus distractor_families ({corpus['distractor_families']}) "
            f"must exceed prior ({prior_families})"
        )

    # Longer streams
    prior_stream = prior_corpus.get("stream_length", 0)
    if corpus["stream_length"] <= prior_stream:
        _fail(
            f"corpus stream_length ({corpus['stream_length']}) "
            f"must exceed prior ({prior_stream})"
        )

    # --- Old-vs-new comparison ---
    if "old_vs_new" not in new:
        _fail("new measurement missing 'old_vs_new' comparison")
    o2n = new["old_vs_new"]
    if "false_supersession" not in o2n:
        _fail("old_vs_new missing 'false_supersession' comparison")
    if "updates" not in o2n and "missed_update" not in o2n:
        _fail("old_vs_new missing 'updates' or 'missed_update' comparison")

    # --- No LLM / no network markers (substance: local, $0) ---
    method = new.get("method", "")
    if isinstance(method, str) and "llm" in method.lower():
        _fail("method must not reference LLM (row declares no LLM)")

    print("PASS")
    sys.exit(0)


def _selftest():
    tmpdir = tempfile.mkdtemp(prefix="s11_3_selftest_")
    try:
        prior_dir = os.path.join(tmpdir, "team", "S7-STATELAYER")
        new_dir = os.path.join(tmpdir, "team", "S10-PI-LCM-HIST")
        os.makedirs(prior_dir, exist_ok=True)
        os.makedirs(new_dir, exist_ok=True)

        prior_good = {
            "native": {"false_supersession": 0, "updates": 12},
            "layer": {"false_supersession": 0, "updates": 12},
            "corpus": {"distractor_families": 3, "stream_length": 10},
        }

        new_good = {
            "native": {"false_supersession": 0, "missed_update": 0},
            "corpus": {
                "distractor_families": 7,
                "stream_length": 50,
                "distractor_shape": "agentmemory 92.9% unfitted",
            },
            "old_vs_new": {
                "false_supersession": {"old": 0, "new": 0},
                "missed_update": {"old": 0, "new": 0},
            },
            "method": "native pi-lcm, local, zero-cost",
        }

        def _write_and_check(prior_data, new_data):
            with open(os.path.join(prior_dir, "verdict.json"), "w") as f:
                json.dump(prior_data, f)
            with open(os.path.join(new_dir, "verdict.json"), "w") as f:
                json.dump(new_data, f)
            try:
                _run_check(tmpdir)
                return None  # passed (exit 0)
            except SystemExit as e:
                if e.code == 1:
                    return e.code
                raise

        # === NON-CONFORMING FIXTURES (each must be rejected) ===

        # 1. Has layer arm (should be native only)
        bad1 = dict(new_good)
        bad1["layer"] = {"false_supersession": 0, "updates": 12}
        r = _write_and_check(prior_good, bad1)
        if r != 1:
            print("SELFTEST FAIL: fixture 1 (layer arm present) was not rejected")
            sys.exit(1)

        # 2. Not broader: distractor_families same as prior
        bad2 = dict(new_good)
        bad2["corpus"] = dict(new_good["corpus"])
        bad2["corpus"]["distractor_families"] = 3  # same as prior
        r = _write_and_check(prior_good, bad2)
        if r != 1:
            print("SELFTEST FAIL: fixture 2 (not broader families) was not rejected")
            sys.exit(1)

        # 3. Distractor shape missing 92.9% reference
        bad3 = dict(new_good)
        bad3["corpus"] = dict(new_good["corpus"])
        bad3["corpus"]["distractor_shape"] = "random unfitted"
        r = _write_and_check(prior_good, bad3)
        if r != 1:
            print("SELFTEST FAIL: fixture 3 (no 92.9% in shape) was not rejected")
            sys.exit(1)

        # 4. Missing old_vs_new comparison
        bad4 = dict(new_good)
        del bad4["old_vs_new"]
        r = _write_and_check(prior_good, bad4)
        if r != 1:
            print("SELFTEST FAIL: fixture 4 (no old_vs_new) was not rejected")
            sys.exit(1)

        # 5. Method references LLM
        bad5 = dict(new_good)
        bad5["method"] = "uses LLM for trial generation"
        r = _write_and_check(prior_good, bad5)
        if r != 1:
            print("SELFTEST FAIL: fixture 5 (LLM in method) was not rejected")
            sys.exit(1)

        # 6. Native arm missing both missed_update and updates
        bad6 = dict(new_good)
        bad6["native"] = {"false_supersession": 0}
        r = _write_and_check(prior_good, bad6)
        if r != 1:
            print("SELFTEST FAIL: fixture 6 (no update count) was not rejected")
            sys.exit(1)

        # 7. Stream length not longer than prior
        bad7 = dict(new_good)
        bad7["corpus"] = dict(new_good["corpus"])
        bad7["corpus"]["stream_length"] = 10  # same as prior
        r = _write_and_check(prior_good, bad7)
        if r != 1:
            print("SELFTEST FAIL: fixture 7 (stream not longer) was not rejected")
            sys.exit(1)

        # 8. Distractor shape not declared unfitted
        bad8 = dict(new_good)
        bad8["corpus"] = dict(new_good["corpus"])
        bad8["corpus"]["distractor_shape"] = "agentmemory 92.9% fitted"
        r = _write_and_check(prior_good, bad8)
        if r != 1:
            print("SELFTEST FAIL: fixture 8 (shape not unfitted) was not rejected")
            sys.exit(1)

        # === CONFORMING FIXTURE (must be accepted) ===
        r = _write_and_check(prior_good, new_good)
        if r is not None:
            print("SELFTEST FAIL: conforming fixture was not accepted")
            sys.exit(1)

        print("SELFTEST PASS")
        sys.exit(0)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        _run_check(BASE)