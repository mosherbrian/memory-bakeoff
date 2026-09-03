#!/usr/bin/env python3
"""Gen35: paired agentmemory retirement ablation, ON vs OFF, one patched build.

Both arms execute external/agentmemory-gen35. The only intended difference is
AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION, which gates the assignment of
supersession state after the >0.7 Jaccard decision. Measurement code is the
Gen33 procedure, unchanged in what it captures.
"""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, os, sys, tempfile, time
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
loader = SourceFileLoader("g13", str(ROOT / "scripts/run_agentmemory_gen13.py"))
spec = importlib.util.spec_from_loader("g13", loader)
g13 = importlib.util.module_from_spec(spec)
loader.exec_module(g13)

from memory_bakeoff import longitudinal as L
from memory_bakeoff.providers import agentmemory_longitudinal as A

AGENTMEMORY = ROOT / "external/agentmemory-gen35"
FLAG = "AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION"
LIMIT = 5
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"
SCORER_SHA = "1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34"
PATCH = ROOT / "research/patches/agentmemory-gen35-retirement-flag.patch"
# Counterbalanced pair order: ON/OFF, OFF/ON, ON/OFF.
PAIR_ORDER = [("on", "off"), ("off", "on"), ("on", "off")]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_rows(base, agent):
    rows = g13.isolated_rows(base, agent)
    return rows.get("results") or rows.get("memories") or []


