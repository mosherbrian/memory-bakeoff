"""Gen85 control: is the LQ16 abstention split an engine difference or an order effect?

perseus, mem0 and hindsight all returned the SAME four records for LQ16. perseus
and mem0 returned them in the same order and the reader asserted; hindsight
returned them in a different order and the reader abstained. This holds the
content fixed and varies only the order.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import reader_layer as reader
from memory_bakeoff.llm.base import LLMMessage, LLMRequest
from memory_bakeoff.llm.openai_compat import OpenAICompatibleLLM
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case)

BASE_URL = "http://127.0.0.1:8080/v1"
RECORDS = ("L001", "L002", "L003", "L004")


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    by_id = {o.id: o for o in fixture.observations}
    case = next(c for c in fixture.cases if c.id == "LQ16")
    client = OpenAICompatibleLLM(base_url=BASE_URL, model=reader.MODEL, timeout_s=300.0)

    rows = []
    for order in itertools.permutations(RECORDS):
        prompt = reader.build_prompt(case.query, tuple((i, by_id[i].assertion) for i in order))
        reader.assert_reader_input_clean(prompt, engine="ablation")
        response = client.complete(LLMRequest(
            messages=[LLMMessage("system", prompt["system"]),
                      LLMMessage("user", prompt["user"])],
            model=reader.MODEL, temperature=reader.TEMPERATURE, max_tokens=reader.MAX_TOKENS))
        grade = reader.grade_abstention(score_answer_claim, score_longitudinal_case,
                                        fixture, case, reader.parse_answer(response.content))
        rows.append({"order": list(order), "status": grade["status"],
                     "cited": list(grade["cited"]), "answer": response.content.strip()})

    abstained = [r for r in rows if r["status"] == "abstained"]
    payload = {
        "question": "does the LQ16 abstention split survive holding the evidence set "
                    "fixed and varying only its order?",
        "records": list(RECORDS),
        "orders_tried": len(rows),
        "abstained": len(abstained),
        "asserted": sum(1 for r in rows if r["status"] == "asserted"),
        "unparsed": sum(1 for r in rows if r["status"] == reader.UNPARSED),
        "verdict": ("ORDER_EFFECT" if 0 < len(abstained) < len(rows)
                    else "ORDER_INDEPENDENT"),
        "rows": rows,
    }
    destination = root / "results" / "reader_layer_gen85"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "order_ablation.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(f"{payload['abstained']} abstained / {payload['asserted']} asserted / "
          f"{payload['unparsed']} unparsed of {payload['orders_tried']} orders "
          f"-> {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
