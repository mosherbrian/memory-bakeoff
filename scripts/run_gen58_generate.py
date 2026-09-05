#!/usr/bin/env python3
"""Gen58 Part C: generate the challenge banks. 12 calls, frozen order.

The generator sees the visible instruction and the shipped repository. It does
not see any candidate implementation, outcome, hidden verifier or reference fix.
Every raw stream is retained under `raw-evidence-retention-v1`.
"""
from __future__ import annotations

import hashlib, json, os, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import challenge_generation as C   # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R           # noqa: E402

OUT = ROOT / "results" / "pi_model_assisted_evidence_gen58"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
ARCHIVE = Path.home() / "gen58-raw-archive"
CAPTURE = OUT / "raw_capture"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "qwen3.6-35b-vulkan-nothink"

# Frozen before the first call: order, repetitions, sampling, budget.
TASK_ORDER = ["IP1", "IP2", "IP3", "IP4"]
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
    body = json.loads(raw)
    return body["choices"][0]["message"]["content"], raw, elapsed


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CAPTURE.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((GEN48 / "task_manifest.json").read_text())

    frozen = {
        "contract": C.contract(),
        "model": MODEL, "endpoint": "local llama-swap on this host",
        "sampling": SAMPLING, "task_order": TASK_ORDER, "repetitions": REPETITIONS,
        "total_calls": len(TASK_ORDER) * REPETITIONS,
        "prompt_template_sha256": hashlib.sha256(C.GENERATOR_PROMPT.encode()).hexdigest(),
        "session": "one stateless HTTP request per repetition; no conversation carried over",
    }
    (OUT / "model_assisted_challenge_contract.json").write_text(
        json.dumps(frozen, indent=2, sort_keys=True) + "\n")

    outputs, streams = [], []
    for task in TASK_ORDER:
        repo = ROOT / manifest["tasks"][task]["repo_path"]
        instruction = manifest["tasks"][task]["prompt"]
        prompt = C.build_prompt(instruction, repo)
        for repetition in range(1, REPETITIONS + 1):
            run_id = f"{task}-rep{repetition}"
            content, raw, elapsed = generate(prompt)
            capture = CAPTURE / f"{run_id}.json"
            capture.write_text(raw)
            archived = R.archive_stream(capture, ARCHIVE, run_id, "provider_stream.json")
            streams.append(archived)
            parsed = C.parse_output(content)
            outputs.append({
                "task": task, "repetition": repetition, "run_id": run_id,
                "seconds": elapsed,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "response_sha256": hashlib.sha256(content.encode()).hexdigest(),
                "response_bytes": len(content.encode()),
                "accepted": parsed["accepted"],
                "reject_reason": parsed.get("reason"),
                "test_functions": parsed.get("test_functions", []),
                "code_sha256": parsed.get("sha256"),
            })
            if parsed["accepted"]:
                (OUT / "generated").mkdir(exist_ok=True)
                (OUT / "generated" / f"{run_id}.py").write_text(parsed["code"])
            print(f"{run_id}: accepted={parsed['accepted']} "
                  f"tests={len(parsed.get('test_functions', []))} {elapsed}s "
                  f"{parsed.get('reason', '')}")

    manifest_out = R.build_manifest(streams, ARCHIVE)
    (OUT / "generation_log.json").write_text(json.dumps(
        {"frozen": frozen, "outputs": outputs,
         "accepted": sum(1 for o in outputs if o["accepted"]),
         "total_seconds": round(sum(o["seconds"] for o in outputs), 1)},
        indent=2, sort_keys=True) + "\n")
    (OUT / "raw_stream_manifest.json").write_text(
        json.dumps(manifest_out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"accepted": sum(1 for o in outputs if o["accepted"]),
                      "of": len(outputs),
                      "total_seconds": round(sum(o["seconds"] for o in outputs), 1)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
