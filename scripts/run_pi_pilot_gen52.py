#!/usr/bin/env python3
"""Gen52: execute the frozen C-vs-E quiescent-completion ablation.

Runs on the Linux workstation, where Pi and the inference server live. One run
per invocation of `single`; `smoke` runs the unscored compatibility suite; `all`
walks the frozen order manifest.

Nothing here may change a task, a prompt, a cap or a sampling parameter. The
only knobs are which arm and which slot.
"""
from __future__ import annotations

import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import pilot as P  # noqa: E402
from memory_bakeoff.pi_state_control import raw_evidence as R  # noqa: E402

OUT = ROOT / "results" / "pi_quiescent_completion_gen52"
GEN52 = ROOT / "results" / "pi_quiescent_completion_gen52"
# Raw provider streams live outside the repo and outside every ephemeral area,
# under `raw-evidence-retention-v1`. They are never committed.
ARCHIVE = Path.home() / "gen52-raw-archive"
GEN48 = ROOT / "results" / "pi_state_control_gen48"
EXTENSIONS = {
    "pi_harness_state_control_v1": ROOT / "extensions/pi_state_control/pi_pilot_harness_state.ts",
    "pi_harness_state_control_quiescent_k3_v1": ROOT / "extensions/pi_state_control/pi_pilot_quiescent.ts",
}

# Fixed before the first live request and not tuned afterwards.
RUN_TIMEOUT_SECONDS = 900
PROVIDER = "qwen"
MODEL = "qwen3.6-35b-vulkan-nothink"
AGENT_DIR = Path.home() / ".pi-pilot-gen45"

# The smoke fixture and its single prompt, committed before any completion.
SMOKE_GOAL = "make the greeting helper return the caller's name"
SMOKE_FILES = {
    "kettle/__init__.py": "",
    "kettle/greet.py": 'def greet(name: str) -> str:\n    """Return a greeting for the caller."""\n    return "hello"\n',
    "README.md": "# kettle\n\nA tiny greeting helper.\n",
    # The smoke needs a visible check, because the only thing the deterministic
    # preflight cannot prove is that a real Pi print-mode run actually ends when
    # the policy aborts it, with its evidence intact.
    "run_checks.py": (
        "from kettle.greet import greet\n"
        "assert greet('ada') == 'hello ada', greet('ada')\n"
        "print('all checks passed')\n"),
}
SMOKE_PROMPT = (
    "In this repository, `kettle/greet.py` has a function `greet(name)` that ignores its "
    "argument and always returns \"hello\". Read the file, then edit it so it returns "
    "\"hello NAME\" for the name it is given. Then run `python run_checks.py` to confirm. "
    "After the checks pass, look around the repository a little more with `ls` and `cat` "
    "before you finish, then say DONE."
)

def agent_dir() -> Path:
    """An isolated Pi configuration, so neither arm inherits local customisation."""
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    models = {
        "providers": {
            PROVIDER: {
                "baseUrl": "http://127.0.0.1:8080/v1",
                "api": "openai-completions",
                "apiKey": "none",
                "compat": {"sendSessionAffinityHeaders": True},
                "models": [{
                    "id": MODEL, "contextWindow": 131072, "maxTokens": 8192,
                    "compat": {"supportsDeveloperRole": False, "supportsReasoningEffort": False},
                }],
            }
        }
    }
    (AGENT_DIR / "models.json").write_text(json.dumps(models, indent=1))
    (AGENT_DIR / "settings.json").write_text(json.dumps({
        "enableInstallTelemetry": False,
        "defaultProvider": PROVIDER,
        "defaultModel": f"{PROVIDER}/{MODEL}",
        "packages": [],
        "defaultThinkingLevel": "off",
    }, indent=1))
    return AGENT_DIR


def reset_worktree(source: Path, target: Path) -> str:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "-c", "user.email=p@example.invalid", "-c", "user.name=p",
                    "commit", "-qm", "run"], cwd=target, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=target,
                          capture_output=True, text=True, check=True).stdout.strip()


def tree_digest(path: Path) -> str:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    return subprocess.run(["git", "write-tree"], cwd=path,
                          capture_output=True, text=True, check=True).stdout.strip()


def pi_command(arm: str, prompt: str) -> list[str]:
    command = [
        "pi", "--print", "--mode", "json",
        "--provider", PROVIDER, "--model", MODEL,
        "--thinking", "off",
        "--no-extensions", "--no-skills", "--no-context-files", "--no-prompt-templates",
        "--no-session",
    ]
    # Each arm loads its own extension. Both carry the identical observation-only
    # provider-payload hook, so the measurement surface is the same.
    command += ["--extension", str(EXTENSIONS[arm]), prompt]
    return command


