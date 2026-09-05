#!/usr/bin/env python3
"""Gen61 Part A: generate with the grounding requirement, then apply the filter.

One change from Gen60: the prompt demands a verbatim REQUIREMENT citation per
test, and `spec_grounded.ground_bank` drops every test whose citation is not in
the visible instruction. Model, sampling, repetitions, corpus, task order and
screen are the Gen60 ones, untouched.

Both banks are kept for every run - the raw one the model wrote and the grounded
one that survives the filter - so the filter's effect can be measured rather
than assumed. Every raw stream is retained under `raw-evidence-retention-v1`.
"""
from __future__ import annotations

import hashlib, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import challenge_generation as C   # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R           # noqa: E402
from memory_bakeoff.evidence_ruler import spec_grounded as G            # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
OUT = ROOT / "results" / "pi_spec_grounded_gen61"
ARCHIVE = Path.home() / "gen61-raw-archive-attempt2"
CAPTURE = OUT / "raw_capture"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "qwen3.6-35b-vulkan-nothink"

TASK_ORDER = ["culvert", "dispatch", "ledger", "manifest",
              "pathsafe", "tally", "thermo", "valve"]
REPETITIONS = 3
SAMPLING = {"temperature": 0.6, "top_p": 0.8, "top_k": 20, "min_p": 0.0, "max_tokens": 4096}


def generate(prompt: str) -> tuple[str, str, float]:
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "stream": False, **SAMPLING}
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(request, timeout=900) as response:
        raw = response.read().decode()
    elapsed = round(time.time() - started, 2)
    return json.loads(raw)["choices"][0]["message"]["content"], raw, elapsed


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CAPTURE.mkdir(parents=True, exist_ok=True)
    screen = json.loads((ROOT / "results/pi_evidence_ruler_gen59"
                         / "gen60_frozen_screen.json").read_text())
    if screen["ruler"]["admitted_tasks"] != TASK_ORDER:
        raise SystemExit("task order does not match the frozen ruler")

    frozen = {
        "contract": G.contract(),
        "inherited_sanitizer": C.contract()["sanitizer"],
        "model": MODEL, "endpoint": "local llama-swap on this host",
        "sampling": SAMPLING, "task_order": TASK_ORDER, "repetitions": REPETITIONS,
        "total_calls": len(TASK_ORDER) * REPETITIONS,
        "prompt_template_sha256": hashlib.sha256(G.GENERATOR_PROMPT.encode()).hexdigest(),
        "gen60_prompt_template_sha256": hashlib.sha256(C.GENERATOR_PROMPT.encode()).hexdigest(),
        "ruler": "evidence-generation-gen59-v1",
        "screen_sha256": screen["contract_sha256"],
        "gen60_baseline": {"unsafe_as_gate": "4 of 8", "sensitivity": 1.0},
        "session": "one stateless HTTP request per repetition; no conversation carried over",
    }
    (OUT / "generation_contract.json").write_text(
        json.dumps(frozen, indent=2, sort_keys=True) + "\n")

    outputs, streams = [], []
    for task in TASK_ORDER:
        repo = FIXTURES / task / "repo"
        instruction = (FIXTURES / task / "spec.txt").read_text()
        # Same builder as Gen58/Gen60; only the template it fills has changed.
        prompt = C.build_prompt(instruction, repo).replace(
            C.GENERATOR_PROMPT.split("{prompt}")[0],
            G.GENERATOR_PROMPT.split("{prompt}")[0], 1)
        for repetition in range(1, REPETITIONS + 1):
            run_id = f"{task}-rep{repetition}"
            content, raw, elapsed = generate(prompt)
            capture = CAPTURE / f"{run_id}.json"
            capture.write_text(raw)
            streams.append(R.archive_stream(capture, ARCHIVE, run_id, "provider_stream.json"))
            parsed = C.parse_output(content)
            record = {
                "task": task, "repetition": repetition, "run_id": run_id,
                "seconds": elapsed,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "response_sha256": hashlib.sha256(content.encode()).hexdigest(),
                "accepted": parsed["accepted"], "reject_reason": parsed.get("reason"),
                "raw_test_functions": parsed.get("test_functions", []),
            }
            if parsed["accepted"]:
                grounded = G.ground_bank(parsed["code"], instruction)
                (OUT / "raw_banks").mkdir(exist_ok=True)
                (OUT / "raw_banks" / f"{run_id}.py").write_text(parsed["code"])
                if grounded["kept_count"]:
                    (OUT / "grounded").mkdir(exist_ok=True)
                    (OUT / "grounded" / f"{run_id}.py").write_text(grounded["code"])
                record.update({
                    "kept": grounded["kept"], "dropped": grounded["dropped"],
                    "kept_count": grounded["kept_count"],
                    "dropped_count": grounded["dropped_count"],
                    "code_sha256": grounded["sha256"],
                    "usable": bool(grounded["kept_count"]),
                })
            outputs.append(record)
            print(f"{run_id}: accepted={record['accepted']} "
                  f"raw={len(record.get('raw_test_functions', []))} "
                  f"kept={record.get('kept_count', 0)} "
                  f"dropped={record.get('dropped_count', 0)} {elapsed}s "
                  f"{record.get('reject_reason') or ''}", flush=True)

    (OUT / "generation_log.json").write_text(json.dumps(
        {"frozen": frozen, "outputs": outputs,
         "accepted": sum(1 for o in outputs if o["accepted"]),
         "usable": sum(1 for o in outputs if o.get("usable")),
         "raw_tests": sum(len(o.get("raw_test_functions", [])) for o in outputs),
         "kept_tests": sum(o.get("kept_count", 0) for o in outputs),
         "dropped_tests": sum(o.get("dropped_count", 0) for o in outputs),
         "total_seconds": round(sum(o["seconds"] for o in outputs), 1)},
        indent=2, sort_keys=True) + "\n")
    (OUT / "raw_stream_manifest.json").write_text(
        json.dumps(R.build_manifest(streams, ARCHIVE), indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "accepted": sum(1 for o in outputs if o["accepted"]), "of": len(outputs),
        "kept_tests": sum(o.get("kept_count", 0) for o in outputs),
        "dropped_tests": sum(o.get("dropped_count", 0) for o in outputs),
        "total_seconds": round(sum(o["seconds"] for o in outputs), 1)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
