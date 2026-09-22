"""P6-r6 live cleanup tool. Removes ONLY the owned exact session IDs recorded
in a live launch manifest, after archiving receipts: the manifest itself,
the launcher record (`agent-deck session show`-equivalent via list --json),
and any witness rows. Guards: refuses manifests whose launcher_source is
not live-agent-deck (dry-run mode only simulates); refuses any ID matching
a main seat or not titled p6-fixture-*; archive is written and verified
before any stop/remove. Order per seat: session stop, then remove.
--dry-run prints the exact argv sequence without executing (review path).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_live import PrepFault, list_sessions, MAIN_SEATS


def owned_ids(manifest_path):
    man = json.load(open(manifest_path))
    if man.get("launcher_source") != "live-agent-deck":
        raise PrepFault("E_NOT_LIVE",
                        "cleanup owns only live-agent-deck manifests")
    ids = []
    for role in ("worker", "verifier"):
        sid = (man.get(role) or {}).get("session_id")
        if not sid:
            continue  # partial manifest: reconcile present sides only
        if sid in MAIN_SEATS:
            raise PrepFault("E_MAIN_SEAT", "refusing main seat " + sid)
        ids.append(sid)
    if not ids:
        raise PrepFault("E_MANIFEST", "no owned session ids recorded")
    return man, ids


def plan_cleanup(man, ids, sessions):
    by_id = {s.get("id"): s for s in sessions if isinstance(s, dict)}
    steps = []
    for sid in ids:
        rec = by_id.get(sid)
        if rec is None:
            steps.append(("note", "session already gone: " + sid))
            continue
        title = rec.get("title") or ""
        if not title.startswith("p6-fixture-"):
            raise PrepFault("E_NOT_OWNED",
                            "session %r not titled p6-fixture-*" % sid)
        steps.append(("stop", ["agent-deck", "session", "stop", sid]))
        steps.append(("remove", ["agent-deck", "session", "remove", sid]))
    return steps


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r6 live cleanup")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--archive-dir", required=True)
    ap.add_argument("--profile", default="campaign4")
    ap.add_argument("--witness-rows", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--inject-list", default="")
    args = ap.parse_args(argv)
    try:
        man, ids = owned_ids(args.manifest)
    except (OSError, ValueError):
        raise PrepFault("E_MANIFEST", "manifest unreadable")
    sessions, _ = list_sessions(args.profile, args.inject_list)
    steps = plan_cleanup(man, ids, sessions)
    if args.dry_run:
        print(json.dumps({"archive_dir": args.archive_dir, "owned": ids,
                          "steps": [[k, v] for k, v in steps],
                          "executed": False}, sort_keys=True))
        return 0
    os.makedirs(args.archive_dir, exist_ok=True)
    shutil.copy(args.manifest, os.path.join(args.archive_dir,
                                            "launch-manifest.json"))
    with open(os.path.join(args.archive_dir, "launcher-records.json"),
              "w") as fh:
        json.dump([s for s in sessions if s.get("id") in ids], fh,
                  sort_keys=True, indent=1)
    if args.witness_rows and os.path.exists(args.witness_rows):
        shutil.copy(args.witness_rows,
                    os.path.join(args.archive_dir, "witness-rows.jsonl"))
    env = dict(os.environ, AGENTDECK_PROFILE=args.profile)
    ran = []
    for kind, cmd in steps:
        if kind == "note":
            ran.append([kind, cmd])
            continue
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=120, env=env)
        ran.append([kind, cmd, proc.returncode])
        if proc.returncode != 0:
            print(json.dumps({"error": "E_CLEANUP",
                              "detail": "%s %s failed: %s" % (
                                  kind, cmd[-1],
                                  (proc.stderr or "")[:200]),
                              "owner": "cairn",
                              "archive_dir": args.archive_dir,
                              "ran": ran}, sort_keys=True))
            return 3
    print(json.dumps({"cleanup": "done", "owned": ids,
                      "archive_dir": args.archive_dir,
                      "ran": ran}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrepFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
