#!/usr/bin/env python3
"""team_sync: single-source the fleet's canonical team files (Kiln RETRO-S1).

The fleet's record lives canonically in the shared team/ directory; some
lanes keep committed mirrors. Hand-copying those mirrors is how the
decision log got clobbered once already (d70007f). This tool makes the
mirror path mechanical and receipted:

    team_sync.py check            # sha256 table: MATCH / DRIFT / LANE-MISSING / ROOT-MISSING
    team_sync.py pull             # copy canonical -> lane for every drift/missing, with receipt

Direction is ONE-WAY (canonical root -> lane). This tool never writes to
the shared team/ directory. The mirrored file list lives in
repo/team/MIRRORS.txt next to the mirrors (one filename per line, '#'
comments allowed) so the convention is explicit and auditable.

Every pull appends one JSON line to repo/team/sync-receipt.log:
{"ts", "action", "file", "root_sha", "lane_sha_before", "lane_sha_after"}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

LANE = Path(__file__).resolve().parents[1] / "team"
ROOT = Path(__file__).resolve().parents[3] / "team"
MANIFEST = LANE / "MIRRORS.txt"
RECEIPT_LOG = LANE / "sync-receipt.log"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mirror_names(manifest: Path) -> list[str]:
    names = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.append(line)
    return names


def check(root: Path, lane: Path, names: list[str]) -> list[dict]:
    rows = []
    for name in names:
        r, l = root / name, lane / name
        if not r.is_file():
            rows.append({"file": name, "status": "ROOT-MISSING"})
        elif not l.is_file():
            rows.append({"file": name, "status": "LANE-MISSING", "root_sha": sha256(r)})
        elif sha256(r) == sha256(l):
            rows.append({"file": name, "status": "MATCH", "sha": sha256(r)})
        else:
            rows.append({"file": name, "status": "DRIFT", "root_sha": sha256(r), "lane_sha": sha256(l)})
    return rows


def pull(root: Path, lane: Path, names: list[str], receipt_log: Path) -> list[dict]:
    pulled = []
    for row in check(root, lane, names):
        if row["status"] not in ("DRIFT", "LANE-MISSING"):
            continue
        name = row["file"]
        source, target = root / name, lane / name
        before = sha256(target) if target.is_file() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        after = sha256(target)
        pulled.append(row | {"lane_sha_after": after})
        receipt = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": "pull",
            "file": name,
            "root_sha": row["root_sha"],
            "lane_sha_before": before,
            "lane_sha_after": after,
        }
        with receipt_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(receipt, sort_keys=True) + "\n")
    return pulled


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["check", "pull"])
    parser.add_argument("--root", type=Path, default=ROOT, help="canonical team/ dir (override for tests)")
    parser.add_argument("--lane", type=Path, default=LANE, help="lane mirror dir (override for tests)")
    parser.add_argument("--manifest", type=Path, default=MANIFEST, help="mirror manifest (override for tests)")
    parser.add_argument("--receipt-log", type=Path, default=RECEIPT_LOG, help="pull receipt log (override for tests)")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"missing mirror manifest: {args.manifest}", file=sys.stderr)
        return 2
    names = mirror_names(args.manifest)
    if args.command == "check":
        rows = check(args.root, args.lane, names)
        for row in rows:
            print(f"{row['status']:<13} {row['file']}")
        drifted = [r for r in rows if r["status"] != "MATCH"]
        print(f"{len(rows) - len(drifted)}/{len(rows)} MATCH")
        return 1 if drifted else 0

    pulled = pull(args.root, args.lane, names, args.receipt_log)
    if not pulled:
        print("nothing to pull: all mirrors MATCH")
        return 0
    for row in pulled:
        print(f"pulled {row['file']} ({row['status']} -> {row['lane_sha_after'][:12]})")
    print(f"{len(pulled)} mirror(s) updated; receipt appended to {args.receipt_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
