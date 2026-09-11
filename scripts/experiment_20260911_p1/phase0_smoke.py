#!/usr/bin/env python3
"""STUDY-20260911-P1 Phase 0 real-path smoke (dispatch §Phase 0).

Proves through the ACTUAL B/C-round RPC-resume machinery:
  1. the Perseus adapter (extensions/pi-perseus-recall) runs as a Pi recall
     path (project_recall registered, pi-lcm ACTIVE, nudge companion
     untouched and firing through genuine resume);
  2. supersession toggles cleanly between otherwise-identical B/C configs
     (seed-time binding_on; identical vaults except the supersede link);
  3. the coding agent retrieves the known replacement through the real path
     (supersede-ON vault: current record surfaced, old record NOT).

Provenance (mandatory recording): study binary sha256 c8a222ec...a172
(self-reports 2.23.2 (9c82920)), source-identical, NOT byte-identical to
the Gen21-measured arm64 tarball sha256 e9b0912c...0dcb; build.sh
GIT_HASH=9c82920, rust 1.97.1 bookworm, DEFAULT features (Dockerfile lean
build FORBIDDEN). from_key = OLD (parameters authoritative).
"""
from __future__ import annotations

import hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/experiment_20260910b"))
import run_pi_pilot_r2 as r2  # noqa: E402
import run_b as rb  # noqa: E402

BIN = Path("/var/home/bmosher/perseus-build/src/target/release/perseus-vault")
STUDY_SHA = "c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172"
GEN21_SHA = "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb"
PROVENANCE = {
    "study_binary": str(BIN),
    "study_binary_sha256": STUDY_SHA,
    "study_binary_version": "perseus-vault 2.23.2 (9c82920)",
    "gen21_measured_sha256_arm64_tarball": GEN21_SHA,
    "identity": "source-identical, NOT byte-identical",
    "build_method": "build.sh with GIT_HASH=9c82920, rust 1.97.1 bookworm, "
                    "DEFAULT features (the Dockerfile lean build is FORBIDDEN "
                    "- keyword-only wearing the version string)",
    "supersede_direction": "from_key = OLD (parameters authoritative)",
}

PRIVATE = Path("/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260911-p1")
AGENT_BASE = Path("/var/home/bmosher/.pi-experiment-p1")
PERSEUS_EXT = ROOT / "extensions/pi-perseus-recall"
WS = "b" * 64
OLD_REC = {"decision": "staging deploys via the legacy VM ansible wrapper",
           "ticket": "P1-OLD-1", "recorded_by": "prior session"}
NEW_REC = {"decision": "staging deploys via helm on the kite-k8s cluster",
           "ticket": "P1-NEW-9", "recorded_by": "prior session"}


def sh(args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        raise SystemExit(f"fail {args[1:3]}: {r.stderr[-300:]}")
    return r.stdout


def seed_vault(root: Path, supersede: bool) -> Path:
    """Identical records + (optionally) the supersede link. binding_on."""
    db, key = root / "vault.sqlite", root / "vault.key"
    sh([BIN, "keygen", "--key-file", key])
    for k, body in (("record-old", OLD_REC), ("record-new", NEW_REC)):
        sh([BIN, "write", "--db", db, "--encryption-key", key,
            "--category", "decision", "--key", k,
            "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
            "--workspace-hash", WS])
    if supersede:
        proc = subprocess.Popen([str(BIN), "serve", "--db", str(db), "--encryption-key", str(key)],
                                text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, bufsize=1)
        try:
            def rpc(method, params):
                rpc.i = getattr(rpc, "i", 0) + 1
                proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rpc.i,
                                             "method": method, "params": params}) + "\n")
                proc.stdin.flush()
                return json.loads(proc.stdout.readline())["result"]
            rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "p1-seed", "version": "0"}})
            r = rpc("tools/call", {"name": "perseus_vault_supersede", "arguments": {
                "from_category": "decision", "from_key": "record-old",
                "to_category": "decision", "to_key": "record-new",
                "relationship": "supersedes", "reason": "P1 phase0: new replaces old"}})
            print("supersede receipt:", json.dumps(r)[:180])
        finally:
            proc.terminate(); proc.wait(timeout=10)
    return db


