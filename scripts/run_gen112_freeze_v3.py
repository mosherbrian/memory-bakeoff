#!/usr/bin/env python3
"""Gen112: freeze `reader-interference-v3`. Repair only; nothing is executed."""
from __future__ import annotations

import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                          # noqa: E402
from memory_bakeoff import reader_interference_v2 as V2            # noqa: E402
from memory_bakeoff import reader_interference_v3 as V3            # noqa: E402

GENERATION = 112


def witness(condition: str, answer: str) -> dict:
    case = next(c for c in V3.build_fixture()["cases"]
                if c["core"] == "throughput:atlas" and c["condition"] == condition)
    cite = [case["current_opaque"] or case["stale_opaque"]]
    reply = json.dumps({"answer": answer, "citations": cite})
    return {"condition": condition, "answer": answer, "citations": cite,
            "v2_outcome": V2.grade(V2.parse_response(reply), case)["outcome"],
            "v3_outcome": V3.grade(V3.parse_response(reply), case)["outcome"],
            "required": V3.MIXED}


def main() -> int:
    for gen, count in ((109, 1), (110, 6), (111, 2)):
        result = EV.verify(ROOT / "results" / f"gen{gen}" / "attempt1")
        if not result["verified"] or result["artifacts"] != count:
            raise SystemExit(f"FAIL CLOSED: gen{gen} does not verify: {result}")
        print(f"gen{gen} verifies ({count} artifacts)")
    frozen_v2 = json.loads(
        (ROOT / "results/gen111/attempt1/reader_interference_v2.json").read_text())
    if frozen_v2["contract_sha256"] != V2.contract_hash():
        raise SystemExit("FAIL CLOSED: v2 contract hash drifted")
    print("v2 contract hash confirmed")

    witnesses = [witness("CLEAN_CURRENT", "41 t/s, previously 27 t/s"),
                 witness("CLEAN_STALE_NEGATIVE_CONTROL", "27 t/s, now 41 t/s")]
    for w in witnesses:
        if w["v3_outcome"] != V3.MIXED:
            raise SystemExit(f"FAIL CLOSED: witness unrepaired: {w}")

    matrix = V3.truth_matrix()
    V3.assert_no_control_pass_from_a_bad_answer(matrix)
    forms = V3.control_passing_forms()
    if {r["outcome"] for r in matrix} != set(V3.OUTCOMES):
        raise SystemExit("FAIL CLOSED: not every outcome is reachable")

    fixture = V3.build_fixture()
    for case in fixture["cases"]:
        V3.assert_prompt_is_blind(case)
        if V3.project_prompt(case) != V2.project_prompt(case):
            raise SystemExit(f"FAIL CLOSED: prompt drifted for {case['id']}")

    out = EV.next_attempt(ROOT, GENERATION)
    EV.write_evidence(out, "reader_interference_v3.json", {
        "contract_version": V3.CONTRACT_VERSION,
        "contract_sha256": V3.contract_hash(),
        "status": "FROZEN_UNRUN",
        "reader_question_state": "OPEN - Gen112 is NOT a reader result",
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
        "supersedes": V3.SUPERSEDES,
        "conditions": list(V3.CONDITIONS),
        "answer_classes": list(V3.ANSWER_CLASSES),
        "citation_relations": list(V3.CITATION_RELATIONS),
        "outcomes": list(V3.OUTCOMES),
        "canonical_values": V3.CANONICAL, "normalization": V3.NORMALIZATION,
        "instruction": V3.INSTRUCTION, "accept_json_fence": V3.ACCEPT_JSON_FENCE,
        "grading_precedence": [
            "parser status", "semantic answer class (case-independent)",
            "citation relation", "condition-relative outcome"],
        "control_gate": V3.CONTROL_RULE,
        "control_passing_forms": forms,
        "across_core_verdicts": list(V3.ACROSS_CORE_VERDICTS),
        "questions": list(V3.QUESTIONS),
        "change_ledger": list(V3.CHANGE_LEDGER),
        "parser_fixtures": {"valid": list(V3.VALID_FIXTURES),
                            "invalid": list(V3.INVALID_FIXTURES)},
        "truth_matrix": matrix,
        "prompt_sha256": {c["id"]: __import__("hashlib").sha256(
            V3.project_prompt(c).encode()).hexdigest() for c in fixture["cases"]},
        "fixture": fixture,
        "future_run": {"gen112_runs_nothing": True,
                       "must_not": ["reuse any prior reader response",
                                    "derive tolerance from Gen110 wording"]},
    })
    EV.write_evidence(out, "gen111_grading_defect_audit.json", {
        "defect": "semantic detection was gated by presented-record pointers",
        "found_by": "control plane, reviewing the frozen v2 truth table and grader",
        "root_cause_branch": [
            'said_current = case["current_opaque"] is not None and contains_value(...)',
            'said_stale   = case["stale_opaque"]   is not None and contains_value(...)'],
        "why_it_matters": "an absent record-role pointer was read as absence of "
                          "that value in the answer, so a self-contradicting "
                          "reply could PASS a control gate and silently certify "
                          "a core as interpretable",
        "witnesses": witnesses,
        "repair": "classify_answer() takes only the answer text and the core "
                  "name, so the defect is unrepresentable rather than merely "
                  "unwritten; BOTH always resolves to mixed_contradictory_answer",
        "gen111_artifacts_modified": False,
        "v2_never_executed": True,
        "scientific_loss": "none - v2 was frozen and never run",
    })
    verified = EV.verify(out)
    print(f"\nwrote {out}\ncontract sha256: {V3.contract_hash()}\nverify: {verified}")
    if not verified["verified"]:
        raise SystemExit("manifest does not verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