def run_arm(fixture, repetition: int, arm: str, position: int, instance: int) -> dict:
    if arm not in ("on", "off"):
        raise SystemExit(f"unknown arm: {arm}")
    state = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen35-{arm}-r{repetition}-", dir="/private/tmp"))
    agent = f"memory-bakeoff-gen35-{arm}-r{repetition}"
    if arm == "off":
        os.environ[FLAG] = "1"
    else:
        os.environ.pop(FLAG, None)
    captured_env = {k: v for k, v in g13.service_env(agent).items()
                    if k.startswith(("AGENT", "EMBEDDING", "CONSOLIDATION", "GRAPH", "OPENAI",
                                     "ANTHROPIC", "GEMINI", "GOOGLE", "OPENROUTER", "MINIMAX", "CI"))}

    truth = {o.id: {"corrects_id": o.corrects_id, "supersedes_id": o.supersedes_id} for o in fixture.observations}
    checkpoints = {c.ingestion_order: c for c in fixture.checkpoints}
    cases_by_checkpoint: dict[str, list] = {}
    for case in fixture.cases:
        cases_by_checkpoint.setdefault(case.checkpoint_id, []).append(case)

    native_to_canonical: dict[str, str] = {}
    records, checkpoint_state, lifecycle_by_checkpoint = [], {}, {}
    supersession_events: list[dict] = []
    ingestion_log: list[dict] = []
    launcher = None
    try:
        base, startup, launcher = g13.start_service(AGENTMEMORY, state, instance, agent)
        for observation in fixture.observations:
            payload = A.remember_arguments(observation, agent)
            A.assert_public_only(payload)
            before = {r.get("id"): r for r in native_rows(base, agent)}
            g13.request_json(base, "/agentmemory/remember", body=payload)
            time.sleep(0.05)
            after = native_rows(base, agent)
            for row in after:
                for source in (row.get("sourceObservationIds") or []):
                    native_to_canonical[row.get("id")] = source
            for row in after:
                previous = before.get(row.get("id"))
                if row.get("isLatest") is False and (previous is None or previous.get("isLatest") is not False):
                    predecessor = native_to_canonical.get(row.get("id"))
                    successor_row = next((r for r in after if row.get("id") in (r.get("supersedes") or [])), None)
                    successor = native_to_canonical.get(successor_row.get("id")) if successor_row else None
                    supersession_events.append({
                        "at_ingestion_order": observation.ingestion_order,
                        "predecessor_native_id": row.get("id"), "predecessor_canonical_id": predecessor,
                        "successor_native_id": successor_row.get("id") if successor_row else None,
                        "successor_canonical_id": successor,
                        "successor_version": successor_row.get("version") if successor_row else None,
                        "classification": A.classify_supersession(predecessor, successor, truth),
                    })
            ingestion_log.append({
                "ingestion_order": observation.ingestion_order,
                "canonical_id": observation.id,
                "rows_total": len(after),
                "rows_live": sum(1 for r in after if r.get("isLatest") is not False),
                "rows_retired": sum(1 for r in after if r.get("isLatest") is False),
                "supersessions_so_far": len(supersession_events),
            })

            checkpoint = checkpoints.get(observation.ingestion_order)
            if checkpoint is None:
                continue

            rows = native_rows(base, agent)
            live = {native_to_canonical.get(r.get("id")) for r in rows if r.get("isLatest") is not False}
            in_kv = {native_to_canonical.get(r.get("id")) for r in rows}
            prefix_ids = {o.id for o in fixture.prefix(checkpoint.id)}
            checkpoint_state[checkpoint.id] = {
                "rows_total": len(rows),
                "rows_live": sum(1 for r in rows if r.get("isLatest") is not False),
                "rows_retired": sum(1 for r in rows if r.get("isLatest") is False),
                "expected_prefix": len(prefix_ids),
                "supersessions_so_far": len(supersession_events),
            }
            lifecycle_by_checkpoint[checkpoint.id] = [
                L.LifecycleEvidence(cid, active_current=cid in live,
                                    historically_recoverable=True if cid in in_kv else None,
                                    disposition=L.LifecycleDisposition.ACTIVE_CURRENT if cid in live
                                    else (L.LifecycleDisposition.RETIRED_SUPERSEDED if cid in in_kv
                                          else L.LifecycleDisposition.UNKNOWN),
                                    evidence_strength="native_memory_row",
                                    native_evidence=f"isLatest={cid in live}; present_in_kv={cid in in_kv}")
                for cid in sorted(prefix_ids)]

            prefix_sha = hashlib.sha256(L.canonical_json([o.public_dict() for o in fixture.prefix(checkpoint.id)]).encode()).hexdigest()
            for case in cases_by_checkpoint.get(checkpoint.id, []):
                arguments = A.search_arguments(case, agent, LIMIT)
                started = time.perf_counter()
                raw = g13.request_json(base, "/agentmemory/smart-search", body=arguments)
                latency_ms = (time.perf_counter() - started) * 1000
                items = []
                for rank, hit in enumerate((raw.get("results") or [])[:LIMIT], start=1):
                    obs = hit.get("obsId")
                    canonical = native_to_canonical.get(obs) or (hit.get("sourceObservationIds") or [None])[0]
                    exact = canonical in {o.id for o in fixture.observations}
                    items.append({"native_rank": rank, "obsId": obs,
                                  "canonical_id": canonical if exact else None, "provenance_exact": exact,
                                  "score": hit.get("score"), "text": (hit.get("content") or "")[:110]})
                records.append({"case_id": case.id, "checkpoint_id": checkpoint.id,
                                "ingested_prefix_sha256": prefix_sha,
                                "native_temporal_operation": A.native_operation(case),
                                "requested_limit": LIMIT, "latency_ms": round(latency_ms, 2),
                                "returned": items,
                                "provenance_exact_all": all(i["provenance_exact"] for i in items)})
    finally:
        if launcher is not None:
            g13.stop_service(AGENTMEMORY, state, instance, agent, launcher)
        os.environ.pop(FLAG, None)

    case_scores = []
    for record in records:
        case = next(c for c in fixture.cases if c.id == record["case_id"])
        returned = tuple(i["canonical_id"] for i in record["returned"] if i["canonical_id"])
        score = L.score_longitudinal_case(fixture, case, returned)
        record["failure_classes"] = list(score.failure_classes)
        case_scores.append(score)
    lifecycle_scores = [L.score_lifecycle_state(fixture, cid, ev) for cid, ev in lifecycle_by_checkpoint.items()]

    if len(records) != len(fixture.cases):
        raise SystemExit(f"{arm} r{repetition}: expected {len(fixture.cases)} cases, captured {len(records)}")
    if len(lifecycle_by_checkpoint) != len(fixture.checkpoints):
        raise SystemExit(f"{arm} r{repetition}: expected {len(fixture.checkpoints)} checkpoints, "
                         f"captured {len(lifecycle_by_checkpoint)}")

    return {"repetition": repetition, "arm": arm, "position_in_pair": position,
            "agent_id": agent, "build_tree": str(AGENTMEMORY),
            "retirement_flag_set": arm == "off", "captured_env": captured_env,
            "cases": records, "checkpoint_state": checkpoint_state,
            "ingestion_log": ingestion_log,
            "supersession_events": supersession_events,
            "supersession_count": len(supersession_events),
            "supersession_classification": {k: sum(1 for e in supersession_events if e["classification"] == k)
                                            for k in ("legitimate_supersession", "false_supersession", "unmapped")},
            "lifecycle": {cid: [{"canonical_id": e.canonical_id, "active_current": e.active_current,
                                 "historically_recoverable": e.historically_recoverable,
                                 "disposition": str(e.disposition)} for e in ev]
                          for cid, ev in lifecycle_by_checkpoint.items()},
            "lifecycle_failures": {s.checkpoint_id: list(s.failure_classes) for s in lifecycle_scores},
            "failure_totals": L.aggregate_failure_classes(case_scores),
            "lifecycle_failure_totals": L.aggregate_failure_classes(lifecycle_scores)}


