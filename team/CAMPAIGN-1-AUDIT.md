# CAMPAIGN-1 — pre-registration criteria audit

**Auditor:** Verity (worker-glm-3), independent. **Date:** 2026-09-12, overnight —
Brian's veto window opens after this. **Input audited:** `CAMPAIGN-1.md` DRAFT v1
(Kiln convergence, commit 16bc951), against `PROBE-remember-admission-FINDINGS.md`,
`PROBE-row6-data-gap.md`, and `docs/EXPERIMENT-20260911-trial.md` (the trial
pre-registration the spine leans on). **Method:** the record's own rules — every
criterion must be measurable with a *named, working* instrument, falsifiable,
free of causal claims its n cannot carry, and honest about what absence means.

**Summary: S1 KEEP (tighten), S2 KEEP (tighten), S3 TIGHTEN, S4 TIGHTEN (hard),
S5 TIGHTEN, S6 KEEP (tighten). No criterion is DROPped — the set is the right
set, and the guardrails section is the correct distillation of what this project
paid to learn. One missing failure mode is adopted from Cairn (scoreboard note,
not a criterion), and three instrument rules need to be standing rather than
implied. Two wording-level causal risks flagged in the thesis.**

---

## Per-criterion verdicts

### S1 — Supersession cycle closes on real work → **KEEP, with tightenings**

The cycle is discrete and observable, the target (≥1) is honest about being a
capability demonstration, and the instrument named — delivered-level, never
stream-level — is the single most important correctness decision in the draft.
It is the direct anti-P1 rule and it is right.

Tighten before the window opens:

1. **Define "deliberate convention change" operationally:** a change to a
   convention that *has a stored record* (a real supersession target exists),
   arising in the course of real work, logged with before/after text. Without
   this, "deliberate" is unfalsifiable flavor.
2. **The delivered-level check must be a programmatic receipt, not a judgment:**
   per cycle, persist the delivered toolResult text and assert — new record's
   key/content PRESENT, old record's key ABSENT (the smoke's
   `recall-after-supersede` pattern), plus the supersede receipt's status flip
   and `valid_to`. This is the P1B `delivery.jsonl` discipline applied per
   cycle. An eyeballed "recall delivered current-only" is an anecdote, and this
   project's history is a museum of anecdotes that lied.

### S2 — Stale-action events = 0 → **KEEP, with tightenings**

Target 0 with prominent failure reporting is correctly falsifiable. Two fixes
so it stays honest:

1. **Operational detection rule.** "Trial ledger" alone is a single-source
   self-report. Add: every artifact written *after* a supersession is checked
   against the current record set (diff against delivered current-only state),
   post-hoc, by Cairn with Verity audit. Detection method must be named in the
   criterion, or 0 is unfalsifiable.
2. **State the absence-of-failure caveat inside the criterion:** zero stale
   actions over n turns is *necessary-not-sufficient* evidence of suppression.
   This is the P1B branch-(i) lesson verbatim — B never exhibited the failure,
   so prevention was unestablishable. Report n (turns and post-supersede
   opportunities) next to the 0. Otherwise "zero" reads as suppression proof,
   which the small n cannot carry.

### S3 — Burden ≤1 confirm/day under tiering → **TIGHTEN**

Measurable in principle, honest about comparing against an estimate. Three
tightenings, the first is the one that matters:

1. **The classification circularity.** T0/T1 is decided by the agent whose
   burden is being measured. Left unmanaged, ≤1/day is gameable by labeling
   high-stakes decisions low-stakes. The draft already schedules Verity's T0
   proportionality audit — promote it into the criterion: post-hoc, I sample
   T0 captures for T1-eligibility and the **misclassification rate is reported
   next to the burden number**, not filed separately.
2. **Define the denominator.** ≤1/day over which days? Specify: working days
   with ≥1 capture-eligible event, and report n days + n confirms. Three days
   of one worker is a very small n — fine, say so in the same breath.
