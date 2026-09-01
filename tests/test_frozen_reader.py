from pathlib import Path

from memory_bakeoff.frozen_reader import prepare_frozen_reader_requests, write_sidecar_request_package


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
