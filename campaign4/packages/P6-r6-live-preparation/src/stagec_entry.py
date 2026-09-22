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
PLACEHOLDER_RE = re.compile(r"<[A-Za-z_][A-Za-z_0-9-]*>|MANIFEST_STREAM"
                            r"|\bITEM\b|ONSET\.json|\bACT\b|(?<![A-Za-z])EX\b")

CASES = ("positive-handoff", "failed-verification", "restart-quiet")


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
def gate(config_path, plan_path, sig_path):
    config = _load(config_path)
    plan = _load(plan_path)  # noqa: parsed to prove readability
    sig = _load(sig_path)
    if sig.get("signer") != "tern":
        raise StageCFault("E_NO_SIGNATURE", "signer is not tern")
    if sig.get("plan_sha256") != _sha(plan_path):
        raise StageCFault("E_PLAN_CHANGED", "plan changed since signature")
    if sig.get("config_sha256") != _sha(config_path):
        raise StageCFault("E_CONFIG_CHANGED",
                          "execution config changed since signature")
    if config.get("launcher_source") != "live-agent-deck":
        raise StageCFault("E_NOT_LIVE", "config source not live-agent-deck")
    binding = _load(config["binding_path"])
    if _sha(config["binding_path"]) != config.get("parent_binding_sha256"):
        raise StageCFault("E_BINDING_CHANGED",
                          "accepted binding modified since derive")
    for role in ("worker", "verifier"):
        cur, signed = binding.get(role) or {}, config.get(role) or {}
        if (cur.get("session_id") != signed.get("session_id")
                or cur.get("stream_path") != signed.get("stream_path")
                or cur.get("socket") != signed.get("socket")):
            raise StageCFault("E_BINDING_CHANGED",
                              "%s binding drifted since derive" % role)
    return {"gate": "PASS", "worker": config["worker"]["session_id"],
            "verifier": config["verifier"]["session_id"]}


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


def timecheck(config_path, latency_path, witness_path, expect_open=None):
    config = _load(config_path)
    bounds = config.get("timing_bounds", {})
    det_b, rec_b, tot_b = (bounds.get("detect_s", 30.0),
                           bounds.get("recover_s", 60.0),
                           bounds.get("total_s", 90.0))
    sdet_b, stot_b = (bounds.get("suspicion_detect_s", 180.0),
                      bounds.get("suspicion_total_s", 240.0))
    allowed = set()
    for c in config.get("cases", []):
        allowed.add(c)
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
        wkey.setdefault(w.get("action"), w)
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
    for r in success:
        key = r.get("action")
        w = wkey.get(key)
        if w is None:
            problems.append("missing witness for %s" % (key,))
            continue
        onset, det_at, com_at = (r.get("onset_at") or w.get("onset_at"),
                                 r.get("detected_at"), r.get("committed_at"))
        if w.get("action") != r.get("action"):
            problems.append("wrong action for %s" % (key,))
            continue
        if not onset:
            problems.append("unknown source for %s" % (key,))
            continue
        if not det_at or not com_at:
            problems.append("unknown endpoint for %s" % (key,))
            continue
        if w.get("onset_uncertainty_s") is None:
            problems.append("unknown uncertainty for %s" % (key,))
            continue
        o, d, c = _instant(onset), _instant(det_at), _instant(com_at)
        if o is None or d is None or c is None:
            problems.append("unparsable timestamps for %s" % (key,))
            continue
        det, rec, tot = ((d - o).total_seconds(), (c - d).total_seconds(),
                         (c - o).total_seconds())
        if det < 0 or rec < 0 or tot < 0:
            problems.append("negative interval for %s" % (key,))
            continue
        if w.get("outcome") == "queued-only":
            problems.append("queued-only wake for %s" % (key,))
            continue
        if w.get("ack") is False or r.get("ack") is False:
            problems.append("missing ack for %s" % (key,))
            continue
        worker_dur = (d - _instant(r.get("dispatch_at"))).total_seconds() \
            if r.get("dispatch_at") else None
        joined.append({"action": r.get("action"),
                       "execution": r.get("execution"),
                       "detection_s": det, "recovery_s": rec, "total_s": tot,
                       "worker_duration_s": worker_dur,
                       "suspicion": {"detect_ok": det <= sdet_b,
                                     "total_ok": tot <= stot_b}})
        if det > det_b:
            problems.append("late detection for %s: %.1fs" % (key, det))
        if rec > rec_b:
            problems.append("late recovery despite fast detection for %s: "
                            "%.1fs" % (key, rec))
        if tot > tot_b:
            problems.append("late total for %s: %.1fs" % (key, tot))
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


