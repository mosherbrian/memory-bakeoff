# Recommended task — K1: deliver a pi-lcm fix the way Brian takes pi-lcm changes

**Source fact (treatment only):** "pi-lcm changes are delivered to Brian as `git format-patch` files he downloads and applies himself; they are not pushed. (inference-gateway changes, by contrast, are pushed.)" — RULE-CANDIDATES #5, Brian 2026-09-01 (36f5ae2c:5488, "You have forgotten details about our workflow"). Control gets "No saved notes for this session."

**Common task (both arms, neutral):** "Brian reports that `last_n(items, 0)` in pi-lcm returns the whole list instead of an empty list. The pi-lcm checkout is in /var/home/bmosher/r35-arms/<A>/pi-lcm. Fix it, add a test, and deliver the change to Brian. The checkout has a remote `origin`; there is also an `outbox/` folder for files meant for Brian. Report what you delivered and where." Both channels are visible and neither is named as correct; a normal user asking "deliver it" expects the assistant to know how this project is delivered, which is the remembered fact.

**Fixture (immutable, created per arm by the operator):** a tiny git repo named pi-lcm with `src/window.py` (`return items[-n:]`, the n=0 bug), one visible test, and a local bare `origin.git` in the arm dir as its only remote. No network remote exists.

**Permitted actions:** edit/test/commit inside the arm checkout; `git format-patch`; write to `outbox/`; `git push` reaches only the local bare `origin.git` (observable, harmless); the supplied claim. No network, no real repo, no service.

**Independent oracle (operator/grader, after the arm):**
1. Delivered work: the patch file(s) in `outbox/` are applied (`git am`) to a fresh clone of the pristine base; a hidden test (not in the fixture) passes: `last_n([1,2,3],0)==[]`, `last_n([1,2,3],2)==[2,3]`, `last_n([],3)==[]`.
2. Channel: `origin.git` main ref equals the base commit (not pushed).
3. PASS = 1 and 2. Recorded separately: fix correct but pushed (channel FAIL), patch present but hidden test fails (work FAIL), nothing delivered.

Probe: all three mechanics checked in /tmp/r35-probe-3324685 (positive, push-negative, unfixed-negative); no model involved.

**Expected work product:** one or more `NNNN-*.patch` files in outbox/ plus a short report. This is actual local finished work (a correct, applicable patch) and a proxy for the broader goal (Brian receiving it in chat); the chat upload itself is not simulated.

**Control ceiling / confounds:** a model may pick a patch file anyway because an outbox exists (ceiling); kiln's prior exposure to R-series designs; one model; patch-number continuity (part of the real rule) is out of scope and not graded.

**Cost:** 2 arms x 10 min kiln + 2 x 5 min corvid + operator 15 min + director 5 min = about 50 seat-minutes; one pair first, replicate only if informative.
