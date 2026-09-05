#!/usr/bin/env python3
"""Gen63: re-score the frozen Gen60, Gen61 and Gen62 outcomes under the guardrail.

No model call, no regeneration, no filter change, no candidate re-run. This reads
outcomes that were already recorded and committed, attaches the retention figures
that were also already recorded, and applies the corrected screen.

Gen60 and Gen61 ran no filter, so their retention is 100% by construction and
their verdicts cannot move. They are included precisely to demonstrate that: the
guardrail must change the one generation that hollowed its banks and no other.
"""
from __future__ import annotations

import ast, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler import retention_screen as S   # noqa: E402

OUT = ROOT / "results" / "pi_retention_guardrail_gen63"
GEN60 = ROOT / "results" / "pi_generated_evidence_gen60"
GEN61 = ROOT / "results" / "pi_spec_grounded_gen61"
GEN62 = ROOT / "results" / "pi_entailment_critic_gen62"


def distinct_tests(code: str) -> int:
    if not code.strip():
        return 0
    return len({node.name for node in ast.walk(ast.parse(code))
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")})


def gen61_bank_sizes() -> dict[str, int]:
    """The distinct-test count each Gen62 bank started from."""
    log = json.loads((GEN61 / "generation_log.json").read_text())
    sizes: dict[str, int] = {}
    for task in {o["task"] for o in log["outputs"]}:
        parts = [(GEN61 / "grounded" / f"{o['run_id']}.py").read_text()
                 for o in log["outputs"] if o["task"] == task and o.get("usable")]
        sizes[task] = distinct_tests("\n\n".join(parts))
    return sizes


def annotate(result: dict, original: dict[str, int], surviving: dict[str, int]) -> dict:
    tasks = json.loads(json.dumps(result["tasks"]))
    for name, task in tasks.items():
        task["original_tests"] = original.get(name, 0)
        task["surviving_tests"] = surviving.get(name, 0)
    return tasks


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rescored = {}

    sizes = gen61_bank_sizes()
    critiqued = {path.stem: distinct_tests(path.read_text())
                 for path in sorted((GEN62 / "critiqued").glob("*.py"))}

    for label, directory, original, surviving in (
        ("gen60", GEN60, None, None),
        ("gen61", GEN61, sizes, sizes),
        ("gen62", GEN62, sizes, critiqued),
    ):
        result = json.loads((directory / "screen_result.json").read_text())
        if original is None:
            # Gen60 ran no filter; every test it generated is still in its bank.
            counts = {name: 1 for name in result["tasks"]}
            tasks = annotate(result, counts, counts)
        else:
            tasks = annotate(result, original, {k: surviving.get(k, 0) for k in original})
        corrected = S.apply_screen(tasks)
        rescored[label] = {
            "as_recorded": {"verdict": result["verdict"],
                            "sensitivity": result["sensitivity"],
                            "unsafe_as_gate_tasks": result["unsafe_as_gate_tasks"]},
            "under_guardrail": {k: corrected[k] for k in
                                ("verdict", "reason", "sensitivity", "specificity",
                                 "hollowed_tasks", "reference_valid_tasks",
                                 "unsafe_as_gate_tasks", "retention",
                                 "primary_population")},
            "changed": corrected["verdict"] != result["verdict"],
        }

    payload = {"contract": S.contract(), "rescored": rescored,
               "note": "Gen60 and Gen61 applied no deletion filter, so retention is "
                       "total and their verdicts are unchanged by construction."}
    (OUT / "rescore.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for label, entry in rescored.items():
        print(f"{label}: {entry['as_recorded']['verdict']} -> "
              f"{entry['under_guardrail']['verdict']}"
              f"{'  (CHANGED)' if entry['changed'] else ''}")
        if entry["under_guardrail"]["hollowed_tasks"]:
            print(f"   hollowed: {', '.join(entry['under_guardrail']['hollowed_tasks'])}")
    print(json.dumps({k: rescored[k]["under_guardrail"]["reason"] for k in rescored},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
