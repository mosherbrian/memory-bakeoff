#!/usr/bin/env python3
"""STUDY-20260911-P1B rerun harness (conductor-dispatched 2026-09-11).

Reruns the P1 walk against the SAME frozen scientific content (cases,
verifiers, schedule, decision rules — freeze commit 4048e12) after the
pi-perseus-recall return-shape fix (STUDY-20260911-P1 root cause 1: bare
string returns were recorded in the execution stream but delivered to the
model as an EMPTY toolResult). Private evidence, run trees and stores go
to a fresh directory (tag p1b); frozen files under scripts/
experiment_20260911_p1/ are NOT modified (decide_p1.py gains only an
env-var path override, logic untouched).

DELIVERED-LEVEL GATE (the conductor's requirement — stream-level
assertions are insufficient; the p1 defect passed them): for every slot,
parsing the session transcript stdout.txt,

  G1 parity   — every `tool_execution_end` for project_recall must have a
                matching DELIVERED `message` with role=toolResult (same
                toolCallId) whose model-visible text is non-empty and
                contains every `record-*` key present in the execution-
                stream result;
  G2 arm A    — zero project_recall executions (no recall tool configured);
  G3 arm B/C  — at least one `record-*` key present in DELIVERED toolResult
                text during the slot.

A gate failure ABORTS the walk immediately (stop-and-report; a delivery
defect invalidates behavioral data — it must not silently become results).

Commands:
  setup    p1b prep manifest: binary sha assert, adapter sha receipt,
           per-case hashes COMPARED against the p1 PREP_MANIFEST (frozen
           case identity), schedule sha
  smoke    run phase0b_smoke (phase-0-style re-smoke incl. delivered gate)
  slot C R / walk   as run_p1, plus the per-slot delivery gate
  analyze  ledger + delivery join
"""
from __future__ import annotations

import hashlib, json, os, re, shutil, sys, time
from pathlib import Path

P1B_PRIVATE_DEFAULT = ("/var/home/bmosher/.local/share/memory-bakeoff/"
                       "experiment-20260911-p1b")
if "EXPERIMENT_P1_PRIVATE" not in os.environ:
    os.environ["EXPERIMENT_P1_PRIVATE"] = P1B_PRIVATE_DEFAULT

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "scripts", ROOT / "scripts/experiment_20260910b",
          ROOT / "scripts/experiment_20260911_p1"):
    sys.path.insert(0, str(p))
import run_p1 as p1  # noqa: E402  (reads EXPERIMENT_P1_PRIVATE at import)

P1_MANIFEST = Path("/var/home/bmosher/.local/share/memory-bakeoff/"
                   "experiment-20260911-p1/PREP_MANIFEST.json")
KEY_RE = re.compile(r"record-[a-z0-9\-]+")
ADAPTER_TS = ROOT / "extensions/pi-perseus-recall/index.ts"


# ── delivered-level transcript parsing (shared with phase0b_smoke) ──────────

