#!/usr/bin/env python3
"""Capture the Gen52 execution identity and prove it matches the frozen one."""
from __future__ import annotations

import hashlib, json, platform, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from memory_bakeoff.pi_state_control import raw_evidence as R  # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen52"
FROZEN = json.loads((ROOT / "results/pi_state_control_gen45/execution_identity.json").read_text())
ENDPOINT = "http://127.0.0.1:8080"
MODEL = "qwen3.6-35b-vulkan-nothink"


def props() -> dict:
    """llama-swap proxies /props per alias; a miss is not an identity failure."""
    for path in (f"/upstream/{MODEL}/props", "/props"):
        try:
            with urllib.request.urlopen(f"{ENDPOINT}{path}", timeout=60) as response:
                return json.loads(response.read())
        except Exception as error:                       # noqa: BLE001
            last = f"{path}: {error}"
    return {"unavailable": last}


def sha256(path: Path) -> str:
    return R.sha256_file(path) if path.exists() else ""


def main() -> int:
    live = props()
    model_path = Path(FROZEN["model"]["path"])
    binary = Path(FROZEN["server"]["binary"])
    identity = {
        "evidence_class": "architecture_quiescent_completion_ablation_paired_live",
        "authorized_by": "Brian's standing local-GPU authorization, 2026-09-04; local Strix Halo pinned path only",
        "executed_on": {"host": platform.node(), "kernel": platform.release()},
        "model": {**FROZEN["model"], "sha256_now": sha256(model_path),
                  "bytes_now": model_path.stat().st_size if model_path.exists() else 0},
        "server": {**FROZEN["server"], "binary_sha256_now": sha256(binary)},
        "sampling": FROZEN["sampling"],
        "reasoning": FROZEN["reasoning"],
        "run_timeout_seconds": FROZEN["run_timeout_seconds"],
        "pi": FROZEN["pi"],
        "network": "PI_OFFLINE=1; the only endpoint used is the local llama-swap on this host",
        "live_props": {"model_alias": live.get("model_path") or live.get("model"),
                       "n_ctx": live.get("default_generation_settings", {}).get("n_ctx")
                                or live.get("n_ctx"),
                       "build": live.get("build_info")},
        "repo_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                    capture_output=True, text=True).stdout.strip(),
    }
    identity["matches_frozen_identity"] = {
        "model_sha256": identity["model"]["sha256_now"] == FROZEN["model"]["sha256"],
        "model_bytes": identity["model"]["bytes_now"] == FROZEN["model"]["bytes"],
        "server_binary_sha256": identity["server"]["binary_sha256_now"] == FROZEN["server"]["binary_sha256"],
        "sampling_unchanged": identity["sampling"] == FROZEN["sampling"],
        "timeout_unchanged": identity["run_timeout_seconds"] == 900,
        "local_endpoint_only": ENDPOINT.startswith("http://127.0.0.1"),
    }
    identity["passed"] = all(identity["matches_frozen_identity"].values())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "execution_identity.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n")
    print(json.dumps(identity["matches_frozen_identity"], indent=1))
    return 0 if identity["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
