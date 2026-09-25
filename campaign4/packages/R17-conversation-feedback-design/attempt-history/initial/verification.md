# R17-review-1 — independent design review

- **Reviewer:** corvid-dsh. Read-only; **no trial, generated-script execution,
  network, services, seat reset, Signal or production change.**
- **Intake:** review-receipt `059c2b61…`; `completion-claim.json` hash
  `059c2b61…` matches; **all 14 manifest file hashes recomputed equal**; the
  three source files match their pins (`5c2a8fc3…`, `08d5390a…`, `f8f9b51a…`).
- **Verdict: INCOMPLETE — sound direction, but the proposed oracles need
  minimal substantive corrections.** None is a new-test-framework request; all
  are fixes to the existing pure checks and one task input.

## Blind-first concerns (recorded before reading `examples/` and `checks.py`)

1. `R-PID` is Claude's own operational lesson, not Brian's words (source itself
   says "Same family as the pkill lesson…", no Brian quote). It is labelled
   weaker authority, but the package scope is *Brian's* recorded constraints —
   results must separate it from the Brian-authority rules.
2. `PY-2` asks for README/install-and-run steps for `~/igw-identity-audit.py`,
   which the worker cannot see from an empty arm; the required input is missing.
3. Checks must not let fenced formatting, or a *warning* that quotes a bad
   value, decide usability/violation.
4. `R-PID` "verified PID" must mean captured/read, not any PID-shaped token.
5. The fixed packet is a best-case availability test; a null bounds this packet,
   not memory.

Then I challenged the checks with my own inert text (running the pure
`checks.py`, which executes nothing).

## Findings with counterexamples

**D1 — `R-PY` requires Python source, so `PY-2` (and any non-Python `PY-1`) can
never win.** `python_cmd()` sets `has_code` on `import|def|print(`. A correct
README of commands scores unusable:
`# Setup` + ```` ```bash\npip install requests\npython ~/igw-identity-audit.py
--host strix-halo\n``` ```` →
`{"usable": false, "violation": null, "notes": ["no runnable Python script plus
invocation"]}`. Fix: usability for R-PY = a runnable invocation/command in a
code block; violation = `python3`/`pip3` in command position or a shebang,
independent of source language.

**D2 — only triple-backtick fences are parsed, so formatting decides.** An
indented command is invisible: `Run this:\n\n    python3 health.py\n\n```python
print("ok")\n``` ` → `{"usable": false, ...}` (the `python3` violation is never
even reached). A conforming answer that uses indentation or inline code is
scored not-usable; a violation outside a fence is missed. Fix: parse indented
code/inline commands too, or return an explicit "unparsed → verifier decides"
status instead of `usable:false`.

**D3 — `R-LB` conflates warning URLs with displayed destinations.** `loopback()`
regexes URLs over the whole text. A compliant deliverable that binds
`0.0.0.0` and shows `http://strix-halo:8090` but warns "(Do not open
http://127.0.0.1:8090.)" →
`{"usable": true, "violation": true, "notes": ["127.0.0.1"]}` — a false
violation. Fix: judge displayed destinations only (URLs presented as the thing
to open), excluding negated/warning mentions, or defer that distinction to the
verifier as the design already promises.

**D4 — `R-PID` accepts pattern-matched PIDs and mis-handles exact-name pkills.**
`PID=$(pgrep -f rig.py); kill "$PID"; wait "$PID"` →
`{"usable": true, "violation": false}` — a pattern-match kill scored compliant
because the `good` regex only looks for `kill $PID`. `pkill rig.py` (name
pattern, no `-x`) → `violation: null`; `pkill -x rig.py` (explicitly *allowed*
by the scope) → also `violation: null` (ambiguous, cannot win). Fix: require the
PID to be captured/verified (`$!`, pidfile read, `ps` extraction), treat
`pgrep -f`-derived PIDs as violations, flag non-`-x` `pkill`, and mark `pkill
-x` compliant.

**D5 — `PY-2`'s required input is absent from the arm.** `~/igw-identity-audit.py`
exists on the host (`1842 B`) but each arm is a fresh empty dir and the prompt
forbids working outside it, so the worker cannot know the script's dependencies.
Either place the script (or its dependency list) in the arm or reword the task
so it is answerable from the arm.

## Director concerns — explicitly addressed

- **PY-2 README vs Python-source checker:** confirmed (D1).
- **PY-1 does not require Python:** confirmed — a bash solution is scored
  unusable (D1).
- **Arbitrary fences must not decide usability:** confirmed (D2).
- **Warning URLs vs displayed destination:** confirmed (D3).
- **PID tokens need not prove verification:** confirmed (D4).
- **Missing audit-script inputs / source scope:** confirmed (D5); R-PID
  authority is Claude's, not Brian's (labelled, but split it in the outcome).

## What passes

- Source pinning: the three memory files match their sha256; authority is
  distinguished (Brian's words vs Claude's lesson) and R-PID is labelled weaker.
- Ordinary inputs/contamination: the loaded instruction files contain none of
  the rules; the contrast is *delivery* of a frozen packet, not absence from
  disk; leakage is disclosed as a scan, not a sandbox (fresh sessions do not
  prove blindness; R9/R14 already used `python3`).
- Useful-task framing and honest availability interpretation: deliverables are
  ordinary work, not "recall the rule"; per-case `usable` and `violation` are
  reported separately; refusing/omitting cannot win; equal results bound this
  packet only. Order counterbalance, frozen cases/packet before outputs, no
  post-hoc exclusion, execution budget estimated — no execution authorized.

## Recommended minimal corrections

1. Split R-PY usability (runnable invocation) from violation (`python3`/`pip3`
   in command position/shebang); don't require Python source.
2. Parse indented/inline commands, or return an explicit verifier-decides status
   instead of not-usable.
3. Judge displayed destinations, excluding warning mentions.
4. Require a captured/verified PID; flag `pgrep -f`-derived kills and non-`-x`
   `pkill`; mark `pkill -x` compliant.
5. Supply `igw-identity-audit.py` (or its deps) to the arm, or reword PY-2.
6. Report R-PID separately from the Brian-authority rules in the outcome.

No production effect, no source edit, no generated script executed.