def assert_env_parity(runs: list[dict]) -> dict:
    """Only the run identifier and the retirement flag itself may differ."""
    allowed = {"AGENT_ID", FLAG}
    baseline = runs[0]["captured_env"]
    differing: dict[str, list] = {}
    for run in runs[1:]:
        env = run["captured_env"]
        for key in sorted(set(baseline) | set(env)):
            if baseline.get(key) != env.get(key):
                differing.setdefault(key, []).append(
                    {"run": f"{run['arm']}-r{run['repetition']}", "value": env.get(key)})
    illegal = {k: v for k, v in differing.items() if k not in allowed}
    if illegal:
        raise SystemExit(f"arm environments differ beyond the allowed identifiers: {sorted(illegal)}")
    if FLAG not in differing:
        raise SystemExit("the retirement flag never differed between arms; the ablation did not vary")
    return {"allowed_differences": sorted(differing), "illegal_differences": [],
            "flag_varied": True}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repetitions", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "results/agentmemory_gen35_retirement_ablation"))
    args = ap.parse_args()
    if L.fixture_sha256() != FIXTURE_SHA or L.scorer_contract_sha256() != SCORER_SHA:
        raise SystemExit("frozen ruler hash drift; refusing to run")
    if not AGENTMEMORY.exists():
        raise SystemExit(f"patched build tree missing: {AGENTMEMORY}")
    if not PATCH.exists():
        raise SystemExit(f"frozen patch artifact missing: {PATCH}")

    fixture = L.build_longitudinal_fixture()
    runs: list[dict] = []
    # agentmemory accepts --instance 0..50 only; 20..25 keeps six distinct ports
    # clear of the Gen13/Gen33 range.
    instance = 19
    for n in range(1, args.repetitions + 1):
        for position, arm in enumerate(PAIR_ORDER[(n - 1) % len(PAIR_ORDER)], start=1):
            instance += 1
            runs.append(run_arm(fixture, n, arm, position, instance))
    if L.fixture_sha256() != FIXTURE_SHA:
        raise SystemExit("fixture hash drifted during the run")

    provenance = {
        "upstream_commit": "e04ba88819c365c9acf9d6661ea802143e728bd6",
        "package_version": "0.9.29",
        "patch_file": str(PATCH.relative_to(ROOT)),
        "patch_sha256": sha256_file(PATCH),
        "patched_source_sha256": sha256_file(AGENTMEMORY / "src/functions/remember.ts"),
        "unpatched_source_sha256": sha256_file(ROOT / "external/agentmemory/src/functions/remember.ts"),
        "built_cli_sha256": sha256_file(AGENTMEMORY / "dist/cli.mjs"),
        "flag": FLAG,
        "fixture_sha256": L.fixture_sha256(),
        "scorer_contract_sha256": L.scorer_contract_sha256(),
        "adapter_contract_sha256": A.adapter_contract_sha256(),
        "adapter_file_sha256": hashlib.sha256(
            (ROOT / "src/memory_bakeoff/providers/agentmemory_longitudinal.py").read_bytes()).hexdigest(),
        "pair_order": [list(p) for p in PAIR_ORDER[:args.repetitions]],
        "environment_parity": assert_env_parity(runs),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for run in runs:
        (out / f"repetition-{run['repetition']}-{run['arm']}.json").write_text(
            json.dumps(run, indent=2, sort_keys=True) + "\n")
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    for run in runs:
        failing = {k: v for k, v in run["failure_totals"].items() if v}
        print(f"  r{run['repetition']} {run['arm']:>3}: supersessions {run['supersession_count']} "
              f"{run['supersession_classification']}, lifecycle "
              f"{ {k: v for k, v in run['lifecycle_failure_totals'].items() if v} or 'clean'}, "
              f"cases {failing or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
