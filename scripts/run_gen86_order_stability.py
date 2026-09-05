"""Gen86: the repaired decision channel, over every feasible ordering.

No engine re-run. Each DISTINCT evidence set from the committed LQ10/LQ16
retrieval is run through the same pinned reader in every permutation, so semantic
correctness can be reported apart from order stability.
"""
from __future__ import annotations

import itertools
import json
import math
import pathlib
import sys
import time
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import reader_contract_v3 as v3
from memory_bakeoff.llm.base import LLMMessage, LLMRequest
from memory_bakeoff.llm.openai_compat import OpenAICompatibleLLM
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case)

BASE_URL = "http://127.0.0.1:8080/v1"
RESULT_DIRS = {
    "perseus": "perseus_vault_gen29_longitudinal",
    "hindsight": "hindsight_gen31_longitudinal",
    "mem0": "mem0_gen32_longitudinal",
    "agentmemory": "agentmemory_gen33_longitudinal",
}
KIND = {"LQ10": "procedure", "LQ16": "unknown"}
MAX_PERMUTATIONS = 720  # feasibility ceiling; every set here is well under it


def retrieved(root: pathlib.Path, engine: str, case_id: str) -> tuple[str, ...]:
    path = root / "results" / RESULT_DIRS[engine] / "repetition-1.json"
    case = next(c for c in json.loads(path.read_text())["cases"] if c["case_id"] == case_id)
    return tuple(r["canonical_id"] for r in case["returned"])


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    by_id = {o.id: o for o in fixture.observations}
    cases = {c.id: c for c in fixture.cases if c.id in KIND}
    client = OpenAICompatibleLLM(base_url=BASE_URL, model=v3.MODEL, timeout_s=300.0)

    # Which engines share which evidence set. Sets, not orders.
    provenance: dict[str, dict[frozenset, dict]] = {}
    for case_id in KIND:
        provenance[case_id] = {}
        for engine in RESULT_DIRS:
            ids = retrieved(root, engine, case_id)
            key = frozenset(ids)
            entry = provenance[case_id].setdefault(
                key, {"records": sorted(ids), "engines": {}, "permutations": []})
            entry["engines"][engine] = list(ids)

    payload: dict[str, Any] = {
        "contract": v3.contract(),
        "contract_sha256": v3.contract_sha256(),
        "controls": v3.controls(score_longitudinal_case, score_answer_claim,
                                fixture, cases["LQ10"], cases["LQ16"]),
        "cases": {},
    }
    started = time.time()
    calls = 0
    for case_id, kind in KIND.items():
        case = cases[case_id]
        payload["cases"][case_id] = {"kind": kind, "evidence_sets": []}
        for key, entry in provenance[case_id].items():
            records = entry["records"]
            total = math.factorial(len(records))
            assert total <= MAX_PERMUTATIONS, f"{len(records)}! exceeds the ceiling"
            rows = []
            for order in itertools.permutations(records):
                prompt = v3.build_prompt(
                    kind, case.query, tuple((i, by_id[i].assertion) for i in order))
                v3.assert_reader_input_clean(prompt, engine="ablation")
                response = client.complete(LLMRequest(
                    messages=[LLMMessage("system", prompt["system"]),
                              LLMMessage("user", prompt["user"])],
                    model=v3.MODEL, temperature=v3.TEMPERATURE, max_tokens=v3.MAX_TOKENS))
                calls += 1
                if kind == "procedure":
                    graded = v3.score_procedure(score_longitudinal_case, fixture, case,
                                                v3.parse_procedure(response.content))
                else:
                    graded = v3.score_unknown(score_answer_claim, case,
                                              v3.parse_unknown(response.content))
                rows.append({"order": list(order), **{k: v for k, v in graded.items()}})
            scored = [r for r in rows if not r["excluded_from_scoring"]]
            correct = [r for r in scored if r["correct"]]
            payload["cases"][case_id]["evidence_sets"].append({
                "records": records,
                "engines": entry["engines"],
                "permutations": len(rows),
                "scored": len(scored),
                "unparsed": len(rows) - len(scored),
                "correct": len(correct),
                "correct_fraction": (len(correct) / len(scored)) if scored else None,
                "order_stable": len(correct) in (0, len(scored)) if scored else None,
                "decisions": sorted({str(r.get("decision") or r.get("adopted")) for r in scored}),
                "rows": rows,
            })
            engines = ", ".join(sorted(entry["engines"]))
            print(f"{case_id} [{engines}] {len(records)} records: "
                  f"{len(correct)}/{len(scored)} correct over {len(rows)} orders "
                  f"({'STABLE' if len(correct) in (0, len(scored)) else 'ORDER-SENSITIVE'})")
    payload["model_calls"] = calls
    payload["wall_clock_seconds"] = round(time.time() - started, 1)

    destination = root / "results" / "order_stability_gen86"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "stability.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(f"\n{calls} calls, {payload['wall_clock_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
