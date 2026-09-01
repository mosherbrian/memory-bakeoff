"""Prepare auditable reader requests from an immutable retrieval artifact.

This module deliberately never instantiates a provider.  It is for downstream
reader evaluation when the retrieval system must not be rerun.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Sequence

from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.llm import LLMMessage, LLMRequest
from memory_bakeoff.models import RetrievalItem, RetrievalResult
from memory_bakeoff.reader_eval import ANSWER_SPECS, AnswerSpec, _reader_prompt


SIDECAR_PROTOCOL_VERSION = 1


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def prepare_frozen_reader_requests(
    run_path: str | Path,
    *,
    provider_label: str,
    specs: Sequence[AnswerSpec] = ANSWER_SPECS,
) -> tuple[list[LLMRequest], list[dict[str, Any]], dict[str, Any]]:
    """Build exact reader prompts from a published ``run.json`` without retrieval."""
    source = Path(run_path).resolve()
    raw = json.loads(source.read_text())
    if not isinstance(raw, list) or len(raw) != 1:
        raise ValueError(f"expected one benchmark row in {source}")
    row = raw[0]
    trace = row.get("provider_diagnostics", {}).get("native_ingest_trace")
    if not isinstance(trace, list):
        raise ValueError(f"{source} has no native ingest trace")
    text_by_id: dict[str, str] = {}
    for entry in trace:
        canonical_id = entry.get("canonical_record_id")
        content = entry.get("native_memory", {}).get("content")
        if not isinstance(canonical_id, str) or not isinstance(content, str):
            raise ValueError(f"invalid native provenance entry in {source}")
        if canonical_id in text_by_id and text_by_id[canonical_id] != content:
            raise ValueError(f"ambiguous native text for {canonical_id} in {source}")
        text_by_id[canonical_id] = content

    distractors = max(0, len(text_by_id) - 50)
    records, cases = build_corpus(distractors=distractors)
    record_by_id = {record.id: record for record in records}
    case_by_id = {case.id: case for case in cases}
    details_by_id = {detail["query_id"]: detail for detail in row.get("details", [])}
    requests: list[LLMRequest] = []
    evidence: list[dict[str, Any]] = []
    for spec in specs:
        case = case_by_id.get(spec.case_id)
        detail = details_by_id.get(spec.case_id)
        if case is None or detail is None:
            raise ValueError(f"missing held-out case {spec.case_id} in {source}")
        retrieved_ids = detail.get("retrieved_ids")
        if not isinstance(retrieved_ids, list) or not all(isinstance(item, str) for item in retrieved_ids):
            raise ValueError(f"invalid retrieved IDs for {spec.case_id} in {source}")
        missing = [item for item in retrieved_ids if item not in text_by_id or item not in record_by_id]
        if missing:
            raise ValueError(f"unmappable frozen evidence for {spec.case_id}: {missing}")
        result = RetrievalResult(
            items=[RetrievalItem(record_id=item, text=text_by_id[item]) for item in retrieved_ids],
            latency_ms=float(detail.get("latency_ms", 0.0)),
        )
        request_id = f"reader_{provider_label}_{case.id}"
        request = LLMRequest(
            messages=(
                LLMMessage("system", "You are a strict memory-grounded coding assistant. Never use outside knowledge or guess."),
                LLMMessage("user", _reader_prompt(case, result)),
            ),
            temperature=0.0,
            request_id=request_id,
            metadata={
                "provider": provider_label,
                "case_id": case.id,
                "mode": row.get("mode"),
                "top_k": len(retrieved_ids),
                "retrieved_ids": retrieved_ids,
                "frozen_retrieval_artifact": str(source),
                "frozen_retrieval_sha256": _sha256(source),
            },
        )
        harmful_ranks = [index + 1 for index, item in enumerate(retrieved_ids) if item in case.prohibited_ids]
        wrong_scope_ranks = (
            [index + 1 for index, item in enumerate(retrieved_ids) if record_by_id[item].scope != case.scope]
            if case.scope != "repo:demo"
            else []
        )
        requests.append(request)
        evidence.append(
            {
                "case_id": case.id,
                "category": case.category,
                "query": case.query,
                "retrieved_ids": retrieved_ids,
                "retrieved_context": request.messages[-1].content,
                "prohibited_ids": list(case.prohibited_ids),
                "prohibited_context_ranks": harmful_ranks,
                "stale_or_prohibited_context_present": bool(harmful_ranks),
                "wrong_scope_context_ranks": wrong_scope_ranks,
                "wrong_scope_context_present": bool(wrong_scope_ranks),
                "request_id": request_id,
                "request_fingerprint": request.fingerprint(),
            }
        )
    manifest = {
        "schema_version": 1,
        "status": "awaiting_interactive_sidecar_responses",
        "provider_label": provider_label,
        "retrieval_artifact": {"path": str(source), "sha256": _sha256(source)},
        "retrieval_identity": {
            "provider": row.get("provider"),
            "experiment_class": row.get("experiment_class"),
            "mode": row.get("mode"),
            "provider_configuration": row.get("provider_configuration"),
            "provenance": row.get("provenance"),
        },
        "reader_identity": {
            "backend": "chatgpt_sidecar",
            "expected_response_model": "GPT-5.6 Sol via ChatGPT sidecar",
            "prompt_template": "memory_bakeoff.reader_eval._reader_prompt",
            "temperature": 0.0,
            "grader": "memory_bakeoff.reader_eval.score_answer",
            "replay_rule": "response replay requires the same request_id and fingerprint",
        },
        "case_count": len(evidence),
        "harmful_context_case_rate": sum(item["stale_or_prohibited_context_present"] for item in evidence) / len(evidence),
        "wrong_scope_context_case_rate": sum(item["wrong_scope_context_present"] for item in evidence) / len(evidence),
        "answer_metrics": None,
        "answer_metrics_reason": "No interactive ChatGPT sidecar responder is available in this Codex session; answers must not be fabricated.",
    }
    return requests, evidence, manifest


def write_sidecar_request_package(
    outdir: str | Path,
    requests: Sequence[LLMRequest],
    evidence: Sequence[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    """Write an immutable, sidecar-compatible pending batch and its evidence."""
    out = Path(outdir)
    if out.exists():
        raise FileExistsError(f"frozen reader package already exists: {out}")
    for name in ("requests", "responses", "batches"):
        (out / name).mkdir(parents=True, exist_ok=False)
    batch_id = hashlib.sha256("\n".join(request.fingerprint() for request in requests).encode()).hexdigest()[:32]
    created_at = time.time()
    request_ids = []
    for index, request in enumerate(requests):
        if not request.request_id:
            raise ValueError("frozen sidecar requests require stable request IDs")
        request_ids.append(request.request_id)
        _atomic_json(
            out / "requests" / f"{request.request_id}.json",
            {
                "protocol_version": SIDECAR_PROTOCOL_VERSION,
                "request_id": request.request_id,
                "batch_id": batch_id,
                "batch_index": index,
                "created_at": created_at,
                "fingerprint": request.fingerprint(),
                "openai_request": request.to_openai(default_model="chatgpt-sidecar"),
                "metadata": request.metadata,
                "worker_instruction": f"Answer this LLM request as the model. Write a response JSON file named responses/{request.request_id}.json conforming to the ChatGPT sidecar protocol.",
            },
        )
    _atomic_json(
        out / "batches" / f"{batch_id}.json",
        {"protocol_version": SIDECAR_PROTOCOL_VERSION, "batch_id": batch_id, "request_ids": request_ids, "created_at": created_at, "status": "pending"},
    )
    _atomic_json(out / "contexts.json", {"cases": list(evidence)})
    _atomic_json(out / "manifest.json", {**manifest, "batch_id": batch_id, "request_ids": request_ids})
