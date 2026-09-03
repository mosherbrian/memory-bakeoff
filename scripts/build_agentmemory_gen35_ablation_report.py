#!/usr/bin/env python3
"""Gen35: derive the paired ON/OFF ablation result from six leaf repetition files.

Reads no summary.json. Every count comes from cases[].failure_classes or from
replaying the frozen lifecycle scorer over leaf checkpoint state. Missing or
malformed evidence raises; it never becomes a zero.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import round2_reporting as R
from memory_bakeoff.longitudinal import canonical_json

CONTRACT_VERSION = "gen35-ablation-v1"
ARMS = ("on", "off")
FINAL_CHECKPOINT = "CP16"
GEN33 = ROOT / "results/agentmemory_gen33_longitudinal"
# Gen33's measured retirement pattern; the ON arm must reproduce it natively.
GEN33_EVENTS = [
    {"predecessor_canonical_id": "L001", "successor_canonical_id": "L003",
     "classification": "false_supersession"},
    {"predecessor_canonical_id": "L002", "successor_canonical_id": "L004",
     "classification": "legitimate_supersession"},
]


def load_runs(directory: Path) -> list[dict]:
    if not directory.is_dir():
        raise R.ReportingError(f"leaf evidence directory missing: {directory}")
    runs = []
    for path in sorted(directory.glob("repetition-*.json")):
        evidence = R.load_json(path)
        arm = R.require(evidence, "arm", str(path))
        if arm not in ARMS:
            raise R.ReportingError(f"{path}: unknown arm {arm!r}")
        R.require(evidence, "repetition", str(path))
        R.validate_repetition(evidence, str(path))
        evidence["_path"] = str(path.relative_to(ROOT))
        runs.append(evidence)
    if len(runs) != 6:
        raise R.ReportingError(f"expected 6 leaf repetitions (3 per arm), found {len(runs)}")
    for arm in ARMS:
        n = sum(1 for r in runs if r["arm"] == arm)
        if n != 3:
            raise R.ReportingError(f"expected 3 {arm} repetitions, found {n}")
    return runs


def product_events(run: dict) -> list[dict]:
    return [{"predecessor_canonical_id": e["predecessor_canonical_id"],
             "successor_canonical_id": e["successor_canonical_id"],
             "classification": e["classification"]}
            for e in R.require(run, "supersession_events", run["_path"])]


def manipulation_checks(runs: list[dict]) -> dict:
    """The treatment must have activated in ON and must be absent in OFF."""
    checks: dict[str, dict] = {}
    for run in runs:
        where = f"{run['arm']}-r{run['repetition']}"
        final = R.require(R.require(run, "checkpoint_state", where), FINAL_CHECKPOINT, where)
        events = product_events(run)
        if run["arm"] == "on":
            ok = (events == GEN33_EVENTS and final["rows_live"] == 14 and final["rows_retired"] == 2)
            detail = {"events": events, "rows_live": final["rows_live"], "rows_retired": final["rows_retired"],
                      "expected_events": GEN33_EVENTS, "expected_live": 14, "expected_retired": 2}
        else:
            ok = (events == [] and final["rows_live"] == 16 and final["rows_retired"] == 0)
            detail = {"events": events, "rows_live": final["rows_live"], "rows_retired": final["rows_retired"],
                      "expected_events": [], "expected_live": 16, "expected_retired": 0}
        checks[where] = {"passed": ok, **detail}
    return checks


def returned_sequences(run: dict) -> dict[str, list[str]]:
    return {c["case_id"]: [i["canonical_id"] for i in c["returned"] if i["canonical_id"]]
            for c in run["cases"]}


def case_classes(run: dict) -> dict[str, list[str]]:
    return {c["case_id"]: sorted(c["failure_classes"]) for c in run["cases"]}


def replication_gate(on_runs: list[dict]) -> dict:
    """The patched ON arm must reproduce Gen33 semantically, or there is no control."""
    gen33 = [R.load_json(p) for p in sorted(GEN33.glob("repetition-*.json"))]
    if not gen33:
        raise R.ReportingError(f"Gen33 leaf evidence missing: {GEN33}")
    for evidence in gen33:
        R.validate_repetition(evidence, str(GEN33))
    reference = {
        "events": product_events({**gen33[0], "_path": str(GEN33)}),
        "case_classes": case_classes(gen33[0]),
        "sequences": returned_sequences(gen33[0]),
        "case_totals": {k: v.count for k, v in R.rebuild_case_totals(gen33[0]).items()},
        "lifecycle_totals": {k: v.count for k, v in R.replay_lifecycle(gen33[0]).items()},
    }
    for other in gen33[1:]:
        if case_classes(other) != reference["case_classes"]:
            raise R.ReportingError("Gen33 leaf repetitions disagree; the reference is not stable")
    mismatches: list[str] = []
    for run in on_runs:
        where = f"on-r{run['repetition']}"
        if product_events(run) != reference["events"]:
            mismatches.append(f"{where}: product lifecycle events differ from Gen33")
        if case_classes(run) != reference["case_classes"]:
            differing = sorted(k for k, v in case_classes(run).items() if reference["case_classes"].get(k) != v)
            mismatches.append(f"{where}: case failure classes differ from Gen33 at {differing}")
        if {k: v.count for k, v in R.rebuild_case_totals(run).items()} != reference["case_totals"]:
            mismatches.append(f"{where}: case failure totals differ from Gen33")
        if {k: v.count for k, v in R.replay_lifecycle(run).items()} != reference["lifecycle_totals"]:
            mismatches.append(f"{where}: lifecycle failure totals differ from Gen33")
        differing_order = sorted(k for k, v in returned_sequences(run).items()
                                 if reference["sequences"].get(k) != v)
        if differing_order:
            mismatches.append(f"{where}: canonical returned ordering differs from Gen33 at {differing_order}")
    return {"passed": not mismatches, "mismatches": mismatches,
            "gen33_repetitions": len(gen33),
            "gen33_case_totals": reference["case_totals"],
            "gen33_lifecycle_totals": reference["lifecycle_totals"]}


def difference_trace(on_runs: list[dict], off_runs: list[dict]) -> list[dict]:
    """Explain every ON/OFF case difference by the records retirement removed."""
    retired = {"L001"}          # retired in ON by L003; the false supersession
    legitimately_retired = {"L002"}   # retired in ON by L004
    trace = []
    on_seq, off_seq = returned_sequences(on_runs[0]), returned_sequences(off_runs[0])
    on_cls, off_cls = case_classes(on_runs[0]), case_classes(off_runs[0])
    for case_id in sorted(set(on_seq) | set(off_seq)):
        if on_seq.get(case_id) == off_seq.get(case_id) and on_cls.get(case_id) == off_cls.get(case_id):
            continue
        only_off = [c for c in off_seq.get(case_id, []) if c not in on_seq.get(case_id, [])]
        only_on = [c for c in on_seq.get(case_id, []) if c not in off_seq.get(case_id, [])]
        explained_by = sorted(set(only_off) & (retired | legitimately_retired))
        trace.append({
            "case_id": case_id,
            "on_returned": on_seq.get(case_id), "off_returned": off_seq.get(case_id),
            "on_failure_classes": on_cls.get(case_id), "off_failure_classes": off_cls.get(case_id),
            "present_only_in_off": only_off, "present_only_in_on": only_on,
            "explained_by_retirement_of": explained_by,
            "possible_confound": not explained_by,
        })
    return trace


def arm_totals(runs: list[dict], stream: R.Stream) -> dict[str, dict]:
    """Per-repetition and aggregate counts for one arm, from leaf evidence only."""
    per_rep: dict[int, dict[str, int]] = {}
    for run in runs:
        rebuilt = (R.rebuild_case_totals(run) if stream is R.Stream.CASE else R.replay_lifecycle(run))
        for name in rebuilt:
            R.legal_stream(name, stream)
        per_rep[run["repetition"]] = {k: v.value_or_raise() for k, v in rebuilt.items()}
    names = sorted({n for counts in per_rep.values() for n in counts})
    aggregate = {}
    for name in names:
        values = [per_rep[r][name] for r in sorted(per_rep)]
        if len(set(values)) != 1:
            aggregate[name] = {"per_repetition": values, "identical": False, "value": None}
        else:
            aggregate[name] = {"per_repetition": values, "identical": True, "value": values[0]}
    return aggregate


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default=str(ROOT / "results/agentmemory_gen35_retirement_ablation"))
    args = ap.parse_args()
    directory = Path(args.results)
    runs = load_runs(directory)
    on_runs = sorted([r for r in runs if r["arm"] == "on"], key=lambda r: r["repetition"])
    off_runs = sorted([r for r in runs if r["arm"] == "off"], key=lambda r: r["repetition"])

    checks = manipulation_checks(runs)
    failed = sorted(k for k, v in checks.items() if not v["passed"])
    gate = replication_gate(on_runs)

    case_on, case_off = arm_totals(on_runs, R.Stream.CASE), arm_totals(off_runs, R.Stream.CASE)
    life_on, life_off = arm_totals(on_runs, R.Stream.LIFECYCLE), arm_totals(off_runs, R.Stream.LIFECYCLE)

    def deltas(on: dict, off: dict) -> dict:
        out = {}
        for name in sorted(set(on) | set(off)):
            a, b = on.get(name), off.get(name)
            per_rep = ([y - x for x, y in zip(a["per_repetition"], b["per_repetition"])]
                       if a and b else None)
            out[name] = {"on": a, "off": b, "delta_off_minus_on_per_repetition": per_rep,
                         "delta_off_minus_on": (b["value"] - a["value"])
                         if a and b and a["identical"] and b["identical"] else None}
        return out

    report = {
        "contract_version": CONTRACT_VERSION,
        "reporting_contract": R.CONTRACT_VERSION,
        "reporting_contract_sha256": R.contract_sha256(),
        "evidence_class": "controlled_core",
        "product_identity": R.load_json(directory / "provenance.json"),
        "leaf_files": [r["_path"] for r in runs],
        "manipulation_checks": checks,
        "manipulation_passed": not failed,
        "control_replication_gate": gate,
        "case_stream": deltas(case_on, case_off),
        "lifecycle_stream": deltas(life_on, life_off),
        "product_events": {f"{r['arm']}-r{r['repetition']}": product_events(r) for r in runs},
        "case_difference_trace": difference_trace(on_runs, off_runs),
    }
    content = {k: v for k, v in report.items() if k != "product_identity"}
    digest = hashlib.sha256(canonical_json(content).encode()).hexdigest()
    report["content_digest"] = digest

    validation = {
        "leaf_repetitions": len(runs),
        "arms": {arm: sum(1 for r in runs if r["arm"] == arm) for arm in ARMS},
        "manipulation_failures": failed,
        "replication_mismatches": gate["mismatches"],
        "streams_kept_separate": True,
        "summaries_consumed": [],
        "false_supersession_source": "lifecycle scorer replay + independent product-event reconciliation",
        "content_digest": digest,
    }
    (directory / "paired-derived.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (directory / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    (directory / "content-digest.txt").write_text(digest + "\n")

    print(f"manipulation checks: {'PASS' if not failed else 'FAIL ' + str(failed)}")
    print(f"control replication gate: {'PASS' if gate['passed'] else 'FAIL'}")
    for m in gate["mismatches"]:
        print(f"  {m}")
    print("case stream (ON -> OFF):")
    for name, row in report["case_stream"].items():
        if (row["on"] and row["on"]["value"]) or (row["off"] and row["off"]["value"]):
            print(f"  {name:>28}: {row['on']['value']} -> {row['off']['value']} "
                  f"(delta {row['delta_off_minus_on']})")
    print("lifecycle stream (ON -> OFF):")
    for name, row in report["lifecycle_stream"].items():
        if (row["on"] and row["on"]["value"]) or (row["off"] and row["off"]["value"]):
            print(f"  {name:>28}: {row['on']['value']} -> {row['off']['value']} "
                  f"(delta {row['delta_off_minus_on']})")
    print(f"content digest {digest}")
    if failed or not gate["passed"]:
        raise SystemExit("gate failed; no causal claim may be published")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
