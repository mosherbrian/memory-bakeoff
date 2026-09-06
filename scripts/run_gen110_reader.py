#!/usr/bin/env python3
"""Gen110: the first controlled `reader-interference-v1` measurement.

Consumes the Gen109 freeze as IMMUTABLE input. Verifies both hashes - the
contract's self-identifying `contract_sha256` and the manifest's file digest,
which are different things and are never conflated - then freezes an execution
addendum and the complete 60-call schedule BEFORE the first scored request.

Fails closed. No silent retry, no cell selection, no ruler edits after output
exists. Every call is stateless: no answer or history from one cell may reach
another.
"""
from __future__ import annotations

import argparse, hashlib, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                      # noqa: E402
from memory_bakeoff import reader_interference as R            # noqa: E402

GENERATION = 110
FROZEN = ROOT / "results" / "gen109" / "attempt1" / "reader_interference_v1.json"
CONTRACT_SHA = "bc00267aed3da0e870387f3193c05536cd1cb5c1a2325d427d7a6b93915817a4"
FILE_SHA = "04222baddf36e6a31758ea152b1d0913a1e1a9635bcf00b147d657b15b67d879"

ENDPOINT = "http://strix-halo.local:8080/v1"
MODEL = "qwen3.6-35b-vulkan-nothink"
TEMPERATURE = 0.0
SEED = 0
MAX_TOKENS = 256
REPETITIONS = 3
EVIDENCE_CLASS = "controlled_reader_interference"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_frozen() -> dict:
    raw = FROZEN.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FILE_SHA:
        raise SystemExit("FAIL CLOSED: Gen109 artifact file digest differs")
    doc = json.loads(raw)
    if doc["contract_sha256"] != CONTRACT_SHA or R.contract_hash() != CONTRACT_SHA:
        raise SystemExit("FAIL CLOSED: contract_sha256 differs from the freeze")
    fixture = doc["fixture"]
    if len(fixture["cases"]) != 20 or len(fixture["cores"]) != 4:
        raise SystemExit("FAIL CLOSED: fixture cardinality differs")
    if {c["condition"] for c in fixture["cases"]} != set(R.CONDITIONS):
        raise SystemExit("FAIL CLOSED: condition set differs")
    for core in fixture["cores"]:
        pair = [c for c in fixture["cases"]
                if c["core"] == core and c["condition"] in R.CONFLICT_PAIR]
        R.assert_conflict_pair_differs_only_in_order(*pair)
        R.assert_within_core(pair[0])
    return doc


def build_prompt(case: dict) -> str:
    """Records in the frozen context order, then the question. Nothing else."""
    by_id = {r["id"]: r for r in case["records"]}
    lines = [case["instruction"], "", "RECORDS:"]
    lines.extend(f"[{rid}] {by_id[rid]['text']}" for rid in case["context_order"])
    if not case["context_order"]:
        lines.append("(no records)")
    lines.extend(["", f"QUESTION: {case['question']}"])
    return "\n".join(lines)


