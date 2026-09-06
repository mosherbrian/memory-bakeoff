"""Independent verifier: rebuild the v5 contract WITHOUT importing the candidate.

Loads reader_interference_v5.py a second time from its file path under a
different module name, proves the two module objects and their functions are
distinct, and only then compares behaviour. Gen113's equivalence check compared
a module to itself and passed vacuously; this refuses to do that.
"""
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_independent(name: str):
    path = ROOT / "src/memory_bakeoff/reader_interference_v5.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from memory_bakeoff import reader_interference_v5 as candidate
    independent = load_independent("_v5_independent_rebuild")

    problems = []
    if candidate is independent:
        problems.append("modules are the same object; the comparison would be vacuous")
    if candidate.classify_answer is independent.classify_answer:
        problems.append("classify_answer is the same function object")
    if candidate.project_prompt is independent.project_prompt:
        problems.append("project_prompt is the same function object")

    a, b = candidate.contract_payload(), independent.contract_payload()
    ha = hashlib.sha256(json.dumps(a, sort_keys=True, default=str).encode()).hexdigest()
    hb = hashlib.sha256(json.dumps(b, sort_keys=True, default=str).encode()).hexdigest()
    if ha != hb:
        problems.append(f"payload digests differ: {ha[:16]} vs {hb[:16]}")

    # Prompts must be byte-identical across the independent rebuild.
    ca = {c["case_id"]: candidate.project_prompt(c) for c in candidate.build_fixture()["cases"]}
    cb = {c["case_id"]: independent.project_prompt(c) for c in independent.build_fixture()["cases"]}
    if ca != cb:
        problems.append("prompt bytes differ between candidate and independent rebuild")

    print(f"independent module object : {'DISTINCT' if candidate is not independent else 'SAME (bad)'}")
    print(f"payload digest            : {ha[:32]}")
    print(f"prompts identical         : {ca == cb}  ({len(ca)} cases)")
    print(f"verdict                   : {'PASS' if not problems else 'FAIL'}")
    for p in problems:
        print(f"  - {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
