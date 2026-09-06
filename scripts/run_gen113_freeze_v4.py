#!/usr/bin/env python3
"""Gen113: freeze `reader-interference-v4`. Identity repair only; nothing runs."""
from __future__ import annotations

import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                          # noqa: E402
from memory_bakeoff import reader_interference_v3 as V3            # noqa: E402
from memory_bakeoff import reader_interference_v4 as V4            # noqa: E402

GENERATION = 113


def blind_spot_witnesses() -> list[dict]:
    """Prove, for the record, what v3's digest could not see."""
    v3_before, v4_before = V3.contract_hash(), V4.contract_hash()
    rows, originals = [], {}

    def probe(name, attribute, replacement, effect):
        originals[attribute] = getattr(V3, attribute)
        setattr(V3, attribute, replacement)
        try:
            v4_moved = V4.contract_hash() != v4_before
        except Exception:
            v4_moved = True
        row = {"mutation": name, "observable_effect": effect,
               "v3_hash_before": v3_before, "v3_hash_after": V3.contract_hash(),
               "v3_hash_moved": V3.contract_hash() != v3_before,
               "v4_hash_moved": v4_moved}
        setattr(V3, attribute, originals[attribute])
        rows.append(row)

    probe("classifier replaced", "classify_answer", lambda a, c: "NEITHER",
          "every answer classifies NEITHER")
    probe("grader replaced", "grade",
          lambda p, c: {"outcome": V3.PROHIBITED_STALE, "answer_class": "X",
                        "citation_relation": "Y", "why": ""},
          "every response grades prohibited_stale")
    probe("parser replaced", "parse_response",
          lambda t: {"parse_status": "PARSED", "parsed": True,
                     "answer": "hijacked", "citations": ()},
          "malformed output parses as valid")
    probe("prompt projection replaced", "project_prompt",
          lambda c: "LEAKED: the second record is the current one",
          "the prompt hands the reader the answer")
    return rows


def main() -> int:
    for gen, count in ((109, 1), (110, 6), (111, 2), (112, 2)):
        result = EV.verify(ROOT / "results" / f"gen{gen}" / "attempt1")
        if not result["verified"] or result["artifacts"] != count:
            raise SystemExit(f"FAIL CLOSED: gen{gen}: {result}")
    print("all prior attempts verify")

    frozen_v3 = json.loads(
        (ROOT / "results/gen112/attempt1/reader_interference_v3.json").read_text())
    if len(frozen_v3["truth_matrix"]) != 360 or \
            {r["outcome"] for r in frozen_v3["truth_matrix"]} != set(V3.OUTCOMES) or \
            len(frozen_v3["prompt_sha256"]) != 20:
        raise SystemExit("FAIL CLOSED: Gen112 artifact is not as described")
    V3.assert_no_control_pass_from_a_bad_answer(frozen_v3["truth_matrix"])
    print("Gen112 artifact confirmed: 360 rows, 9 outcomes, 20 prompts, no bad control pass")

    witnesses = blind_spot_witnesses()
    if any(w["v3_hash_moved"] for w in witnesses):
        raise SystemExit("FAIL CLOSED: a v3 witness moved the hash; re-derive")
    if not all(w["v4_hash_moved"] for w in witnesses):
        missed = [w["mutation"] for w in witnesses if not w["v4_hash_moved"]]
        raise SystemExit(f"FAIL CLOSED: v4 still blind to {missed}")
    print(f"witnesses: {len(witnesses)} mutations invisible to v3, all visible to v4")

    equivalence = V4.assert_behaviour_identical_to_v3()
    payload = V4.contract_payload()
    digest = V4.contract_hash(payload)

    out = EV.next_attempt(ROOT, GENERATION)
    EV.write_evidence(out, "reader_interference_v4.json", {
        "contract_version": V4.CONTRACT_VERSION,
        "contract_sha256": digest,
        "status": "FROZEN_UNRUN",
        "reader_question_state": "OPEN - Gen113 is NOT a reader result",
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
        "supersedes": V4.SUPERSEDES,
        "exclusions": list(V4.EXCLUSIONS),
        "behaviour_identical_to_v3": equivalence,
        "contract_payload": payload,
    })
    EV.write_evidence(out, "gen112_contract_hash_gap_audit.json", {
        "defect": "the v3 contract digest committed to declarations only",
        "found_by": "control plane, reviewing the v3 payload against its "
                    "implementation",
        "omitted_from_v3_payload": [
            "parse_response", "classify_answer", "citation_relation", "grade",
            "project_prompt", "build_fixture", "truth_matrix", "prompt hashes",
            "control_passing_forms", "source file bytes"],
        "scientific_consequence": "parser, classifier, grading or prompt "
                                  "behaviour could change while contract_sha256 "
                                  "stayed constant - including a prompt that "
                                  "leaks which record is current, which is "
                                  "precisely what a freeze must detect",
        "witnesses": witnesses,
        "executor_found_gap_in_its_own_repair": {
            "detail": "v4's first prompt_hashes bound project_prompt at import, "
                      "so runtime substitution left the digest unmoved - one of "
                      "four mutations still missed, and the worst one",
            "repair": "resolve through the module at call time",
            "found_by": "executor, by running its own mutation probe"},
        "gen112_files_modified": False,
        "v3_never_executed": True,
        "scientific_loss": "none",
    })
    verification = V4.verify_contract(
        json.loads((out / "reader_interference_v4.json").read_text()))
    manifest = EV.verify(out)
    print(f"\nwrote {out}\ncontract sha256: {digest}")
    print(f"independent verify: {verification['verified']} {verification['problems']}")
    print(f"manifest verify   : {manifest}")
    if not (verification["verified"] and manifest["verified"]):
        raise SystemExit("verification failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