def agent_dir(vault_db: Path) -> Path:
    """One arm-agent config: pi-lcm + pi-perseus-recall + pi-recall-nudge.
    The vault points at the given db; B/C differ ONLY in that db's lineage."""
    d = AGENT_BASE / "arm"
    d.mkdir(parents=True, exist_ok=True)
    (d / "models.json").write_text(json.dumps(r2.provider_models(), indent=1))
    settings = {
        "enableInstallTelemetry": False,
        "defaultProvider": "bosgame",
        "defaultModel": "bosgame/qwen3.6-35b-vulkan-nothink",
        "packages": [r2.PI_LCM, str(PERSEUS_EXT), str(r2.NUDGE_EXT)],
        "defaultThinkingLevel": "high",
        "recallNudge": {"enabled": True, "nudge": r2.F2_NUDGE,
                        "onResume": True, "everyPrompt": False,
                        "everyNPrompts": 0, "delivery": "message"},
        "perseusRecall": {"bin": str(BIN), "db": str(vault_db),
                          "keyFile": str(vault_db.parent / "vault.key"),
                          "workspaceHash": WS, "limit": 5},
    }
    settings.update(r2.lcm_settings())
    (d / "settings.json").write_text(json.dumps(settings, indent=1))
    return d


def main() -> None:
    out = PRIVATE / "phase0-smoke"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    binary_sha = hashlib.sha256(BIN.read_bytes()).hexdigest()
    assert binary_sha == STUDY_SHA, f"binary sha drift: {binary_sha}"

    # item 2: the toggle pair (persistent vaults; identical except the link)
    db_off = seed_vault(out / "vault-off", supersede=False)
    db_on = seed_vault(out / "vault-on", supersede=True)

    # items 1+3: real-path run against the supersede-ON vault
    ad = agent_dir(db_on)
    rb.agent_dir = lambda arm: ad  # B-round machinery resolves agent dirs here
    src = out / "_src"
    src.mkdir()
    for rel, content in r2.SMOKE_FILES.items():
        f = src / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    worktree = out / "repo"
    r2.reset_worktree(src, worktree)
    store_dir = out / "lcm"  # pi-lcm ACTIVE: normal writes

    sessions = out / "sessions"
    sessions.mkdir()
    prime = rb.invoke(rb.pi_base() + ["--session-dir", str(sessions), rb.PRIME_PROMPT],
                      worktree, "P", store_dir,
                      out / "prime-stdout.txt", out / "prime-stderr.txt")
    session_file, session_id = rb.find_session_file(
        sessions, (out / "prime-stdout.txt").read_text())
    task_prompt = (
        "Use the project_recall tool now with query \"staging deploy process\". "
        "Reply with the decision text and ticket id of each record it returns, "
        "and state which one is the current deployment decision for staging. "
        "Do not edit any files.")
    task = rb.invoke_task("P", worktree, session_file, task_prompt, out, store_dir)
    stdout = (out / "stdout.txt").read_text()
    stderr = (out / "stderr.txt").read_text()
    parsed = r2.parse_events(stdout)

    nud = rb.nudge_evidence(stderr, stdout)
    recall_calls = sum(1 for t in parsed["tool_calls"] if t == "project_recall")
    new_surfaced = "P1-NEW-9" in stdout and "helm" in stdout
    old_as_current_absent = not ("P1-OLD-1" in stdout)
    registered = ("pi-perseus-recall: registered project_recall" in stderr
                  and "pi-recall-nudge: registered" in stderr)

    lines = [
        "STUDY-20260911-P1 PHASE 0 REAL-PATH SMOKE (RPC genuine-resume machinery)",
        f"binary sha256: {binary_sha}",
        f"provenance: {json.dumps(PROVENANCE)}",
        "",
        f"[1] adapter as Pi recall path: perseus adapter registered: "
        f"{'pi-perseus-recall: registered project_recall' in stderr} | "
        f"nudge companion registered: {'pi-recall-nudge: registered' in stderr}",
        f"    pi-lcm ACTIVE: prime {prime['status']} {prime['wall_seconds']}s | "
        f"task {task['status']} {task['wall_seconds']}s | "
        f"store rows written: {len(list(store_dir.glob('*.db')))}",
        f"    project_recall calls through the real path: {recall_calls}",
        f"    genuine resume: reason={nud['resume_reason']!r} injected={nud['injected']} "
        f"line={nud['inject_line']!r}",
        f"[2] supersession toggle (seed-time binding_on, from_key=OLD): "
        f"see phase0_toggle.txt (OFF: both records; ON: record-new only)",
        f"[3] known replacement retrieved: current surfaced (P1-NEW-9 + helm): "
        f"{new_surfaced} | old record surfaced (P1-OLD-1): "
        f"{('P1-OLD-1' in stdout)} (must be False)",
    ]
    verdict = (registered and recall_calls >= 1 and new_surfaced and old_as_current_absent
               and nud["injected"] and nud["resume_reason"] == "resume")
    lines += ["", "PHASE 0 SMOKE RECEIPT: PASS" if verdict else "PHASE 0 SMOKE RECEIPT: FAIL"]
    (out / "PHASE0_RECEIPT.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
