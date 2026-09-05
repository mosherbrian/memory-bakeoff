"""Gen85: replay each engine's frozen evidence through one identical reader.

No engine is re-run. The committed LQ10 and LQ16 retrieval outputs are replayed
into a single pinned reader, and the reader's citations are graded by the frozen
scorer.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import reader_layer as reader
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
CASES = ("LQ10", "LQ16")


def retrieved_ids(root: pathlib.Path, engine: str, case_id: str) -> tuple[str, ...]:
    """Exactly what that engine returned, in its own order. Repetition 1."""
    path = root / "results" / RESULT_DIRS[engine] / "repetition-1.json"
    case = next(c for c in json.loads(path.read_text())["cases"] if c["case_id"] == case_id)
    return tuple(row["canonical_id"] for row in case["returned"])


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    by_id = {o.id: o for o in fixture.observations}
    cases = {c.id: c for c in fixture.cases if c.id in CASES}
    procedure, unknown = cases["LQ10"], cases["LQ16"]

    payload: dict[str, Any] = {
        "reader_contract": reader.contract(),
        "reader_contract_sha256": reader.contract_sha256(),
        "controls": reader.controls(score_longitudinal_case, score_answer_claim,
                                    fixture, procedure, unknown),
        "runs": {},
    }

    client = OpenAICompatibleLLM(base_url=BASE_URL, model=reader.MODEL, timeout_s=300.0)
    started = time.time()
    for engine in RESULT_DIRS:
        payload["runs"][engine] = {}
        for case_id in CASES:
            case = cases[case_id]
            ids = retrieved_ids(root, engine, case_id)
            records = tuple((i, by_id[i].assertion) for i in ids)
            prompt = reader.build_prompt(case.query, records)
            reader.assert_reader_input_clean(prompt, engine=engine)
            rows = []
            for repetition in range(1, reader.REPETITIONS + 1):
                response = client.complete(LLMRequest(
                    messages=[LLMMessage("system", prompt["system"]),
                              LLMMessage("user", prompt["user"])],
                    model=reader.MODEL, temperature=reader.TEMPERATURE,
                    max_tokens=reader.MAX_TOKENS))
                parsed = reader.parse_answer(response.content)
                row = {"repetition": repetition, "answer": response.content.strip(),
                       "parsed": parsed}
                if case_id == "LQ10":
                    if not parsed["parsed"]:
                        row["classes"] = []
                        row["status"] = reader.UNPARSED
                        row["excluded_from_scoring"] = True
                        row["adopted"] = None
                    else:
                        row["classes"] = list(score_longitudinal_case(
                            fixture, case, parsed["cited_ids"]).failure_classes)
                        row["status"] = "cited" if parsed["cited_ids"] else "declined"
                        row["excluded_from_scoring"] = False
                        row["adopted"] = row["classes"] == []
                else:
                    row["grade"] = reader.grade_abstention(
                        score_answer_claim, score_longitudinal_case, fixture, case, parsed)
                    row["abstained"] = row["grade"]["status"] == "abstained"
                rows.append(row)
            payload["runs"][engine][case_id] = {
                "retrieved_ids": list(ids), "records_shown": len(records),
                "repetitions": rows}
            flag = "adopted" if case_id == "LQ10" else "abstained"
            print(f"{engine:12s} {case_id} -> {[r[flag] for r in rows]}")
    payload["wall_clock_seconds"] = round(time.time() - started, 1)

    destination = root / "results" / "reader_layer_gen85"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "reader.json").write_text(json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(f"\nwall clock {payload['wall_clock_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
