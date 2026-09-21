"""CLI: apply ledger events, publish snapshots, validate boundaries.

Reads explicitly supplied fixture/store paths only. Emits structured JSON.
Never calls wake/stop/Signal, never creates agents, never writes
campaign state. Subcommands:

  apply      --store DB --event FILE.json [--budget FILE.json]
  snapshot   --store DB --out FILE.json [--extra FILE.json]
  validate   --store DB --snapshot FILE.json --now ISO
             [--triggers-fired FILE.json]
  reproduce  --store DB --script FILE.json --out-dir DIR  (fixture runner)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from src.store import Store  # noqa: E402
from src.validator import validate  # noqa: E402
from src.lifecycle import TransitionError  # noqa: E402


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def cmd_apply(args):
    store = Store(args.store)
    try:
        event = _load(args.event)
        budget = _load(args.budget) if args.budget else None
        outcome, dup = store.append(event, budget)
        print(json.dumps({"ok": True, "outcome": outcome,
                          "duplicate": dup}, sort_keys=True))
    except TransitionError as exc:
        print(json.dumps({"ok": False, "code": exc.code,
                          "detail": exc.detail}, sort_keys=True))
    finally:
        store.close()


def cmd_snapshot(args):
    store = Store(args.store)
    try:
        extra = _load(args.extra) if args.extra else None
        snap = store.publish_snapshot(args.out, extra)
        print(json.dumps({"ok": True, "ledger_revision": store.conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0],
            "snapshot": snap}, sort_keys=True))
    finally:
        store.close()


def cmd_validate(args):
    store = Store(args.store)
    try:
        try:
            snap = _load(args.snapshot)
        except (FileNotFoundError, json.JSONDecodeError):
            snap = None
        fired = set()
        if args.triggers_fired:
            fired = set(_load(args.triggers_fired))
        ledger = {"revision": store.ledger_revision(),
                  "packages": ledger_packages(store)}
        verdict = validate(snap, ledger, args.now, fired)
        print(json.dumps(verdict, sort_keys=True))
    finally:
        store.close()


def ledger_packages(store):
    out = {}
    for q, revs in store.ledger_view().items():
        for rev, rec in revs.items():
            out["%s-r%d" % (q, rev)] = rec
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--store", required=True)
    a.add_argument("--event", required=True)
    a.add_argument("--budget", default=None)
    s = sub.add_parser("snapshot")
    s.add_argument("--store", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--extra", default=None)
    v = sub.add_parser("validate")
    v.add_argument("--store", required=True)
    v.add_argument("--snapshot", required=True)
    v.add_argument("--now", required=True)
    v.add_argument("--triggers-fired", default=None)
    args = ap.parse_args(argv)
    {"apply": cmd_apply, "snapshot": cmd_snapshot,
     "validate": cmd_validate}[args.cmd](args)


if __name__ == "__main__":
    main()
