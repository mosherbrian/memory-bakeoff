#!/usr/bin/env python3
"""R10 planted faults: each must make test-acp-worker-new.py fail."""
import os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
SRC = open(f"{H}/acp-worker").read()
M = {
 "no-new-lock": ("if not self.ctl.acquire(blocking=False):", "if not (self.ctl.acquire(blocking=False) or True):"),
 "prompt-admission-unlocked": ("        with self.ctl:\n            if self.running:", "        if True:\n            if self.running:"),
 "busy-not-refused": ("if self.running or depth or self.pending is not None:", "if False:"),
 "same-id-accepted": ("if not sid or sid == old:", "if not sid:"),
 "missing-id-accepted": ("if not sid or sid == old:", "if sid == old:"),
 "error-reported-as-success": ('return f"new failed: adapter refused session/new ({exc}) - still on {old}"', 'return f"new {old}"'),
 "resume-not-refused": ("        if RESUME:\n            return \"new refused", "        if False:\n            return \"new refused"),
 "proven-kept": ("self.proven = self.resumed = self.stalled = False", "self.resumed = self.stalled = False"),
 "no-boundary": ('self.record("assistant", line)', 'pass'),
 "model-not-reapplied": ("applied = self.apply_mode() + self.apply_model() + self.apply_config_model()", "applied = self.apply_mode()"),
 "new-not-routed": ('if text == "/new":\n            return self.new_session()', 'if text == "/new-disabled":\n            return self.new_session()'),
}
bad = 0
for name, (a, b) in M.items():
    assert SRC.count(a) == 1, name
    f = tempfile.NamedTemporaryFile("w", suffix="-acp-worker", delete=False); f.write(SRC.replace(a, b)); f.close()
    r = subprocess.run([sys.executable, f"{H}/test-acp-worker-new.py", f.name], capture_output=True, text=True, timeout=200)
    os.unlink(f.name)
    caught = r.returncode != 0; bad += not caught
    print(("CAUGHT  " if caught else "SURVIVED") + " " + name, flush=True)
print(f"{len(M) - bad}/{len(M)} caught")
sys.exit(1 if bad else 0)