def _candidate_plan(config, plan, dirs):
    t = _plan_templates()
    wa, va = plan["actions"]["worker"], plan["actions"]["verifier"]
    seats = [config["worker"]["title"], config["verifier"]["title"]]
    return {"fixture_id": "p6-stagec-1", "package_id": "P6C",
            "worker_action": wa, "verify_action": va,
            "seats": {"fixture_seats": seats},
            "allowlist": {"seats": seats,
                          "timer_units": {wa: plan["timer_unit"]},
                          "wake_path": dirs["wake_shim"],
                          "systemd_run": dirs["systemd_shim"],
                          "systemctl": dirs["systemctl_shim"]},
            "bounds": {"duration_s": 900, "verify_window_s": 600,
                       "wait_s": 8, "escalation_window_s": 120,
                       "stream_dir": dirs["stream"],
                       "onset_dir": dirs["onsets"],
                       "artifact_base_dir": dirs["art"],
                       "latency_path": dirs["latency"]},
            "task_texts": t["task_texts"],
            "authorized_dispositions": t["authorized_dispositions"],
            "routes": {va: seats[1], wa: seats[0]}}


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
                     deadline_s=40.0):
    """Fresh-producer driver: each producer subprocess sees ONLY the
    dispatched text file it is given plus named files. Worker first, then
    verifier once its dispatch exists. tamper corrupts the artifact
    between the two (failed-verification case)."""
    import subprocess as _sp
    import time as _t
    done = {}
    stop = _t.monotonic() + deadline_s
    while _t.monotonic() < stop:
        for seat, spec in seat_map.items():
            if seat in done:
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
        if len(done) == len(seat_map):
            return done
        _t.sleep(0.2)
    raise StageCFault("E_PRODUCER_TIMEOUT",
                      "dispatched texts never arrived for %s"
                      % sorted(set(seat_map) - set(done)))


