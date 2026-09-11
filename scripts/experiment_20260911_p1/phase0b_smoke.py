#!/usr/bin/env python3
"""STUDY-20260911-P1B phase-0-style re-smoke (conductor-dispatched).

Re-proves the three original phase-0 checkpoint items after the
pi-perseus-recall return-shape fix, PLUS the NEW DELIVERED-LEVEL GATE the
conductor ordered: the toolResult message VISIBLE IN MODEL CONTEXT must
contain the expected record content. The original smoke passed while its
agent received empty toolResults because it asserted stream-level presence
only (`"P1-NEW-9" in stdout`) — that assertion level is retained here as
necessary-but-insufficient, and the delivered level is what gates PASS.

Items:
  1. adapter as Pi recall path (registration, pi-lcm ACTIVE, nudge via
     genuine resume) — as before;
  2. supersession toggle (direct vault RPC, no agent): OFF both records /
     ON record-new only — as before, receipt phase0b_toggle.txt;
  3. stream-level retrieval (current surfaced, old absent anywhere in the
     stream) — as before (insufficient alone);
  4. DELIVERED-LEVEL GATE: parity per toolCallId (every project_recall
     execution has a model-visible toolResult with non-empty text carrying
     the same record keys), expected content (P1-NEW-9 + helm) present in
     DELIVERED text, P1-OLD-1 absent from DELIVERED text. Final-answer
     mention is recorded as evidence (not a gate — the smoke proves
     integration, not task behavior).

Provenance: unchanged from PROVENANCE.md (binary sha asserted before any
vault operation; block recorded in the receipt).
"""
from __future__ import annotations

import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "scripts", ROOT / "scripts/experiment_20260910b",
          ROOT / "scripts/experiment_20260911_p1"):
    sys.path.insert(0, str(p))
import run_pi_pilot_r2 as r2  # noqa: E402
import run_b as rb  # noqa: E402
from run_p1b import parse_delivery, gate_slot  # noqa: E402

BIN = Path("/var/home/bmosher/perseus-build/src/target/release/perseus-vault")
STUDY_SHA = "c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172"
GEN21_SHA = "e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb"
PROVENANCE = {
    "study_binary": str(BIN),
    "study_binary_sha256": STUDY_SHA,
    "study_binary_version": "perseus-vault 2.23.2 (9c82920)",
    "gen21_measured_sha256_arm64_tarball": GEN21_SHA,
    "identity": "source-identical, NOT byte-identical",
    "build_method": "build.sh with GIT_HASH=9c82920, rust 1.97.1, bookworm, "
                    "DEFAULT features (the Dockerfile lean build is FORBIDDEN "
                    "- keyword-only wearing the version string)",
    "supersede_direction": "from_key = OLD (parameters authoritative)",
}
PRIVATE = Path("/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260911-p1b")
AGENT_BASE = Path("/var/home/bmosher/.pi-experiment-p1")
PERSEUS_EXT = ROOT / "extensions/pi-perseus-recall"
ADAPTER_TS = PERSEUS_EXT / "index.ts"
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
    db, key = root / "vault.sqlite", root / "vault.key"
    sh([BIN, "keygen", "--key-file", key])
    for k, body in (("record-old", OLD_REC), ("record-new", NEW_REC)):
        sh([BIN, "write", "--db", db, "--encryption-key", key,
            "--category", "decision", "--key", k,
            "--body", json.dumps(body, sort_keys=True, separators=(",", ":")),
            "--workspace-hash", WS])
    if supersede:
        proc = subprocess.Popen([str(BIN), "serve", "--db", str(db),
                                 "--encryption-key", str(key)],
                                text=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                bufsize=1)
        try:
            def rpc(method, params):
                rpc.i = getattr(rpc, "i", 0) + 1
                proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rpc.i,
                                             "method": method, "params": params}) + "\n")
                proc.stdin.flush()
                return json.loads(proc.stdout.readline())["result"]
            rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "p1b-seed", "version": "0"}})
            rpc("tools/call", {"name": "perseus_vault_supersede", "arguments": {
                "from_category": "decision", "from_key": "record-old",
                "to_category": "decision", "to_key": "record-new",
                "relationship": "supersedes",
                "reason": "P1B re-smoke: new replaces old"}})
        finally:
            proc.terminate(); proc.wait(timeout=10)
    return db


def vault_recall_keys(db: Path) -> list:
    """Direct vault recall (no agent): which record keys come back."""
    proc = subprocess.Popen([str(BIN), "serve", "--db", str(db),
                             "--encryption-key", str(db.parent / "vault.key")],
                            text=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1)
    try:
        def rpc(method, params):
            rpc.i = getattr(rpc, "i", 0) + 1
            proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rpc.i,
                                         "method": method, "params": params}) + "\n")
            proc.stdin.flush()
            return json.loads(proc.stdout.readline())["result"]
        rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "p1b-toggle", "version": "0"}})
        result = rpc("tools/call", {"name": "perseus_vault_recall",
                                    "arguments": {"query": "staging deploy process",
                                                  "limit": 5, "mode": "hybrid",
                                                  "workspace_hash": WS}})
        payload = result.get("structuredContent") if isinstance(result, dict) else None
        if payload is None and isinstance(result, dict):
            try:
                payload = json.loads(result["content"][0]["text"])
            except Exception:
                payload = {}
        items = payload.get("items", []) if isinstance(payload, dict) else []
        return sorted(str(i.get("key")) for i in items if i.get("key"))
    finally:
        proc.terminate(); proc.wait(timeout=10)


