#!/usr/bin/env python3
"""Gen66 preflight: prove the critic prompt carries no candidate or evaluator text.

The whole claim of this generation is that the critic sees the code without
seeing the answer. That has to be checked on the prompt the critic actually
receives, not asserted in a docstring.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.evidence_ruler import repo_context_critic as K   # noqa: E402
from memory_bakeoff.pi_state_control.challenge_generation import render_tree  # noqa: E402

FIXTURES = ROOT / "fixtures" / "evidence_generation_gen59_v1"
GEN61 = ROOT / "results" / "pi_spec_grounded_gen61"
TOKENS = ("verifier", "candidates.json", "failed_requirement", "VERIFIER OK",
          "passes_visible", "known_false", "UNSAFE_AS_GATE")


def main() -> int:
    log = json.loads((GEN61 / "generation_log.json").read_text())
    findings, leaks = {}, 0
    for task in sorted({o["task"] for o in log["outputs"]}):
        truth = json.loads((FIXTURES / task / "truth" / "candidates.json").read_text())
        quote = next(k["quote"] for o in log["outputs"]
                     if o["task"] == task and o.get("usable") for k in o["kept"])
        prompt = K.build_prompt(quote=quote, test="def test_x():\n    assert True\n",
                                tree=render_tree(FIXTURES / task / "repo"))
        report = K.isolation_report(prompt, TOKENS)

        # No candidate body may appear. Compare on the distinctive lines each
        # overlay introduces, ignoring lines the shipped repo already contains.
        shipped = set(render_tree(FIXTURES / task / "repo").splitlines())
        bled = []
        for group in ("positives", "wrongs"):
            for name, entry in truth[group].items():
                overlay = entry["overlay"] if group == "wrongs" else entry
                for text in overlay.values():
                    novel = [line.strip() for line in text.splitlines()
                             if line.strip() and line.strip() not in
                             {s.strip() for s in shipped}]
                    hits = [line for line in novel if line in prompt]
                    if hits:
                        bled.append({"candidate": f"{group}:{name}",
                                     "lines": hits[:3]})
        findings[task] = {**report, "candidate_lines_in_prompt": bled}
        leaks += len(report["found"]) + len(bled)

    payload = {"contract": K.contract(), "tokens_checked": TOKENS,
               "tasks": findings, "total_leaks": leaks,
               "clean": leaks == 0}
    out = ROOT / "results" / "pi_repo_context_gen66"
    out.mkdir(parents=True, exist_ok=True)
    (out / "isolation_preflight.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"clean": payload["clean"], "total_leaks": leaks,
                      "tasks": len(findings)}, indent=1))
    return 0 if leaks == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