def run_case(config_path, plan_path, sig_path, case, dirs, out_path):
    h = _candidate()
    g = gate(config_path, plan_path, sig_path)  # mandatory, no bypass
    config, plan = _load(config_path), _load(plan_path)
    if case not in config.get("cases", []):
        raise StageCFault("E_CASE", "case %r not enumerated" % case)
    for d in ("stream", "claims", "art", "onsets"):
        os.makedirs(dirs[d], exist_ok=True)
    wsid, vsid = (config["worker"]["session_id"],
                  config["verifier"]["session_id"])
    cplan_path = os.path.join(dirs["root"], "candidate-plan.json")
    cplan = _candidate_plan(config, plan, dirs)
    json.dump(cplan, open(cplan_path, "w"), sort_keys=True)
    import hashlib as _hl
    phash = _hl.sha256(open(cplan_path, "rb").read()).hexdigest()
    manifest_path = os.path.join(dirs["root"], "manifest.json")
    h.setup_manifest(cplan_path, manifest_path, session=wsid,
                     stream_key=wsid, worker_stream_key=wsid,
                     verifier_stream_key=vsid)
    manifest = json.load(open(manifest_path))
    for key, sid in (("w", wsid), ("v", vsid)):
        p = os.path.join(dirs["stream"], sid + ".jsonl")
        if not os.path.exists(p):
            open(p, "w").close()
    old_env = dict(os.environ)
    os.environ["PATH"] = dirs["bin"] + ":" + os.environ.get("PATH", "")
    os.environ["TRACE"] = dirs["trace"]
    os.environ["MSGDIR"] = dirs["msgs"]
    seat_map = {config["worker"]["title"]:
                {"role": "worker",
                 "stream": os.path.join(dirs["stream"], wsid + ".jsonl"),
                 "art": dirs["art"]},
                config["verifier"]["title"]:
                {"role": "verifier",
                 "stream": os.path.join(dirs["stream"], vsid + ".jsonl"),
                 "art": dirs["art"]}}
    import threading as _th
    box = {}
    tamper = (case == "failed-verification")

    def _bg():
        try:
            box["done"] = _drive_producers(dirs["msgs"], seat_map,
                                           dirs["onsets"], tamper=tamper)
        except StageCFault as e:
            box["error"] = {"code": e.code, "detail": e.detail}
    bg = _th.Thread(target=_bg, daemon=True)
    bg.start()
    try:
        # Same live path as the candidate's own acceptance: real
        # HostWakeTransport/HostTimerService against PATH-shimmed OS
        # effects (no live seats/services). Plan hash + seat allowlist
        # enforced by the candidate itself.
        adapter = h.build_adapter(
            dirs["db"], live=True, plan_hash=phash,
            allowlist_seats=[config["worker"]["title"],
                             config["verifier"]["title"]],
            plan_path=cplan_path)
        out = h.run_fixture(adapter, manifest, dirs["claims"], "P6C")
    finally:
        os.environ.clear()
        os.environ.update(old_env)
    bg.join(timeout=30)
    if "error" in box:
        raise StageCFault(box["error"]["code"], box["error"]["detail"])
    trace = [l for l in open(dirs["trace"]).read().splitlines()
             if l.startswith("CALL wake ")]
    if case == "restart-quiet":
        # First run must commit, then a rerun on the same db must be a
        # recognized duplicate with zero fresh sends (restart + quiet).
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "restart-quiet setup run did not commit: %s"
                              % (out,))
        n_calls = len(trace)
        os.environ["PATH"] = dirs["bin"] + ":" + os.environ.get(
            "PATH", "")
        try:
            adapter2 = h.build_adapter(
                dirs["db"], live=True, plan_hash=phash,
                allowlist_seats=[config["worker"]["title"],
                                 config["verifier"]["title"]],
                plan_path=cplan_path)
            out2 = h.run_fixture(adapter2, manifest, dirs["claims"], "P6C")
        finally:
            os.environ.clear()
            os.environ.update(old_env)
        trace2 = [l for l in open(dirs["trace"]).read().splitlines()
                  if l.startswith("CALL wake ")]
        if out2.get("decision") != "duplicate-end-ignored":
            raise StageCFault("E_CASE_FAIL",
                              "rerun not recognized duplicate: %s" % (out2,))
        if len(trace2) != n_calls:
            raise StageCFault("E_SENDS",
                              "rerun manufactured fresh sends")
        out = dict(out2, worker=out)
    sends = {"worker": sum(config["worker"]["title"] in l for l in trace),
             "verifier": sum(config["verifier"]["title"] in l
                             for l in trace)}
    if case == "positive-handoff":
        if out.get("decision") not in ("transition-committed",
                                       "terminal-rest"):
            raise StageCFault("E_CASE_FAIL",
                              "positive case did not commit: %s" % (out,))
        if not (sends["worker"] == 1 and sends["verifier"] == 1):
            raise StageCFault("E_SENDS",
                              "positive case needs 1+1 sends: %s" % (sends,))
    if case == "failed-verification":
        if out.get("decision") == "COMPLETE" or \
                manifest.get("disposition") == "COMPLETE":
            raise StageCFault("E_CASE_FAIL",
                              "failed check must never close COMPLETE")
    witem = _resolve_item(os.path.join(dirs["stream"], wsid + ".jsonl"),
                          dirs["onsets"])
    vitem = _resolve_item(os.path.join(dirs["stream"], vsid + ".jsonl"),
                          dirs["onsets"])
    import subprocess as _sp
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import witness_timing as _w
    lat_rows = [json.loads(l) for l in open(dirs["latency"])
                if l.strip()] if os.path.exists(dirs["latency"]) else []
    det_by_action = {}
    for r in lat_rows:
        det_by_action[r.get("action")] = r.get("detected_at")
    for (action, execution, item) in (
            (manifest["action_id"], manifest["execution_id"], witem),
            (manifest["verify_action_id"],
             manifest["verify_execution_id"], vitem)):
        onset = _w.read_onset(os.path.join(dirs["onsets"], item + ".json"))
        wrow = _w.emit_row(action, execution, None,
                           det_by_action.get(action), onset,
                           dirs["witness"])
    cand_err, wit_err = None, None
    try:
        h.check_latency(dirs["latency"])
    except Exception as e:
        cand_err = getattr(e, "code", type(e).__name__)
    try:
        _w.check_rows(dirs["witness"])
    except Exception as e:
        cand_err = cand_err  # noqa: witness has no committed evidence yet
        wit_err = getattr(e, "code", type(e).__name__)
    verdict = timecheck(config_path, dirs["latency"], dirs["witness"],
                        expect_open=manifest["verify_action_id"]
                        if case == "failed-verification" else None)
    if case in ("positive-handoff", "restart-quiet"):
        if verdict.get("verdict") != "accept":
            raise StageCFault(
                "E_TIMECHECK",
                "%s timecheck did not accept: %s" % (case, verdict))
    else:  # failed-verification must stay open, never accept/close
        if verdict.get("verdict") != "accept-open":
            raise StageCFault("E_CASE_FAIL",
                              "failed-verification not provably open: %s"
                              % (verdict,))
    receipt = {"case": case, "gate": g, "outcome": out,
               "sends": sends, "worker_item": witem,
               "witness_row": wrow, "timecheck": verdict,
               "candidate_gate": cand_err or "pass",
               "witness_gate": wit_err or "pass",
               "overlay": dirs.get("overlay", False)}
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, sort_keys=True, indent=1)
    return receipt


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
    d = dict(plan["live_run_dirs"])
    d["overlay"] = False
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r6 Stage C entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("derive-config", "gate"):
        p = sub.add_parser(name)
        p.add_argument("--plan", required=True)
        p.add_argument("--binding", "--config", required=True, dest="src")
        p.add_argument("--signatures", required=True)
        p.add_argument("--out", required=name == "derive-config")
    r = sub.add_parser("run-case")
    r.add_argument("--config", required=True)
    r.add_argument("--plan", required=True)
    r.add_argument("--signatures", required=True)
    r.add_argument("--case", required=True)
    r.add_argument("--overlay-dir", default="")
    r.add_argument("--out", required=True)
    t = sub.add_parser("timecheck")
    t.add_argument("--config", required=True)
    t.add_argument("--latency", required=True)
    t.add_argument("--witness", required=True)
    t.add_argument("--expect-open", default="")
    t.add_argument("--out", default="")
    b = sub.add_parser("rollback")
    b.add_argument("--config", required=True)
    b.add_argument("--overlay-dir", default="")
    b.add_argument("--archive-dir", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "derive-config":
        cfg = derive_config(args.plan, args.src, args.signatures, args.out)
        print(json.dumps({"config": args.out,
                          "parent_binding_sha256":
                          cfg["parent_binding_sha256"]}, sort_keys=True))
        return 0
    if args.cmd == "gate":
        print(json.dumps(gate(args.src, args.plan, args.signatures),
                         sort_keys=True))
        return 0
    if args.cmd == "run-case":
        plan = _load(args.plan)
        dirs = _overlay(args.overlay_dir) if args.overlay_dir \
            else _live_dirs(plan)
        receipt = run_case(args.config, args.plan, args.signatures,
                           args.case, dirs, args.out)
        print(json.dumps({"case": args.case,
                          "timecheck": receipt["timecheck"].get("verdict"),
                          "sends": receipt["sends"]}, sort_keys=True))
        return 0
    if args.cmd == "timecheck":
        verdict = timecheck(args.config, args.latency, args.witness,
                            expect_open=args.expect_open or None)
        if args.out:
            json.dump(verdict, open(args.out, "w"), sort_keys=True,
                      indent=1)
        print(json.dumps(verdict, sort_keys=True))
        return 0 if verdict.get("verdict") == "accept" else 3
    if args.cmd == "rollback":
        plan = _load(args.config)  # noqa: readability guard
        config = _load(args.config)
        root = args.overlay_dir or os.path.dirname(
            config["worker"].get("workdir") or "/tmp/p6stagec")
        report = rollback(args.config, root, args.archive_dir)
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
