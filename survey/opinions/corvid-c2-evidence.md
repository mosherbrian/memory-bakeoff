# Contrarian continuation — the evidence moves me from “episode-first” to a conditional

**corvid · 2026-09-26 · cycle 2 continuation.** Signed opinion, not an audit. ROLES.md:
*“argue the strongest case AGAINST the current position memo, and for the best rival idea.”*
Primary abstracts read this cycle: AFTER (2606.23127), BASM (2608.22339), Skill-Evo4GUI
(2609.04869).

**It changes my default — honestly.** I said “retrieve episodes + executive reasoning.”
Three matched-control results now make a *universal* episode-first bet indefensible:

- **Skill-Evo4GUI** is the cleanest causal evidence for stored skills I have seen: a
  configuration-matched **empty-library control**, same action stack/tasks/horizon, five-iteration
  warm-up. The evolving library beats empty in **all four OSWorld domains, +5.7 to +18.6 pts** —
  procedure retention, not prompt length. `[read]`
- **AFTER** shows enterprise-scale gains (one refinement round **+3.7–6.7 pts**; multi-model
  evolved skills **73.1%** cross-model) across 6 roles/22 skills. `[read]`
- **BASM** is the strongest pro-skill case *and* the strongest objection: success-only skills
  create a **Skill Imitation Trap** — procedure skills raise the **wrong-tool margin +47%** over
  memory-free; adding explicit boundary fields (applicability, risk cues, avoidance, recovery)
  flips it to **+23.8% AppWorld / +5.0% BFCL / −4.6% ASR**. `[read]` That is my applicability
  argument, measured: **unconditional stored procedures are harmful; boundary-aware ones pay.**

**So the conditional, not the gate.** Store a procedure when (a) the task family genuinely
repeats, (b) applicability is cheaply decidable *and* authored as boundary fields rather than
implied, (c) verifier + environment identity are attached. Reconstruct from episodes for one-off
or churn-heavy work. My c2 rule stands as the tie-breaker; the evidence only moves the threshold
toward *store* for repeated, boundary-aware families. **Medium-high confidence.**

**Concessions I owe the memo.** (1) **Raw episodes rot too**: a 2024 transcript cannot tell you
today’s tool versions, so reconstruction cost is *not* bounded by retrieval alone — an
environment drift term belongs on both sides of the rule. (2) R53 was a **ceiling null**, not
failed application; I over-read it in c2 and should not have used it as R53-as-application-failure.
(3) I said “prefer reconstruction”; with these controls the honest position is **conditional
choice**.

**Strongest remaining objection to the pro-skill case.** The gain is only demonstrated when the
skill is **supplied or hand-annotated** (AFTER: “skills supplied by task annotation”; BASM’s
boundary fields are authored artifacts). None of the three prices **authoring/upkeep**, and
Skill-Evo4GUI’s own provenance analysis shows **revision churn where repeated accepted edits fail
to recover the originating task** — the skill mutates away from what passed, i.e. a stored skill
can corrupt its own provenance. Selection also stays unsolved: “retrieving more skills” still
raised wrong-tool confidence. So the case FOR storage does **not** yet cover auto-distilled,
unpriced, churn-exposed skills — exactly Brian’s default. **Medium confidence.**

**Single most decision-relevant unresolved comparison for cycle 3:** on one repeated, Brian-like
task family with a **mid-cycle version change**, head-to-head — *hand-authored boundary-aware
skill* vs *auto-distilled skill (no annotations)* vs *raw-episode reconstruction* — scoring
recovery of the originating task after revision, total authoring+upkeep minutes, and stale-
adoption errors. That one comparison decides the rule’s binding terms; everything else is
bookkeeping. No experiment this cycle.

— corvid. `[read]` abstracts fetched 2026-09-26; no source reproduction; no experiment.
