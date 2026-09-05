#!/usr/bin/env python3
"""Fold hindsight's per-repetition probe files into the Gen70 engine summary."""
from __future__ import annotations

import json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from memory_bakeoff import longitudinal as L                    # noqa: E402
from memory_bakeoff import temporal_reachability as T           # noqa: E402
from run_gen70_leakage import answer_claim_probe, score         # noqa: E402

OUT = ROOT / "results" / "temporal_blind_spot_gen70"
FIXTURE_SHA = "a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd"


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/gen70hs")
    fixture = L.build_longitudinal_fixture()
    if L.fixture_sha256(fixture) != FIXTURE_SHA:
        raise SystemExit("fixture changed; refusing to collect")
    OUT.mkdir(parents=True, exist_ok=True)

    repetitions = []
    for path in sorted(source.glob("rep*.json")):
        payload = json.loads(path.read_text())
        payload["records"] = score(fixture, payload["records"])
        payload["unknown_hallucination"] = answer_claim_probe(fixture, payload["records"])
        repetitions.append(payload)

    summary = {
        "engine": "hindsight", "generation": 70, "probe": T.LEAKAGE_PROBE,
        "fixture_sha256": FIXTURE_SHA, "suite_rerun": False,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repetitions": repetitions,
        "future_leakage_cases": sum(1 for rep in repetitions
                                    for r in rep["records"] if r["future_leakage"]),
        "probe_cases_total": sum(len(rep["records"]) for rep in repetitions),
        "pinned_model_note": "the pinned e5-small snapshot had been purged from "
                             "/private/tmp; restored at the same revision "
                             "614241f622f53c4eeff9890bdc4f31cfecc418b3 before running",
    }
    (OUT / "hindsight.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("engine", "future_leakage_cases", "probe_cases_total")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
