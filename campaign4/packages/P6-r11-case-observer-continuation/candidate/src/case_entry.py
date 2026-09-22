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
              "cases": plan.get("cases", {c: {} for c in CASES}),
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
        got = sig.get("candidate_" + name.replace(".py", "") + "_sha256")
        if not got or got != want:
            raise StageCFault("E_TOOL_CHANGED",
                              "candidate %s hash missing or not bound by "
                              "signature; fail-closed, never defaulted"
                              % name)
    r3want = sig.get("r3_harness_sha256")
    if not r3want:
        raise StageCFault("E_TOOL_CHANGED",
                          "R3 revision hash missing from signature")
    r3base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "r3harness")
    with open(os.path.join(r3base, "harness.py"), "rb") as fh:
        if hashlib.sha256(fh.read()).hexdigest() != r3want:
            raise StageCFault("E_TOOL_CHANGED",
                              "R3 working copy changed since signature")
    # D4/HC4.3 transitive execution surface: every invoked module and
    # wrapper beyond entry/candidate/R3 must be hash-bound too.
    _here = os.path.dirname(os.path.abspath(__file__))
    for rel, key in (("fixture_control.py", "fixture_control_sha256"),
                     ("fixture-wake-deposit", "deposit_sha256"),
                     ("seat_emulator.py", "seat_emulator_sha256"),
                     ("fault_onset.py", "fault_onset_sha256")):
        with open(os.path.join(_here, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if not sig.get(key) or sig.get(key) != got:
            raise StageCFault("E_TOOL_CHANGED",
                              "%s missing or drifted since signature" % rel)
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
    committed = set(receipt.get("committed_actions", []))
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
        if w.get("ack") is not True or (action not in settled
                                        and action not in committed):
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
                  vkey=None, wa=None, va=None, unit=None, case="stagec"):
    t = _plan_templates()
    if wa is None:
        wa, va = plan["actions"]["worker"], plan["actions"]["verifier"]
        unit = plan.get("timer_unit")
    seats = [config["worker"]["title"], config["verifier"]["title"]]
    wsid, vsid = (config["worker"]["session_id"],
                  config["verifier"]["session_id"])
    if stream_dir is None:  # overlay layout: one dir, sid-named files
        stream_dir, wkey, vkey = dirs["stream"], wsid, vsid
    # Signed-grant bounds may be narrowed by the authorized plan (e.g.
    # small-grant candidate tests through the same production path).
    # wait_s stays pinned at 8: it is a legacy observation slice, never
    # the observation bound (harness derives that from the signed grant
    # via _observe_until), so narrowing grants cannot smuggle in a magic
    # constant change.
    pover = plan.get("bounds") or {}
    cplan = {"fixture_id": "p6-stagec-" + case, "package_id": "P6C",
             "worker_action": wa, "verify_action": va,
             "seats": {"fixture_seats": seats},
             "allowlist": {"seats": seats,
                           "timer_units": {wa: unit},
                           "wake_path": dirs["wake_shim"],
                           "systemd_run": dirs["systemd_shim"],
                           "systemctl": dirs["systemctl_shim"]},
             "bounds": {"duration_s": pover.get("duration_s", 900),
                        "verify_window_s": pover.get("verify_window_s",
                                                     600),
                        "wait_s": 8,
                        "escalation_window_s": pover.get(
                            "escalation_window_s", 120),
                        "stream_dir": stream_dir,
                        "onset_dir": dirs["onsets"],
                        "artifact_base_dir": dirs["art"],
                        "latency_path": dirs["latency"]},
             "live_stop_utc": plan.get("live_stop_utc"),
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


def _cli(cmd, env_extra=None, timeout=240):
    """Exact CLI invocation helper: returns (rc, parsed-stdout-or-raw).
    All candidate/witness interaction in run_case flows through real
    subprocess CLIs — never direct imports (H4.1)."""
    import subprocess as _sp
    env = dict(os.environ)
    env.update(env_extra or {})
    proc = _sp.run(cmd, capture_output=True, text=True, timeout=timeout,
                   env=env)
    try:
        return proc.returncode, json.loads(proc.stdout or "")
    except ValueError:
        return proc.returncode, {"raw": proc.stdout,
                                 "stderr": proc.stderr}


def _raise_for_harness_error(out, where):
    """Propagate a structured harness authority/routing failure BEFORE any
    timing or case-acceptance gate. A harness CLI error result carries
    {"error": CODE, "detail": ...} with NO "decision" key; surfacing its
    actual code/reason preserves the cause the controller needs instead of
    masking it as missing timing evidence. Results WITH a "decision" key
    (verified-rejection, transition-committed, terminal-rest, owned
    outcomes) are legitimate harness results and pass through untouched."""
    if isinstance(out, dict) and "decision" not in out and out.get("error"):
        code = out.get("error") or "E_HARNESS"
        detail = out.get("detail") or "harness CLI failure"
        raise StageCFault(code, "%s: %s" % (where, detail))


def _r3harness_cli():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "r3harness", "harness.py")


def _witness_cli():
    return os.path.join(P6R6_SRC, "witness_timing.py")


def _wstream(stream_dir, key):
    return os.path.join(stream_dir, key + ".jsonl")


def _r3_hash_check():
    """Manifest-bound R3 revision gate: the working copy must match
    R3_REVISION.json, and the pinned parent bytes must match too
    (retained/compared, never edited)."""
    rev = _load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "r3harness", "R3_REVISION.json"))
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "r3harness")
    parent = ("/home/bmosher/memory-bake-off/campaign4/packages/"
              "P6-r5-launch-binding/src")
    parent = os.path.normpath(parent)  # layout adaptation only
    for name, rec in rev.get("files", {}).items():
        with open(os.path.join(base, name), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != rec.get("copy_sha256"):
            raise StageCFault("E_R3_DRIFT",
                              "R3 working copy %s drifted" % name)
        with open(os.path.join(parent, name), "rb") as fh:
            pg = hashlib.sha256(fh.read()).hexdigest()
        if pg != rec.get("parent_sha256"):
            raise StageCFault("E_CORE_DRIFT",
                              "pinned parent %s changed" % name)
    return rev.get("revision", "R3")


def _kv_rows(db_path):
    """Read-only durable evidence: driver_kv from the case database."""
    import sqlite3 as _sq
    try:
        con = _sq.connect("file:%s?mode=ro" % db_path, uri=True)
    except Exception:
        return {}
    try:
        rows = con.execute("select key, value from driver_kv").fetchall()
    except Exception:
        rows = []
    try:
        con.close()
    except Exception:
        pass
    return dict(rows)


def _maybe_apply_corrupt_tamper(cdirs, manifest, db_path, intervention,
                                claim):
    """Post-commit fault gate (corrupt-after-worker): apply the armed
    artifact tamper only after the worker handoff durably committed.
    Returns the tamper record, or None when the fault must wait (claim
    observed but commit absent) or does not apply. Never tampers on
    claim observation alone: see _commit_present."""
    import fixture_control as _fc
    if (intervention or {}).get("control") != "corrupt-after-worker":
        return None
    if (claim or {}).get("outcome") != "completed":
        return None
    if not _commit_present(db_path, manifest["action_id"],
                           manifest["execution_id"]):
        return None
    return _fc.apply_artifact_control(cdirs["art"], intervention)


def _commit_present(db_path, action, execution):
    """True iff the durable ledger records handoff-done for
    (action, execution). The commit record is written only after claim
    validation + artifact recompute + ledger drive, so its presence
    proves the handoff already consumed the pre-fault artifacts. A
    post-commit fault (e.g. corrupt-after-worker) must wait for this,
    never for mere claim-file observation: the producer publishes
    artifact -> claim -> end sequentially, and a claim-observed tamper
    can land between publication and the handoff's recompute, failing
    the worker handoff it was meant to follow."""
    try:
        kv = _kv_rows(db_path)
    except Exception:
        return False
    return bool(kv.get("handoff-done:%s:%s" % (action, execution)))


def _sends_from_kv(kv):
    """Transport-level send evidence from durable msg records (never a
    shim trace): per-seat counts plus per-message states."""
    sends, states = {}, {}
    for key, value in kv.items():
        if not key.startswith("msg:"):
            continue
        try:
            rec = json.loads(value)
        except ValueError:
            continue
        seat = rec.get("seat")
        sends[seat] = sends.get(seat, 0) + 1
        states[key] = {"state": rec.get("state"),
                       "action": rec.get("action"),
                       "execution": rec.get("execution")}
    return sends, states


def _msg_count_kv(kv):
    return sum(1 for k in kv if k.startswith("msg:"))


def _only_ambiguous_pending(db_path, detail):
    """True iff every outstanding intent's sent message is in ambiguous
    state (un-settleable by design). Any sent/queued/delivered-but-
    unsettled intent, or any unreadable evidence, returns False."""
    import re as _re
    oids = _re.findall(r"outbox-pending:(ob-[0-9a-f]+)", detail or "")
    if not oids:
        return False
    try:
        kv = _kv_rows(db_path)
    except Exception:
        return False
    for oid in oids:
        mid = kv.get("outbox-sent:" + oid)
        if not mid:
            return False
        try:
            rec = json.loads(kv.get("msg:" + mid, "") or "{}")
        except ValueError:
            return False
        if rec.get("state") != "ambiguous":
            return False
    return True


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


def _committed_actions(kv, manifest):
    """H3.2 positive evidence beyond transport ack: durable ledger commit
    (handoff-done) for this execution. An ambiguous send can never
    transport-settle, but a committed handoff with verified claim and
    recomputed artifacts is actual recorded positive evidence — never
    absence-of-false."""
    got = []
    for action, execution in ((manifest["action_id"],
                              manifest["execution_id"]),
                             (manifest["verify_action_id"],
                              manifest["verify_execution_id"])):
        if kv.get("handoff-done:%s:%s" % (action, execution)):
            got.append(action)
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


# --- fault protocol (R1) -----------------------------------------------------------
FAULT_CONTROLS = ("none-declared", "hold-verifier-texts",
                  "corrupt-after-worker", "transport-queued-first",
                  "delay-worker-completion")
FAULT_CASES = ("lost-completion", "failed-verification",
               "queued-ambiguous-restart")


def _now_z():
    import time as _t
    return _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime())


