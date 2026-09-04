#!/usr/bin/env python3
"""Gen42: MemBukkit intended models over the frozen three-persona calibration.

The frozen Gen37 procedure is imported and executed unchanged; this script only
registers the MemBukkit engine into it, proves the pins first, blocks the
network, and attaches the routing observation the Gen37 leaf has no field for.

Development-exposed calibration. Not an official MemConflict score, not a full
release, no reader, no upstream judge.
"""
from __future__ import annotations

import argparse, importlib, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import memconflict as M  # noqa: E402
from memory_bakeoff import memconflict_engines_gen42 as G42  # noqa: E402
from memory_bakeoff.membukkit_gen40 import block_network, reconcile_snapshot, snapshot_identity  # noqa: E402
from memory_bakeoff.membukkit_gen41 import CONFIGURATIONS, EXPECTED_RETRIEVAL  # noqa: E402
from memory_bakeoff.providers import membukkit_memconflict as ADAPTER  # noqa: E402
from memory_bakeoff.round2_reporting import ReportingError  # noqa: E402

G37 = importlib.import_module("run_memconflict_gen37_calibration")

FROZEN_CONTRACT_SHA = "0521210818e448c8f189dacc33e287b15525f89d63f39cb627f9cdc7a3dccd28"
GEN41_PINS = ROOT / "results" / "membukkit_gen41_manifest" / "pins.json"


def assert_pins() -> dict:
    """Model identity, offline, against the manifest Gen41 committed."""
    pins = json.loads(GEN41_PINS.read_text())["intended"]
    out = {}
    for role, spec in CONFIGURATIONS["intended"].items():
        local = Path(spec["local"])
        if not local.exists():
            raise ReportingError(f"pinned snapshot missing at {local}")
        committed = pins[role]
        if committed["revision"] != spec["revision"]:
            raise ReportingError(f"{role} revision drift: {committed['revision']}")
        remote = {
            name: {"lfs_sha256": meta["sha256"], "oid": meta["git_oid"]}
            for name, meta in committed["files"].items()
        }
        rec = reconcile_snapshot(snapshot_identity(local), remote)
        if not rec["all_match"]:
            raise ReportingError(f"{role} snapshot drift: {rec['mismatched'] + rec['local_only']}")
        out[role] = {"repo": spec["repo"], "revision": spec["revision"],
                     "local": str(local), "files_reconciled": len(rec["matched"])}
    return out


def assert_preflight(out_dir: Path) -> dict:
    payload = json.loads((out_dir / "preflight.json").read_text())
    if not payload.get("passed"):
        raise ReportingError("preflight did not pass; refusing to expose calibration")
    if payload["adapter"]["sha256"] != ADAPTER.adapter_contract_sha256():
        raise ReportingError("adapter changed after the preflight freeze")
    return {"adapter_sha256": payload["adapter"]["sha256"],
            "engine_module_sha256": payload["adapter"]["engine_module_sha256"]}


def routing_for(engine, persona, leaf) -> list[dict]:
    """What the router opened for each question, mapped nowhere near retrieval."""
    text_by_key = {q.key: q.text for q in M.questions(persona)}
    rows = []
    for record in leaf["questions"]:
        text = text_by_key[record["question_key"]]
        rows.append({
            "question_key": record["question_key"],
            "candidate_region_native_ids": engine.regions.get(text, []),
            "candidate_region_size": len(engine.regions.get(text, [])),
            "trace": engine.traces.get(text, {}),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/membukkit_memconflict_gen42_calibration"))
    ap.add_argument("--state-root", default="/private/tmp")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if M.dataset_sha256() != M.DATASET_SHA256:
        raise ReportingError("pinned dataset hash drift; refusing to run")
    if M.contract_sha256() != FROZEN_CONTRACT_SHA:
        raise ReportingError("frozen benchmark contract drifted; refusing to run")

    manifest = json.loads(
        (ROOT / "results/memconflict_gen36_contract/calibration-manifest.json").read_text()
    )
    calibration = set(manifest["calibration_persona_ids"])
    personas = [p for p in M.load_personas() if p["ID"] in calibration]
    if len(personas) != manifest["calibration_persona_count"]:
        raise ReportingError("calibration subset does not match the frozen manifest")

    identity = {
        "membukkit_source": subprocess.run(
            ["git", "-C", str(ROOT / "external" / "membukkit"), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip(),
        "models": assert_pins(),
        "preflight": assert_preflight(out),
        "retrieval": {k: (list(v) if isinstance(v, tuple) else v) for k, v in EXPECTED_RETRIEVAL.items()},
        "required_devices": G42.REQUIRED_DEVICES,
        "native_top_k": G42.NATIVE_TOP_K,
        "adapter_version": ADAPTER.ADAPTER_VERSION,
        "calibration_persona_ids": sorted(calibration),
        "evidence_class": "external_benchmark_calibration_raw_product_exact_provenance",
        "lane": "memconflict-exact-whitebox-v1",
        "development_exposed": True,
    }

    G37.ADAPTERS["membukkit"] = ADAPTER
    G37.FROZEN_ADAPTER_SHA["membukkit"] = ADAPTER.adapter_contract_sha256()
    G37.E.ENGINES.update(G42.ENGINES)

    state_root = Path(args.state_root) / f"membukkit-gen42-{int(time.time())}"
    state_root.mkdir(parents=True)

    # Models load from the pinned local snapshots before the network closes.
    G42.MemBukkitEngine._models()
    block_network()
    identity["device_proof"] = G42.MemBukkitEngine._shared["proof"]
    (out / "identity.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n")

    original_engine = G42.MemBukkitEngine
    live: dict = {}

    class _Capturing(original_engine):
        def __init__(self, persona_id, root):
            super().__init__(persona_id, root)
            live["engine"] = self

    G37.E.ENGINES["membukkit"] = _Capturing

    for persona in personas:
        leaf, ledger = G37.run_persona("membukkit", persona, state_root)
        engine = live["engine"]
        leaf["routing"] = routing_for(engine, persona, leaf)
        leaf["scan_fraction_distribution"] = sorted(engine.scan_fractions)
        (out / f"persona-{persona['ID']}.json").write_text(
            json.dumps(leaf, indent=2, sort_keys=True) + "\n")
        (out / f"ledger-{persona['ID']}.json").write_text(
            json.dumps(ledger, indent=2, sort_keys=True) + "\n")
        ops = leaf["operations"]
        print(f"membukkit {persona['ID']}: {ops['successful_writes']}/{ops['attempted_writes']} writes, "
              f"{ops['questions_executed']} questions, {ops['wall_seconds']}s, "
              f"write p50 {ops['write_latency'].get('p50_ms')}ms, "
              f"query p50 {ops['query_latency'].get('p50_ms')}ms")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
