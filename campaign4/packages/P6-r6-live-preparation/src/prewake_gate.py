"""P6-r6 pre-wake gate: rejects before any task wake unless ALL hold:
- manifest launcher_source is live ("live-agent-deck"); fixture-injected or
  dry-run manifests reject (P3);
- Tern's signature file approves THIS plan hash AND THIS manifest hash
  (signer "tern"); missing/changed signature rejects (P4);
- both bindings re-resolve in the launcher list and match recorded session
  IDs, profile, lane; sockets still exist, are real sockets, and match the
  recorded incarnation ino (stale incarnation rejects); stream root matches
  (P2). Identity is never inferred from filename/title alone.

--dry-run with --inject-list/--inject-sock-dir validates the boundary logic
against fixtures (used by candidate review; never a live pass).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_live import (PrepFault, check_record, check_socket_real,
                          list_sessions, MAIN_SEATS)


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def gate(manifest_path, plan_path, sig_path, profile="campaign4",
         inject_list="", inject_sock_dir=""):
    try:
        man = json.load(open(manifest_path))
    except (OSError, ValueError):
        raise PrepFault("E_MANIFEST", "manifest unreadable")
    if man.get("launcher_source") != "live-agent-deck":
        raise PrepFault("E_NOT_LIVE",
                        "launcher_source %r is not live-agent-deck; "
                        "fixture-injected/shim identities rejected"
                        % man.get("launcher_source"))
    try:
        sig = json.load(open(sig_path))
    except (OSError, ValueError):
        raise PrepFault("E_NO_SIGNATURE", "signature file missing/unreadable")
    if sig.get("signer") != "tern":
        raise PrepFault("E_NO_SIGNATURE", "signer is not tern")
    if sig.get("plan_sha256") != _sha(plan_path):
        raise PrepFault("E_PLAN_CHANGED", "plan hash not Tern-signed")
    if sig.get("manifest_sha256") != _sha(manifest_path):
        raise PrepFault("E_BINDING_CHANGED", "manifest hash not Tern-signed")
    sessions, _ = list_sessions(profile, inject_list)
    by_id = {s.get("id"): s for s in sessions if isinstance(s, dict)}
    sock_dir = inject_sock_dir or os.path.expanduser(
        "~/.config/agent-deck/acp-sock")
    for role in ("worker", "verifier"):
        side = man.get(role) or {}
        sid = side.get("session_id")
        rec = by_id.get(sid)
        if rec is None:
            raise PrepFault("E_GONE",
                            "%s session %r not in launcher list" % (role,
                                                                    sid))
        if (rec.get("title") or "") in MAIN_SEATS or sid in MAIN_SEATS:
            raise PrepFault("E_MAIN_SEAT", "main seat adopted?!")
        check_record(rec, rec.get("title") or sid,
                     side.get("role_lane"), profile)
        sock = os.path.join(sock_dir, sid + ".sock")
        try:
            st = os.stat(sock)
        except OSError:
            raise PrepFault("E_NO_SOCKET", "socket gone for " + sid)
        if not stat.S_ISSOCK(st.st_mode):
            raise PrepFault("E_FAKE_SOCKET", "socket not real for " + sid)
        want_ino = (side.get("incarnation") or {}).get("ino")
        if want_ino is not None and st.st_ino != want_ino:
            raise PrepFault("E_STALE", "socket incarnation changed for "
                            + sid)
        if os.path.dirname(side.get("stream_path", "")) != \
                side.get("producer_root"):
            raise PrepFault("E_MISMATCH", "stream/root mismatch for " + sid)
    return {"gate": "PASS", "worker": man["worker"]["session_id"],
            "verifier": man["verifier"]["session_id"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r6 pre-wake gate")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--signatures", required=True)
    ap.add_argument("--profile", default="campaign4")
    ap.add_argument("--inject-list", default="")
    ap.add_argument("--inject-sock-dir", default="")
    args = ap.parse_args(argv)
    print(json.dumps(gate(args.manifest, args.plan, args.signatures,
                          args.profile, args.inject_list,
                          args.inject_sock_dir), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrepFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
