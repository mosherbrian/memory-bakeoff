#!/usr/bin/env python3
"""Gen111: freeze `reader-interference-v2`. Design and integrity only.

No reader, model, sidecar, memory engine, inference endpoint or GPU is invoked.
Writes the repaired contract plus a separate audit of the leakage defect the
control plane found, without touching a byte of Gen109 or Gen110.
"""
from __future__ import annotations

import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                          # noqa: E402
from memory_bakeoff import reader_interference_v2 as V             # noqa: E402

GENERATION = 111
GEN110 = ROOT / "results" / "gen110" / "attempt1"
GEN109 = ROOT / "results" / "gen109" / "attempt1"


def main() -> int:
    # Verify the prior attempts before relying on anything in them.
    for name, path in (("gen109", GEN109), ("gen110", GEN110)):
        result = EV.verify(path)
        if not result["verified"]:
            raise SystemExit(f"FAIL CLOSED: {name} manifest does not verify: {result}")
        print(f"{name} verifies: {result['artifacts']} artifacts")

    fixture = V.build_fixture()
    table = V.truth_table()
    reachable = {r["outcome"] for r in table}
    missing = set(V.OUTCOMES) - reachable
    if missing:
        raise SystemExit(f"FAIL CLOSED: outcomes unreachable in the truth table: {missing}")

    payload = {
        "contract_version": V.CONTRACT_VERSION,
        "contract_sha256": V.contract_hash(),
        "status": "FROZEN_UNRUN",
        "reader_question_state": "OPEN - Gen111 is NOT a reader result",
        "supersedes": V.SUPERSEDES,
        "conditions": list(V.CONDITIONS),
        "outcomes": list(V.OUTCOMES),
        "canonical_values": V.CANONICAL,
        "normalization": V.NORMALIZATION,
        "instruction": V.INSTRUCTION,
        "accept_json_fence": V.ACCEPT_JSON_FENCE,
        "questions": list(V.QUESTIONS),
        "control_gate": V.CONTROL_RULE,
        "across_core_verdicts": list(V.ACROSS_CORE_VERDICTS),
        "change_ledger": list(V.CHANGE_LEDGER),
        "parser_fixtures": {"valid": list(V.VALID_FIXTURES),
                            "invalid": list(V.INVALID_FIXTURES)},
        "truth_table": table,
        "fixture": fixture,
        "future_run": {
            "gen111_runs_nothing": True,
            "must": ["consume this contract and fixture unmodified",
                     "verify contract_sha256 and the manifest digest separately",
                     "write only under immutable-evidence-v1 attempt paths",
                     "apply the control gate before reporting any Q1-Q4 result"],
            "must_not": ["reuse Gen110 responses as a reader result",
                         "derive aliases or tolerances from Gen110 wording"],
        },
    }
    out = EV.next_attempt(ROOT, GENERATION)
    EV.write_evidence(out, "reader_interference_v2.json", payload)

    # The leakage defect gets its own artifact; Gen110's NON_EVIDENCE is immutable.
    sample = next(c for c in fixture["cases"]
                  if c["condition"] == "CONFLICT_STALE_FIRST")
    EV.write_evidence(out, "v1_leakage_audit.json", {
        "defect": "model-facing record ids disclosed the answer",
        "found_by": "control plane, reading the exact Gen110 requests",
        "detail": "v1 presented ids C1-CUR and C1-SUP. The suffixes name which "
                  "record is current and which is superseded, so every conflict "
                  "prompt handed the reader the answer. No v1 conflict "
                  "measurement could have meant anything.",
        "negative_regression_examples": ["C0-CUR", "C0-SUP", "C1-CUR", "C1-SUP",
                                         "C2-CUR", "C2-SUP", "C3-CUR", "C3-SUP"],
        "note": "These strings are used ONLY as things a prompt must never "
                "contain. No Gen110 answer is used as calibration.",
        "repair": "opaque role-neutral ids, evaluator-only mapping, and an "
                  "enforced prompt-projection audit",
        "example_repaired_prompt": V.project_prompt(sample),
        "gen110_artifacts_modified": False,
    })
    verified = EV.verify(out)
    print(f"\nwrote {out}")
    print(f"contract sha256: {V.contract_hash()}")
    print(f"verify         : {verified}")
    if not verified["verified"]:
        raise SystemExit("manifest does not verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
