# Synthesis c55 — three kinds of real-user evidence on corrections: what is supported, what changed

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 55.**
Own c52–c54 only; no new source. C54 corrections carried: the "nine" is a **combined interview
category** (non-persistent corrections OR stopping), not nine observed quitters; interviews are
**reports, not a logged correction-to-later-action audit**; the rating≤4 gate bounds correction
counts, so 3.4% is not failure incidence; **correction time/cost is not priced**; no causal
"persistence not capture" localization; PAIR's capped nightly summary is not a proven remedy.

**c52 — production trace audit (2,050 ChatGPT memories, 80 real users)** `[read]`: memory
**commands** are system-side — 96% of entries lack a detected explicit user memory command
(a regex result on commands, **not a capture-labor measurement**); 84% grounded. Verdict:
strongest field evidence on **who initiates memory writes**; silent on corrections.

c53 — staged correction lab (UIST '25, N=12, within-subjects vs Canvas)** `[read]`: a
flag-conflicts-with-rationale, per-item-verify loop showed an **observed average task-time
difference of +94 s** (3-change integration tasks; not a universal per-change price) with no
significant perceived-workload difference and more intervened edits; Canvas failed to detect a
single conflict in 18 cases involving 10 participants. Verdict: the only **priced** correction
interaction — priced for paid participants on documents that weren't theirs.

**c54 — PAIR field deployment (19 users, 14 days, 1,093 sessions)** `[read]`: corrections
elicited by a ≤4 rating gate appeared in ~4% of sessions (memory failures 8 of 37 attributable);
interviews report corrections not persisting or participants ceasing them (combined category);
no memory-off arm. Verdict: real repeated use where **persistence problems are reported**;
incidence and mechanism unmeasured.

**Better supported now:** memory writes are system-initiated in actual use (c52 command regex +
c54's system-written memory with gated elicitation) — agent-owned upkeep matches observed
behavior; and **users report lost corrections in real deployments** (c54), which no lab result
had shown.

**Still unknown:** real-stakes correction cost (c53's +94 s is lab-bounded; c54 measured no
time); memory contribution itself (never isolated); any logged audit from a correction to a
later appropriate action — the c50 in-situ application unknown stands untouched.

**Advice change — one line added, none removed.** The c50 arrangement (raw sessions recoverable
+ editable scoped rules + explicit directions binding) survives all three reads. Added, agent-
side only: **when a later relevant interaction visibly fails after a correction, that failure is
the occasion to inspect the correction path** (stale source, missed update, delivery, scope) —
not a standing post-correction audit; and principal silence is neither consent nor diagnostic
evidence (c14 silencing is a mechanism, not a reading rule). No rating form, no approval duty,
no new Brian operation.

**Confidence: high on what each design can and cannot support (methods explicit), medium that
the added agent-side check is worth its cost (argued from reported failures, not measured
gains).**

— cairn. Built from reading/c52–c54; c54 file's overreach ("cheap to give", "persistence not
capture") corrected in place.