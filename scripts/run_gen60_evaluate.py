#!/usr/bin/env python3
"""Gen60 Part B: score the generated banks against the frozen Gen59 ruler.

No generation happens here and no generated test is altered. Each task's bank is
the concatenation of that task's accepted outputs, exactly as Gen58 assembled
them. The screen was frozen at `gen60-generated-evidence-screen-v1` before the
first Gen60 call, and is applied here without modification.

Order of operations matters. A bank is checked against every trusted positive
FIRST. A bank that rejects known-correct code is marked UNSAFE_AS_GATE and its
task leaves the primary population - it is kept and reported, never repaired.
Only banks that survive that check are allowed to say anything about wrongs.
"""
from __future__ import annotations

import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler import gen60_screen as S   # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
RULER = ROOT / "results" / "pi_evidence_ruler_gen59"
OUT = ROOT / "results" / "pi_generated_evidence_gen60"
BANK_FILE = "test_generated_challenge.py"


def materialise(task: str, overlay: dict[str, str]) -> Path:
    tree = Path(tempfile.mkdtemp(prefix=f"gen60-{task}-"))
    shutil.rmtree(tree)
    shutil.copytree(FIXTURES / task / "repo", tree)
    for relative, text in overlay.items():
        path = tree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return tree


def run_bank(tree: Path, bank: str) -> dict:
    """Run only the generated bank, in the candidate tree, leaving it untouched."""
    target = tree / "tests" / BANK_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(bank)
    try:
        done = subprocess.run(
            [sys.executable, "-m", "pytest", f"tests/{BANK_FILE}", "-q",
             "-p", "no:cacheprovider"],
            cwd=tree, capture_output=True, text=True, timeout=300,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(tree)})
        tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
        return {"passed": done.returncode == 0, "tail": tail[0][:160]}
    except subprocess.TimeoutExpired:
        return {"passed": False, "tail": "TIMEOUT"}
    finally:
        target.unlink(missing_ok=True)


def main() -> int:
    screen = json.loads((RULER / "gen60_frozen_screen.json").read_text())
    log = json.loads((OUT / "generation_log.json").read_text())

    banks: dict[str, dict] = {}
    for task in screen["ruler"]["admitted_tasks"]:
        parts = [(OUT / "generated" / f"{o['run_id']}.py").read_text()
                 for o in log["outputs"] if o["task"] == task and o["accepted"]]
        banks[task] = {"parts": len(parts), "code": "\n\n".join(parts)}

    tasks: dict[str, dict] = {}
    for task, bank in banks.items():
        candidates = json.loads((FIXTURES / task / "truth" / "candidates.json").read_text())
        entry: dict = {"accepted_outputs": bank["parts"], "positives": {}, "wrongs": {}}
        if not bank["parts"]:
            tasks[task] = entry
            continue

        for name, overlay in candidates["positives"].items():
            tree = materialise(task, overlay)
            entry["positives"][name] = run_bank(tree, bank["code"])
            shutil.rmtree(tree, ignore_errors=True)
        # A bank that rejects known-correct code cannot be used as a gate, and
        # its verdicts on wrong code carry no weight.
        for name, wrong in candidates["wrongs"].items():
            tree = materialise(task, wrong["overlay"])
            entry["wrongs"][name] = {**run_bank(tree, bank["code"]),
                                     "failed_requirement": wrong["failed_requirement"],
                                     "passes_visible": wrong["passes_visible"]}
            shutil.rmtree(tree, ignore_errors=True)
        tasks[task] = entry

    result = {
        "screen_sha256": screen["contract_sha256"],
        "ruler": screen["ruler"]["name"],
        "generation_calls": len(log["outputs"]),
        "accepted_outputs": log["accepted"],
        "tasks": tasks,
        **S.apply_screen(tasks),
        "absence_is_not_sufficiency": screen["absence_is_not_sufficiency"],
    }
    (OUT / "screen_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("verdict", "reason", "sensitivity", "specificity",
                       "reference_valid_tasks", "unsafe_as_gate_tasks",
                       "flagged_wrongs", "accepted_outputs")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