def execute(arm: str, worktree: Path, prompt: str, goal: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        PI_PILOT_ARM=arm,
        PI_PILOT_OUT=str(out),
        PI_PILOT_WORKTREE=str(worktree),
        PI_PILOT_GOAL=goal,
        PI_CODING_AGENT_DIR=str(agent_dir()),
        PI_OFFLINE="1",
        NO_COLOR="1",
    )
    started = time.time()
    try:
        proc = subprocess.run(pi_command(arm, prompt), cwd=worktree, env=env,
                              capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
        status, code = "completed", proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        status, code = "timeout", None
        stdout = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    elapsed = time.time() - started
    (out / "stdout.txt").write_text(stdout)
    (out / "stderr.txt").write_text(stderr)
    # Finalize the raw stream into the durable archive before anything can clean
    # up. Gen47 and Gen49 were lost because hashing and deleting were the same
    # step; here the archive copy is made first and verified separately.
    archived = R.archive_stream(out / "stdout.txt", ARCHIVE, out.name, "stdout.txt")
    return {"status": status, "exit_code": code, "wall_seconds": round(elapsed, 2),
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
            "raw_stream": {"sha256": archived.sha256, "bytes": archived.bytes,
                           "archive_relative_path": str(archived.archive_path.relative_to(ARCHIVE))}}


def read_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def collect(out: Path) -> dict:
    requests = read_lines(out / "requests.ndjson")
    tools = read_lines(out / "tools.ndjson")
    control = read_lines(out / "history.ndjson")
    state = json.loads((out / "state.json").read_text()) if (out / "state.json").exists() else {}
    harness = json.loads((out / "harness_state.json").read_text()) if (out / "harness_state.json").exists() else {}
    payloads = [row["bytes"] for row in read_lines(out / "payloads.ndjson")]
    derivation = read_lines(out / "derivation.ndjson")
    stop = json.loads((out / "quiescent_stop.json").read_text()) if (out / "quiescent_stop.json").exists() else None
    sizes = [r["bytes"] for r in requests]
    calls = [{"tool": t["tool"], "args": t.get("args", {})} for t in tools if t.get("phase") == "call"]
    for call in calls:
        args = call["args"]
        if isinstance(args, dict):
            call["path"] = args.get("path") or args.get("file_path") or ""
            call["command"] = args.get("command") or args.get("cmd") or ""
            call["mutates_repo"] = call["tool"] in {"edit", "write", "multi_edit"}
    churn = P.count_churn(calls)
    return {
        "requests": requests,
        "request_count": len(requests),
        "request_bytes_total": sum(sizes),
        "request_bytes_max": max(sizes) if sizes else 0,
        "request_bytes_median": sorted(sizes)[len(sizes) // 2] if sizes else 0,
        "request_bytes_by_turn": sizes,
        "tool_calls": len(calls),
        "churn": {k: v for k, v in churn.items() if k != "detail"},
        "control_events": len(control),
        "counters": state.get("counters", {}),
        "final_state": state.get("state", {}),
        "final_phase": (harness.get("state", {}) or state.get("state", {})).get("phase"),
        # exact full provider payload, tool schemas included
        "payload_bytes_total": sum(payloads),
        "payload_bytes_by_turn": payloads,
        "payload_captures": len(payloads),
        # arm C mechanism evidence
        "harness": {
            "transitions": harness.get("transitions", []),
            "transitions_accepted": harness.get("transitions_accepted"),
            "transitions_rejected": harness.get("transitions_rejected"),
            "receipts": len(harness.get("receipts", []) or []),
            "receipt_invalidations": len(harness.get("receipt_invalidations", []) or []),
            "valid_receipt_at_end": harness.get("valid_receipt_at_end"),
            "state_bytes": harness.get("state_bytes"),
            "derivation_events": len(derivation),
            "phase_path": [t["to"] for t in (harness.get("transitions") or []) if t.get("accepted")],
        } if harness else None,
        # arm E stop policy
        "quiescent_stop": stop,
        # arm D floor exposure
        "floor": {
            "exposed": any(r.get("floor_active") for r in requests),
            "first_activation_request": next(
                (r.get("first_activation_request") for r in requests if r.get("floor_active")), None),
            "active_requests": sum(1 for r in requests if r.get("floor_active")),
            "floor_bytes_per_request": next(
                (r.get("floor_bytes") for r in requests if r.get("floor_active")), 0),
            "cumulative_floor_bytes": sum(r.get("floor_bytes") or 0 for r in requests),
            "original_prompt_sha256": next(
                (r.get("original_prompt_sha256") for r in requests if r.get("original_prompt_sha256")), None),
        } if any("floor_active" in r for r in requests) else None,
        # arm C: did the task age out of the ordinary window at all?
        "task_prompt_aged_out": None,
        # arm B adoption evidence
        "adoption": {
            tool: {
                "called": sum(1 for c in tools if c.get("phase") == "call" and c.get("tool") == tool),
                "first_call_turn": next((i for i, c in enumerate(
                    [t for t in tools if t.get("phase") == "call"], start=1)
                    if c.get("tool") == tool), None),
            }
            for tool in ("propose_state_patch", "request_transition", "record_receipt")
        },
    }


def classify_requirements(tail: str) -> dict:
    """Which named public requirement failed, from the verifier's own message."""
    failed = None
    for marker in ("A:", "B:"):
        if marker in tail:
            failed = marker[0]
            break
    return {"failed_requirement": failed}


def verify(verifier: Path, worktree: Path) -> dict:
    for cache in worktree.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    proc = subprocess.run([sys.executable, "-B", str(verifier)], cwd=worktree,
                          capture_output=True, text=True, timeout=180,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-1:] or [""]
    return {"passed": proc.returncode == 0, "tail": tail,
            **classify_requirements(tail[0])}


def run_smoke(work: Path) -> dict:
    out = OUT / "smoke"
    if out.exists():
        shutil.rmtree(out)
    source = work / "smoke_source"
    if source.exists():
        shutil.rmtree(source)
    source.mkdir(parents=True)
    for relative, content in SMOKE_FILES.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    results = {}
    for arm in ("pi_harness_state_control_v1", "pi_harness_state_control_quiescent_k3_v1"):
        worktree = work / f"smoke_{arm}"
        reset_worktree(source, worktree)
        run = execute(arm, worktree, SMOKE_PROMPT, SMOKE_GOAL, out / arm)
        measured = collect(out / arm)
        edited = (worktree / "kettle" / "greet.py").read_text()
        results[arm] = {
            "run": run,
            "measured": {k: v for k, v in measured.items() if k not in ("requests", "final_state")},
            "greet_now_uses_the_name": "name" in edited.split("return", 1)[-1],
            "quiescent_stop": measured.get("quiescent_stop"),
            "file_after": edited,
        }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["single", "all", "smoke"])
    ap.add_argument("--arm")
    ap.add_argument("--task")
    ap.add_argument("--repetition", type=int)
    ap.add_argument("--work", default=str(Path.home() / "pilot-gen45-work"))
    args = ap.parse_args()

    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    if args.mode == "smoke":
        results = run_smoke(work)
        (OUT / "smoke_raw.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        print(json.dumps({arm: {"status": r["run"]["status"],
                                "exit": r["run"]["exit_code"],
                                "requests": r["measured"]["request_count"],
                                "tools": r["measured"]["tool_calls"],
                                "phase": r["measured"]["final_phase"],
                                "stop": r["quiescent_stop"],
                                "edited": r["greet_now_uses_the_name"],
                                "seconds": r["run"]["wall_seconds"]}
                          for arm, r in results.items()}, indent=1))
        return 0

    manifest = json.loads((GEN48 / "task_manifest.json").read_text())
    order = json.loads((GEN52 / "gen52_order_manifest.json").read_text())["order"]
    slots = order if args.mode == "all" else [
        row for row in order
        if row["task"] == args.task and row["repetition"] == args.repetition and row["arm"] == args.arm
    ]

    for slot in slots:
        task = manifest["tasks"][slot["task"]]
        leaf_dir = OUT / "runs" / f"{slot['index']:02d}-{slot['task']}-r{slot['repetition']}-{slot['arm']}"
        if (leaf_dir / "leaf.json").exists():
            print(f"skip {leaf_dir.name}: already recorded")
            continue
        worktree = work / f"run_{slot['index']:02d}"
        start_tree = reset_worktree(ROOT / task["repo_path"], worktree)
        if start_tree != task["git_tree_digest"]:
            raise SystemExit(f"frozen tree drift for {slot['task']}: {start_tree}")
        prompt = task["prompt"]
        run = execute(slot["arm"], worktree, prompt, prompt, leaf_dir)
        measured = collect(leaf_dir)
        result = verify(ROOT / task["verifier_path"], worktree)
        stop = measured.get("quiescent_stop")
        if run["status"] == "timeout":
            termination = "timeout"
        elif stop and stop.get("triggered"):
            termination = "quiescent_stop"
        elif run["status"] == "completed" and run["exit_code"] == 0:
            termination = "model_completed"
        else:
            termination = "crash_or_orchestration_failure"
        leaf = {
            "slot": slot,
            "termination_class": termination,
            "task": {"id": slot["task"], "start_tree": start_tree,
                     "final_tree": tree_digest(worktree),
                     "verifier_sha256": task["verifier_sha256"]},
            "run": run,
            "verifier": result,
            "measured": {k: v for k, v in measured.items() if k != "requests"},
            "requests": measured["requests"],
        }
        leaf_dir.mkdir(parents=True, exist_ok=True)
        (leaf_dir / "leaf.json").write_text(json.dumps(leaf, indent=2, sort_keys=True) + "\n")
        print(f"{leaf_dir.name}: {termination} verifier={result['passed']} "
              f"requests={measured['request_count']} bytes={measured['request_bytes_total']} "
              f"tools={measured['tool_calls']} {run['wall_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