def _result_text(result) -> str:
    """Normalize an execution-stream tool result: the adapter's old shape was
    a flat string; the fixed shape is {content:[{type:'text',text}]}."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        cont = result.get("content")
        if isinstance(cont, list):
            return "\n".join(c.get("text", "") for c in cont
                             if isinstance(c, dict) and c.get("type") == "text")
    return json.dumps(result) if result else ""


def parse_delivery(stdout_text: str) -> dict:
    """Split project_recall evidence into execution-stream vs DELIVERED
    (model-visible toolResult message) sides, matched by toolCallId."""
    exec_recall: dict[str, dict] = {}
    delivered: dict[str, str] = {}
    for line in stdout_text.splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("type") == "tool_execution_end" and e.get("toolName") == "project_recall":
            result = _result_text(e.get("result"))
            exec_recall[e.get("toolCallId")] = {
                "result_len": len(result),
                "keys": sorted(set(KEY_RE.findall(result))),
                "text": result,
            }
        elif e.get("type") in ("message_start", "message_end"):
            m = e.get("message", {})
            if m.get("role") != "toolResult":
                continue
            tcid = m.get("toolCallId")
            cont = m.get("content")
            text = ""
            if isinstance(cont, list):
                for c in cont:
                    if isinstance(c, dict):
                        tcid = tcid or c.get("toolCallId")
                        if c.get("type") == "text":
                            text += c.get("text", "") + "\n"
            elif isinstance(cont, str):
                text = cont
            if tcid is None:
                continue
            if e["type"] == "message_end" or tcid not in delivered:
                # message_end carries final content; keep the richest copy
                delivered[tcid] = text if e["type"] == "message_end" \
                    else max(delivered.get(tcid, ""), text, key=len)
    return {"exec": exec_recall, "delivered": delivered}


def gate_slot(arm: str, stdout_text: str) -> dict:
    d = parse_delivery(stdout_text)
    exec_ids = set(d["exec"])
    delivered_ids = {k for k, v in d["delivered"].items() if v.strip()}
    parity_detail, parity_ok = [], True
    for tcid, ex in sorted(d["exec"].items()):
        got = d["delivered"].get(tcid, "")
        missing = [k for k in ex["keys"] if k not in got]
        ok = bool(got.strip()) and not missing
        parity_ok &= ok
        parity_detail.append({"toolCallId": (tcid or "")[:8],
                              "exec_keys": ex["keys"], "delivered_len": len(got),
                              "missing_in_delivered": missing, "ok": ok})
    delivered_keys = sorted({k for v in d["delivered"].values() for k in KEY_RE.findall(v)})
    g1 = parity_ok
    g2 = (arm != "A") or (len(exec_ids) == 0)
    g3 = (arm == "A") or (len(delivered_keys) > 0)
    return {"arm": arm, "recall_exec": len(exec_ids),
            "recall_delivered_nonempty": len(exec_ids & delivered_ids),
            "keys_delivered": delivered_keys, "g1_parity": g1,
            "g1_detail": parity_detail, "g2_armA_no_recall": g2,
            "g3_BC_records_delivered": g3, "gate_ok": g1 and g2 and g3}


# ── commands ────────────────────────────────────────────────────────────────

def cmd_setup(args) -> None:
    cases = p1.load_cases()
    p1.PRIVATE.mkdir(parents=True, exist_ok=True)
    adapter_sha = hashlib.sha256(ADAPTER_TS.read_bytes()).hexdigest()
    manifest = {
        "tag": "p1b",
        "prepared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance": p1.PROVENANCE,
        "binary_sha_check": hashlib.sha256(p1.BIN.read_bytes()).hexdigest(),
        "adapter_index_ts_sha256": adapter_sha,
        "adapter_fix": "execute() returns {content:[{type:'text',text}]} "
                       "(STUDY-20260911-P1 root cause 1)",
        "cases": {cid: {
            "kind": c["kind"],
            "case_json": p1.r2.sha256_file(c["dir"] / "case.json"),
            "records_json": p1.r2.sha256_file(c["dir"] / "records.json"),
            "verifier_py": p1.r2.sha256_file(c["verifier"]),
        } for cid, c in cases.items()},
        "schedule_sha256": p1.r2.sha256_file(p1.SCHEDULE_PATH),
        "delivery_gate": {"G1": "exec->delivered parity per toolCallId",
                          "G2": "arm A: zero project_recall executions",
                          "G3": "arm B/C: >=1 record key in delivered text"},
    }
    assert manifest["binary_sha_check"] == p1.PROVENANCE["study_binary_sha256"]
    # frozen-case identity vs the p1 prep manifest (freeze 4048e12 content)
    old = json.loads(P1_MANIFEST.read_text())
    drift = []
    for cid, hashes in manifest["cases"].items():
        oc = old["cases"].get(cid, {})
        for k in ("case_json", "records_json", "verifier_py"):
            if hashes[k] != oc.get(k):
                drift.append(f"{cid}.{k}: p1={oc.get(k)} p1b={hashes[k]}")
    if drift:
        raise SystemExit(f"FROZEN-CASE DRIFT vs p1 manifest:\n" + "\n".join(drift))
    manifest["frozen_case_identity_vs_p1"] = "VERIFIED (hashes identical)"
    (p1.PRIVATE / "PREP_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"p1b prep manifest: {p1.PRIVATE / 'PREP_MANIFEST.json'}")
    print(f"adapter index.ts sha256: {adapter_sha}")
    print(f"private dir: {p1.PRIVATE}")


def run_slot_with_gate(cid: str, arm: str, rep: int) -> dict:
    row = p1.do_slot(p1.load_cases()[cid], cid, arm, rep)
    stdout = (p1.RUNS / row["run"] / "stdout.txt").read_text(errors="replace")
    gate = gate_slot(arm, stdout)
    rec = {"run": row["run"], "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           **gate}
    with (p1.PRIVATE / "delivery.jsonl").open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in
                      ("run", "recall_exec", "recall_delivered_nonempty",
                       "keys_delivered", "gate_ok")}))
    if not gate["gate_ok"]:
        print("\nDELIVERY GATE FAILURE — walk aborted (stop-and-report):")
        print(json.dumps(gate, indent=1))
        raise SystemExit(2)
    return rec


def cmd_slot(args) -> None:
    run_slot_with_gate(args.case, args.arm, args.rep)


def cmd_walk(args) -> None:
    cases = p1.load_cases()
    for b in json.loads(p1.SCHEDULE_PATH.read_text()):
        for arm in b["order"]:
            run_slot_with_gate(b["case"], arm, b["rep"])


def cmd_analyze(args) -> None:
    rows = [json.loads(l) for l in (p1.PRIVATE / "ledger.jsonl").read_text().splitlines() if l.strip()]
    gates = {r["run"]: r for r in
             (json.loads(l) for l in (p1.PRIVATE / "delivery.jsonl").read_text().splitlines() if l.strip())}
    for r in rows:
        g = gates.get(r["run"], {})
        print(json.dumps({k: r.get(k) for k in ("run", "verifier", "recall_calls",
                                                "vault_isolation_ok", "supersession")}))
        print(f"  gate: {json.dumps({k: g.get(k) for k in ('gate_ok', 'recall_exec', 'recall_delivered_nonempty', 'keys_delivered')})}")
    print(f"total slots: {len(rows)} | gates ok: {sum(1 for g in gates.values() if g.get('gate_ok'))}/{len(gates)}")


def cmd_smoke(args) -> None:
    import phase0b_smoke
    phase0b_smoke.main()


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    sub.add_parser("smoke")
    p = sub.add_parser("slot"); p.add_argument("case"); p.add_argument("arm", choices=["A", "B", "C"])
    p.add_argument("rep", type=int, choices=[1, 2])
    sub.add_parser("walk")
    sub.add_parser("analyze")
    args = ap.parse_args()
    {"setup": cmd_setup, "smoke": cmd_smoke, "slot": cmd_slot,
     "walk": cmd_walk, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
