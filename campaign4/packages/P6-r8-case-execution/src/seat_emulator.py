"""P6-r8 injected-seat stand-in (explicit external step, NEVER a hidden
substitute). Real model seats perform worker/verifier work live; under the
injected grant this emulator plays the seat role, and ONLY the seat role:
it reads a dispatched wake text file plus the files that text names, honors
the armed intervention record for its case, and runs the PINNED candidate
producer code (hash-checked) to write the claim and append the end record
with a producer onset sidecar. It never invents streams, onsets, acks or
verification outcomes. Controls:

- hold-<role>: exit produced-nothing with a held record (lost-completion).
- corrupt-after-worker: tamper the artifact dir immediately before a
  verifier production (verifier dispatch implies worker commit, so the
  tamper provably lands post-commit with no race); the independent
  candidate check then fails honestly.
- (transport queueing is honored by the signed wake executable reading the
  armed intervention file; this emulator never fabricates acks.)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

CANDIDATE_SRC = ("/home/bmosher/memory-bake-off/campaign4/packages/"
                 "P6-r5-launch-binding/src")
_CANDIDATE_HASHES = {
    "fixture_worker.py":
    "8ebb4e6593225efcde4d13f58e1c65bfabd107a2cf25443b110623f0f9860ebe",
    "harness.py":
    "cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142"}


class SeatFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _producer():
    for name, want in _CANDIDATE_HASHES.items():
        with open(os.path.join(CANDIDATE_SRC, name), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != want:
            raise SeatFault("E_CORE_DRIFT",
                            "pinned candidate %s drifted: %s" % (name,
                                                                 got[:12]))
    if CANDIDATE_SRC not in sys.path:
        sys.path.insert(0, CANDIDATE_SRC)
    import fixture_worker as fw
    return fw


def _pinned_worker_hash():
    with open(os.path.join(CANDIDATE_SRC, "fixture_worker.py"),
              "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def emulate(seat, role, text_dir, stream_file, onset_dir, art_dir,
            intervention_path="", timeout_s=60.0, poll_s=0.2):
    fw = _producer()
    control = ""
    if intervention_path and os.path.exists(intervention_path):
        try:
            control = (json.load(open(intervention_path)).get("control")
                       or "")
        except ValueError:
            control = ""
    if control == "hold-" + role:
        held = {"seat": seat, "role": role, "held": True,
                "control": control}
        print(json.dumps(held, sort_keys=True))
        return held
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            files = sorted(f for f in os.listdir(text_dir)
                           if f.startswith("to-" + seat + "-"))
        except OSError:
            files = []
        if files:
            text_file = os.path.join(text_dir, files[-1])
            if control == "corrupt-after-worker" and role == "verifier":
                # Verifier dispatch implies worker commit (candidate
                # enforces the order), so this tamper provably lands
                # post-commit with no race; the independent check fails.
                import glob as _g
                for art in _g.glob(os.path.join(art_dir, "*")):
                    with open(art, "wb") as fh:
                        fh.write(b"tampered-by-fixture-fault")
            rc = fw.main(["--role", role, "--text-file", text_file,
                          "--stream-file", stream_file, "--onset-dir",
                          onset_dir])
            if rc != 0:
                raise SeatFault("E_PRODUCER",
                                "pinned producer rc%d for %s" % (rc, seat))
            done = {"seat": seat, "role": role, "produced": True,
                    "text_file": text_file,
                    "producer_hash": _pinned_worker_hash()[:12]}
            print(json.dumps(done, sort_keys=True))
            return done
        time.sleep(poll_s)
    raise SeatFault("E_NO_TEXT",
                    "no dispatched text for %s within %.0fs" % (seat,
                                                                timeout_s))


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r8 injected seat stand-in")
    ap.add_argument("--seat", required=True)
    ap.add_argument("--role", required=True, choices=("worker", "verifier"))
    ap.add_argument("--text-dir", required=True)
    ap.add_argument("--stream-file", required=True)
    ap.add_argument("--onset-dir", required=True)
    ap.add_argument("--art-dir", required=True)
    ap.add_argument("--intervention", default="")
    ap.add_argument("--timeout-s", type=float, default=60.0)
    args = ap.parse_args(argv)
    emulate(args.seat, args.role, args.text_dir, args.stream_file,
            args.onset_dir, args.art_dir, args.intervention,
            args.timeout_s)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SeatFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
