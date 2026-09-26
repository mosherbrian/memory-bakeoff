# Reading note — Agent Workflow Memory: induced workflows as memory — does the control separate workflows from mere context?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 42.**
One primary read (Tern): **Agent Workflow Memory, arXiv 2409.07429v1** — identity as
commissioned. Method shape: the agent **induces reusable "workflows" (routine sub-procedures +
adaptive variants) from past trajectories** and injects them into the prompt of the same
agent; two modes — **offline** (workflows mined from a training set before evaluation) and
**online** (workflows induced continuously from the agent's own recent successes, including
within the test stream). Questions at source: **how success is judged** for what gets
induced; **train/test separation and what reuse inside the test stream means** for the
headline; **fixed-executor / content / representation controls** (is there a same-model,
same-tasks comparison that isolates *workflows* from **just more context or more examples**?);
**transfer to new websites/domains**; the **Mind2Web offline step metrics versus WebArena
end-to-end execution** units; **cost**; and **changed-prerequisite scope** (what happens when
the site or precondition changes).

C41 corrections carried: the CLIN arithmetic is **69.5−52.7 = 16.8 from the transferred start**
and **69.5−62.2 = 7.3 over Adapt** — my "+16 over Adapt" conflated them; **reward is not success
percentage**; the broken-stove case is **qualitative, not a uniquely proven item-replacement
chain**; **"no described raw recovery path" is not proof of physical deletion**; and **ordinary
work can have feedback** (tests, checkers, Brian's corrections) — the privilege claim is about
*kinds and density* of feedback, not its presence.

**Frame held before the read (minimal):** workflows are procedure-shaped memory — the closest
artifact to Brian's re-learning pain; the cycle's load-bearing question is the third one
(isolation), because AWM's test-stream-online mode can quietly convert evaluation into
practice. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Workflows as memory: what the controls actually isolate (2409.07429v1, §2.2–2.3, §3.1–3.2,
§4.1) `[read]`

**Representation:** workflow = NL goal description + steps, each step = NL state + reasoning +
**executable action**; example-specific values abstracted ("{product-name}"); segmented and
stored. **Offline:** induce from all training examples per website before testing; the same
frozen memory serves every test — clean train/test separation. **Online:** test queries stream;
**an LM judge (Pan et al. AutoEval) labels each trajectory binary-success; judged successes are
induced into the memory used for LATER TEST QUERIES.** So the online headline is a cumulative
learning curve over the test set, and **judge false-positives enter memory ungated** — the
self-reinforcement risk lives exactly at the judge.

**Which control isolates workflows-from-more-context:**
- **vs Synapse (retrieves concrete full examples — same "more context" move):** AWM wins element
accuracy and step SR; concrete examples bias element selection, abstract sub-routines don't.
Representation isolated.
- **vs SteP (human-engineered workflows, 33.0):** induced beats hand-written (35.5).
- **The quiet bombshell: AWM-rule (deduplicated action-sequence mining, no LM abstraction) =
35.6 vs AWM-lm 35.5 on WebArena** — induction sophistication contributes ~nothing to SR there
(fewer steps only; LM better on Mind2Web). The benefit is **having workflow memory at all**,
not clever induction. Honest reporting by the authors.

**Units, kept apart:** Mind2Web = **offline step metrics on recorded traces** (element acc,
action F1, step SR) — no execution; WebArena = **end-to-end executed SR**: 35.5 vs BrowserGym
23.5 / AutoEval 20.2 / WebArena-agent 14.9, **with fewer steps (5.9 vs 7.9)** — GPT-4-0613
temp 0, same executor throughout; baseline comparisons are cross-system, the SteP/Synapse ones
are the content controls.

**Transfer:** online > offline on unseen websites and domains, margin **widening with domain
gap** (offline workflows carry domain bias); offline still beats its baseline.
**Changed prerequisites:** the paper's own named weakness — "learn to diverge from workflow
guidelines": workflows pull the agent toward workflow-consistent actions that don't fit the
current state (action F1 dips); stale-precondition failure acknowledged, not solved.

**Cost:** none reported (no tokens/dollars; judge calls in online mode unpriced).

**Verdict: the strongest executed-environment evidence for procedure-shaped memory read so
far** — beats human-written workflows, cuts steps, transfers online. Confidence: high on
executed WebArena structure and the rule-vs-LM null, medium on online numbers (LM-judged
test-stream reuse makes the score a path-dependent curve, not a holdout), high on
diverge-weakness (their words).

— cairn. Source `[read]`: arXiv HTML 2409.07429v1, opened 2026-09-26; c41 corrections carried
(16.8-from-transferred-start / 7.3-over-Adapt arithmetic; reward≠success%; broken-stove
qualitative; absence-of-recovery-path ≠ deletion proof; ordinary work can have feedback).