"""P6-r6 live preparation tool (candidate grant: author only; execution needs
Tern's separately signed preparation release and is NOT authorized here).

Live mode creates/starts exactly two NEW idle sessions in the campaign4
profile via `agent-deck launch` with NO -message (supported idle mode,
verified read-only from `launch --help`), worker on the inventoried acp-go
lane and verifier on acp-go-deepseek, with isolated working directories and
no task dispatch. It records real session IDs, profile, role, launch
command, producer root, stream paths and Unix socket identity/incarnation
for BOTH into a launch manifest with launcher_source "live-agent-deck".

Refusals (fail closed, before any creation where possible): name collision
with any existing session (never adopt unrelated sessions); main-four seats
never touched (explicit guard); lane missing/not executable; launched record
profile/command mismatch; socket missing or not a real socket (regular-file
fakes rejected via S_ISSOCK); stream root mismatch.

--dry-run runs every check against injected directories/files and writes a
manifest labeled "dry-run-injected" (never live). No live effect in dry-run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import time

MAIN_SEATS = ("tern", "corvid", "kiln", "cairn")
LIVE_SOCK_DIR = os.path.expanduser("~/.config/agent-deck/acp-sock")
LIVE_STREAM_ROOT = os.path.expanduser("~/.config/agent-deck/acp-stream")
WORKER_LANE = "/home/bmosher/.config/agent-deck/acp-go"
VERIFIER_LANE = "/home/bmosher/.config/agent-deck/acp-go-deepseek"


class PrepFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _run(cmd, timeout=60):
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout)
    return proc


def list_sessions(profile, inject_file=""):
    if inject_file:
        return json.load(open(inject_file)), "dry-run-injected"
    env = dict(os.environ, AGENTDECK_PROFILE=profile)
    proc = subprocess.run(["agent-deck", "list", "--json"],
                          capture_output=True, text=True, timeout=60,
                          env=env)
    if proc.returncode != 0:
        raise PrepFault("E_LAUNCHER", "session list failed: "
                        + (proc.stderr or "")[:200])
    try:
        return json.loads(proc.stdout or "[]"), "live-agent-deck"
    except ValueError:
        raise PrepFault("E_LAUNCHER", "session list malformed")


def check_no_collision(sessions, names):
    titles = {s.get("title") for s in sessions if isinstance(s, dict)}
    ids = {s.get("id") for s in sessions if isinstance(s, dict)}
    for n in names:
        if n in titles or n in ids:
            raise PrepFault("E_COLLISION",
                            "name %r already exists; refusing to adopt" % n)


def check_socket_real(sock_path):
    try:
        st = os.stat(sock_path)
    except OSError:
        raise PrepFault("E_NO_SOCKET", "no socket at " + sock_path)
    if not stat.S_ISSOCK(st.st_mode):
        raise PrepFault("E_FAKE_SOCKET",
                        "not a Unix socket (regular-file fakes rejected): "
                        + sock_path)
    return {"mtime": st.st_mtime, "ino": st.st_ino}


def check_record(record, name, lane, profile):
    if record.get("profile", "campaign4") != profile:
        raise PrepFault("E_WRONG_PROFILE",
                        "session %r profile %r" % (name, record.get(
                            "profile")))
    if record.get("command") not in (lane,):
        raise PrepFault("E_WRONG_ROLE",
                        "session %r command %r is not lane %r"
                        % (name, record.get("command"), lane))
    return True


def launch_idle(path, name, lane, profile, idle_timeout, workdir,
                runner=None):
    """Repair-1: idle-timeout binds parser-safe as ONE --flag=value token.
    The installed CLI's reorder pass has no separate-value entry for
    idle-timeout, so `-idle-timeout 25m` demotes `25m` to positional and
    binds the following flag (`-json`) as the value. The `=` form is never
    split by either normalization pass (verified parser-only against the
    installed binary). No -message: idle by construction."""
    os.makedirs(workdir, exist_ok=True)
    env = dict(os.environ, AGENTDECK_PROFILE=profile)
    cmd = ["agent-deck", "launch", path, "-t", name, "-cmd", lane,
           "--idle-timeout=%s" % idle_timeout, "-json", "-q"]
    run = runner or subprocess.run
    proc = run(cmd, capture_output=True, text=True, timeout=180,
               env=env, cwd=workdir)
    if proc.returncode != 0:
        raise PrepFault("E_LAUNCH",
                        "launch %r failed: %s" % (name, (proc.stderr or
                                                         proc.stdout or "")
                                                  [:300]))
    try:
        out = json.loads(proc.stdout or "{}")
    except ValueError:
        raise PrepFault("E_LAUNCH", "launch output malformed for " + name)
    if not isinstance(out, dict) or not out.get("id"):
        raise PrepFault("E_LAUNCH_NO_ID",
                        "launch %r returned no session id; refusing "
                        "title-only fallback here" % name)
    return out


def build_manifest(plan_sha, profile, worker, verifier, source):
    return {"plan_sha256": plan_sha, "launcher_source": source,
            "profile": profile, "worker": worker, "verifier": verifier,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                        time.gmtime())}


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r6 live preparation")
    ap.add_argument("--profile", default="campaign4")
    ap.add_argument("--worker-name", default="p6-fixture-worker")
    ap.add_argument("--verifier-name", default="p6-fixture-verifier")
    ap.add_argument("--worker-lane", default=WORKER_LANE)
    ap.add_argument("--verifier-lane", default=VERIFIER_LANE)
    ap.add_argument("--workdir-base", default="/tmp/p6live")
    ap.add_argument("--idle-timeout", default="25m")
    ap.add_argument("--plan", default="")
    ap.add_argument("--manifest-out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--inject-list", default="")
    ap.add_argument("--inject-sock-dir", default="")
    ap.add_argument("--inject-stream-root", default="")
    args = ap.parse_args(argv)
    for n in (args.worker_name, args.verifier_name):
        if n in MAIN_SEATS:
            raise PrepFault("E_MAIN_SEAT",
                            "refusing to repurpose main seat " + n)
        if not n.startswith("p6-fixture-"):
            raise PrepFault("E_NAME",
                            "fixture names must be p6-fixture-*: " + n)
    for lane in (args.worker_lane, args.verifier_lane):
        if not (os.path.isfile(lane) and os.access(lane, os.X_OK)):
            raise PrepFault("E_LANE", "lane not executable: " + lane)
    sessions, live_source = list_sessions(args.profile, args.inject_list)
    if not args.dry_run:
        check_no_collision(sessions, (args.worker_name, args.verifier_name))
    if args.dry_run:
        source = "dry-run-injected"
        sock_dir = args.inject_sock_dir or LIVE_SOCK_DIR
        stream_root = args.inject_stream_root or LIVE_STREAM_ROOT
        sides = {}
        for role, name, lane in (("worker", args.worker_name,
                                  args.worker_lane),
                                 ("verifier", args.verifier_name,
                                  args.verifier_lane)):
            matches = [s for s in sessions
                       if isinstance(s, dict) and (s.get("id") == name or
                                                   s.get("title") == name)]
            if len(matches) != 1:
                raise PrepFault("E_COLLISION" if len(matches) > 1
                                else "E_DRY_RUN",
                                "injected list must hold exactly one "
                                "record for " + name)
            rec = matches[0]
            check_record(rec, name, lane, args.profile)
            ident = check_socket_real(os.path.join(sock_dir, rec["id"]
                                                   + ".sock"))
            stream = os.path.join(stream_root, rec["id"] + ".jsonl")
            sides[role] = {"session_id": rec["id"], "title": name,
                           "profile": args.profile, "role_lane": lane,
                           "launch_command": rec.get("command"),
                           "producer_root": stream_root,
                           "stream_path": stream,
                           "stream_exists": os.path.exists(stream),
                           "socket": os.path.join(sock_dir, rec["id"]
                                                  + ".sock"),
                           "incarnation": ident}
        plan_sha = (hashlib.sha256(open(args.plan, "rb").read())
                    .hexdigest() if args.plan else "dry-run-no-plan")
        man = build_manifest(plan_sha, args.profile, sides["worker"],
                             sides["verifier"], source)
        with open(args.manifest_out, "w") as fh:
            json.dump(man, fh, sort_keys=True, indent=1)
        print(json.dumps({"manifest": args.manifest_out,
                          "launcher_source": source}, sort_keys=True))
        return 0
    # Live path: separate signed preparation release required; the tool
    # records that expectation in the manifest flow but cannot grant it.
    # Partial creation is journaled per completed launch: if the second
    # launch fails, the first is recorded in a partial manifest (same schema
    # shape, pending role noted) reconcilable by cleanup WITHOUT retrying
    # the first launch.
    journal_path = args.manifest_out + ".partial"
    try:
        os.remove(journal_path)
    except OSError:
        pass
    launched = {}
    sides = {}
    pending = None
    launch_error = None
    for role, name, lane in (("worker", args.worker_name, args.worker_lane),
                             ("verifier", args.verifier_name,
                              args.verifier_lane)):
        wdir = os.path.join(args.workdir_base, name)
        try:
            out = launch_idle(wdir, name, lane, args.profile,
                              args.idle_timeout, wdir)
        except PrepFault as e:
            pending, launch_error = role, e
            break
        launched[role] = (name, lane, wdir, out)
        sides[role] = {"session_id": out["id"], "title": name,
                       "identity_source": "launch-response-id",
                       "preparation_argv": ["agent-deck", "launch", wdir,
                                            "-t", name, "-cmd", lane,
                                            "--idle-timeout=%s"
                                            % args.idle_timeout,
                                            "-json", "-q"],
                       "idle_timeout": args.idle_timeout}
        with open(journal_path, "w") as fh:
            json.dump({"launcher_source": live_source,
                       "journal": "partial-launch-record",
                       "completed": sides, "pending": None}, fh,
                      sort_keys=True, indent=1)
    if pending is not None:
        partial = {"plan_sha256": (hashlib.sha256(
            open(args.plan, "rb").read()).hexdigest() if args.plan
            else "unsigned-plan"),
            "launcher_source": live_source, "profile": args.profile,
            "journal": "partial-launch-record",
            "pending_role": pending,
            "launch_error": {"code": launch_error.code,
                             "detail": launch_error.detail}}
        for role, side in sides.items():
            partial[role] = side
        with open(journal_path, "w") as fh:
            json.dump(partial, fh, sort_keys=True, indent=1)
        print(json.dumps({"error": "E_LAUNCH_PARTIAL",
                          "detail": "%s launch failed after %d completed; "
                                    "partial record at %s; reconcile with "
                                    "cleanup, do not retry completed sides"
                                    % (pending, len(sides), journal_path),
                          "owner": "cairn",
                          "partial_manifest": journal_path}, sort_keys=True))
        return 3
    sessions2, _ = list_sessions(args.profile)
    by_id = {s.get("id"): s for s in sessions2 if isinstance(s, dict)}
    full = {}
    for role, name, lane, wdir, out in (("worker",) + launched["worker"],
                                        ("verifier",) + launched["verifier"]):
        sid = out["id"]  # launch_idle guarantees exact returned identity
        rec = by_id.get(sid)
        if rec is None:
            raise PrepFault("E_BIND",
                            "launched session %r not in launcher list" % name)
        check_record(rec, name, lane, args.profile)
        ident = check_socket_real(os.path.join(LIVE_SOCK_DIR, sid
                                               + ".sock"))
        stream = os.path.join(LIVE_STREAM_ROOT, sid + ".jsonl")
        full[role] = {"session_id": sid, "title": name,
                      "profile": args.profile, "role_lane": lane,
                      "launch_command": rec.get("command"),
                      "workdir": wdir,
                      "identity_source": "launch-response-id",
                      "preparation_argv": sides[role]["preparation_argv"],
                      "idle_timeout": args.idle_timeout,
                      "producer_root": LIVE_STREAM_ROOT,
                      "stream_path": stream,
                      "stream_exists": os.path.exists(stream),
                      "socket": os.path.join(LIVE_SOCK_DIR, sid + ".sock"),
                      "incarnation": ident}
    plan_sha = (hashlib.sha256(open(args.plan, "rb").read()).hexdigest()
                if args.plan else "unsigned-plan")
    man = build_manifest(plan_sha, args.profile, full["worker"],
                         full["verifier"], live_source)
    with open(args.manifest_out, "w") as fh:
        json.dump(man, fh, sort_keys=True, indent=1)
    try:
        os.remove(journal_path)  # full manifest supersedes the journal
    except OSError:
        pass
    print(json.dumps({"manifest": args.manifest_out,
                      "launcher_source": live_source,
                      "worker": full["worker"]["session_id"],
                      "verifier": full["verifier"]["session_id"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrepFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
