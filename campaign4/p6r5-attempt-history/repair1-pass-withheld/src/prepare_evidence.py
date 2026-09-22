"""Executable L2 preparation: read-only discovery of the producer root,
then emit launcher evidence JSON {session, stream_key, worker_stream_key,
verifier_stream_key, producer_root}. Never creates, truncates, or fabricates
streams; fails closed (E_UNBOUND) when the producer root is absent. Isolated
fixture seats obtain bindings from this output, passed explicitly to setup."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import discover_runtime
from host_adapter import OwnedFault


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r5 L2 evidence preparation")
    ap.add_argument("--producer-root", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--stream-key", required=True)
    ap.add_argument("--worker-stream-key", required=True)
    ap.add_argument("--verifier-stream-key", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    disc = discover_runtime(args.producer_root)
    evidence = {"session": args.session, "stream_key": args.stream_key,
                "worker_stream_key": args.worker_stream_key,
                "verifier_stream_key": args.verifier_stream_key,
                "producer_root": disc["producer_root"],
                "observed_streams": sorted(disc["streams"].keys())}
    text = json.dumps(evidence, sort_keys=True)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OwnedFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": e.owner}, sort_keys=True))
        raise SystemExit(3)