def fault_arm(case, run_root, control, actor, params=None):
    """Executable fault intervention (R1): records WHAT fault, for WHICH
    future isolated fixture, applied by WHOM and WHEN — before any send.
    Controls touch only the future isolated fixture (mode/intervention
    files under the run root); never production seats or shared
    transports. A transport fault is labelled induced; true underlying
    receipts are preserved by the transport and asserted, never replaced.
    Missing/failed intervention is INCOMPLETE/FAIL downstream, never a
    passing fault case."""
    if case not in CASES:
        raise StageCFault("E_CASE", "case %r not enumerated" % case)
    if control not in FAULT_CONTROLS:
        raise StageCFault("E_CONTROL",
                          "control %r not an executable control" % control)
    if not actor:
        raise StageCFault("E_ACTOR", "responsible actor required")
    rec = {"case": case, "control": control, "actor": actor,
           "armed_at": _now_z(), "params": params or {},
           "induced": control != "none-declared",
           "scope": "future isolated fixture only"}
    fdir = os.path.join(run_root, "faults")
    os.makedirs(fdir, exist_ok=True)
    with open(os.path.join(fdir, case + ".json"), "w") as fh:
        json.dump(rec, fh, sort_keys=True, indent=1)
    return rec


def fault_show(run_root, case):
    return _load(os.path.join(run_root, "faults", case + ".json"))


