#!/usr/bin/env python3
"""Run isolated, authoritative agentmemory raw-product repetitions.

Each repetition gets a new iii data directory and an agentmemory-native isolated
agent ID.  The harness never filters retrieved rows; the service itself applies
the agent-ID boundary.  Result directories are created only by the standard
benchmark runner and are never overwritten.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from memory_bakeoff.corpus import build_corpus


ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def request_json(base_url: str, path: str, *, body: dict | None = None) -> dict:
    request = Request(
        base_url.rstrip("/") + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method="POST" if body is not None else "GET",
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"agentmemory request failed for {path}: {exc}") from exc


def service_env(agent_id: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "CI": "1",
            "EMBEDDING_PROVIDER": "local",
            "AGENTMEMORY_AGENT_SCOPE": "isolated",
            "AGENT_ID": agent_id,
            "CONSOLIDATION_ENABLED": "false",
            "GRAPH_EXTRACTION_ENABLED": "false",
            "AGENTMEMORY_AUTO_COMPRESS": "false",
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "OPENROUTER_API_KEY": "",
            "MINIMAX_API_KEY": "",
            "OPENAI_API_KEY_FOR_LLM": "false",
        }
    )
    return env


def start_service(
    agentmemory_dir: Path, state_dir: Path, instance: int, agent_id: str
) -> tuple[str, str, subprocess.Popen[str]]:
    port = 3111 + instance * 100
    command = ["node", "dist/cli.mjs", "--instance", str(instance), "--data-dir", str(state_dir)]
    launcher = subprocess.Popen(
        command,
        cwd=agentmemory_dir,
        env=service_env(agent_id),
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    startup = f"launcher pid={launcher.pid}; command={command!r}; instance={instance}; data_dir={state_dir}"
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if launcher.poll() is not None:
            raise RuntimeError(f"agentmemory launcher exited early ({launcher.returncode}): {startup}")
        try:
            health = request_json(base_url, "/agentmemory/health")
            if health.get("status") == "healthy":
                return base_url, startup, launcher
        except RuntimeError:
            time.sleep(0.25)
    raise RuntimeError(f"agentmemory did not become healthy at {base_url}\n{startup[-4000:]}")


def stop_service(
    agentmemory_dir: Path, state_dir: Path, instance: int, agent_id: str, launcher: subprocess.Popen[str] | None = None
) -> str:
    stopped = subprocess.run(
        ["node", "dist/cli.mjs", "stop", "--instance", str(instance), "--data-dir", str(state_dir)],
        cwd=agentmemory_dir,
        env=service_env(agent_id),
        text=True,
        capture_output=True,
        timeout=60,
    )
    if launcher is not None and launcher.poll() is None:
        launcher.terminate()
        try:
            launcher.wait(timeout=10)
        except subprocess.TimeoutExpired:
            launcher.kill()
            launcher.wait(timeout=10)
    return stopped.stdout + stopped.stderr


def isolated_rows(base_url: str, agent_id: str) -> dict:
    return request_json(base_url, f"/agentmemory/memories?agentId={agent_id}")


def run_preflight(agentmemory_dir: Path, instance: int, out: Path) -> None:
    if out.exists():
        raise RuntimeError(f"refusing to overwrite preflight directory: {out}")
    state_a = Path(tempfile.mkdtemp(prefix="agentmemory-gen13-preflight-a-", dir="/private/tmp"))
    agent_a = "memory-bakeoff-gen13-preflight-a"
    state_b = Path(tempfile.mkdtemp(prefix="agentmemory-gen13-preflight-b-", dir="/private/tmp"))
    agent_b = "memory-bakeoff-gen13-preflight-b"
    evidence: dict = {"status": "started", "state_directories": [str(state_a), str(state_b)]}
    launcher_a = launcher_b = None
    try:
        base_a, startup_a, launcher_a = start_service(agentmemory_dir, state_a, instance, agent_a)
        writes = []
        for project, record_id, content in (
            ("preflight-atlas", "PREFLIGHT_A", "Atlas release branch is release/atlas-2.x."),
            ("preflight-beacon", "PREFLIGHT_B", "Beacon release branch is stable."),
        ):
            writes.append(
                request_json(
                    base_a,
                    "/agentmemory/remember",
                    body={
                        "project": project,
                        "agentId": agent_a,
                        "content": content,
                        "type": "fact",
                        "sourceObservationIds": [record_id],
                    },
                )
            )
        visible = request_json(
            base_a,
            "/agentmemory/smart-search",
            body={"agentId": agent_a, "query": "What are the Atlas and Beacon release branches?", "limit": 5},
        )
        first_rows = isolated_rows(base_a, agent_a)
        stop_a = stop_service(agentmemory_dir, state_a, instance, agent_a, launcher_a)
        launcher_a = None
        first_ids = {row["memory"]["id"] for row in writes}
        base_b, startup_b, launcher_b = start_service(agentmemory_dir, state_b, instance, agent_b)
        second_search = request_json(
            base_b,
            "/agentmemory/smart-search",
            body={"agentId": agent_b, "query": "What are the Atlas and Beacon release branches?", "limit": 5},
        )
        second_rows = isolated_rows(base_b, agent_b)
        stop_b = stop_service(agentmemory_dir, state_b, instance, agent_b, launcher_b)
        launcher_b = None
        second_ids = {row.get("obsId") for row in second_search.get("results", [])}
        if not first_ids.issubset({row.get("obsId") for row in visible.get("results", [])}):
            raise RuntimeError("same-run two-project preflight records were not both visible to native smart-search")
        if first_ids & second_ids or second_rows.get("total") != 0:
            raise RuntimeError("cross-run leakage found in fresh isolated agentmemory state")
        evidence.update(
            {
                "status": "passed",
                "first": {"base_url": base_a, "agent_id": agent_a, "startup": startup_a, "writes": writes, "smart_search": visible, "memories": first_rows, "stop": stop_a},
                "second": {"base_url": base_b, "agent_id": agent_b, "startup": startup_b, "smart_search": second_search, "memories": second_rows, "stop": stop_b},
            }
        )
    except Exception as exc:
        evidence.update({"status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        raise
    finally:
        if launcher_a is not None:
            stop_service(agentmemory_dir, state_a, instance, agent_a, launcher_a)
        if launcher_b is not None:
            stop_service(agentmemory_dir, state_b, instance, agent_b, launcher_b)
        out.mkdir(parents=True, exist_ok=False)
        (out / "preflight.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")


def classify_lifecycle(run_json: dict, memories: dict) -> dict:
    trace = run_json[0]["provider_diagnostics"]["native_ingest_trace"]
    native = {entry["native_memory"]["id"]: entry["canonical_record_id"] for entry in trace}
    records, cases = build_corpus(distractors=max(0, len(trace) - 50))
    record_by_id = {record.id: record for record in records}
    prohibited_ids = {record_id for case in cases for record_id in case.prohibited_ids}
    rows = memories.get("memories", [])
    retired = [row for row in rows if row.get("isLatest") is False]
    live_native = {row["id"] for row in rows if row.get("isLatest") is not False}
    live_canonical = {native.get(row_id) for row_id in live_native}
    source_rows = {row["id"]: row for row in rows}
    successors = {
        retired_native_id: entry["canonical_record_id"]
        for entry in trace
        for retired_native_id in entry["native_memory"].get("supersedes", [])
    }
    retired_relationships = []
    for row in retired:
        retired_native_id = row["id"]
        retired_canonical_id = native.get(retired_native_id)
        successor_canonical_id = successors.get(retired_native_id)
        legitimate = bool(
            retired_canonical_id
            and successor_canonical_id
            and record_by_id[successor_canonical_id].supersedes_id == retired_canonical_id
        )
        retired_relationships.append(
            {
                "retired_native_id": retired_native_id,
                "retired_canonical_id": retired_canonical_id,
                "successor_canonical_id": successor_canonical_id,
                "legitimate_benchmark_supersession": legitimate,
                "false_supersession": bool(successor_canonical_id) and not legitimate,
                "retired_prohibited_record": retired_canonical_id in prohibited_ids,
                "parent_id": row.get("parentId"),
                "source_observation_ids": row.get("sourceObservationIds", []),
            }
        )
    legitimate_count = sum(item["legitimate_benchmark_supersession"] for item in retired_relationships)
    false_count = sum(item["false_supersession"] for item in retired_relationships)
    return {
        "native_memory_count": len(rows),
        "live_memory_count": len(live_native),
        "retired_memory_count": len(retired),
        "live_canonical_ids": sorted(item for item in live_canonical if item),
        "retired_relationships": retired_relationships,
        "legitimate_benchmark_supersession_count": legitimate_count,
        "false_supersession_count": false_count,
        "false_supersession_rate_of_retired": false_count / len(retired) if retired else 0.0,
        "retired_prohibited_record_count": sum(item["retired_prohibited_record"] for item in retired_relationships),
        "canonical_records_lost_from_live": sorted(
            set(native.values()) - {item for item in live_canonical if item}
        ),
        "native_id_to_canonical_id": native,
        "raw_rows": source_rows,
    }


def run_repetition(agentmemory_dir: Path, instance: int, condition: str, repetition: int, out: Path) -> None:
    if out.exists():
        raise RuntimeError(f"refusing to overwrite result directory: {out}")
    state_dir = Path(tempfile.mkdtemp(prefix=f"agentmemory-gen13-{condition}-r{repetition}-", dir="/private/tmp"))
    agent_id = f"memory-bakeoff-gen13-{condition}-r{repetition}"
    project = f"memory-bakeoff-gen13-{condition}-r{repetition}"
    base_url, startup, launcher = start_service(agentmemory_dir, state_dir, instance, agent_id)
    try:
        env = service_env(agent_id)
        env.update({"AGENTMEMORY_URL": base_url, "AGENTMEMORY_AGENT_ID": agent_id, "AGENTMEMORY_PROJECT": project})
        distractors = "0" if condition == "core" else "450"
        command = [str(VENV_PYTHON), "-m", "memory_bakeoff.cli", "run", "--providers", "agentmemory", "--mode", "raw", "--top-k", "5", "--distractors", distractors, "--out", str(out)]
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=900)
        if not out.exists():
            out.mkdir(parents=True)
        (out / "benchmark_stdout.txt").write_text(completed.stdout + completed.stderr)
        (out / "service_startup.txt").write_text(startup)
        if completed.returncode:
            raise RuntimeError(f"benchmark command failed ({completed.returncode})")
        run_json = json.loads((out / "run.json").read_text())
        row = run_json[0]
        rows = isolated_rows(base_url, agent_id)
        lifecycle = classify_lifecycle(run_json, rows)
        lifecycle.update({"agent_id": agent_id, "project": project, "state_directory": str(state_dir)})
        (out / "lifecycle.json").write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n")
        if row["status"] != "ok" or not row["publishability"]["publishable"]:
            raise RuntimeError(f"non-publishable benchmark result: {row['status']} {row['publishability']}")
        if len(lifecycle["native_id_to_canonical_id"]) != (50 if condition == "core" else 500):
            raise RuntimeError("native ingest trace does not cover every canonical record")
    finally:
        stop = stop_service(agentmemory_dir, state_dir, instance, agent_id, launcher)
        if out.exists():
            (out / "service_stop.txt").write_text(stop)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agentmemory-dir", type=Path, default=ROOT / "external" / "agentmemory")
    parser.add_argument("--instance", type=int, default=10)
    parser.add_argument("--results-root", type=Path, default=ROOT / "results")
    parser.add_argument(
        "--condition",
        choices=("core", "stress"),
        action="append",
        help="Run only this condition (repeatable); default runs both.",
    )
    parser.add_argument(
        "--repetition",
        type=int,
        action="append",
        choices=(1, 2, 3),
        help="Run only this repetition (repeatable); default runs all three.",
    )
    parser.add_argument(
        "--preflight-name",
        default="agentmemory_raw_product_gen13_isolation_preflight-r2",
        help="New result-directory name for this preflight attempt; never overwritten.",
    )
    args = parser.parse_args()
    if not VENV_PYTHON.exists():
        raise SystemExit(f"missing benchmark virtualenv: {VENV_PYTHON}")
    if not (args.agentmemory_dir / "dist" / "cli.mjs").exists():
        raise SystemExit(f"missing built pinned agentmemory checkout: {args.agentmemory_dir}")

    selected_conditions = args.condition or ("core", "stress")
    selected_repetitions = args.repetition or (1, 2, 3)
    if not args.condition and not args.repetition:
        preflight_out = args.results_root / args.preflight_name
        run_preflight(args.agentmemory_dir, args.instance, preflight_out)
    for condition in selected_conditions:
        for repetition in selected_repetitions:
            out = args.results_root / f"agentmemory_raw_product_gen13_{condition}-r{repetition}"
            run_repetition(args.agentmemory_dir, args.instance, condition, repetition, out)


if __name__ == "__main__":
    main()
