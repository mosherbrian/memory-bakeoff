#!/usr/bin/env python3
"""Gen64 Part A: label every Gen61 test, then let the JUSTIFIED critic delete.

Two passes, in this order, and the order is deliberate.

First the labelling pass, which is evaluator-side and never shown to the critic:
each Gen61 test is run against that task's trusted positive implementations. A
test that rejects a known-correct tree is KNOWN_FALSE - it is one of the 27
assertions that made four banks unusable. A test that rejects none of them is
VALID. These labels exist so the critic's deletions can be scored, not so they
can guide it.

Then the critic pass: one stateless call per test, seeing only the cited
requirement and that test's source.
"""
from __future__ import annotations

import ast, hashlib, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler import justified_critic as K   # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R      # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
GEN61 = ROOT / "results" / "pi_spec_grounded_gen61"
OUT = ROOT / "results" / "pi_justified_critic_gen64"
ARCHIVE = Path.home() / "gen64-raw-archive"
CAPTURE = OUT / "raw_capture"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "qwen3.6-35b-vulkan-nothink"
SAMPLING = {"temperature": 0.6, "top_p": 0.8, "top_k": 20, "min_p": 0.0, "max_tokens": 512}
TASK_ORDER = ["culvert", "dispatch", "ledger", "manifest",
              "pathsafe", "tally", "thermo", "valve"]


def ask(prompt: str) -> tuple[str, str, float]:
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "stream": False, **SAMPLING}
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(request, timeout=900) as response:
        raw = response.read().decode()
    return (json.loads(raw)["choices"][0]["message"]["content"], raw,
            round(time.time() - started, 2))


def bank_for(task: str, log: dict) -> tuple[str, dict[str, str]]:
    """The frozen Gen61 bank for a task, plus each test's cited requirement."""
    parts, quotes = [], {}
    for output in log["outputs"]:
        if output["task"] != task or not output.get("usable"):
            continue
        parts.append((GEN61 / "grounded" / f"{output['run_id']}.py").read_text())
        for kept in output["kept"]:
            quotes[kept["test"]] = kept["quote"]
    return "\n\n".join(parts), quotes


def materialise(task: str, overlay: dict[str, str]) -> Path:
    tree = Path(tempfile.mkdtemp(prefix=f"gen64-{task}-"))
    shutil.rmtree(tree)
    shutil.copytree(FIXTURES / task / "repo", tree)
    for relative, text in overlay.items():
        path = tree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return tree


def failing_tests(task: str, bank: str, overlay: dict[str, str]) -> set[str]:
    """Which tests in the bank reject this tree."""
    tree = materialise(task, overlay)
    (tree / "tests" / "tb.py").write_text(bank)
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/tb.py", "-q", "--tb=no",
         "-p", "no:cacheprovider"], cwd=tree, capture_output=True, text=True,
        timeout=300, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                          "PYTHONPATH": str(tree)})
    shutil.rmtree(tree, ignore_errors=True)
    return {line.split("::")[-1].split()[0]
            for line in done.stdout.splitlines() if line.startswith("FAILED")}


def test_sources(code: str) -> dict[str, str]:
    tree = ast.parse(code)
    found = {}
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")):
            found[node.name] = ast.unparse(node)
    return found


def strip_tests(code: str, remove: set[str]) -> str:
    tree = ast.parse(code)

    def sift(body):
        out = []
        for node in body:
            if isinstance(node, ast.ClassDef):
                node.body = sift(node.body) or [ast.Pass()]
                out.append(node)
                continue
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name in remove):
                continue
            out.append(node)
        return out

    tree.body = sift(tree.body)
    return ast.unparse(tree)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CAPTURE.mkdir(parents=True, exist_ok=True)
    log = json.loads((GEN61 / "generation_log.json").read_text())

    frozen = {
        "contract": K.contract(), "model": MODEL, "sampling": SAMPLING,
        "endpoint": "local llama-swap on this host",
        "prompt_template_sha256": hashlib.sha256(K.CRITIC_PROMPT.encode()).hexdigest(),
        "source_banks": "results/pi_spec_grounded_gen61/grounded/, unmodified",
        "session": "one stateless HTTP request per test; no conversation carried over",
    }
    (OUT / "critic_contract.json").write_text(
        json.dumps(frozen, indent=2, sort_keys=True) + "\n")

    records, streams = [], []
    for task in TASK_ORDER:
        bank, quotes = bank_for(task, log)
        if not bank.strip():
            continue
        sources = test_sources(bank)
        candidates = json.loads((FIXTURES / task / "truth" / "candidates.json").read_text())

        # Evaluator-side labels. Never shown to the critic.
        rejects_a_positive: set[str] = set()
        for overlay in candidates["positives"].values():
            rejects_a_positive |= failing_tests(task, bank, overlay)

        removed: set[str] = set()
        for name, source in sources.items():
            quote = quotes.get(name, "")
            prompt = K.CRITIC_PROMPT.format(quote=quote, test=source)
            content, raw, elapsed = ask(prompt)
            run_id = f"{task}-{name}"
            capture = CAPTURE / f"{run_id}.json"
            capture.write_text(raw)
            streams.append(R.archive_stream(capture, ARCHIVE, run_id, "provider_stream.json"))
            parsed = K.parse_verdict(content)
            if parsed["removed"]:
                removed.add(name)
            records.append({
                "task": task, "test": name, "quote": quote,
                "label": "KNOWN_FALSE" if name in rejects_a_positive else "VALID",
                "verdict": parsed["verdict"], "removed": parsed["removed"],
                "readable": parsed["readable"], "seconds": elapsed,
                "justification": parsed.get("justification"),
                "refused_reason": parsed.get("reason"),
                "reply_sha256": hashlib.sha256(content.encode()).hexdigest(),
            })
        kept_code = strip_tests(bank, removed)
        (OUT / "critiqued").mkdir(exist_ok=True)
        (OUT / "critiqued" / f"{task}.py").write_text(kept_code)
        print(f"{task}: tests={len(sources)} known_false={len(rejects_a_positive)} "
              f"removed={len(removed)}", flush=True)

    known_false = [r for r in records if r["label"] == "KNOWN_FALSE"]
    valid = [r for r in records if r["label"] == "VALID"]
    summary = {
        "frozen": frozen, "records": records,
        "tests_reviewed": len(records),
        "known_false_total": len(known_false),
        "known_false_removed": sum(1 for r in known_false if r["removed"]),
        "valid_total": len(valid),
        "valid_removed": sum(1 for r in valid if r["removed"]),
        "unreadable_replies": sum(1 for r in records if not r["readable"]),
        "removals_refused_for_no_named_condition":
            sum(1 for r in records if r["verdict"] == "REMOVE" and not r["removed"]),
        "total_seconds": round(sum(r["seconds"] for r in records), 1),
    }
    (OUT / "critic_log.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (OUT / "raw_stream_manifest.json").write_text(
        json.dumps(R.build_manifest(streams, ARCHIVE), indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("tests_reviewed", "known_false_total", "known_false_removed",
                       "valid_total", "valid_removed", "unreadable_replies",
                       "removals_refused_for_no_named_condition",
                       "total_seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
