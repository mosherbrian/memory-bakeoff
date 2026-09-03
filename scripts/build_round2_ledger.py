#!/usr/bin/env python3
"""Gen34: rebuild the Round-2 ledger from leaf evidence, fail-closed.

Reads only committed per-repetition evidence. Stored summary.json files are
verification targets, never inputs. No product runs, no services.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import round2_reporting as R
from memory_bakeoff.longitudinal import canonical_json, fixture_sha256, scorer_contract_sha256

ENGINES = {
    "gen29_perseus": "results/perseus_vault_gen29_longitudinal",
    "gen31_hindsight": "results/hindsight_gen31_longitudinal",
    "gen32_mem0": "results/mem0_gen32_longitudinal",
    "gen33_agentmemory": "results/agentmemory_gen33_longitudinal",
}
APPEND_ONLY = ("gen29_perseus", "gen31_hindsight", "gen32_mem0")
RETIRING = "gen33_agentmemory"
PREREGISTERED_SEVEN = ("stale_persistence", "configuration_collapse", "failed_procedure_adoption",
                       "late_history_corruption", "false_persistence", "missing_required_truth",
                       "unsupported_evidence")


def build() -> dict:
    ledger, validation = {}, {"engines": {}, "reconciliation": [], "notes": []}
    for engine, rel in ENGINES.items():
        directory = ROOT / rel
        paths = sorted(directory.glob("repetition-*.json"))
        if len(paths) != R.EXPECTED_REPETITIONS:
            raise R.ReportingError(f"{engine}: expected {R.EXPECTED_REPETITIONS} repetitions, found {len(paths)}")
        stored_summary = None
        summary_path = directory / "summary.json"
        if summary_path.exists():
            stored_summary = R.load_json(summary_path)

        case_totals: dict[str, int] = {}
        lifecycle_totals: dict[str, int] = {}
        lineage: dict[str, list[str]] = {}
        for path in paths:
            evidence = R.load_json(path)
            where = f"{engine}/{path.name}"
            R.validate_repetition(evidence, where)

            rebuilt_case = R.rebuild_case_totals(evidence)
            R.reconcile(evidence.get("failure_totals"), rebuilt_case, where, R.Stream.CASE)
            for name, measurement in rebuilt_case.items():
                case_totals[name] = case_totals.get(name, 0) + measurement.value_or_raise()

            replayed = R.replay_lifecycle(evidence)
            R.reconcile(evidence.get("lifecycle_failure_totals"), replayed, where, R.Stream.LIFECYCLE)
            for name, measurement in replayed.items():
                lifecycle_totals[name] = lifecycle_totals.get(name, 0) + measurement.value_or_raise()

            for case in evidence["cases"]:
                for name in case["failure_classes"]:
                    lineage.setdefault(name, []).append(f"{path.name}:{case['case_id']}")

        product_events = R.Measurement.unsupported("engine performs no native retirement")
        if engine == RETIRING:
            total = 0
            for path in paths:
                total += len(R.load_json(path).get("supersession_events", []))
            product_events = R.Measurement.measured(total, "native write-time supersessions")

        ledger[engine] = {
            "evidence_files": [str(p.relative_to(ROOT)) for p in paths],
            "case_scorer": {n: R.Measurement.measured(c).payload() for n, c in sorted(case_totals.items())},
            "lifecycle_scorer": {n: R.Measurement.measured(c).payload() for n, c in sorted(lifecycle_totals.items())},
            "product_lifecycle_event": product_events.payload(),
            "lineage": {n: sorted(v) for n, v in sorted(lineage.items())},
        }
        validation["engines"][engine] = {
            "repetitions": len(paths), "schema": "valid",
            "stored_summary_verified": stored_summary is not None,
        }
    return ledger, validation


def derive(ledger: dict) -> dict:
    def case_count(engine: str, klass: str) -> int:
        cell = ledger[engine]["case_scorer"].get(klass)
        if cell is None:
            raise R.ReportingError(f"{engine}: {klass} absent from rebuilt case stream; refusing to assume zero")
        return cell["count"]

    def life_count(engine: str, klass: str) -> int:
        R.legal_stream(klass, R.Stream.LIFECYCLE)
        cell = ledger[engine]["lifecycle_scorer"].get(klass)
        if cell is None:
            raise R.ReportingError(f"{engine}: {klass} absent from rebuilt lifecycle stream")
        return cell["count"]

    seven = {k: {e: case_count(e, k) for e in APPEND_ONLY} for k in PREREGISTERED_SEVEN}
    identical = sorted(k for k, v in seven.items() if len(set(v.values())) == 1 and next(iter(v.values())))
    recurring = sorted(k for k, v in seven.items() if all(v.values()))
    fs = {e: life_count(e, "false_supersession") for e in ENGINES}
    contrast = {k: {e: case_count(e, k) for e in ENGINES}
                for k in ("configuration_collapse", "false_persistence", "stale_persistence",
                          "correction_failure", "history_erasure", "scope_collapse")}
    return {
        "preregistered_seven_recur_in_all_append_only": recurring == sorted(PREREGISTERED_SEVEN),
        "preregistered_seven_counts": seven,
        "identical_across_append_only": identical,
        "false_supersession_lifecycle": fs,
        "false_supersession_unique_to_retiring_engine": (
            fs[RETIRING] > 0 and all(fs[e] == 0 for e in APPEND_ONLY)),
        "four_engine_case_contrast": contrast,
        "claim_retirement_halves_configuration_collapse": (
            contrast["configuration_collapse"][RETIRING] * 2 == contrast["configuration_collapse"]["gen29_perseus"]),
        "claim_retirement_reduces_false_persistence": (
            contrast["false_persistence"][RETIRING] < min(contrast["false_persistence"][e] for e in APPEND_ONLY)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/round2_gen34_integrity"))
    args = ap.parse_args()
    if fixture_sha256() != "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd":
        raise R.ReportingError("fixture hash drift")
    if scorer_contract_sha256() != "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34":
        raise R.ReportingError("scorer contract hash drift")

    ledger, validation = build()
    derived = derive(ledger)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    content = {"contract_version": R.CONTRACT_VERSION, "contract_sha256": R.contract_sha256(),
               "fixture_sha256": fixture_sha256(), "scorer_contract_sha256": scorer_contract_sha256(),
               "engines": ledger}
    (out / "evidence-ledger.json").write_text(canonical_json(content) + "\n")
    (out / "four-engine-derived.json").write_text(canonical_json(derived) + "\n")
    (out / "validation.json").write_text(canonical_json(validation) + "\n")
    digest = hashlib.sha256(canonical_json({"ledger": content, "derived": derived}).encode()).hexdigest()
    (out / "content-digest.txt").write_text(digest + "\n")

    print(f"wrote {out}")
    print(" content digest:", digest)
    print(" seven recur in all append-only:", derived["preregistered_seven_recur_in_all_append_only"])
    print(" identical across append-only:", derived["identical_across_append_only"])
    print(" false_supersession (lifecycle):", derived["false_supersession_lifecycle"])
    print(" unique to retiring engine:", derived["false_supersession_unique_to_retiring_engine"])
    print(" halves configuration_collapse:", derived["claim_retirement_halves_configuration_collapse"])
    print(" reduces false_persistence:", derived["claim_retirement_reduces_false_persistence"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