def _carry_bindings(config, suite_root, case, db_path, stream_dir, wkey,
                  vkey, verify_action):
    """R2 continuity without cross-case authority: turn bindings recorded
    as evidence by EARLIER completed cases in the same suite are restored
    into this case's database through the production bind_turn API (fresh
    interpreter, R3 copy). Foreign ends are then recognized as bound to
    other executions and skipped — never adopted as first-observation
    binds. Only completed (accept/accept-open) receipts contribute; values
    are recorded facts, never invented."""
    import subprocess as _sp
    carried = []
    for other in sorted(os.listdir(suite_root)):
        if other == case:
            continue
        rpath = os.path.join(suite_root, other, "receipt.json")
        if not os.path.exists(rpath):
            continue
        try:
            rec = json.load(open(rpath))
        except ValueError:
            continue
        if rec.get("timecheck", {}).get("verdict") not in ("accept",
                                                           "accept-open"):
            continue
        for action, execution in (rec.get("executions") or {}).items():
            item = rec.get("worker_item") if action != rec.get(
                "verify_action", verify_action) else rec.get(
                    "verifier_item")
            if not item:
                continue
            key = vkey if action == rec.get("verify_action",
                                            verify_action) else wkey
            step = "verify-run" if action == rec.get(
                "verify_action", verify_action) else "worker-run"
            code = ("import sys; sys.path.insert(0, %r); "
                    "from driver import Driver; "
                    "from host_adapter import HostAdapter; "
                    "d = Driver(%r); a = HostAdapter(d); "
                    "a.bind_turn(%r, %r, %r, %r, %r); d.close()"
                    % (os.path.join(os.path.dirname(os.path.abspath(
                        __file__)), "r3harness"), db_path, key, item,
                        execution, action, step))
            proc = _sp.run([sys.executable, "-c", code],
                           capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                raise StageCFault("E_BIND_CARRY",
                                  "binding restore failed: %s"
                                  % (proc.stderr or "")[:200])
            carried.append({"action": action, "execution": execution,
                            "item": item})
    return carried


def _check_causal(intervention, onsets_dir, det_by_action, worker_action):
    """R1.3 causal order: armed intervention predates independent onset,
    onset predates observer detection — each comparison incorporating the
    recorded finite uncertainty (second-resolution stamps included).
    Violations are FAIL, never pass."""
    onset_path = None
    for f in sorted(os.listdir(onsets_dir)):
        if f.endswith(".json") and not f.endswith(".marker.json"):
            onset_path = os.path.join(onsets_dir, f)
            break
    if onset_path is None:
        raise StageCFault("E_NO_ONSET",
                          "fault case has no independent onset; INCOMPLETE")
    try:
        rec = json.load(open(onset_path))
        onset = rec.get("onset_at")
        unc = rec.get("uncertainty_s")
    except ValueError:
        onset, unc = None, None
    if not onset or not intervention.get("armed_at"):
        raise StageCFault("E_NO_ONSET", "onset/intervention time missing")
    if not isinstance(unc, (int, float)) or unc < 0:
        raise StageCFault("E_NO_ONSET", "onset uncertainty unbounded")
    import datetime as _dt
    o, a = _instant(onset), _instant(intervention["armed_at"])
    # Order is guaranteed by process sequence (arm CLI completes before
    # run-case starts); same-second equality is stamp truncation, but any
    # armed-after-onset still fails.
    if o is None or a is None or not (a <= o):
        raise StageCFault("E_CAUSAL",
                          "intervention not before onset: %s vs %s"
                          % (intervention["armed_at"], onset))
    det = det_by_action.get(worker_action)
    if det is not None:
        d = _instant(det)
        if d is None or (d - o).total_seconds() < -unc:
            raise StageCFault("E_CAUSAL",
                              "onset not before detection "
                              "(beyond uncertainty): %s vs %s"
                              % (onset, det))
    return {"armed_at": intervention["armed_at"], "onset_at": onset,
            "detected_at": det}


def run_case(config_path, plan_path, sig_path, case, suite_root, out_path,
             registry_file="", simulated=False):
    """R1/R2/H1/H4 entry. Suite root holds immutable per-case subroots;
    runtime streams/sockets stay the actual launch-bound paths (shared
    across cases, never case-invented). Per-case actions/executions/db/
    claims/artifacts/receipts/manifest/onset/latency/witness/timer-units
    derive from the signed plan/config. The candidate runs ONLY through
    its real subprocess CLIs (R3 copy); sends count from durable kv msg
    records; items resolve from observed records; fault cases require an
    armed intervention whose armed_at predates onset (causal order)."""
    _r3_hash_check()  # bound R3 revision verified before any effect
    g = gate(config_path, plan_path, sig_path, registry_file)  # mandatory
    config, plan = _load(config_path), _load(plan_path)
    spec = (config.get("cases") or {}).get(case)
    if spec is None:
        raise StageCFault("E_CASE", "case %r not enumerated" % case)
    wa, va, unit = (spec["worker_action"], spec["verifier_action"],
                    spec["timer_unit"])
    croot = os.path.join(suite_root, case)
    if os.path.exists(out_path):
        prior = _load(out_path)
        if prior.get("timecheck", {}).get("verdict") in ("accept",
                                                         "accept-open"):
            raise StageCFault("E_SEALED",
                              "case %s evidence sealed; replay inside the "
                              "original run only" % case)
    faults_dir = os.path.join(suite_root, "faults")
    intervention = None
    ipath = os.path.join(faults_dir, case + ".json")
    if os.path.exists(ipath):
        intervention = json.load(open(ipath))
    if case in FAULT_CASES and intervention is None:
        raise StageCFault("E_NO_INTERVENTION",
                          "fault case %s has no armed intervention; "
                          "INCOMPLETE, never passing" % case)
    # NOTE: no interference guard here by design — a faulted clean case
    # (e.g. hold armed on positive-handoff) must RUN and fail on its
    # outcome assertions and provenance gate, producing evidence, not
    # be rejected up front. Adversarial tests rely on this.
    cdirs = {"root": croot,
             "claims": os.path.join(croot, "claims"),
             "art": os.path.join(croot, "art"),
             "onsets": os.path.join(croot, "onsets"),
             "msgs": os.path.join(croot, "msgs"),
             "outbox": os.path.join(croot, "outbox"),
             "inbox": os.path.join(croot, "inbox")}
    for d in cdirs.values():
        os.makedirs(d, exist_ok=True)
    if simulated:
        sim = {"stream": os.path.join(suite_root, "sim", "stream"),
               "bin": os.path.join(suite_root, "sim", "bin"),
               "trace": os.path.join(suite_root, "sim", "trace.log"),
               "msgs": cdirs["msgs"]}
        os.makedirs(sim["stream"], exist_ok=True)
        child_extra = {"PATH": sim["bin"] + ":" + os.environ.get("PATH",
                                                                 ""),
                       "TRACE": sim["trace"], "MSGDIR": cdirs["msgs"],
                       "FAULT_ROOT": faults_dir,
                       "FIXTURE_OUTBOX": cdirs["outbox"]}
        # Pass-through only: an externally-set FAULT_CASE lets test
        # executables honor the armed intervention; the tool never sets
        # it, reads the intervention file itself, and live ignores it.
        if os.environ.get("FAULT_CASE"):
            child_extra["FAULT_CASE"] = os.environ["FAULT_CASE"]
        stream_dir, wkey, vkey = _signed_stream_binding(config, True, sim)
    else:
        sim = None
        child_extra = {"MSGDIR": cdirs["msgs"], "FAULT_ROOT": faults_dir,
                       "FIXTURE_OUTBOX": cdirs["outbox"]}
        stream_dir, wkey, vkey = _signed_stream_binding(config, False, {})
        root = os.path.dirname(config["worker"].get("stream_path") or "")
        if not root or not os.path.isdir(root):
            raise StageCFault("E_HOST_PATH",
                              "signed producer root absent: %r" % (root,))
    pdirs = _plan_dirs(plan, cdirs, sim)
    wsid, vsid = (config["worker"]["session_id"],
                  config["verifier"]["session_id"])
    wtitle, vtitle = (config["worker"]["title"],
                      config["verifier"]["title"])
    cplan_path = os.path.join(croot, "candidate-plan.json")
    cplan, _, _ = _candidate_plan(config, plan, pdirs,
                                  stream_dir=stream_dir, wkey=wkey,
                                  vkey=vkey, wa=wa, va=va, unit=unit,
                                  case=case)
    json.dump(cplan, open(cplan_path, "w"), sort_keys=True)
    import hashlib as _hl
    phash = _hl.sha256(open(cplan_path, "rb").read()).hexdigest()
    manifest_path = os.path.join(croot, "manifest.json")
    r3 = _r3harness_cli()
    db_path = os.path.join(croot, "fixture.db")
    rc, setup_out = _cli(
        [sys.executable, r3, "--plan", cplan_path, "--manifest",
         manifest_path, "--session", wsid, "--stream-key", wkey,
         "--worker-stream-key", wkey, "--verifier-stream-key", vkey,
         "setup"], child_extra)
    if rc != 0:
        raise StageCFault("E_SETUP",
                          "candidate setup failed: %s" % (setup_out,))
    manifest = json.load(open(manifest_path))
    carried = _carry_bindings(config, suite_root, case,
                             os.path.join(croot, "fixture.db"), stream_dir,
                             wkey, vkey, manifest["verify_action_id"])
    if simulated:  # simulated surface only; host never touches runtime
        for key in (wkey, vkey):
            p = os.path.join(stream_dir, key + ".jsonl")
            if not os.path.exists(p):
                open(p, "w").close()
    live_args = ["--live", "--plan", cplan_path, "--plan-hash", phash,
                 "--allowlist-seat", wtitle, "--allowlist-seat", vtitle,
                 "--db", db_path, "--manifest", manifest_path, "--claims",
                 cdirs["claims"], "--qid", "P6C"]
    # R1/D3 executing consumer: notification-primary deliver loop, run
    # HERE on the real host path in every branch. Attaches the existing
    # DirNotifier BEFORE the initial drain, drains, then waits on
    # notifications with bounded timeouts — no bespoke polling loop.
    # Reopen reconciliation runs first: prior intents reconcile from the
    # append-only journal without blind resends.
    import threading as _th
    import fixture_control as _fc
    applied = []
    tampered = {}
    deliver_error = []
    stop_delivery = _th.Event()
    live_wake = None if simulated else pdirs.get("live_wake")
    bindings = {wtitle: {"role": "worker",
                         "action": manifest["action_id"],
                         "execution": manifest["execution_id"]},
                vtitle: {"role": "verifier",
                         "action": manifest["verify_action_id"],
                         "execution": manifest["verify_execution_id"]}}

    def _deliver_loop():
        try:
            _fc.reconcile_journal(cdirs["outbox"], cdirs["inbox"], croot)
        except _fc.ControlFault as e:
            deliver_error.append({"code": e.code, "detail": e.detail})
            return
        while not stop_delivery.is_set():
            try:
                if not _fc.wait_for_deposits(cdirs["outbox"], croot, 5.0):
                    continue
                recs = _fc.deliver_pending(
                    cdirs["outbox"], cdirs["inbox"], intervention,
                    bindings, croot, live_wake=live_wake,
                    run_cwd=croot)
                applied.extend(recs)
            except _fc.ControlFault as e:
                deliver_error.append({"code": e.code,
                                      "detail": e.detail})
                return
            if intervention is not None and \
                    intervention.get("control") == "corrupt-after-worker" \
                    and not tampered.get("done"):
                wclaim = os.path.join(cdirs["claims"],
                                      manifest["execution_id"] + ".json")
                try:
                    claim = json.load(open(wclaim))
                except (OSError, ValueError):
                    claim = {}
                if claim.get("outcome") == "completed":
                    try:
                        rec = _maybe_apply_corrupt_tamper(
                            cdirs, manifest, db_path, intervention, claim)
                    except _fc.ControlFault as e:
                        deliver_error.append({"code": e.code,
                                              "detail": e.detail})
                        return
                    if rec is not None:
                        tampered["rec"] = rec
                        tampered["done"] = True

    deliverer = _th.Thread(target=_deliver_loop, daemon=True)
    deliverer.start()
    try:
        rc, out = _cli([sys.executable, r3] + live_args + ["run-fixture"],
                       child_extra)
    except Exception:
        stop_delivery.set()
        deliverer.join(timeout=30)
        raise
    if deliver_error:
        raise StageCFault(deliver_error[0]["code"],
                          deliver_error[0]["detail"])
    if rc not in (0, 3) or not isinstance(out, dict):
        _stop_deliverer()
        raise StageCFault("E_CANDIDATE",
                          "run-fixture usage failure: %s" % (out,))
    def _provenance_gate():
        # Fail-closed provenance: every resolved end must trace to a
        # delivery record for its (seat, execution). Pre-planted ends
        # the candidate alone would adopt are rejected here, never
        # certified. Runs before any case-specific assertions.
        import fixture_control as _fcx
        found = {}
        for sid, path in ((wsid, _wstream(stream_dir, wkey)),
                          (vsid, _wstream(stream_dir, vkey))):
            try:
                found[sid] = _resolve_item(path, cdirs["onsets"])
            except StageCFault:
                found[sid] = None
        for (seat, execution, sid) in (
                (wtitle, manifest["execution_id"], wsid),
                (vtitle, manifest["verify_execution_id"], vsid)):
            if found[sid] is not None and not _fcx.check_delivered(
                    applied, seat, execution):
                raise StageCFault("E_UNDELIVERED",
                                  "produced end for %s has no delivery "
                                  "record; forged or out-of-band "
                                  "production rejected" % (seat,))
        return found

    items = _provenance_gate()
    extra = {}

    def _rerun_cli():
        rc, res = _cli([sys.executable, r3] + live_args + ["run-fixture"],
                       child_extra)
        try:
            _raise_for_harness_error(res, "rerun run-fixture")
        except StageCFault:
            _stop_deliverer()
            raise
        return rc, res

    def _reattach_cli():
        # R3 reattach: consume late completion under the same
        # action/execution with zero new sends (tool-applied recovery).
        rc, res = _cli([sys.executable, r3] + live_args + ["reattach"],
                       child_extra)
        try:
            _raise_for_harness_error(res, "reattach")
        except StageCFault:
            _stop_deliverer()
            raise
        return rc, res

    def _stop_deliverer():
        stop_delivery.set()
        deliverer.join(timeout=30)
        if deliver_error:
            raise StageCFault(deliver_error[0]["code"],
                              deliver_error[0]["detail"])

    # Routing/authority errors from the harness surface here, before
    # provenance/timing/case gates can mask them as missing evidence.
    try:
        _raise_for_harness_error(out, "run-fixture")
    except StageCFault:
        _stop_deliverer()
        raise

    def _kv():
        return _kv_rows(db_path)

    def _grant_remaining_s(action, execution, margin_s=5.0):
        """Remaining seconds on the ORIGINAL signed grant (r3 resume
        facts persisted at first dispatch), minus a margin for the
        reattach to observe. Never extends, never invents:
        absent/malformed facts read as no remaining grant."""
        import datetime as _dt
        try:
            raw = _kv().get("r3:%s:%s:verify_deadline" % (action,
                                                           execution))
            end = _dt.datetime.strptime(
                raw, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=_dt.timezone.utc)
            now = _dt.datetime.now(_dt.timezone.utc)
            return (end - now).total_seconds() - margin_s
        except Exception:
            return 0.0

    if case == "positive-handoff":
        # Normal slow turn: the first bounded slice may miss a late end
        # while the signed grant remains valid. The observer then
        # explicitly reattaches the SAME action/execution (zero new
        # sends, original absolute grant preserved) and observes the
        # remainder. A normal delayed completion commits as
        # transition-committed -- never reclassified as a recovery. An
        # expired grant stays an honest owned failure, never success.
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            if out.get("reason") == "no-end" and _grant_remaining_s(
                    manifest["action_id"],
                    manifest["execution_id"]) > 0:
                n_msg = _msg_count_kv(_kv())
                rc_r, out_r = _reattach_cli()
                if (out_r.get("decision")
                        if isinstance(out_r, dict) else None) in (
                            "transition-committed", "terminal-rest"):
                    if _msg_count_kv(_kv()) != n_msg + 1:
                        _stop_deliverer()
                        raise StageCFault("E_SENDS",
                                          "reattach resent worker traffic")
                    out = dict(out_r, worker=out_r.get("worker", out))
                else:
                    _stop_deliverer()
                    raise StageCFault("E_CASE_FAIL",
                                      "positive reattach did not commit "
                                      "under valid grant: %s" % (out_r,))
            else:
                _stop_deliverer()
                raise StageCFault(
                    "E_CASE_FAIL",
                    "positive case did not commit: %s" % (out,))
    elif case == "lost-completion":
        # Real lost worker-completion signal: the first bounded wait
        # expires with no end (owned-failure, never false success);
        # the tool then applies bounded reattach recovery, which must
        # consume the late end exactly once with zero worker resends.
        if out.get("decision") != "owned-failure" or \
                out.get("reason") != "no-end":
            _stop_deliverer()
            raise StageCFault("E_CASE_FAIL",
                              "lost case must first miss the bound end: %s"
                              % (out,))
        n_msg = _msg_count_kv(_kv())
        oids = sorted(k for k in _kv() if k.startswith("outbox-sent:"))
        rc_r, out_r = _reattach_cli()
        if (out_r.get("decision") if isinstance(out_r, dict) else None) \
                not in ("transition-committed", "terminal-rest"):
            _stop_deliverer()
            raise StageCFault("E_CASE_FAIL",
                              "reattach did not recover the late end: %s"
                              % (out_r,))
        kv_r = _kv()
        if _msg_count_kv(kv_r) != n_msg + 1:
            _stop_deliverer()
            raise StageCFault("E_SENDS",
                              "reattach resent worker traffic")
        for oid in oids:
            if kv_r.get(oid) != _kv().get(oid):
                _stop_deliverer()
                raise StageCFault("E_SENDS",
                                  "reattach mutated prior send identity")
        wclaim = os.path.join(cdirs["claims"],
                              manifest["execution_id"] + ".json")
        if not os.path.exists(wclaim):
            _stop_deliverer()
            raise StageCFault("E_CASE_FAIL",
                              "worker evidence not retained")
        extra["first_run"] = out
        extra["reattached"] = True
        out = dict(out_r, worker=out_r.get("worker", out))
    elif case == "failed-verification":
        if out.get("decision") == "COMPLETE" or \
                manifest.get("disposition") == "COMPLETE":
            raise StageCFault("E_CASE_FAIL",
                              "failed check must never close COMPLETE")
        # Shared NORMAL observer continuation (same as positive-handoff):
        # first slice may miss late end while original grant remains valid.
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            if out.get("reason") == "no-end" and _grant_remaining_s(
                    manifest["action_id"],
                    manifest["execution_id"]) > 0:
                n_msg = _msg_count_kv(_kv())
                rc_r, out_r = _reattach_cli()
                if (out_r.get("decision")
                        if isinstance(out_r, dict) else None) in (
                            "transition-committed", "terminal-rest",
                            "verified-rejection"):
                    if _msg_count_kv(_kv()) != n_msg + 1:
                        _stop_deliverer()
                        raise StageCFault("E_SENDS",
                                          "reattach resent worker traffic")
                    out = dict(out_r, worker=out_r.get("worker", out))
                    if out.get("decision") == "verified-rejection":
                        extra["verified_rejection"] = {
                            "expected": out.get("expected"),
                            "observed": out.get("observed"),
                            "reason": out.get("reason")}
                else:
                    _stop_deliverer()
                    raise StageCFault("E_CASE_FAIL",
                                      "failed-verification reattach did not "
                                      "commit under valid grant: %s" % (out_r,))
        if out.get("decision") == "COMPLETE" or \
                manifest.get("disposition") == "COMPLETE":
            _stop_deliverer()
            raise StageCFault("E_CASE_FAIL",
                              "failed check must never close COMPLETE")
    elif case == "queued-ambiguous-restart":
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "queued run did not commit: %s" % (out,))
        kv = _kv()
        states_all = _sends_from_kv(kv)[1]
        # Induced transport states live in the durable transport
        # receipts (kv msg: records written by the candidate transport's
        # deposit-time wake invocation: rc3+wake: => queued,
        # garbage-no-receipt => ambiguous), labeled induced via the armed
        # intervention. The executing consumer's applied delivery receipts
        # record inbox handoff, not transport classification, so they must
        # not be the sole source for transport-state kinds.
        applied_kinds = {a.get("receipt_state") for a in applied}
        transport_kinds = set(applied_kinds) | \
            {s.get("state") for s in states_all.values()}
        if "queued" not in transport_kinds:
            raise StageCFault("E_CASE_FAIL",
                              "no queued transport receipt observed; "
                              "induced fault missing, case INCOMPLETE")
        if "ambiguous" not in transport_kinds:
            raise StageCFault("E_CASE_FAIL",
                              "no ambiguous transport receipt observed; "
                              "induced fault missing, case INCOMPLETE")
        if not intervention.get("induced"):
            raise StageCFault("E_CASE_FAIL",
                              "queued/ambiguous receipts not labeled "
                              "induced; case INCOMPLETE")
        extra["transport_states"] = {
            "applied-%d" % i: {"state": a.get("receipt_state"),
                               "seat": a.get("seat"),
                               "induced": a.get("induced")}
            for i, a in enumerate(applied)}
        extra["transport_states"]["durable-receipts"] = {
            k: {"state": s.get("state"), "action": s.get("action"),
                "execution": s.get("execution")}
            for k, s in states_all.items()}
        n_msg = _msg_count_kv(kv)
        rc2, out2 = _rerun_cli()
        if (out2.get("decision") if isinstance(out2, dict) else None) != \
                "duplicate-end-ignored":
            raise StageCFault("E_CASE_FAIL",
                              "rerun not recognized duplicate: %s" % (out2,))
        if _msg_count_kv(_kv()) != n_msg:
            raise StageCFault("E_SENDS",
                              "rerun manufactured fresh sends/identities")
        out = dict(out2, worker=out,
                   outbox_settled=out.get("outbox_settled"),
                   worker_outbox=out.get("worker_outbox"),
                   verifier_outbox=out.get("verifier_outbox"))
    elif case == "quiet-rest":
        # Shared NORMAL observer continuation for setup commit.
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            if out.get("reason") == "no-end" and _grant_remaining_s(
                    manifest["action_id"],
                    manifest["execution_id"]) > 0:
                n_msg = _msg_count_kv(_kv())
                rc_r, out_r = _reattach_cli()
                if (out_r.get("decision")
                        if isinstance(out_r, dict) else None) in (
                            "transition-committed", "terminal-rest"):
                    if _msg_count_kv(_kv()) != n_msg + 1:
                        _stop_deliverer()
                        raise StageCFault("E_SENDS",
                                          "reattach resent worker traffic")
                    out = dict(out_r, worker=out_r.get("worker", out))
                else:
                    _stop_deliverer()
                    raise StageCFault("E_CASE_FAIL",
                                      "quiet-rest reattach did not commit "
                                      "under valid grant: %s" % (out_r,))
            else:
                _stop_deliverer()
                raise StageCFault(
                    "E_CASE_FAIL",
                    "quiet-rest setup run did not commit: %s"
                    % (out,))
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            _stop_deliverer()
            raise StageCFault("E_CASE_FAIL",
                              "quiet-rest setup run did not commit: %s"
                              % (out,))
        import time as _t
        before = (_sizes(_wstream(stream_dir, wkey),
                         _wstream(stream_dir, vkey)),
                  _msg_count_kv(_kv()))
        _t.sleep(3)
        if (_sizes(_wstream(stream_dir, wkey),
                   _wstream(stream_dir, vkey)),
                _msg_count_kv(_kv())) != before:
            raise StageCFault("E_CASE_FAIL",
                              "quiet rest showed spurious activity")
        rc2, out2 = _rerun_cli()
        if (out2.get("decision") if isinstance(out2, dict) else None) != \
                "duplicate-end-ignored":
            raise StageCFault("E_CASE_FAIL",
                              "rerun not recognized duplicate: %s" % (out2,))
        if _msg_count_kv(_kv()) != before[1]:
            raise StageCFault("E_SENDS",
                              "rerun manufactured fresh sends")
        out = dict(out2, worker=out,
                   outbox_settled=out.get("outbox_settled"),
                   worker_outbox=out.get("worker_outbox"),
                   verifier_outbox=out.get("verifier_outbox"))
    else:
        _stop_deliverer()
        raise StageCFault("E_CASE", "unknown case %r" % case)
    _stop_deliverer()
    kv = _kv()
    sends_all, states_all = _sends_from_kv(kv)
    sends = {"worker": sends_all.get(wtitle, 0),
             "verifier": sends_all.get(vtitle, 0)}
    if case == "positive-handoff":
        if not (sends["worker"] == 1 and sends["verifier"] == 1):
            raise StageCFault("E_SENDS",
                              "positive case needs 1+1 sends: %s" % (sends,))
    if case == "failed-verification":
        if not (sends["worker"] == 1 and sends["verifier"] == 1):
            raise StageCFault("E_SENDS",
                              "failed-verification needs 1+1 sends: %s"
                              % (sends,))
        if out.get("decision") == "verified-rejection":
            vr = extra.get("verified_rejection") or {}
            exp = vr.get("expected") or out.get("expected")
            obs = vr.get("observed") or out.get("observed")
            if exp:
                extra["verified_rejection"] = {
                    "expected": exp, "observed": obs,
                    "reason": vr.get("reason") or out.get("reason")}
            if not exp or not obs:
                raise StageCFault("E_CASE_FAIL",
                                  "verified rejection lacks hashes")
    items = {}
    for sid, path in ((wsid, _wstream(stream_dir, wkey)),
                      (vsid, _wstream(stream_dir, vkey))):
        try:
            items[sid] = _resolve_item(path, cdirs["onsets"])
        except StageCFault:
            items[sid] = None
    # R1-E fail-closed, before any evidence specifics: every resolved end
    # must trace to a delivery record for its (seat, execution).
    # Production without delivery — including pre-planted ends a
    # candidate alone would accept — is rejected here, never certified.
    import fixture_control as _fc2
    for (seat, execution, sid) in (
            (wtitle, manifest["execution_id"], wsid),
            (vtitle, manifest["verify_execution_id"], vsid)):
        if items[sid] is not None and not _fc2.check_delivered(
                applied, seat, execution):
            raise StageCFault("E_UNDELIVERED",
                              "produced end for %s has no delivery record; "
                              "forged or out-of-band production rejected"
                              % (seat,))
    if case == "lost-completion":
        wclaim = os.path.join(cdirs["claims"],
                              manifest["execution_id"] + ".json")
        if not os.path.exists(wclaim):
            raise StageCFault("E_CASE_FAIL",
                              "worker evidence not retained")
    applied_path = os.path.join(faults_dir, case + ".applied.json")
    _fc2.write_applied(
        applied_path, case, [manifest["action_id"],
                             manifest["verify_action_id"]],
        [manifest["execution_id"], manifest["verify_execution_id"]],
        intervention, applied, tampered.get("rec"),
        {k: v.get("state") for k, v in states_all.items()})
    wit_cli = _witness_cli()
    lat_path = os.path.join(croot, "latency.jsonl")
    wit_path = os.path.join(croot, "witness-rows.jsonl")
    lat_rows = [json.loads(l) for l in open(lat_path)
                if l.strip()] if os.path.exists(lat_path) else []
    det_by_action = {}
    for r in lat_rows:
        det_by_action[r.get("action")] = r.get("detected_at")
    for (action, execution, sid) in (
            (manifest["action_id"], manifest["execution_id"], wsid),
            (manifest["verify_action_id"],
             manifest["verify_execution_id"], vsid)):
        item = items[sid]
        if item is None:
            continue  # no observed end: join stays missing (INCOMPLETE)
        onset_file = os.path.join(cdirs["onsets"], item + ".json")
        ocmd = [sys.executable, wit_cli, "observe", "--stream",
                _wstream(stream_dir, wkey if sid == wsid else vkey),
                "--item", item, "--action", action, "--execution",
                execution, "--timeout-s", "5", "--out", wit_path]
        if os.path.exists(onset_file):
            ocmd += ["--onset-file", onset_file]
        rc_o, _ = _cli(ocmd, {"PATH": os.environ.get("PATH", "")})
        if rc_o != 0:
            raise StageCFault("E_WITNESS", "witness observe failed")
        _annotate_witness(
            wit_path, action, execution, case,
            action in _settled_actions(out, manifest) or action in
            _committed_actions(_kv(), manifest))
    rc_c, _ = _cli([sys.executable, r3, "--manifest", manifest_path,
                    "check-latency"], child_extra)
    cand_err = None if rc_c == 0 else "check-latency-rc%d" % rc_c
    receipt = {"case": case, "gate": g, "outcome": out,
               "sends": sends, "worker_item": items[wsid],
               "verifier_item": items[vsid],
               "carried_bindings": carried,
               "candidate_gate": cand_err or "pass",
               "intervention": intervention,
               "induced": bool(intervention and intervention.get("induced")),
               "applied_receipt": applied_path,
               "overlay": False, "simulated": bool(simulated),
               "verify_action": manifest["verify_action_id"],
               "committed_actions": _committed_actions(_kv(), manifest),
               "executions": {manifest["action_id"]:
                              manifest["execution_id"],
                              manifest["verify_action_id"]:
                              manifest["verify_execution_id"]},
                "settled_actions": _settled_actions(out, manifest),
                "transport_states": extra.get("transport_states", {})}
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, sort_keys=True, indent=1)
    if case in FAULT_CASES:
        receipt["causal"] = _check_causal(intervention, cdirs["onsets"],
                                          det_by_action, wa)
        with open(out_path, "w") as fh:
            json.dump(receipt, fh, sort_keys=True, indent=1)
    expect = manifest["verify_action_id"] if case == \
        "failed-verification" else None
    verdict = timecheck(config_path, lat_path, wit_path,
                        receipt_path=out_path, expect_open=expect)
    if case in ("positive-handoff", "lost-completion",
                "queued-ambiguous-restart", "quiet-rest"):
        if verdict.get("verdict") != "accept":
            raise StageCFault(
                "E_TIMECHECK",
                "%s timecheck did not accept: %s" % (case, verdict))
    else:
        if verdict.get("verdict") != "accept-open":
            raise StageCFault("E_CASE_FAIL",
                              "%s not provably open: %s" % (case, verdict))
    receipt["timecheck"] = verdict
    receipt["evidence_sha256"] = {
        name: _sha(os.path.join(croot, name))
        for name in ("latency.jsonl", "witness-rows.jsonl",
                     "manifest.json") if os.path.exists(
                         os.path.join(croot, name))}
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, sort_keys=True, indent=1)
    receipt.update(extra)
    return receipt


