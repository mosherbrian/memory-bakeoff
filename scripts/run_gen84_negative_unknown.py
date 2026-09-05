"""Gen84: audit the negative_unknown axis. No engine runs, no reader added."""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff import negative_unknown as audit
from memory_bakeoff.longitudinal import (build_longitudinal_fixture, score_answer_claim,
                                         score_longitudinal_case)

RESULT_DIRS = {
    "perseus": "perseus_vault_gen29_longitudinal",
    "hindsight": "hindsight_gen31_longitudinal",
    "mem0": "mem0_gen32_longitudinal",
    "agentmemory": "agentmemory_gen33_longitudinal",
}


def top_score(case: dict, engine: str):
    rows = case["returned"]
    if not rows:
        return None
    return rows[0]["scores"]["final"] if engine == "hindsight" else rows[0].get("score")


def committed(root: pathlib.Path) -> dict[str, Any]:
    """Re-derive the table from the records, including the separability count."""
    out = {}
    for engine, directory in RESULT_DIRS.items():
        rows = []
        lower = None
        for repetition in (1, 2, 3):
            cases = json.loads(
                (root / "results" / directory / f"repetition-{repetition}.json").read_text())["cases"]
            target = next(c for c in cases if c["case_id"] == audit.CASE_ID)
            peak = top_score(target, engine)
            rows.append({
                "repetition": repetition,
                "returned": [r["canonical_id"] for r in target["returned"]],
                "failure_classes": target["failure_classes"],
                "top_score": peak,
                "threshold": target.get("threshold"),
            })
            if repetition == 1 and peak is not None:
                others = [top_score(c, engine) for c in cases
                          if c["case_id"] != audit.CASE_ID]
                others = [s for s in others if s is not None]
                lower = sum(1 for s in others if s < peak)
                rows[0]["scored_cases_with_expected_evidence"] = len(others)
        out[engine] = {"repetitions": rows, "cases_scoring_lower": lower}
    return out


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    fixture = build_longitudinal_fixture()
    case = next(c for c in fixture.cases if c.id == audit.CASE_ID)
    payload = {
        "contract": audit.verdict(),
        "controls": audit.controls(score_longitudinal_case, score_answer_claim, fixture, case),
        "abstention_surface": audit.ABSTENTION_SURFACE,
        "layers": audit.layers(),
        "committed": committed(root),
        "corpus_at_checkpoint": len(fixture.prefix(audit.CHECKPOINT_ID)),
        "requested_limit": audit.REQUESTED_LIMIT,
    }
    destination = root / "results" / "negative_unknown_gen84"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "audit.json").write_text(json.dumps(payload, indent=1, sort_keys=True, default=str))
    print(json.dumps(payload["contract"], indent=1))
    return 0


if __name__ == "__main__":
    from typing import Any  # noqa: F401  (annotation use only)
    raise SystemExit(main())
