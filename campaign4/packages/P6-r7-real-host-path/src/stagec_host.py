"""P6-r6 Stage C composition entrypoint (single executable gate-to-effect path).

Subcommands (one entrypoint; `run-case` ALWAYS gates internally first —
no standalone check plus hand-written wake sequence exists):
  derive-config : Tern-signed stagec plan + accepted live binding manifest
      -> execution config. Rejects changed hashes, non-live sources,
      synthetic bindings (stream/socket paths must sit under the recorded
      producer root / sock dir; no placeholder tokens; session IDs used
      verbatim). Accepted manifest is NEVER modified; the config is
      separately derived and records parent hash + re-sign requirements.
  gate          : signature + binding-continuity check immediately before
      any send. Raw IDs retained as evidence; expired sockets do NOT fail
      (liveness is re-witnessed at execution); changed IDs/bindings fail.
  run-case      : gate, then one enumerated case through the pinned P6-r5
      candidate (imported by absolute path, unchanged): setup_manifest ->
      run_fixture -> resolve item from OBSERVED stream records (never
      operator guess) -> witness observe with producer onset sidecar ->
      join candidate detection + committed recovery/ack evidence ->
      candidate check-latency + witness check. Counts wake sends from the
      transport trace: positive case demands exactly one worker + one
      verifier send.
  timecheck     : phase-5 gate that actually enforces recovery/total. Joins
      candidate latency rows with witness rows on (action, execution) and
      enforces detection/recovery/total 30/60/90 with suspicion 180/60/240
      reported. The full negative list (unknown source/endpoint, missing
      success, all-failure corpus, negative intervals, late recovery with
      fast detection, late total, wrong action, missing ack, queued-only
      wake, unknown uncertainty) cannot yield acceptance. Worker execution
      duration is reported separately, never as stall latency.
  rollback      : archive witness rows + execution config FIRST, then the
      candidate rollback_verify (archive-before-cleanup).

Injected effects only unless --live-resolve is passed (Stage C execution,
separately signed): no fixture wakes/launches/restarts here. --overlay-dir
redirects runtime DIRECTORIES to tmp for injected runs; identities are
never remapped.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys

PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATE_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
                 "P6-r5-launch-binding/src")
P6R6_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
            "P6-r6-live-preparation/src")
# Pinned parent bytes (P6-r6 1b8a166d): hash-checked on import, never edited.
_CANDIDATE_HASHES = {
    "harness.py":
    "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142"}
P6R6_ENTRY_SHA256 = ("211f495be11eaa44e1a3c3f9fc497b365aa7ab24bef099374d1"
                     "78bc9caf95a6a")
PLACEHOLDER_RE = re.compile(r"<[A-Za-z_][A-Za-z_0-9-]*>|MANIFEST_STREAM"
                            r"|\bITEM\b|ONSET\.json|\bACT\b|(?<![A-Za-z])EX\b")

CASES = ("positive-handoff", "lost-completion", "failed-verification",
         "queued-ambiguous-restart", "quiet-rest")


class StageCFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _load(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        raise StageCFault("E_UNREADABLE", "unreadable: " + path)


def _candidate():
    for name, want in _CANDIDATE_HASHES.items():
        with open(os.path.join(CANDIDATE_SRC, name), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != want:
            raise StageCFault("E_CORE_DRIFT",
                              "pinned candidate %s changed (%s); refusing "
                              "to compose against drifted core" % (name,
                                                                   got[:12]))
    if CANDIDATE_SRC not in sys.path:
        sys.path.insert(0, CANDIDATE_SRC)
    import harness as h
    return h


# --- derive-config -------------------------------------------------------------
def derive_config(plan_path, binding_path, sig_path, out_path):
    plan = _load(plan_path)
    binding = _load(binding_path)
    sig = _load(sig_path)
    if sig.get("signer") != "tern":
        raise StageCFault("E_NO_SIGNATURE", "signer is not tern")
    if sig.get("plan_sha256") != _sha(plan_path):
        raise StageCFault("E_PLAN_CHANGED", "stagec plan not Tern-signed")
    if sig.get("binding_sha256") != _sha(binding_path):
        raise StageCFault("E_BINDING_CHANGED",
                          "binding manifest not Tern-signed")
    if binding.get("launcher_source") != "live-agent-deck":
        raise StageCFault("E_NOT_LIVE",
                          "binding source %r is not live-agent-deck"
                          % binding.get("launcher_source"))
    sides = {}
    for role in ("worker", "verifier"):
        side = binding.get(role) or {}
        for key in ("session_id", "socket", "stream_path",
                    "producer_root"):
            val = side.get(key) or ""
            if not val or PLACEHOLDER_RE.search(val):
                raise StageCFault("E_SYNTHETIC",
                                  "%s.%s missing or placeholder" % (role,
                                                                    key))
        if os.path.dirname(side["stream_path"]) != side["producer_root"]:
            raise StageCFault("E_MISMATCH",
                              "%s stream not under recorded producer root"
                              % role)
        if os.path.dirname(side["socket"]) != os.path.dirname(
                side["socket"]):
            raise StageCFault("E_MISMATCH",
                              "%s socket path malformed" % role)
        sock_dir = os.path.dirname(side["socket"])
        if not sock_dir or sock_dir == side["producer_root"]:
            raise StageCFault("E_MISMATCH",
                              "%s socket dir implausible" % role)
        sides[role] = {"session_id": side["session_id"],
                       "title": side.get("title"),
                       "role_lane": side.get("role_lane"),
                       "launch_command": side.get("launch_command"),
                       "workdir": side.get("workdir"),
                       "producer_root": side["producer_root"],
                       "stream_path": side["stream_path"],
                       "socket": side["socket"],
                       "incarnation": side.get("incarnation")}
    config = {"stagec_plan_sha256": _sha(plan_path),
              "parent_binding_sha256": _sha(binding_path),
              "binding_path": os.path.abspath(binding_path),
              "launcher_source": "live-agent-deck",
              "profile": binding.get("profile", "campaign4"),
              "candidate_src": CANDIDATE_SRC,
              "worker": sides["worker"], "verifier": sides["verifier"],
              "timing_bounds": {"detect_s": 30.0, "recover_s": 60.0,
                                "total_s": 90.0, "suspicion_detect_s": 180.0,
                                "suspicion_recover_s": 60.0,
                                "suspicion_total_s": 240.0},
              "cases": list(CASES),
              "resign_required": ["any config/plan/tool byte change",
                                  "any binding ID/socket/stream change",
                                  "socket expiry re-witness at execution"]}
    with open(out_path, "w") as fh:
        json.dump(config, fh, sort_keys=True, indent=1)
    return config


# --- gate ----------------------------------------------------------------------
def _current_registry(profile, registry_file=""):
    if registry_file:
        return _load(registry_file), "injected:" + registry_file
    import subprocess as _sp
    env = dict(os.environ, AGENTDECK_PROFILE=profile)
    proc = _sp.run(["agent-deck", "list", "--json"], capture_output=True,
                   text=True, timeout=60, env=env)
    if proc.returncode != 0:
        raise StageCFault("E_REGISTRY",
                          "live registry unreadable: "
                          + (proc.stderr or "")[:200])
    try:
        return json.loads(proc.stdout or "[]"), "live-agent-deck"
    except ValueError:
        raise StageCFault("E_REGISTRY", "live registry malformed")


def gate(config_path, plan_path, sig_path, registry_file=""):
    """H2 live gate, immediately before any send: signature binds plan +
    config + executable code/candidate hashes (purpose must be stagec-task;
    preparation-only signatures rejected); then CURRENT registry/profile/
    lane/workdir and BOTH live sockets/incarnations are verified against
    the signed binding — never two stale disk copies. Expired/stopped/
    rebound/mismatched runtimes reject before any send. No hardcoded IDs."""
    import stat as _stat
    config = _load(config_path)
    plan = _load(plan_path)  # noqa: parsed to prove readability
    sig = _load(sig_path)
    if sig.get("signer") != "tern":
        raise StageCFault("E_NO_SIGNATURE", "signer is not tern")
    if sig.get("purpose") != "stagec-task":
        raise StageCFault("E_NO_SIGNATURE",
                          "purpose %r cannot authorize task sends"
                          % sig.get("purpose"))
    if sig.get("plan_sha256") != _sha(plan_path):
        raise StageCFault("E_PLAN_CHANGED", "plan changed since signature")
    if sig.get("config_sha256") != _sha(config_path):
        raise StageCFault("E_CONFIG_CHANGED",
                          "execution config changed since signature")
    if sig.get("stagec_entry_sha256") != _sha(__file__):
        raise StageCFault("E_TOOL_CHANGED",
                          "entrypoint changed since signature")
    for name, want in _CANDIDATE_HASHES.items():
        if sig.get("candidate_" + name.replace(".py", "") + "_sha256",
                   want) != want:
            raise StageCFault("E_TOOL_CHANGED",
                              "candidate hash not bound by signature")
    if config.get("launcher_source") != "live-agent-deck":
        raise StageCFault("E_NOT_LIVE", "config source not live-agent-deck")
    binding = _load(config["binding_path"])
    if _sha(config["binding_path"]) != config.get("parent_binding_sha256"):
        raise StageCFault("E_BINDING_CHANGED",
                          "accepted binding modified since derive")
    sessions, reg_source = _current_registry(config.get("profile",
                                                        "campaign4"),
                                             registry_file)
    by_id = {s.get("id"): s for s in sessions if isinstance(s, dict)}
    for role in ("worker", "verifier"):
        cur, signed = binding.get(role) or {}, config.get(role) or {}
        if (cur.get("session_id") != signed.get("session_id")
                or cur.get("stream_path") != signed.get("stream_path")
                or cur.get("socket") != signed.get("socket")):
            raise StageCFault("E_BINDING_CHANGED",
                              "%s binding drifted since derive" % role)
        sid = signed.get("session_id")
        rec = by_id.get(sid)
        if rec is None:
            raise StageCFault("E_EXPIRED",
                              "%s session %s gone from live registry"
                              % (role, sid))
        if (rec.get("status") in ("stopped", "error", "archived")
                or rec.get("archived") is True):
            raise StageCFault("E_EXPIRED",
                              "%s session %s state %r; stopped/expired "
                              "runtime rejected before send"
                              % (role, sid, rec.get("status")))
        if rec.get("profile", "campaign4") != config.get("profile",
                                                         "campaign4"):
            raise StageCFault("E_MISMATCH",
                              "%s profile mismatch" % role)
        if rec.get("command") != signed.get("role_lane"):
            raise StageCFault("E_MISMATCH",
                              "%s lane/command mismatch" % role)
        if (rec.get("path") or "") != (signed.get("workdir") or ""):
            raise StageCFault("E_MISMATCH",
                              "%s workdir mismatch" % role)
        try:
            st = os.stat(signed["socket"])
        except OSError:
            raise StageCFault("E_EXPIRED",
                              "%s socket gone: %s" % (role,
                                                      signed["socket"]))
        if not _stat.S_ISSOCK(st.st_mode):
            raise StageCFault("E_MISMATCH",
                              "%s socket not a real socket" % role)
        want_ino = (signed.get("incarnation") or {}).get("ino")
        if want_ino is not None and st.st_ino != want_ino:
            raise StageCFault("E_REBOUND",
                              "%s socket incarnation changed (rebound); "
                              "re-witness required" % role)
    return {"gate": "PASS", "worker": config["worker"]["session_id"],
            "verifier": config["verifier"]["session_id"],
            "registry_source": reg_source}


# --- timecheck (phase-5 gate) ----------------------------------------------------
def _instant(v):
    import datetime as _dt
    if not isinstance(v, str):
        return None
    try:
        s = v.strip().replace("Z", "+00:00")
        dt = _dt.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_dt.timezone.utc)
        return dt
    except ValueError:
        return None


def timecheck(config_path, latency_path, witness_path, receipt_path=None,
              expect_open=None):
    """H3 phase-5 gate. Joins candidate rows with witness rows on the EXACT
    (action, execution, case) triple — executions come from the signed case
    receipt, so an old-execution witness can never certify a new execution.
    Acceptance needs actual recorded positive ack/recovery evidence
    (settled sends + witness ack:true), never absence of ack:false.
    Uncertainty must be finite/nonnegative and is added conservatively to
    every bound; unknown/unbounded intervals are INCOMPLETE. Worker
    execution duration is reported separately, never stall latency."""
    import math as _math
    config = _load(config_path)
    bounds = config.get("timing_bounds", {})
    det_b, rec_b, tot_b = (bounds.get("detect_s", 30.0),
                           bounds.get("recover_s", 60.0),
                           bounds.get("total_s", 90.0))
    sdet_b, stot_b = (bounds.get("suspicion_detect_s", 180.0),
                      bounds.get("suspicion_total_s", 240.0))
    receipt = _load(receipt_path) if receipt_path else {}
    executions = receipt.get("executions", {})
    settled = set(receipt.get("settled_actions", []))
    case = receipt.get("case")
    try:
        lat = [json.loads(l) for l in open(latency_path) if l.strip()]
    except OSError:
        raise StageCFault("E_NO_LATENCY", "candidate latency rows missing")
    try:
        wit = [json.loads(l) for l in open(witness_path) if l.strip()]
    except OSError:
        raise StageCFault("E_NO_WITNESS", "witness rows missing")
    wkey = {}
    for w in wit:
        wkey.setdefault((w.get("action"), w.get("execution"),
                         w.get("case")), w)
    dupes = len(wit) - len(wkey)
    success = [r for r in lat if r.get("outcome") in ("transition-committed",
                                                      "terminal-rest")]
    failures = [r for r in lat if r not in success]
    if not lat:
        return {"verdict": "incomplete", "reason": "no candidate rows"}
    if expect_open:
        closed = [r for r in success if r.get("action") == expect_open]
        if closed:
            return {"verdict": "reject",
                    "reason": "action %s closed despite failed check: "
                              "failed verification must never close"
                    % expect_open}
        if not success:
            return {"verdict": "incomplete",
                    "reason": "no success rows at all; fixture did not run"}
        return {"verdict": "accept-open",
                "reason": "worker success present, %s correctly open"
                % expect_open,
                "success": len(success), "failures": len(failures)}
    if not success:
        return {"verdict": "reject",
                "reason": "all-failure corpus (%d rows, 0 success): "
                          "never vacuous acceptance" % len(lat),
                "failures": [r.get("outcome") for r in failures]}
    joined, problems = [], []
    if dupes:
        problems.append("duplicate witness rows: %d" % dupes)
    for r in success:
        action = r.get("action")
        execution = executions.get(action)
        if not execution:
            problems.append("no signed execution for %s" % (action,))
            continue
        w = wkey.get((action, execution, case))
        if w is None:
            problems.append("missing/wrong-execution witness for %s "
                            "(old executions cannot certify new ones)"
                            % (action,))
            continue
        onset, det_at, com_at = (r.get("onset_at") or w.get("onset_at"),
                                 r.get("detected_at"), r.get("committed_at"))
        if not onset:
            problems.append("unknown source for %s" % (action,))
            continue
        if not det_at or not com_at:
            problems.append("unknown endpoint for %s" % (action,))
            continue
        unc = w.get("onset_uncertainty_s")
        if unc is None or not isinstance(unc, (int, float)) \
                or not _math.isfinite(unc) or unc < 0:
            problems.append("unknown/unbounded uncertainty for %s"
                            % (action,))
            continue
        o, d, c = _instant(onset), _instant(det_at), _instant(com_at)
        if o is None or d is None or c is None:
            problems.append("unparsable timestamps for %s" % (action,))
            continue
        det, rec, tot = ((d - o).total_seconds(), (c - d).total_seconds(),
                         (c - o).total_seconds())
        if det < -unc or rec < 0 or tot < 0:
            problems.append("negative/contradictory clock for %s "
                            "(beyond uncertainty bound)" % (action,))
            continue
        if w.get("outcome") == "queued-only":
            problems.append("queued-only wake for %s" % (action,))
            continue
        if w.get("ack") is not True or action not in settled:
            problems.append("missing ack for %s (positive ack/recovery "
                            "evidence required)" % (action,))
            continue
        worker_dur = (d - _instant(r.get("dispatch_at"))).total_seconds() \
            if r.get("dispatch_at") else None
        det_e, rec_e, tot_e = det + unc, rec + unc, tot + unc
        joined.append({"action": action, "execution": execution,
                       "detection_s": det, "recovery_s": rec,
                       "total_s": tot, "uncertainty_s": unc,
                       "conservative": {"detection_s": det_e,
                                        "recovery_s": rec_e,
                                        "total_s": tot_e},
                       "worker_duration_s": worker_dur,
                       "suspicion": {"detect_ok": det_e <= sdet_b,
                                     "total_ok": tot_e <= stot_b}})
        if det_e > det_b:
            problems.append("late detection for %s: %.1fs+%.1fs unc"
                            % (action, det, unc))
        if rec_e > rec_b:
            problems.append("late recovery despite fast detection for %s: "
                            "%.1fs+%.1fs unc" % (action, rec, unc))
        if tot_e > tot_b:
            problems.append("late total for %s: %.1fs+%.1fs unc"
                            % (action, tot, unc))
    if problems:
        return {"verdict": "reject", "reasons": problems,
                "joined": len(joined), "success": len(success),
                "failures": len(failures)}
    return {"verdict": "accept", "joined": len(joined),
            "success": len(success), "failures": len(failures),
            "worker_durations_s": [j["worker_duration_s"] for j in joined]}


# --- run-case --------------------------------------------------------------------
def _plan_templates():
    """Copy ONLY dispatch text templates + dispositions from the pinned
    candidate plan. All IDs/paths/seats come from the execution config."""
    pinned = _load(os.path.join(CANDIDATE_SRC, "..", "fixture-plan.json"))
    texts = dict(pinned["task_texts"])
    for k in texts:  # composition package line: the fresh producer binds
        texts[k] = texts[k] + "\npackage: P6C"  # its claim to the dispatch
    return {"task_texts": texts,
            "authorized_dispositions": pinned.get("authorized_dispositions",
                                                  [])}


def _candidate_plan(config, plan, dirs, stream_dir=None, wkey=None,
                  vkey=None):
    t = _plan_templates()
    wa, va = plan["actions"]["worker"], plan["actions"]["verifier"]
    seats = [config["worker"]["title"], config["verifier"]["title"]]
    wsid, vsid = (config["worker"]["session_id"],
                  config["verifier"]["session_id"])
    if stream_dir is None:  # overlay layout: one dir, sid-named files
        stream_dir, wkey, vkey = dirs["stream"], wsid, vsid
    cplan = {"fixture_id": "p6-stagec-1", "package_id": "P6C",
             "worker_action": wa, "verify_action": va,
             "seats": {"fixture_seats": seats},
             "allowlist": {"seats": seats,
                           "timer_units": {wa: plan["timer_unit"]},
                           "wake_path": dirs["wake_shim"],
                           "systemd_run": dirs["systemd_shim"],
                           "systemctl": dirs["systemctl_shim"]},
             "bounds": {"duration_s": 900, "verify_window_s": 600,
                        "wait_s": 8, "escalation_window_s": 120,
                        "stream_dir": stream_dir,
                        "onset_dir": dirs["onsets"],
                        "artifact_base_dir": dirs["art"],
                        "latency_path": dirs["latency"]},
             "task_texts": t["task_texts"],
             "authorized_dispositions": t["authorized_dispositions"],
             "routes": {va: seats[1], wa: seats[0]}}
    return cplan, wkey, vkey


def _signed_stream_binding(config, overlay, dirs):
    """Stream dir + per-seat keys from the SIGNED binding (host) or the
    overlay surface (simulated). Keys are never invented: host keys are
    the signed stream filenames; overlay keys are the signed session IDs
    mapped onto the overlay surface (labeled simulated)."""
    if overlay:
        wsid = config["worker"]["session_id"]
        vsid = config["verifier"]["session_id"]
        return dirs["stream"], wsid, vsid
    out = []
    for role in ("worker", "verifier"):
        sp = config[role]["stream_path"]
        root, base = os.path.dirname(sp), os.path.basename(sp)
        if not base.endswith(".jsonl") or not root:
            raise StageCFault("E_SYNTHETIC",
                              "%s signed stream path malformed: %r"
                              % (role, sp))
        out.append((root, base[:-len(".jsonl")]))
    if out[0][0] != out[1][0]:
        raise StageCFault("E_MISMATCH",
                          "worker/verifier producer roots differ")
    return out[0][0], out[0][1], out[1][1]


def _resolve_item(stream_file, onset_dir):
    """Item resolved from OBSERVED records: end items in the stream
    intersected with producer onset sidecars. Never operator guess."""
    ends = set()
    try:
        with open(stream_file) as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("t") == "end" \
                        and row.get("item"):
                    ends.add(row["item"])
    except OSError:
        pass
    try:
        onsets = {f[:-len(".json")] for f in os.listdir(onset_dir)
                  if f.endswith(".json")}
    except OSError:
        onsets = set()
    both = sorted(ends & onsets)
    if not both:
        raise StageCFault("E_NO_ITEM",
                          "no observed end+onset item in " + stream_file)
    return both[-1]


def _drive_producers(msgs_dir, seat_map, onset_dir, tamper=False,
                     only=None, deadline_s=40.0):
    """SIMULATED producer driver (overlay tests only): each producer
    subprocess sees ONLY the dispatched text file it is given plus named
    files. `only` restricts which seats are driven (lost-completion holds
    the verifier back); `tamper` corrupts the artifact between worker and
    verifier (failed-verification). NEVER used on the host branch."""
    import subprocess as _sp
    import time as _t
    want = set(only) if only else set(seat_map)
    done = {}
    stop = _t.monotonic() + deadline_s
    while _t.monotonic() < stop:
        for seat, spec in seat_map.items():
            if seat in done or seat not in want:
                continue
            prefix = "to-" + seat + "-"
            queries = [f for f in os.listdir(msgs_dir)
                       if f.startswith(prefix)]
            if not queries:
                continue
            text_file = os.path.join(msgs_dir, sorted(queries)[-1])
            cmd = [sys.executable, os.path.join(CANDIDATE_SRC,
                                                "fixture_worker.py"),
                   "--role", spec["role"], "--text-file", text_file,
                   "--stream-file", spec["stream"], "--onset-dir",
                   onset_dir]
            proc = _sp.run(cmd, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                raise StageCFault("E_PRODUCER",
                                  "%s producer rc%d: %s" % (
                                      seat, proc.returncode,
                                      (proc.stdout or proc.stderr or "")
                                      [:300]))
            done[seat] = json.loads(proc.stdout)
            if tamper and spec["role"] == "worker":
                import glob as _g
                for art in _g.glob(os.path.join(spec["art"], "*")):
                    with open(art, "wb") as fh:
                        fh.write(b"tampered-by-fixture-fault")
        if want <= set(done):
            return done
        _t.sleep(0.2)
    raise StageCFault("E_PRODUCER_TIMEOUT",
                      "dispatched texts never arrived for %s"
                      % sorted(want - set(done)))


def run_case(config_path, plan_path, sig_path, case, dirs, out_path,
             registry_file=""):
    """H1/H4 entry: the overlay flag selects ONLY the effects plane, never
    the logic. Host branch (no --overlay-dir): signed actual stream/socket
    paths used verbatim — no substitute stream files, no producer driver,
    no shim-trace assumption; the seat side (real model seats live, test
    producer-boundary harness injected) acts concurrently outside this
    tool. Overlay branch: explicitly simulated equivalent for tests."""
    h = _candidate()
    g = gate(config_path, plan_path, sig_path, registry_file)  # mandatory
    config, plan = _load(config_path), _load(plan_path)
    if case not in config.get("cases", []):
        raise StageCFault("E_CASE", "case %r not enumerated" % case)
    overlay = bool(dirs.get("overlay"))
    if overlay:
        for d in ("stream", "claims", "art", "onsets", "msgs"):
            os.makedirs(dirs[d], exist_ok=True)
    else:
        for d in ("claims", "art", "onsets", "msgs"):
            os.makedirs(dirs[d], exist_ok=True)
        root = os.path.dirname(
            config["worker"].get("stream_path") or "")
        if not root or not os.path.isdir(root):
            raise StageCFault("E_HOST_PATH",
                              "signed producer root absent: %r" % (root,))
    wsid, vsid = (config["worker"]["session_id"],
                  config["verifier"]["session_id"])
    stream_dir, wkey, vkey = _signed_stream_binding(config, overlay, dirs)
    cplan_path = os.path.join(dirs["root"], "candidate-plan.json")
    cplan, _, _ = _candidate_plan(config, plan, dirs,
                                  stream_dir=stream_dir, wkey=wkey, vkey=vkey)
    json.dump(cplan, open(cplan_path, "w"), sort_keys=True)
    import hashlib as _hl
    phash = _hl.sha256(open(cplan_path, "rb").read()).hexdigest()
    manifest_path = os.path.join(dirs["root"], "manifest.json")
    h.setup_manifest(cplan_path, manifest_path, session=wsid,
                     stream_key=wkey, worker_stream_key=wkey,
                     verifier_stream_key=vkey)
    manifest = json.load(open(manifest_path))
    if overlay:  # simulated surface only; host branch never touches these
        for key in (wkey, vkey):
            p = os.path.join(stream_dir, key + ".jsonl")
            if not os.path.exists(p):
                open(p, "w").close()
    wstream = os.path.join(stream_dir, wkey + ".jsonl")
    vstream = os.path.join(stream_dir, vkey + ".jsonl")
    old_env = dict(os.environ)
    if overlay:
        os.environ["PATH"] = dirs["bin"] + ":" + os.environ.get("PATH", "")
        os.environ["TRACE"] = dirs["trace"]
        os.environ["MSGDIR"] = dirs["msgs"]
    wtitle, vtitle = config["worker"]["title"], config["verifier"]["title"]
    seat_map = {wtitle: {"role": "worker", "stream": wstream,
                         "art": dirs["art"]},
                vtitle: {"role": "verifier", "stream": vstream,
                         "art": dirs["art"]}}
    import threading as _th
    box = {}
    bg = None
    if overlay:  # simulated seats; host seats act outside this tool
        tamper = (case == "failed-verification")
        only = None if case != "lost-completion" else {wtitle}

        def _bg():
            try:
                box["done"] = _drive_producers(dirs["msgs"], seat_map,
                                               dirs["onsets"], tamper=tamper,
                                               only=only)
            except StageCFault as e:
                box["error"] = {"code": e.code, "detail": e.detail}
        bg = _th.Thread(target=_bg, daemon=True)
        bg.start()
    try:
        # Same candidate live path in both branches: real
        # HostWakeTransport/HostTimerService; plan hash + seat allowlist
        # enforced by the candidate itself. Only external effects differ
        # (signed host commands live, signed test executables injected).
        adapter = h.build_adapter(
            dirs["db"], live=True, plan_hash=phash,
            allowlist_seats=[wtitle, vtitle], plan_path=cplan_path)
        out = h.run_fixture(adapter, manifest, dirs["claims"], "P6C")
    finally:
        os.environ.clear()
        os.environ.update(old_env)
    if bg is not None:
        bg.join(timeout=30)
    if "error" in box:
        raise StageCFault(box["error"]["code"], box["error"]["detail"])
    calls = list(getattr(adapter.transport, "calls", []))
    sends = {"worker": sum(1 for s, t, k in calls if s == wtitle),
             "verifier": sum(1 for s, t, k in calls if s == vtitle)}
    def _rerun():
        env_now = dict(os.environ)
        if overlay:
            os.environ["PATH"] = dirs["bin"] + ":" + os.environ.get(
                "PATH", "")
        try:
            adapter_r = h.build_adapter(
                dirs["db"], live=True, plan_hash=phash,
                allowlist_seats=[wtitle, vtitle], plan_path=cplan_path)
            return adapter_r, h.run_fixture(adapter_r, manifest,
                                            dirs["claims"], "P6C")
        finally:
            os.environ.clear()
            os.environ.update(env_now)

    def _calls(adapter_obj):
        return list(getattr(adapter_obj.transport, "calls", []))

    extra = {}
    if case == "positive-handoff":
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "positive case did not commit: %s" % (out,))
        if not (sends["worker"] == 1 and sends["verifier"] == 1):
            raise StageCFault("E_SENDS",
                              "positive case needs 1+1 sends: %s" % (sends,))
    elif case == "lost-completion":
        # Verifier end never arrived: owned recovery, worker evidence
        # retained, nothing closed.
        if out.get("decision") != "owned-recovery":
            raise StageCFault("E_CASE_FAIL",
                              "lost completion must recover owned: %s"
                              % (out,))
        if out.get("decision") == "COMPLETE":
            raise StageCFault("E_CASE_FAIL", "lost completion closed?!")
        wclaim = os.path.join(dirs["claims"],
                              manifest["execution_id"] + ".json")
        if not os.path.exists(wclaim):
            raise StageCFault("E_CASE_FAIL",
                              "worker evidence not retained")
    elif case == "failed-verification":
        if out.get("decision") == "COMPLETE" or \
                manifest.get("disposition") == "COMPLETE":
            raise StageCFault("E_CASE_FAIL",
                              "failed check must never close COMPLETE")
    elif case == "queued-ambiguous-restart":
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "queued run did not commit: %s" % (out,))
        states = {}
        for key in list(adapter.driver.kv.keys()):
            if key.startswith("outbox-sent:"):
                mid = adapter.driver.kv.get(key)
                try:
                    states[mid] = adapter.transport.state(mid)
                except Exception:
                    states[mid] = "unknown"
        if "queued" not in states.values():
            raise StageCFault("E_CASE_FAIL",
                              "no queued transport receipt observed: %s"
                              % (states,))
        extra["transport_states"] = states
        n_calls, n_msg = len(calls), _msg_count(adapter)
        adapter2, out2 = _rerun()
        if out2.get("decision") != "duplicate-end-ignored":
            raise StageCFault("E_CASE_FAIL",
                              "rerun not recognized duplicate: %s" % (out2,))
        if len(_calls(adapter2)) != 0 or _msg_count(adapter2) != n_msg:
            raise StageCFault("E_SENDS",
                              "rerun manufactured fresh sends/identities")
        # Ambiguous delivery through the SAME production transport: held
        # for reconciliation, never blind redispatch.
        amid = adapter2.transport.send(wtitle, "probe-ambiguous",
                                       kind="wake",
                                       action=manifest["action_id"],
                                       execution=manifest["execution_id"])
        if adapter2.transport.state(amid) != "ambiguous":
            raise StageCFault("E_CASE_FAIL",
                              "ambiguous receipt not mapped, state=%s"
                              % adapter2.transport.state(amid))
        rec = adapter2.reconcile_send(amid, manifest["action_id"])
        if rec.get("decision") not in ("hold-for-reconciliation",
                                       "hold-for-receipt"):
            raise StageCFault("E_CASE_FAIL",
                              "ambiguous delivery not held: %s" % (rec,))
        extra["ambiguous"] = {"mid": amid, "reconcile": rec}
        out = dict(out2, worker=out, outbox_settled=out.get(
            "outbox_settled"), worker_outbox=out.get("worker_outbox"),
            verifier_outbox=out.get("verifier_outbox"))
    elif case == "quiet-rest":
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "quiet-rest setup run did not commit: %s"
                              % (out,))
        import time as _t
        before = (_sizes(wstream, vstream), len(calls))
        _t.sleep(3)
        if (_sizes(wstream, vstream), len(_calls(adapter))) != before:
            raise StageCFault("E_CASE_FAIL",
                              "quiet rest showed spurious activity")
        adapter2, out2 = _rerun()
        if out2.get("decision") != "duplicate-end-ignored":
            raise StageCFault("E_CASE_FAIL",
                              "rerun not recognized duplicate: %s" % (out2,))
        if len(_calls(adapter2)) != 0:
            raise StageCFault("E_SENDS",
                              "rerun manufactured fresh sends")
        out = dict(out2, worker=out, outbox_settled=out.get(
            "outbox_settled"), worker_outbox=out.get("worker_outbox"),
            verifier_outbox=out.get("verifier_outbox"))
    else:
        raise StageCFault("E_CASE", "unknown case %r" % case)
    # Witness rows for BOTH ends, resolved from observed records; onset
    # from the producer sidecar, else the executable operator marker for
    # the action, else None (INCOMPLETE downstream — never invented).
    items = {}
    for sid, path in ((wsid, wstream), (vsid, vstream)):
        try:
            items[sid] = _resolve_item(path, dirs["onsets"])
        except StageCFault:
            items[sid] = None
    import subprocess as _sp
    if P6R6_SRC not in sys.path:
        sys.path.insert(0, P6R6_SRC)
    import witness_timing as _w
    lat_rows = [json.loads(l) for l in open(dirs["latency"])
                if l.strip()] if os.path.exists(dirs["latency"]) else []
    det_by_action = {}
    for r in lat_rows:
        det_by_action[r.get("action")] = r.get("detected_at")
    for (action, execution, sid) in (
            (manifest["action_id"], manifest["execution_id"], wsid),
            (manifest["verify_action_id"],
             manifest["verify_execution_id"], vsid)):
        onset = (None, None, None)
        if items[sid]:
            onset = _w.read_onset(os.path.join(dirs["onsets"],
                                               items[sid] + ".json"))
        if onset[0] is None:
            marker = os.path.join(dirs["onsets"], action + ".marker.json")
            try:
                rec = json.load(open(marker))
                onset = (rec.get("onset_at"), rec.get("provenance"),
                         rec.get("uncertainty_s"))
            except (OSError, ValueError):
                pass
        wrow = _w.emit_row(action, execution, None,
                           det_by_action.get(action), onset,
                           dirs["witness"])
        _annotate_witness(dirs["witness"], action, execution, case,
                          action in _settled_actions(out, manifest))
    cand_err, wit_err = None, None
    try:
        h.check_latency(dirs["latency"])
    except Exception as e:
        cand_err = getattr(e, "code", type(e).__name__)
    try:
        _w.check_rows(dirs["witness"])
    except Exception as e:
        wit_err = getattr(e, "code", type(e).__name__)
    receipt = {"case": case, "gate": g, "outcome": out,
               "sends": sends, "worker_item": items[wsid],
               "verifier_item": items[vsid],
               "candidate_gate": cand_err or "pass",
               "witness_gate": wit_err or "pass",
               "overlay": overlay,
               "executions": {manifest["action_id"]:
                              manifest["execution_id"],
                              manifest["verify_action_id"]:
                              manifest["verify_execution_id"]},
               "settled_actions": _settled_actions(out, manifest)}
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, sort_keys=True, indent=1)
    expect = manifest["verify_action_id"] if case in (
        "failed-verification", "lost-completion") else None
    verdict = timecheck(config_path, dirs["latency"], dirs["witness"],
                        receipt_path=out_path, expect_open=expect)
    if case in ("positive-handoff", "queued-ambiguous-restart",
                "quiet-rest"):
        if verdict.get("verdict") != "accept":
            raise StageCFault(
                "E_TIMECHECK",
                "%s timecheck did not accept: %s" % (case, verdict))
    else:
        if verdict.get("verdict") != "accept-open":
            raise StageCFault("E_CASE_FAIL",
                              "%s not provably open: %s" % (case, verdict))
    receipt["timecheck"] = verdict
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, sort_keys=True, indent=1)
    receipt.update(extra)
    return receipt


def _msg_count(adapter):
    try:
        return sum(1 for k in adapter.driver.kv.keys()
                   if k.startswith("msg:"))
    except Exception:
        return -1


def _sizes(*paths):
    out = []
    for p in paths:
        try:
            out.append(os.path.getsize(p))
        except OSError:
            out.append(-1)
    return tuple(out)


def _settled_actions(out, manifest):
    settled = set(out.get("outbox_settled") or [])
    got = []
    if out.get("worker_outbox") in settled:
        got.append(manifest["action_id"])
    if out.get("verifier_outbox") in settled:
        got.append(manifest["verify_action_id"])
    worker = out.get("worker") or {}
    if worker.get("worker_outbox") in settled and \
            manifest["action_id"] not in got:
        got.append(manifest["action_id"])
    return sorted(got)


def _annotate_witness(witness_path, action, execution, case, ack):
    rows = [json.loads(l) for l in open(witness_path) if l.strip()]
    for r in rows:
        if r.get("action") == action and r.get("execution") == execution:
            r["case"] = case
            r["ack"] = bool(ack)
    with open(witness_path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


# --- rollback --------------------------------------------------------------------
def rollback(config_path, overlay_root, archive_dir):
    import shutil as _sh
    config = _load(config_path)
    wit = os.path.join(overlay_root, "witness-rows.jsonl")
    man = os.path.join(overlay_root, "manifest.json")
    os.makedirs(archive_dir, exist_ok=True)
    for src in (wit, config_path):
        if os.path.exists(src):
            _sh.copy(src, os.path.join(archive_dir,
                                       os.path.basename(src)))
    h = _candidate()
    db = os.path.join(overlay_root, "fixture.db")
    report = h.rollback_verify(db, man, archive_dir)
    report["witness_archived"] = os.path.exists(
        os.path.join(archive_dir, "witness-rows.jsonl"))
    with open(os.path.join(archive_dir, "rollback-report.json"),
              "w") as fh:
        json.dump(report, fh, sort_keys=True)
    return report


def _overlay(root):
    return {"root": root, "overlay": True,
            "stream": os.path.join(root, "stream"),
            "claims": os.path.join(root, "claims"),
            "art": os.path.join(root, "art"),
            "onsets": os.path.join(root, "onsets"),
            "msgs": os.path.join(root, "msgs"),
            "bin": os.path.join(root, "bin"),
            "wake_shim": os.path.join(root, "bin", "wake"),
            "systemd_shim": os.path.join(root, "bin", "systemd-run"),
            "systemctl_shim": os.path.join(root, "bin", "systemctl"),
            "db": os.path.join(root, "fixture.db"),
            "latency": os.path.join(root, "latency.jsonl"),
            "witness": os.path.join(root, "witness-rows.jsonl"),
            "trace": os.path.join(root, "trace.log")}


def _live_dirs(plan):
    """H1 actual host branch: real authorized commands from the SIGNED plan
    plus signed actual runtime paths from the execution config (resolved by
    the caller). Missing host paths fail OWNED (E_HOST_PATH) — never an
    uncaught KeyError. Nothing here creates streams, shims, or producers."""
    try:
        cmds = plan["host_commands"]
        wake, srun, sctl = (cmds["wake"], cmds["systemd_run"],
                            cmds["systemctl"])
    except KeyError as e:
        raise StageCFault("E_HOST_PATH",
                          "signed plan lacks host command %s" % (e,))
    for label, path in (("wake", wake), ("systemd_run", srun),
                        ("systemctl", sctl)):
        if not (os.path.isfile(path) and os.access(path, os.X_OK)):
            raise StageCFault("E_HOST_PATH",
                              "host command %s not executable: %s"
                              % (label, path))
    d = dict(plan["live_run_dirs"])
    d["overlay"] = False
    d["wake_shim"] = wake
    d["systemd_shim"] = srun
    d["systemctl_shim"] = sctl
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r7 real-host entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("derive-config", "gate"):
        p = sub.add_parser(name)
        p.add_argument("--plan", required=True)
        p.add_argument("--binding", "--config", required=True, dest="src")
        p.add_argument("--signatures", required=True)
        p.add_argument("--registry-file", default="")
        p.add_argument("--out", required=name == "derive-config")
    r = sub.add_parser("run-case")
    r.add_argument("--config", required=True)
    r.add_argument("--plan", required=True)
    r.add_argument("--signatures", required=True)
    r.add_argument("--case", required=True)
    r.add_argument("--overlay-dir", default="")
    r.add_argument("--registry-file", default="")
    r.add_argument("--out", required=True)
    t = sub.add_parser("timecheck")
    t.add_argument("--config", required=True)
    t.add_argument("--latency", required=True)
    t.add_argument("--witness", required=True)
    t.add_argument("--receipt", required=True)
    t.add_argument("--expect-open", default="")
    t.add_argument("--out", default="")
    b = sub.add_parser("rollback")
    b.add_argument("--config", required=True)
    b.add_argument("--root-dir", required=True)
    b.add_argument("--archive-dir", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "derive-config":
        cfg = derive_config(args.plan, args.src, args.signatures, args.out)
        print(json.dumps({"config": args.out,
                          "parent_binding_sha256":
                          cfg["parent_binding_sha256"]}, sort_keys=True))
        return 0
    if args.cmd == "gate":
        print(json.dumps(gate(args.src, args.plan, args.signatures,
                              args.registry_file), sort_keys=True))
        return 0
    if args.cmd == "run-case":
        plan = _load(args.plan)
        dirs = _overlay(args.overlay_dir) if args.overlay_dir \
            else _live_dirs(plan)
        receipt = run_case(args.config, args.plan, args.signatures,
                           args.case, dirs, args.out,
                           registry_file=args.registry_file)
        print(json.dumps({"case": args.case,
                          "timecheck": receipt["timecheck"].get("verdict"),
                          "sends": receipt["sends"],
                          "overlay": receipt["overlay"]}, sort_keys=True))
        return 0
    if args.cmd == "timecheck":
        verdict = timecheck(args.config, args.latency, args.witness,
                            receipt_path=args.receipt,
                            expect_open=args.expect_open or None)
        if args.out:
            json.dump(verdict, open(args.out, "w"), sort_keys=True,
                      indent=1)
        print(json.dumps(verdict, sort_keys=True))
        return 0 if verdict.get("verdict") in ("accept", "accept-open") \
            else 3
    if args.cmd == "rollback":
        report = rollback(args.config, args.root_dir, args.archive_dir)
        print(json.dumps({"archive": args.archive_dir,
                          "witness_archived":
                          report["witness_archived"]}, sort_keys=True))
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StageCFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