# --- rollback + verify-suite ---------------------------------------------------------
def rollback(config_path, suite_root, case_or_all, archive_dir):
    """Archive-before-disable per case: receipt+manifest+witness+latency
    copied first, then the R3 candidate rollback verifies each case db.
    Covers every case's effects (R2.5)."""
    import shutil as _sh
    config = _load(config_path)
    cases = [case_or_all] if case_or_all != "all" else list(
        (config.get("cases") or {}).keys()) or list(CASES)
    reports = {}
    for case in cases:
        croot = os.path.join(suite_root, case)
        adir = os.path.join(archive_dir, case)
        os.makedirs(adir, exist_ok=True)
        for name in ("receipt.json", "manifest.json", "witness-rows.jsonl",
                     "latency.jsonl", "candidate-plan.json"):
            src = os.path.join(croot, name)
            if os.path.exists(src):
                _sh.copy(src, os.path.join(adir, name))
        r3 = _r3harness_cli()
        rc, out = _cli([sys.executable, r3, "--db",
                        os.path.join(croot, "fixture.db"), "--manifest",
                        os.path.join(croot, "manifest.json"), "rollback",
                        "--archive-dir", adir], {})
        if rc != 0:
            # Open recoveries keep un-acked intents BY CANDIDATE DESIGN
            # (settlement requires full commit; ambiguous sends never
            # settle; nothing is forged here). Evidence is already
            # archived above; the block is recorded explicitly. Injected
            # scope has no live seats/timers to disable beyond this.
            # Anything settleable-but-unsettled still fails hard.
            rec = {}
            try:
                rec = json.load(open(os.path.join(croot, "receipt.json")))
            except (OSError, ValueError):
                pass
            retainable = rec.get("timecheck", {}).get("verdict") in (
                "accept-open",)
            if not retainable and isinstance(out, dict) and \
                    "outstanding intents remain" in out.get("detail", ""):
                retainable = _only_ambiguous_pending(
                    os.path.join(croot, "fixture.db"),
                    out.get("detail", ""))
            if retainable:
                out = dict(out, retained_as_evidence=True,
                           note="intents outstanding by design (open "
                                "recovery or induced ambiguous send); "
                                "evidence archived; no live effects remain "
                                "in injected scope")
                with open(os.path.join(adir, "rollback-report.json"),
                          "w") as fh:
                    json.dump({"rollback": "archived-with-open-intents",
                               "case": case,
                               "candidate_error": out}, fh, sort_keys=True,
                              indent=1)
            else:
                raise StageCFault("E_ROLLBACK",
                                  "rollback failed for %s: %s" % (case, out))
        reports[case] = out
    with open(os.path.join(archive_dir, "rollback-report.json"),
              "w") as fh:
        json.dump({"cases": reports}, fh, sort_keys=True, indent=1)
    return reports


