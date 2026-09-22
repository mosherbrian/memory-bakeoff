"""Executable L2 preparation (repair-2): verify every claimed binding against
an authoritative launcher source before emitting evidence. Read-only.

Authority (inspected read-only on the live host):
- `agent-deck list --json` -> [{id, title, path, tool, ...}] (session source)
- ~/.config/agent-deck/acp-sock/<session-id>.sock (live worker incarnation)
- ~/.config/agent-deck/acp-stream/<session-id>.jsonl (runtime stream root,
  actual-format {t, item, ...} records)

Checks, all fail-closed before any wake:
- session/stream keys must resolve in the launcher session list
  (E_UNKNOWN_SESSION otherwise; caller values are never certified merely
  because a directory exists).
- the session's worker socket must exist (E_NO_SOCKET otherwise); its mtime
  is recorded as incarnation evidence. Distinct incarnations bind explicitly.
- worker/verifier stream keys must exist as files in the producer root
  (E_UNBOUND otherwise). Unrelated valid streams do NOT satisfy this:
  invented identifiers are rejected even when the directory is non-empty.
- an idle genuine runtime need not have emitted an end yet: only file/binding
  presence is required, never an end record.

Fixture/injected runs pass --session-list-file (sanitized real-schema
fixture) and --sock-dir explicitly; evidence records launcher_source as
"fixture-injected" so shim-created identities can never substitute for the
declared live launcher path at Stage C. Never creates, truncates, or
fabricates streams."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import discover_runtime
from host_adapter import OwnedFault

LIVE_SOCK_DIR = os.path.expanduser("~/.config/agent-deck/acp-sock")
LIVE_STREAM_ROOT = os.path.expanduser("~/.config/agent-deck/acp-stream")


def _load_sessions(args):
    if args.session_list_file:
        try:
            data = json.load(open(args.session_list_file))
        except (OSError, ValueError):
            raise OwnedFault("E_UNBOUND",
                             "session list fixture unreadable: "
                             + args.session_list_file)
        return data, "fixture-injected:" + args.session_list_file
    cmd = (args.session_list_cmd or "agent-deck list --json").split()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=30)
    except (OSError, subprocess.SubprocessError):
        raise OwnedFault("E_UNBOUND", "launcher session list unavailable")
    if proc.returncode != 0:
        raise OwnedFault("E_UNBOUND", "launcher session list failed")
    try:
        return json.loads(proc.stdout or "[]"), "live-agent-deck"
    except ValueError:
        raise OwnedFault("E_UNBOUND", "launcher session list malformed")


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r5 L2 evidence preparation")
    ap.add_argument("--producer-root", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--stream-key", required=True)
    ap.add_argument("--worker-stream-key", required=True)
    ap.add_argument("--verifier-stream-key", required=True)
    ap.add_argument("--sock-dir", default=LIVE_SOCK_DIR)
    ap.add_argument("--session-list-file", default="")
    ap.add_argument("--session-list-cmd", default="agent-deck list --json")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    sessions, source = _load_sessions(args)
    ids = {s.get("id") for s in sessions if isinstance(s, dict)}
    for key, label in ((args.session, "session"),
                       (args.stream_key, "stream-key"),
                       (args.worker_stream_key, "worker-stream-key"),
                       (args.verifier_stream_key, "verifier-stream-key")):
        if key not in ids:
            raise OwnedFault("E_UNKNOWN_SESSION",
                             "%s %r not in launcher source (%s)"
                             % (label, key, source))
    sock_path = os.path.join(args.sock_dir, args.session + ".sock")
    if not os.path.exists(sock_path):
        raise OwnedFault("E_NO_SOCKET",
                         "no worker socket for session %r in %s"
                         % (args.session, args.sock_dir))
    try:
        incarnation_mtime = os.stat(sock_path).st_mtime
    except OSError:
        raise OwnedFault("E_NO_SOCKET",
                         "worker socket unreadable for " + args.session)
    disc = discover_runtime(args.producer_root)
    for key, label in ((args.worker_stream_key, "worker-stream-key"),
                       (args.verifier_stream_key, "verifier-stream-key")):
        if key not in disc["streams"]:
            raise OwnedFault("E_UNBOUND",
                             "%s %r has no stream file under %s "
                             "(unrelated streams do not bind)"
                             % (label, key, args.producer_root))
    evidence = {"session": args.session, "stream_key": args.stream_key,
                "worker_stream_key": args.worker_stream_key,
                "verifier_stream_key": args.verifier_stream_key,
                "producer_root": disc["producer_root"],
                "observed_streams": sorted(disc["streams"].keys()),
                "launcher_source": source,
                "worker_socket": sock_path,
                "incarnation_mtime": incarnation_mtime}
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
