#!/usr/bin/env python3
"""Arm A prep loader — dead-end guardrail records (DRAFT).

Reads team/dead-end-records.json and emits (or executes) the six
`perseus-vault write` commands. Dry-run by default: nothing touches any vault
unless --execute is passed. The row's deliverable is the draft, not a write.

Usage:
  # show the exact commands (no writes)
  python3 load_dead_end_records.py --db /path/to/arm-a.vault \
      --key-file /path/to/arm-a.vault.key --workspace-hash ws-arm-a

  # actually write (explicit opt-in)
  python3 load_dead_end_records.py ... --execute
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RECORDS = HERE / "dead-end-records.json"
DEFAULT_BIN = "/var/home/bmosher/perseus-build/src/target/release/perseus-vault"


def build_body(rec: dict, defaults: dict) -> str:
    body = {
        "content": rec["content"],
        "dead_end": rec["key"],
        "do_not": rec["do_not"],
        "working_alternative": rec["working_alternative"],
        "evidence_paths": rec["evidence_paths"],
        "status": "confirmed",
        "authored_at": defaults.get("authored_at", "2026-09-12"),
        "kind": "dead-end-guardrail",
    }
    return json.dumps(body, separators=(",", ":"), sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="arm-A vault db path")
    ap.add_argument("--key-file", required=True, help="arm-A vault key file")
    ap.add_argument("--workspace-hash", required=True,
                    help="workspace hash for the arm-A vault")
    ap.add_argument("--agent-id", default="dead-end-guardrails")
    ap.add_argument("--binary", default=DEFAULT_BIN)
    ap.add_argument("--records", default=str(DEFAULT_RECORDS))
    ap.add_argument("--execute", action="store_true",
                    help="actually write; default is dry-run")
    args = ap.parse_args()

    doc = json.loads(Path(args.records).read_text())
    defaults = doc.get("defaults", {})
    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"[{mode}] {len(doc['records'])} records from {args.records}")

    failures = 0
    for rec in doc["records"]:
        cmd = [
            args.binary, "write",
            "--db", args.db,
            "--encryption-key", args.key_file,
            "--category", defaults.get("category", "dead-end"),
            "--key", rec["key"],
            "--body", build_body(rec, defaults),
            "--tags", ",".join(rec["tags"]),
            "--entity-type", defaults.get("entity_type", "observation"),
            "--importance", str(defaults.get("importance", 0.9)),
            "--visibility", defaults.get("visibility", "workspace"),
            "--workspace-hash", args.workspace_hash,
            "--agent-id", args.agent_id,
        ]
        if defaults.get("always_on", True):
            cmd.append("--always-on")
        print("\n$ " + " ".join(cmd))
        if args.execute:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            print(f"  rc={proc.returncode} {proc.stdout.strip()[:200]} "
                  f"{proc.stderr.strip()[:200]}")
            if proc.returncode != 0:
                failures += 1

    if not args.execute:
        print("\nDry-run only. Re-run with --execute to write to the vault.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