def verify_suite(suite_root, config_path):
    """R2.5 aggregate: all five cases exactly once on one suite root, each
    with matching per-case evidence, byte-exact preservation, and no
    cross-case authority. Re-runs each case timecheck through the real CLI.
    Returns PASS only if everything holds."""
    config = _load(config_path)
    cases = list((config.get("cases") or {}).keys()) or list(CASES)
    if sorted(cases) != sorted(CASES):
        raise StageCFault("E_SUITE",
                          "suite must enumerate exactly the five cases")
    seen_actions = {}
    results = {}
    for case in cases:
        croot = os.path.join(suite_root, case)
        receipt_path = os.path.join(croot, "receipt.json")
        receipt = _load(receipt_path)
        if receipt.get("case") != case:
            raise StageCFault("E_SUITE",
                              "receipt/case mismatch for %s" % case)
        # R1-E: applied receipt must exist and match this case's
        # actions/executions; a missing or mismatched application
        # record fails the suite even if everything else passed.
        applied = _load(receipt.get("applied_receipt") or "")
        if applied.get("case") != case or \
                sorted(applied.get("actions", [])) != sorted(
                    receipt.get("executions", {}).keys()) or \
                sorted(applied.get("executions", [])) != sorted(
                    receipt.get("executions", {}).values()):
            raise StageCFault("E_SUITE",
                              "applied receipt missing/mismatched for %s"
                              % case)
        for name, want in (receipt.get("evidence_sha256") or {}).items():
            if _sha(os.path.join(croot, name)) != want:
                raise StageCFault("E_SUITE",
                                  "evidence changed under %s/%s" % (case,
                                                                   name))
        lat_path = os.path.join(croot, "latency.jsonl")
        wit_path = os.path.join(croot, "witness-rows.jsonl")
        for path in (lat_path, wit_path):
            for line in open(path):
                if not line.strip():
                    continue
                action = json.loads(line).get("action")
                if action in seen_actions and seen_actions[action] != case:
                    raise StageCFault(
                        "E_CONTAMINATION",
                        "action %s in %s and %s" % (action,
                                                   seen_actions[action],
                                                   case))
                seen_actions[action] = case
        expect = receipt.get("verify_action") if case == \
            "failed-verification" else None
        rc, verdict = _cli(
            [sys.executable, os.path.abspath(__file__), "timecheck",
             "--config", config_path, "--latency", lat_path, "--witness",
             wit_path, "--receipt", receipt_path] +
            (["--expect-open", expect] if expect else []), {})
        if rc != 0:
            raise StageCFault("E_SUITE",
                              "timecheck failed for %s: %s" % (case,
                                                              verdict))
        results[case] = verdict.get("verdict")
    if sorted(results) != sorted(cases) or \
            any(v not in ("accept", "accept-open")
                for v in results.values()):
        raise StageCFault("E_SUITE", "incomplete suite: %s" % (results,))
    return {"suite": "PASS", "cases": results}