3. **Comparison discipline.** "vs the proposal's 1–3/day estimate" must stay
   labeled *estimate-vs-measured* forever. There is no control arm; "tiering
   reduced burden by X%" is a causal claim the design cannot support. Same for
   the fallback arm (universal T1): that is an untiered baseline measurement,
   not a comparison.

Clarity rating: fine as written — the trial prereg has Brian marking each
prompt clear/unclear (finding-#1 format), which is the correct rater. Report
the unclear count, not just the average.

### S4 — Self-noticing ≥3/5 relevant turns → **TIGHTEN (hard)**

This is the weakest criterion as drafted, for one structural reason: **it
conflates two different claims.** Self-noticing (the agent spontaneously
retrieves — the F1 0/8 weakness) and trigger efficacy (the new change-aware
layer fires on change events) are not the same thing. If the trigger is built
and on, a retrieval in a relevant turn is *machine-prompted* — measuring it
under the name "self-noticing" is exactly the kind of quiet redefinition this
project exists to catch.

Required tightenings:

1. **Split the metric and rename.** (a) *Trigger fire-rate:* fraction of
   adjudicated stored-record-relevant turns where the trigger fired — the ≥3/5
   target lives here. (b) *Application rate:* when fired (or recall otherwise
   available), did the agent use the delivered content. "Self-noticing"
   unqualified may only describe trigger-OFF observation, reported separately
   against the F1 0/8 baseline.
2. **Mandatory false-fire count.** ≥3/5 with no precision requirement passes
   trivially by firing always. Count trigger activations on turns adjudicated
   non-relevant and report it beside the fire-rate. A criterion with a target
   and no counter-pressure is half a criterion.
3. **Pre-register relevance adjudication.** "Stored-record-relevant turn" is
   adjudicated by Verity, blind to trigger state, under a rule written before
   the window starts. I take that job.
4. **Delivered-level here too.** Count only retrievals whose toolResult
   *delivered* the relevant record — the trial prereg already defines "recall
   deliveries" this way; S4's wording should inherit it, not fall back to
   counting calls.

### S5 — Overhead within +25% → **TIGHTEN**

Measurable and falsifiable; "beyond → flagged, not hidden" is the right
pre-commitment. The load-bearing weakness is "paired no-memory turn": pairing
is doing all the work and no pairing rule exists. This project already had to
withdraw an inflated overhead story once (the P1B "4–10×" withdrawal — favorable
numbers built on contaminated pairs). Don't grow a new one.

1. **Pre-register the pairing rule** (e.g., same task family, same worker,
   both turns completed, nearest-in-time; "descriptive pairing only" is in the
   trial prereg — promote the actual rule into the criterion and state n pairs).
2. **Symmetric skepticism.** A favorable direction (memory turns *faster*) is
   flagged and pair-audited exactly like an unfavorable one. Cost criteria that
   only bite one direction train people to look good rather than be good.
3. Report tokens as primary (wall on the local pi lane is noisy) with both
   shown.

### S6 — Capture-at-rest integrity, 0 demotions → **KEEP, with tightenings**

The stop-and-report trigger (any `active→proposed` = stop) is precise and
points at exactly the right wall — the probe-proven demotion hazard, reproduced
twice, with an `ok:true, action:"updated"` receipt while the record silently
left the serveable set. Tighten so success can't trip it and receipts can't
fool it:

1. **Whitelist expected transitions.** A *successful* supersession legitimately
   flips the OLD record `active→deprecated` with `valid_to` set. As drafted,
   "no record lost or demoted" could read S6 into stopping on a correct S1
   cycle. Scope S6 to *unsanctioned* transitions; the supersession flip is
   expected and receipted.
2. **Instrument = the vault's own stored state via scan after every write,
   never the write receipt alone.** The probe's decisive result is that a
   receipt said `ok:true` while the record was demoted out of recall. Receipts
   claim; state is. This is a standing instrument rule (see below), stated
   here where it bites first.
3. **Add "capture path = CLI write only" as an explicit S6 sub-check** — any
   native `remember` call in the live arm is itself a stop event, per
   guardrail 1.
4. Define "lost": absent from the scan of its environment's workspace, or
   status other than expected-at-that-step.

---

## Cross-cutting: hidden causal claims and small-n sweep

1. **The one-line thesis reads as an outcome.** "An agent demonstrably adapts…
   with the human paying roughly one confirmation a day and zero stale actions"
   will be quoted as if achieved. Keep it anchored: every external sentence
   about this campaign carries "(demonstration = S1–S6, descriptive, small-n)".
   The criteria header already disclaims causality — keep that disclaimer
   attached wherever the thesis travels.
2. **"Correctable by supersede" is doing quiet work in the T0 arm.** Correction
   requires detection; detection is post-hoc sampling. Report sample size and
   misses. Correctable ≠ corrected.
3. **"Decisive test" (spine section) overstates for n=1 cycle.** The trial
   prereg itself says the trial "cannot show that decision memory improves
   worker performance" — that sentence should be visible in every window-end
   report, not buried in a doc two commits deep.
4. **Good pre-commitments worth keeping visible:** the universal-T1 fallback if
   Brian rejects tiering (the burden numbers then measure the untiered
   baseline — publishable either way) is exactly the right way to pre-commit;
   the dsh metering honesty and "Brian's attention is the real cost" framing
   are correct. Kiln fusing Cairn's pushback into a measured arm instead of
   overriding it is good convergence discipline and I say so on the record.

## Missing failure modes (adopt these as standing rules)

1. **Delivered-level must reach S4, not just S1.** Guardrail 3 is stated
   globally but S4's instrument ("session logs") currently counts calls. A
   retrieval that silently delivers nothing is the P1 failure at miniature
   scale. Rule: every criterion that counts retrievals counts *deliveries*.
2. **Receipts claim; state is.** Standing instrument rule: every criterion's
   instrument asserts *observed state* (vault scan, delivered toolResult text),
   never an echoed receipt alone. Named once here; applied in S1 and S6.
3. **Vocabulary-trap failure mode.** Guardrail 4 lists the trap but no criterion
   carries it. Any automated vault interaction (trigger auto-drafts, window-end
   tooling, notify watchers) must use the verified nouns
   (`memory.propose`/`memory.commit`/`memory.read`), explicit
   `capability_constraints_json`, explicit `mode: "enforce"` — and must assert
   post-action observed state, because the wrong noun *silently denies while
   echoing a success-shaped string*. Without this rule, an automation that did
   nothing is structurally scoreable as success. Make it impossible.
4. **Operator-unavailable expiry** — see next section; adopted as a scoreboard
   sub-count, not a criterion.

## Cairn's proposal — 'expiries caused by operator-unavailable'

**Verdict: SCOREBOARD NOTE — mandatory, but not a criterion.** Three reasons:

1. **Criteria gate success; diagnostics explain outcomes.** S1–S6 are the
   campaign's falsifiable spine. Expiry diagnostics don't gate success; they
   interpret S1 (cycle not closed — why?) and S3 (burden includes *latency* —
   a confirm that lands 14 hours later because Brian slept still costs the
   workstream wall-clock, a burden dimension a per-day count never sees).
2. **"Caused by operator-unavailable" is a causal attribution the instrument
   cannot make.** The observable is: draft expired with no operator
   acknowledgment in the window. That can mean operator asleep — or notifier
   send failure (best-effort, never-throws: `delivered:false` is possible and
   quiet), wrong channel, the file stub nobody watches, or an operator who saw
   it and declined. Recording the causal story invites exactly the
   motivated-attribution the capability-vocabulary trap teaches us to expect.
3. **It is already half-instrumented.** The trial prereg defines "TTL expiry
   events" and "confirm latency" as metrics. Cairn's ask slots underneath them.

**Required shape:** rename to the observable — *TTL expiries with no operator
acknowledgment observed* — tracked as a mandatory sub-count of the existing
TTL-expiry metric, with two companion sub-counts: notifier receipts with
`delivered:false`, and wrong-code draft destructions. Reported beside S1/S3.
Pre-register the interpretation now: if expiries ≥ confirmed cycles, that is a
*gate-friction finding* delivered to Brian as a campaign-2 design input (TTL /
channel redesign), not a campaign failure and not a reason to quietly raise TTL
or reach for auto-confirm mid-window.

## Pre-window checklist (before the first evaluated cycle)

1. Provenance receipt: frozen extension lineage hash (060d842 as drafted) +
   binary sha asserted in the window-opening receipt; Kiln's mirror and the
   live pi lane must show the same hashes. Drift here invalidates everything
   silently.
2. S4 relevance-adjudication rule written and frozen (I adjudicate blind).
3. S5 pairing rule written and frozen.
4. Notify-file location + Signal channel config recorded; `delivered:false`
   visible in the ledger.
5. S6 scan-after-write wired into the cycle (one command, receipted).

## What would change my verdict

- If the window design changes (longer window, more workers), S3's small-n
  caveats ease but the S4 precision requirement and S6 whitelist do not.
- If Brian rejects tiering, S3 reverts to measuring the untiered baseline and
  the ≤1/day target is withdrawn, not quietly kept.
- If any criterion's instrument turns out to depend on a receipt where only
  observed state will do, that criterion reopens.

— **Verity** (worker-glm-3), independent audit. Receipts, or it didn't happen.

---

## Addendum — v3 diff-audit (2026-09-12, GiLMore-dispatched)

**Task:** independently test Kiln's "no other edits" claim — diff v1 (16bc951,
Kiln's mirror `implementer/repo`) against canonical `team/CAMPAIGN-1.md`;
sign off only if every change is this audit's, verbatim in substance.

**Verified clean:**

- Mirror v3 (5a0d414) is **byte-identical** to the canonical disk file.
- **v2→v3 is exactly the three parked wording folds** — thesis anchor
  "(demonstration = S1–S6, descriptive, small-n — no causal claims)";
  "correctable ≠ corrected" (detection is post-hoc sampling; sample size and
  misses reported); spine "decisive test" softened to the prereg's own limit
  ("cannot show that decision memory improves worker performance") with the
  sentence required in every window-end report. Faithful in substance to this
  audit's cross-cutting flags; nothing else moves. The wording-only claim
  holds *for v3 itself*.
- **All 28 deletions in v1→v3 are accounted for:** versioned header/status,
  three renamed section titles, the spine rewrite (cycle description preserved
  verbatim, claim softened as flagged), the T0 extension, and the S1–S6 table
  replaced by subsections carrying every per-criterion tightening, the three
  standing instrument rules, the 5-item checklist, and Cairn's sub-count —
  all verbatim in substance. Guardrails, budgets, roles, and open items are
  untouched; raw material gains exactly one receipt line (this audit).

**DRIFT FOUND — sign-off withheld.** v1's operative window line was silently
dropped in the v2 table→subsections rewrite and survives **nowhere** in v3:

> Window: 10 confirmed T1 cycles OR 3 working days, whichever first; Brian
> stop-anytime (kill switch `PI_PERSEUS_RECALL=0` or a word).

It is unrecorded in the change log, so "no other edits" is false as stated.
Consequence: the window bounds S1–S6 evaluation and the kill switch is the
stop mechanism; both now live only in the frozen prereg (6df91c7) and, for
the window, in Brian's open item #2. The morning package's self-contained
summary buries its own stop rule two commits deep — the exact failure this
audit flagged in the spine, recurring on the safety line. (The control itself
still exists in the extension and runbook; this is a documentation
regression, not a lost control.)

**Remedy (one line):** restore the window line verbatim at the end of the
S6/scoreboard block and record the restore in the change log. On that
restore: **"v3+restore audited = audit-complete, Verity."**

— **Verity** (worker-glm-3), diff-audit addendum.
