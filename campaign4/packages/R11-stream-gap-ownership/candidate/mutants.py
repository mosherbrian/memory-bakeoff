#!/usr/bin/env python3
"""Planted faults: each mutant must make the suite fail."""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(f"{HERE}/research-gap-check").read()
M = {
 "notice-at-29m": ("age >= OPEN_S", "age >= OPEN_S - 60"),
 "escalate-early": ("NOW - g[\"tern_at\"] >= ESC_S", "NOW - g[\"tern_at\"] >= ESC_S - 60"),
 "timed-out-counts-as-active": ('if p.get("step") in EXECUTING_STEPS]', 'if p.get("step") != "closed"]'),
 "decision-executes": ('EXECUTING_STEPS = {"worker", "verify"}', 'EXECUTING_STEPS = {"worker", "verify", "decision"}'),
 "held-executes": ('EXECUTING_STEPS = {"worker", "verify"}', 'EXECUTING_STEPS = {"worker", "verify", "held"}'),
 "blocked-executes": ('EXECUTING_STEPS = {"worker", "verify"}', 'EXECUTING_STEPS = {"worker", "verify", "blocked"}'),
 "only-open-is-unresolved": ('items = [i for i in d["items"] if i.get("status") not in RESOLVED]', 'items = [i for i in d["items"] if i.get("status") == "open"]'),
 "unknown-status-resolves": ('if i.get("status") in RESOLVED}', 'if i.get("status") != "open"}'),
 "absent-question-resolves": ('if resolved is not None and q in resolved:', 'if resolved is not None and (q in resolved or q not in {top}):'),
 "unknown-gap-dropped-on-recovery": ('            state["gaps"][top] = u', '            pass'),
 "name-inference": ("elif qids == {q}:", "elif qids == {q} or q in p:"),
 "invalid-row-extends": ("            bad.append(f\"REST.jsonl line {n}: invalid", "            best = (r, ts(r.get('revisit_at')) or 9e9); bad.append(f\"REST.jsonl line {n}: invalid"),
 "missing-rest-exempts": ("        return None, []\n    best", "        return {'revisit_at': 'none'}, []\n    best"),
 "status-failure-quiet": ("        live = None\n        unknown.append", "        live = []\n        (lambda *a: None)"),
 "contradiction-is-active": ("if len(qids) > 1 and q in qids:", "if False:"),
 "clock-reset-on-restart": ("if not g:\n            g = state", "if True:\n            g = state"),
 "no-resolve-on-close": ("            run([RESOLVE,", "            0 and run([RESOLVE,"),
 "wake-not-retried": ("g[\"tern_woken\"] = run([WAKE, DIRECTOR, g[\"tern_text\"]]) in (0, 3)", "g[\"tern_woken\"] = run([WAKE, DIRECTOR, g[\"tern_text\"]]) or True"),
 "top-switch-drops-incident": ("qs = set(state[\"gaps\"]) | ", "qs = set() | "),
 "corrupt-state-silent": ("    if problem:\n        run(", "    if 0:\n        run("),
}
bad = 0
for name, (a, b) in M.items():
    assert SRC.count(a) >= 1, f"mutant {name} anchor not unique/absent"
    with tempfile.NamedTemporaryFile("w", suffix="-mut", delete=False) as f:
        f.write(SRC.replace(a, b, 1))
    r = subprocess.run([sys.executable, f"{HERE}/test_research_gap_check.py"], env=dict(os.environ, R5_CHECK=f.name), capture_output=True, text=True)
    os.unlink(f.name)
    caught = r.returncode != 0
    bad += not caught
    print(f"{'CAUGHT ' if caught else 'SURVIVED'} {name}")
print(f"{len(M) - bad}/{len(M)} caught")
sys.exit(1 if bad else 0)