def call(prompt: str) -> dict:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE, "seed": SEED, "max_tokens": MAX_TOKENS,
    }).encode()
    request = urllib.request.Request(
        f"{ENDPOINT}/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = json.loads(response.read())
    choice = payload["choices"][0]
    return {"content": choice["message"]["content"],
            "finish_reason": choice.get("finish_reason"),
            "served_model": payload.get("model"),
            "elapsed_s": round(time.time() - started, 2)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="freeze the addendum and schedule, make no calls")
    args = parser.parse_args()

    doc = load_frozen()
    fixture = doc["fixture"]
    cases = sorted(fixture["cases"], key=lambda c: c["id"])   # frozen serial order

    out = EV.attempt_dir(ROOT, GENERATION, 1)
    PRE_EXECUTION = {"execution_addendum.json", "call_schedule.json",
                     EV.MANIFEST}
    if out.exists():
        present = {p.name for p in out.iterdir()}
        # Continuing into a pre-execution freeze is the intended flow: the
        # addendum and schedule MUST land before the first request. Any reader
        # output already present means a run happened, and this fails closed
        # rather than overwriting it or silently picking another attempt.
        if not present <= PRE_EXECUTION:
            raise SystemExit(
                f"FAIL CLOSED: {out} already holds reader output "
                f"({sorted(present - PRE_EXECUTION)}); report rather than "
                "overwriting evidence or choosing another attempt")
        print(f"continuing into the pre-execution freeze at {out}")

    schedule = [{"call_index": i, "repetition": rep, "case_id": case["id"],
                 "core": case["core"], "condition": case["condition"],
                 "prompt_sha256": sha(build_prompt(case))}
                for i, (rep, case) in enumerate(
                    ((r, c) for r in range(1, REPETITIONS + 1) for c in cases), 1)]

    addendum = {
        "generation": GENERATION,
        "consumes": {"path": str(FROZEN.relative_to(ROOT)),
                     "contract_sha256": CONTRACT_SHA, "file_sha256": FILE_SHA},
        "evidence_class": EVIDENCE_CLASS,
        "endpoint": ENDPOINT, "requested_model": MODEL,
        "thinking": "disabled (nothink alias)",
        "temperature": TEMPERATURE, "seed": SEED, "seed_support": "ACCEPTED",
        "max_tokens": MAX_TOKENS, "repetitions": REPETITIONS,
        "planned_calls": len(schedule), "stateless": True,
        "no_silent_retry": True,
        "scope_note": "This experiment CONTROLS which benchmark-owned records the "
                      "reader sees. It does NOT establish that any tested memory "
                      "product presents this context or this order.",
    }
    addendum["addendum_sha256"] = sha(json.dumps(addendum, sort_keys=True))

    if not (out / "execution_addendum.json").exists():
        EV.write_evidence(out, "execution_addendum.json", addendum)
        EV.write_evidence(out, "call_schedule.json",
                          {"schedule_sha256": sha(json.dumps(schedule, sort_keys=True)),
                           "calls": schedule})
        print(f"froze addendum and {len(schedule)}-call schedule at {out}")
    else:
        frozen_add = json.loads((out / "execution_addendum.json").read_text())
        if frozen_add["addendum_sha256"] != addendum["addendum_sha256"]:
            raise SystemExit("FAIL CLOSED: execution parameters changed after "
                             "the addendum was frozen")
        frozen_sched = json.loads((out / "call_schedule.json").read_text())
        if frozen_sched["schedule_sha256"] != sha(json.dumps(schedule, sort_keys=True)):
            raise SystemExit("FAIL CLOSED: call schedule changed after freezing")
        print(f"reusing the frozen addendum and schedule at {out} (hashes match)")
    if args.dry_run:
        return 0

    requests_path, responses_path = out / "reader_requests.jsonl", out / "reader_responses.jsonl"
    rows = []
    with requests_path.open("w") as rq, responses_path.open("w") as rs:
        for entry in schedule:
            case = next(c for c in cases if c["id"] == entry["case_id"])
            prompt = build_prompt(case)
            rq.write(json.dumps({**entry, "prompt": prompt}) + "\n")
            try:
                result = call(prompt)
                disposition = "COMPLETED"
            except Exception as exc:                       # preserve, never retry
                result = {"content": "", "finish_reason": None,
                          "served_model": None, "elapsed_s": None,
                          "error": f"{type(exc).__name__}: {exc}"}
                disposition = "FAILED"
            fingerprint = sha(result["content"] or result.get("error", ""))
            rs.write(json.dumps({**entry, **result,
                                 "response_sha256": fingerprint,
                                 "disposition": disposition}) + "\n")
            parsed = R.parse_response(result["content"] or "")
            graded = R.grade(parsed, current_id=case["current_id"],
                             stale_id=case["stale_id"],
                             current_answer=case["current_answer"],
                             stale_answer=case["stale_answer"],
                             answerable=case["answerable"])
            R.assert_parse_and_grade_are_separate({**parsed, **graded})
            rows.append({**entry, "disposition": disposition,
                         "served_model": result["served_model"],
                         "finish_reason": result["finish_reason"],
                         "response_sha256": fingerprint,
                         "parse_status": parsed["parse_status"],
                         "answer_text": parsed["answer_text"],
                         "cited_record_ids": list(parsed["cited_record_ids"]),
                         "grade": graded["grade"], "decision": graded["decision"],
                         "why": graded["why"]})
            print(f"  [{entry['call_index']:>2}/{len(schedule)}] "
                  f"{entry['case_id']:<44} {graded['grade']}")

    for name, body in (("reader_requests.jsonl", requests_path.read_text()),
                       ("reader_responses.jsonl", responses_path.read_text())):
        EV.record(out, name, body)
    EV.write_evidence(out, "reader_interference_results.json",
                      {"generation": GENERATION, "evidence_class": EVIDENCE_CLASS,
                       "addendum_sha256": addendum["addendum_sha256"],
                       "contract_sha256": CONTRACT_SHA,
                       "planned_calls": len(schedule),
                       "completed": sum(r["disposition"] == "COMPLETED" for r in rows),
                       "cells": rows})
    print(f"\nverify: {EV.verify(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