def agent_dir(vault_db: Path) -> Path:
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
    out = PRIVATE / "phase0b-smoke"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    binary_sha = hashlib.sha256(BIN.read_bytes()).hexdigest()
    assert binary_sha == STUDY_SHA, f"binary sha drift: {binary_sha}"
    adapter_sha = hashlib.sha256(ADAPTER_TS.read_bytes()).hexdigest()

    # item 2: toggle pair (direct vault RPC, deterministic)
    db_off = seed_vault(out / "vault-off", supersede=False)
    db_on = seed_vault(out / "vault-on", supersede=True)
    keys_off, keys_on = vault_recall_keys(db_off), vault_recall_keys(db_on)
    toggle_ok = (keys_off == ["record-new", "record-old"]
                 and keys_on == ["record-new"])
    (out / "phase0b_toggle.txt").write_text(
        f"OFF ({db_off}): {keys_off}\nON  ({db_on}): {keys_on}\n"
        f"toggle_ok: {toggle_ok}\n")

    # items 1+3+4: real-path run against the supersede-ON vault
    ad = agent_dir(db_on)
    rb.agent_dir = lambda arm: ad
    src = out / "_src"
    src.mkdir()
    for rel, content in r2.SMOKE_FILES.items():
        f = src / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    worktree = out / "repo"
    r2.reset_worktree(src, worktree)
    store_dir = out / "lcm"
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
    registered = ("pi-perseus-recall: registered project_recall" in stderr
                  and "pi-recall-nudge: registered" in stderr)

    # item 3 (stream level — insufficient alone, retained)
    new_surfaced_stream = "P1-NEW-9" in stdout and "helm" in stdout
    old_absent_stream = "P1-OLD-1" not in stdout

    # item 4 (DELIVERED level — the gate)
    delivery = parse_delivery(stdout)
    delivered_union = "\n---\n".join(delivery["delivered"].values())
    gate = gate_slot("C", stdout)  # supersede-ON vault == arm-C-shaped recall
    new_delivered = "P1-NEW-9" in delivered_union and "helm" in delivered_union
    old_delivered_absent = "P1-OLD-1" not in delivered_union
    final_answer = rb.final_answer_text(stdout)
    final_mentions = "P1-NEW-9" in final_answer and "helm" in final_answer

    lines = [
        "STUDY-20260911-P1B PHASE-0-STYLE RE-SMOKE (delivered-level gate)",
        f"binary sha256: {binary_sha} (asserted)",
        f"adapter index.ts sha256: {adapter_sha} (return-shape fix applied)",
        f"provenance: {json.dumps(PROVENANCE)}",
        "",
        f"[1] adapter as Pi recall path: registered={registered} | "
        f"pi-lcm ACTIVE: prime {prime['status']} {prime['wall_seconds']}s, "
        f"task {task['status']} {task['wall_seconds']}s, "
        f"store dbs: {len(list(store_dir.glob('*.db')))} | "
        f"project_recall calls: {recall_calls} | "
        f"genuine resume: reason={nud['resume_reason']!r} injected={nud['injected']}",
        f"[2] supersession toggle (direct vault RPC): OFF={keys_off} ON={keys_on} "
        f"-> {'OK' if toggle_ok else 'FAIL'} (receipt phase0b_toggle.txt)",
        f"[3] stream-level retrieval (insufficient alone): current (P1-NEW-9+helm) "
        f"in stream={new_surfaced_stream} | old (P1-OLD-1) absent from stream={old_absent_stream}",
        f"[4] DELIVERED-LEVEL GATE: exec={gate['recall_exec']} "
        f"delivered_nonempty={gate['recall_delivered_nonempty']} "
        f"keys_delivered={gate['keys_delivered']} | G1 parity={gate['g1_parity']} "
        f"({json.dumps(gate['g1_detail'])}) | current record in DELIVERED "
        f"toolResult={new_delivered} | old record absent from DELIVERED "
        f"text={old_delivered_absent}",
        f"    evidence (not gated): final answer mentions current record "
        f"(P1-NEW-9+helm)={final_mentions}",
        f"    final answer: {final_answer[:300]!r}",
    ]
    verdict = (registered and recall_calls >= 1 and toggle_ok
               and new_surfaced_stream and old_absent_stream
               and nud["injected"] and nud["resume_reason"] == "resume"
               and gate["gate_ok"] and gate["recall_exec"] >= 1
               and new_delivered and old_delivered_absent)
    lines += ["", "PHASE0B RE-SMOKE RECEIPT: PASS" if verdict
              else "PHASE0B RE-SMOKE RECEIPT: FAIL"]
    (out / "PHASE0B_RECEIPT.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
