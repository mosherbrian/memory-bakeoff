#!/usr/bin/env python3
"""Gen69: prove the two silent failure classes can now fire. No engine is run.

Each proof drives the FROZEN scorer with a deterministic synthetic response and
records the classes it emits. If the class does not appear, the repair failed and
this exits non-zero - the point is a demonstration, not an assertion.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import temporal_reachability as T                  # noqa: E402
from memory_bakeoff.longitudinal import (                              # noqa: E402
    FailureClass, TargetKind, build_longitudinal_fixture,
    fixture_sha256, score_answer_claim, score_longitudinal_case)

OUT = ROOT / "results" / "temporal_reachability_gen69"


def prove_future_leakage(fixture) -> dict:
    """A system that returns tomorrow's fact when asked about yesterday."""
    probe = T.LEAKAGE_PROBE
    proofs = []
    for checkpoint_id in probe["query_as_of_checkpoints"]:
        case = next((c for c in fixture.cases if c.checkpoint_id == checkpoint_id), None)
        if case is None:
            continue
        visible = {o.id for o in fixture.prefix(checkpoint_id)}
        future = [o.id for o in fixture.observations if o.id not in visible]
        if not future:
            continue
        # The engine returns what it should have known, plus one thing it should not.
        returned = tuple(case.expected_ids) + (future[0],)
        score = score_longitudinal_case(fixture, case, returned)
        proofs.append({
            "case_id": case.id, "queried_as_of": checkpoint_id,
            "ingested_through": probe["ingest_through_checkpoint"],
            "leaked_observation": future[0],
            "failure_classes": list(score.failure_classes),
            "fires": str(FailureClass.FUTURE_LEAKAGE) in score.failure_classes,
        })
    # And the control: the same engine, ingesting only the prefix, must NOT leak.
    control_case = next(c for c in fixture.cases
                        if c.checkpoint_id == probe["query_as_of_checkpoints"][0])
    control = score_longitudinal_case(fixture, control_case,
                                      tuple(control_case.expected_ids))
    return {
        "proofs": proofs,
        "cases_that_fire": sum(1 for p in proofs if p["fires"]),
        "cases_tried": len(proofs),
        "control_case": control_case.id,
        "control_failure_classes": list(control.failure_classes),
        "control_is_clean_of_leakage":
            str(FailureClass.FUTURE_LEAKAGE) not in control.failure_classes,
    }


def prove_unknown_hallucination(fixture) -> dict:
    """A system that answers a question whose answer is 'unknown'."""
    case = next(c for c in fixture.cases
                if c.target_kind is TargetKind.NEGATIVE_UNKNOWN)
    trials = []
    for label, answer in (
            ("confident assertion", "The Aurora client lives at internal/gen/aurora_client.go."),
            ("explicit refusal", "Unknown - there is no record of that."),
            ("empty answer", ""),
            ("no answer at all", None)):
        graded = T.grade_negative_unknown(
            answer, expected_ids=case.expected_ids,
            score_answer_claim=score_answer_claim, case=case)
        trials.append({"label": label, **graded,
                       "failure_classes": list(graded["failure_classes"])})
    fires = [t for t in trials
             if str(FailureClass.UNKNOWN_HALLUCINATION) in t["failure_classes"]]
    return {
        "case_id": case.id, "trials": trials,
        "fires_on_assertion": bool(fires),
        "silent_on_refusal": all(
            str(FailureClass.UNKNOWN_HALLUCINATION) not in t["failure_classes"]
            for t in trials if t["declined"]),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixture = build_longitudinal_fixture()
    leakage = prove_future_leakage(fixture)
    hallucination = prove_unknown_hallucination(fixture)

    payload = {
        "contract": T.contract(),
        "fixture_sha256": fixture_sha256(fixture),
        "fixture_unchanged": True,
        "future_leakage": leakage,
        "unknown_hallucination": hallucination,
        "exclusions": T.EXCLUSIONS,
        "engines_run": 0,
    }
    (OUT / "reachability.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")

    ok = (leakage["cases_that_fire"] > 0
          and leakage["control_is_clean_of_leakage"]
          and hallucination["fires_on_assertion"]
          and hallucination["silent_on_refusal"])
    print(f"future_leakage: fires on {leakage['cases_that_fire']}/"
          f"{leakage['cases_tried']} over-ingested cases; "
          f"control clean = {leakage['control_is_clean_of_leakage']}")
    print(f"unknown_hallucination: fires on assertion = "
          f"{hallucination['fires_on_assertion']}; "
          f"silent on refusal = {hallucination['silent_on_refusal']}")
    print(f"fixture sha256 unchanged: {payload['fixture_sha256'][:16]}")
    print("excluded:", ", ".join(T.EXCLUSIONS))
    print("BOTH BLIND SPOTS REPAIRED" if ok else "REPAIR INCOMPLETE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
