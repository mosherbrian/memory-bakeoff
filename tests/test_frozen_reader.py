import json
from pathlib import Path
import shutil

from memory_bakeoff.frozen_reader import (
    grade_frozen_sidecar_responses,
    prepare_frozen_reader_requests,
    write_frozen_reader_grades,
    write_sidecar_request_package,
)


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_reader_preserves_gen13_ranked_context(tmp_path):
    run = ROOT / "results" / "agentmemory_raw_product_gen13_stress-r1" / "run.json"
    requests, evidence, manifest = prepare_frozen_reader_requests(run, provider_label="agentmemory_gen13_stress_r1")
    q007 = next(item for item in evidence if item["case_id"] == "Q007")
    assert q007["retrieved_ids"][:2] == ["M011", "M012"]
    assert q007["prohibited_context_ranks"] == [1]
    assert "[M011] The build coordinator is strix03." in q007["retrieved_context"]
    assert manifest["answer_metrics"] is None
    out = tmp_path / "package"
    write_sidecar_request_package(out, requests, evidence, manifest)
    assert len(list((out / "requests").glob("*.json"))) == 14
    assert len(list((out / "responses").glob("*.json"))) == 0


def test_frozen_reader_grades_imported_sidecar_layout(tmp_path):
    package = tmp_path / "package"
    shutil.copytree(ROOT / "results" / "agentmemory_raw_product_gen14_reader_requests", package)
    for condition in ("core", "stress"):
        for request in (package / condition / "requests").glob("*.json"):
            raw = json.loads(request.read_text())
            answer = "INSUFFICIENT_MEMORY" if raw["metadata"]["case_id"] in {"Q025", "Q026"} else "wrong"
            (package / condition / "responses" / request.name).write_text(json.dumps({"protocol_version": 1, "request_id": raw["request_id"], "content": answer, "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}))
    result = grade_frozen_sidecar_responses(package)
    assert result["conditions"]["core"]["cases"] == 14
    out = tmp_path / "grades"
    write_frozen_reader_grades(result, out)
    assert (out / "reader_summary.md").exists()