def _plan_dirs(plan, cdirs, sim=None):
    """Plan-doc inputs for _candidate_plan. The candidate's wake command is
    ALWAYS the fixture wake-deposit wrapper (signed path): transport sends
    deposit; seat notification happens exclusively in the deliver loop.
    Missing/unexecutable paths fail owned E_HOST_PATH, never KeyError."""
    import shutil as _sh
    if sim is not None:
        deposit = os.path.join(sim["bin"], "wake-deposit")
        if not (os.path.isfile(deposit) and os.access(deposit, os.X_OK)):
            raise StageCFault("E_HOST_PATH",
                              "test deposit wrapper missing: " + deposit)
        return {"wake_shim": deposit,
                "systemd_shim": os.path.join(sim["bin"], "systemd-run"),
                "systemctl_shim": os.path.join(sim["bin"], "systemctl"),
                "onsets": cdirs["onsets"], "art": cdirs["art"],
                "latency": os.path.join(cdirs["root"], "latency.jsonl")}
    try:
        cmds = plan["host_commands"]
    except KeyError as e:
        raise StageCFault("E_HOST_PATH",
                          "signed plan lacks host command %s" % (e,))
    deposit = cmds.get("deposit_wake") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixture-wake-deposit")
    for label, path in (("deposit_wake", deposit),
                        ("wake", cmds.get("wake", "")),
                        ("systemd_run", cmds.get("systemd_run", "")),
                        ("systemctl", cmds.get("systemctl", ""))):
        if not (path and os.path.isfile(path) and os.access(path, os.X_OK)):
            raise StageCFault("E_HOST_PATH",
                              "host command %s not executable: %s"
                              % (label, path))
    return {"wake_shim": deposit,
            "systemd_shim": cmds["systemd_run"],
            "systemctl_shim": cmds["systemctl"],
            "live_wake": cmds["wake"],
            "onsets": cdirs["onsets"], "art": cdirs["art"],
            "latency": os.path.join(cdirs["root"], "latency.jsonl")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r8 case entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("derive-config", "gate"):
        p = sub.add_parser(name)
        p.add_argument("--plan", required=True)
        p.add_argument("--binding", "--config", required=True, dest="src")
        p.add_argument("--signatures", required=True)
        p.add_argument("--registry-file", default="")
        p.add_argument("--out", required=name == "derive-config")
    f = sub.add_parser("fault")
    f.add_argument("op", choices=("arm", "show"))
    f.add_argument("--case", required=True)
    f.add_argument("--run-root", required=True)
    f.add_argument("--control", default="none-declared")
    f.add_argument("--actor", default="")
    r = sub.add_parser("run-case")
    r.add_argument("--config", required=True)
    r.add_argument("--plan", required=True)
    r.add_argument("--signatures", required=True)
    r.add_argument("--case", required=True)
    r.add_argument("--suite-root", required=True)
    r.add_argument("--simulated", action="store_true")
    r.add_argument("--registry-file", default="")
    r.add_argument("--out", default="")
    t = sub.add_parser("timecheck")
    t.add_argument("--config", required=True)
    t.add_argument("--latency", required=True)
    t.add_argument("--witness", required=True)
    t.add_argument("--receipt", required=True)
    t.add_argument("--expect-open", default="")
    t.add_argument("--out", default="")
    b = sub.add_parser("rollback")
    b.add_argument("--config", required=True)
    b.add_argument("--suite-root", required=True)
    b.add_argument("--case", default="all")
    b.add_argument("--archive-dir", required=True)
    v = sub.add_parser("verify-suite")
    v.add_argument("--suite-root", required=True)
    v.add_argument("--config", required=True)
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
    if args.cmd == "fault":
        if args.op == "arm":
            print(json.dumps(fault_arm(args.case, args.run_root,
                                       args.control, args.actor),
                             sort_keys=True))
        else:
            print(json.dumps(fault_show(args.run_root, args.case),
                             sort_keys=True))
        return 0
    if args.cmd == "run-case":
        out = args.out or os.path.join(args.suite_root, args.case,
                                       "receipt.json")
        receipt = run_case(args.config, args.plan, args.signatures,
                           args.case, args.suite_root, out,
                           registry_file=args.registry_file,
                           simulated=args.simulated)
        print(json.dumps({"case": args.case,
                          "timecheck": receipt["timecheck"].get("verdict"),
                          "sends": receipt["sends"],
                          "simulated": receipt["simulated"]},
                         sort_keys=True))
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
        reports = rollback(args.config, args.suite_root, args.case,
                           args.archive_dir)
        print(json.dumps({"archive": args.archive_dir,
                          "cases": sorted(reports)}, sort_keys=True))
        return 0
    if args.cmd == "verify-suite":
        print(json.dumps(verify_suite(args.suite_root, args.config),
                         sort_keys=True))
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StageCFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
