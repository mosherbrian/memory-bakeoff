"""Fixture producer: a fresh seat that sees ONLY the actual outgoing wake
text plus the files that text names. It never reads hidden manifest
variables and never pre-stages claims or end events.

The wake text carries labeled lines (written by the launcher-owned task
template, formatted with dispatch facts):

  action: <id>          execution: <id>      attempt: <id>
  step: worker-run|verify-run
  claim: <absolute claim path>      artifacts: <absolute artifact root>
  artifact: <relative artifact path>
  worker_claim: <absolute path>      (verify role only)
  check: <deterministic check name>  (verify role only)

Worker role: writes the pinned artifact bytes, hashes the file, publishes
the route-free claim atomically, appends one end record to the stream.
Verifier role: recomputes the worker artifact hash (independent
deterministic check named in the text), publishes its own step claim with
outcome passed/failed, appends one end record. A failed check reports
failed and can never close COMPLETE downstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


def parse_text(text):
    fields = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip().lower(), value.strip()
        if key and value and key in (
                "action", "execution", "attempt", "step", "claim",
                "artifacts", "artifact", "worker_claim", "check",
                "pinned_input", "item", "package"):
            fields[key] = value
    return fields


def sha_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, sort_keys=True)
    os.replace(tmp, path)


def append_end(stream_path, item, extra=None):
    rec = {"t": "end", "item": item}
    rec.update(extra or {})
    with open(stream_path, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def run_worker(fields, stream_path, payload_bytes):
    artifact_path = os.path.join(fields["artifacts"],
                                 fields["artifact"])
    os.makedirs(os.path.dirname(artifact_path) or ".", exist_ok=True)
    with open(artifact_path, "wb") as fh:
        fh.write(payload_bytes)
    claim = {"package": fields.get("package", "P6H"),
             "attempt": fields["attempt"], "action": fields["action"],
             "execution": fields["execution"],
             "contract_step": fields["step"], "outcome": "completed",
             "artifacts": {
                 fields["artifact"]: {
                     "path": fields["artifact"],
                     "sha256": sha_file(artifact_path)}}}
    atomic_write_json(fields["claim"], claim)
    append_end(stream_path, fields["item"])
    return {"claim": fields["claim"], "item": fields["item"]}


def run_verifier(fields, stream_path):
    with open(fields["worker_claim"]) as fh:
        worker = json.load(fh)
    check = fields.get("check", "recompute-sha256")
    ok, detail = _independent_check(worker, fields, check)
    claim = {"package": worker.get("package", "P6H"),
             "attempt": fields["attempt"], "action": fields["action"],
             "execution": fields["execution"],
             "contract_step": fields["step"],
             "outcome": "completed" if ok else "failed",
             "artifacts": worker.get("artifacts", {}),
             "check": check, "check_detail": detail}
    atomic_write_json(fields["claim"], claim)
    append_end(stream_path, fields["item"])
    return {"claim": fields["claim"], "item": fields["item"],
            "check": ok}


def _independent_check(worker, fields, check):
    if check != "recompute-sha256":
        return (False, "unknown check " + check)
    base = fields.get("artifacts") or os.path.dirname(
        fields["worker_claim"])
    for name, spec in (worker.get("artifacts") or {}).items():
        path = spec.get("path", "")
        full = path if os.path.isabs(path) else os.path.join(base, path)
        try:
            digest = sha_file(full)
        except OSError:
            return (False, "artifact unreadable: " + name)
        if digest != spec.get("sha256"):
            return (False, "hash mismatch: " + name)
    if not worker.get("artifacts"):
        return (False, "no artifacts bound")
    return (True, "all artifact hashes recomputed equal")


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6 fixture producer")
    ap.add_argument("--role", required=True, choices=("worker",
                                                      "verifier"))
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--stream-file", required=True)
    ap.add_argument("--payload", default="fixture-artifact-bytes")
    args = ap.parse_args(argv)
    with open(args.text_file) as fh:
        raw = fh.read()
    # Production transport delivers a JSON envelope carrying the labeled
    # task under "text"; accept the envelope by unwrapping it, else
    # parse the file as labeled task lines directly.
    try:
        env = json.loads(raw)
    except ValueError:
        env = None
    if isinstance(env, dict) and isinstance(env.get("text"), str):
        raw = env["text"]
    fields = parse_text(raw)
    required = ("action", "execution", "attempt", "step", "claim",
                  "artifacts")
    # Worker names its own artifact to write; verifier binds the worker
    # claim's artifacts and needs no artifact line of its own.
    required += ("artifact",) if args.role == "worker" else ("worker_claim",)
    for req in required:
        if req not in fields:
            print(json.dumps({"error": "missing-field:" + req}))
            return 2
    import secrets as _secrets
    # The runtime assigns the turn item; the fixture producer mints an
    # opaque one and the harness binds it at observation time.
    fields.setdefault("item", "i" + _secrets.token_hex(6))
    if args.role == "worker":
        if fields["step"] != "worker-run":
            print(json.dumps({"error": "role-step-mismatch"}))
            return 2
        out = run_worker(fields, args.stream_file,
                         args.payload.encode())
    else:
        if fields["step"] != "verify-run" or "worker_claim" not in fields:
            print(json.dumps({"error": "role-step-mismatch"}))
            return 2
        out = run_verifier(fields, args.stream_file)
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
