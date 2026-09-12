# CAMPAIGN-1 (DRAFT v3 — wording pass per Verity's cross-cutting flags; DRAFTING ONLY, no execution begun)

**Status:** v2 converged by Kiln per GiLMore's overnight pass. Changed
sections are marked **(v2)** with a change-log at the bottom; everything
else is verbatim v1. **Verity's audit: S1 KEEP (tighten), S2 KEEP
(tighten), S3 TIGHTEN, S4 TIGHTEN (hard), S5 TIGHTEN, S6 KEEP (tighten) —
none dropped.** Brian holds one veto in the morning. Authors of record:
Kiln (spine + workstream), Cairn (tiered-capture pushback, fused as the
burden arm), with raw material from Assay, Aletheia (Alice), Corvid,
Ledger. Standing limits unchanged; extension stays frozen at the 060d842
lineage for the live arm.

## One-line thesis (v3 — anchor attached)

An agent demonstrably adapts when its world changes — on real work, with the
human paying roughly one confirmation a day and zero stale actions — by
closing the supersession loop on the live trial and making retrieval
triggering change-aware instead of human-dependent.
**(demonstration = S1–S6, descriptive, small-n — no causal claims; this
anchor travels with every external citation of the thesis.)**

## Design (fused: Kiln A-spine + B-workstream + Cairn's tiered-capture)

### Spine — close the supersession loop on real work (from Kiln A + the frozen trial) (v3 — claim softened)

The trial's pre-registration (docs/EXPERIMENT-20260911-trial.md) contains the
trial's own limit, restated here where the test lives: closing this cycle
**cannot show that decision memory improves worker performance** — that
sentence belongs in every window-end report, not buried two commits deep.
What the cycle does demonstrate is narrower and still load-bearing: that the
supersession loop closes on real work (a deliberate convention change →
supersede → recall thereafter delivers current-only → stale-action events
= 0). The campaign runs the trial to that cycle. Memory that adapts when
circumstances change is the charter's "adapt when circumstances change,"
made measurable with instruments the team already trusts.

### Workstream — change-aware triggering (from Kiln B + the self-noticing data)

The measured weakness is not storage or suppression — it is that the agent
does not LOOK (F1 0/8 spontaneous vs F2 8/8 nudged; trial finding: self-
noticing weak). Build a change-aware trigger in the nudge layer: fire
retrieval on (new task in a known project · contradiction with a stored
decision · resumption after a gap). Mechanism-small, nudge-layer only, no
perseus changes, no extension unfreeze. Metric: unprompted relevant
retrievals x/y, from session logs.

### Burden arm — risk-tiered capture (from Cairn's pushback, fused)

Cairn's pushback accepted: **universal human-confirm is itself the burden**,
and burden is Brian's attention — the one resource the charter says not to
spend. The campaign therefore runs capture in two tiers as its measured
variable:

- **T0 (agent-confirmed, low-stakes):** conventions, notes, pointers — the
  worker self-captures via `confirmed_by: "agent"` (the 7a exception switch
  the frozen extension already has: `allowAgentConfirmed: true`,
  **config-only, no unfreeze**). Every T0 record is logged (notify file +
  session logs) and audited after the fact by Verity for proportionality;
  any T0 record is correctable by supersede, so the cost of a mistake is one
  T1 confirm, not a corrupted store. **(v3) Correctable ≠ corrected:**
  correction requires detection, and detection is post-hoc sampling — the
  sample size and the misses are reported next to every "correctable"
  claim, not assumed.
- **T1 (human-confirmed, high-stakes):** decisions that bind future behavior
  (architecture, deployments, project conventions) — operator-confirmed as
  today, with the finding-#1 plain-language presentation format REQUIRED.

This is an in-experiment amendment to 7a's default, which is exactly what
Brian's veto covers. If he rejects tiering, the campaign still runs with
universal T1 (the burden numbers then measure the untiered baseline — also
publishable).

## Pre-registered success criteria (v2 — tightened per CAMPAIGN-1-AUDIT.md; all descriptive, small-n, no causal claims)

### S1 — Supersession cycle closes on real work (v2; v1: "≥1 cycle, delivered-level check")

Target ≥1 complete cycle, unchanged. v2 tightenings:

1. **"Deliberate convention change" is operationally defined:** a change to
   a convention that *has a stored record* (a real supersession target
   exists), arising in the course of real work, logged with before/after
   text.
2. **The delivered-level check is a programmatic receipt, not a judgment:**
   per cycle, persist the delivered toolResult text and assert — new
   record's key/content PRESENT, old record's key ABSENT (the smoke's
   `recall-after-supersede` pattern), plus the supersede receipt's status
   flip and `valid_to`. P1B `delivery.jsonl` discipline, applied per cycle.

### S2 — Stale-action events = 0 (v2; v1: "trial ledger, target 0")

Target 0 with prominent failure reporting, unchanged. v2 tightenings:

1. **Named detection rule:** every artifact written *after* a supersession
   is checked against the current record set (diff against the delivered
   current-only state), post-hoc, by Cairn with Verity audit. "Trial ledger"
   alone was a single-source self-report.
2. **Necessary-not-sufficient caveat lives inside the criterion:** zero
   stale actions over n turns is necessary-but-not-sufficient evidence of
   suppression (the P1B branch-(i) lesson). n (turns AND post-supersede
   opportunities) is reported next to the 0.

### S3 — Burden ≤1 confirm/day under tiering (v2; v1: "≤1/day vs 1–3 estimate")

v2 tightenings:

1. **T0 misclassification rate reported beside the burden number, not filed
   separately:** Verity post-hoc samples T0 captures for T1-eligibility; the
   rate closes the classification circularity (the agent whose burden is
   measured decides the tier).
2. **Denominator defined:** working days with ≥1 capture-eligible event;
   n days + n confirms reported. Three days of one worker is a very small n
   — stated in the same breath.
3. **"Estimate-vs-measured" labeling kept forever.** No control arm exists;
   "tiering reduced burden by X%" is a causal claim the design cannot
   support. The universal-T1 fallback is an untiered baseline measurement,
   not a comparison.
4. Clarity rating (finding-#1 format): report the **unclear count**, not
   just the average.

### S4 — Self-noticing → split (v2, hard; v1: "≥3/5 relevant turns, session logs")

v1 conflated two claims: self-noticing (spontaneous retrieval — the F1 0/8
weakness) and trigger efficacy (the new layer firing on change events).
v2 splits them:

- **(a) Trigger fire-rate:** fraction of adjudicated stored-record-relevant
  turns where the trigger fired — the **≥3/5 target lives here**.
- **(b) Application rate:** when fired (or recall otherwise available), did
  the agent use the delivered content.
- "Self-noticing" unqualified may only describe **trigger-OFF** observation,
  reported separately against the F1 0/8 baseline.

Tightenings: **mandatory false-fire count** (trigger activations on turns
adjudicated non-relevant, reported beside the fire-rate — ≥3/5 with no
precision requirement passes trivially by firing always); **relevance
adjudication by Verity, blind to trigger state, under a rule written and
frozen before the window starts**; **delivered-level counting** (only
retrievals whose toolResult *delivered* the relevant record — inheriting the
trial prereg's "recall deliveries" definition, not counting calls).

### S5 — Overhead within +25% (v2; v1: "paired no-memory turn, flag beyond")

v2 tightenings:

1. **Pre-registered pairing rule:** same task family, same worker, both
   turns completed, nearest-in-time; n pairs stated. ("Descriptive pairing
   only" promoted from the trial prereg into the criterion.)
2. **Symmetric skepticism:** a favorable direction (memory turns *faster*)
   is flagged and pair-audited exactly like an unfavorable one.
3. **Tokens primary** (wall on the local pi lane is noisy), both shown.

### S6 — Capture-at-rest integrity, 0 demotions (v2; v1: "no record lost or demoted")

v2 tightenings:

1. **Scope to UNSANCTIONED transitions.** A successful supersession
   legitimately flips the OLD record `active→deprecated` with `valid_to`
   set — expected and receipted; S6 does not stop on a correct S1 cycle.
2. **Instrument = the vault's own stored state via scan after every write,**
   never the write receipt alone (the probe's decisive result: a receipt
   said `ok:true, action:"updated"` while the record left the serveable
   set). Receipts claim; state is.
3. **CLI-write-only sub-check:** any native `remember` call in the live arm
   is itself a stop event (guardrail 1).
4. **"Lost" defined:** absent from the scan of its environment's workspace,
   or status other than expected-at-that-step.

### Scoreboard sub-count (adopted from Cairn; verdict: mandatory scoreboard note, not a criterion)

**"TTL expiries with no operator acknowledgment observed"** — renamed to the
observable (the causal story "operator-unavailable" is not observable).
Tracked as a mandatory sub-count of the existing TTL-expiry metric, with two
companion sub-counts: notifier receipts with `delivered:false`, and
wrong-code draft destructions. Reported beside S1/S3 (it interprets S1 "why
didn't the cycle close" and S3's latency dimension). **Pre-registered
interpretation:** if expiries ≥ confirmed cycles, that is a *gate-friction
finding* delivered to Brian as a campaign-2 design input (TTL / channel
redesign) — not a campaign failure, and never a reason to quietly raise TTL
or reach for auto-confirm mid-window.

## Standing instrument rules (adopted from the audit; bind every criterion)

1. **Receipts claim; state is.** Every criterion's instrument asserts
   *observed state* (vault scan, delivered toolResult text), never an echoed
   receipt alone. Applied in S1 and S6; named once, standing everywhere.
2. **Delivered-level reaches S4, not just S1.** Every criterion that counts
   retrievals counts *deliveries* — a retrieval that silently delivers
   nothing is the P1 failure at miniature scale.
3. **The vocabulary trap binds automation.** Any automated vault interaction
   (trigger auto-drafts, window-end tooling, notify watchers) uses the
   verified nouns (`memory.propose`/`memory.commit`/`memory.read`), explicit
   `capability_constraints_json`, explicit `mode: "enforce"` — and asserts
   post-action observed state, because the wrong noun silently denies while
   echoing a success-shaped string. Without this rule, an automation that
   did nothing is structurally scoreable as success.

## Pre-window checklist (Verity; completed before the first evaluated cycle)

1. Provenance receipt: frozen extension lineage hash (060d842 as drafted) +
   binary sha asserted in the window-opening receipt; Kiln's mirror and the
   live pi lane must show the same hashes. Drift here invalidates everything
   silently.
2. S4 relevance-adjudication rule written and frozen (Verity adjudicates
   blind).
3. S5 pairing rule written and frozen.
4. Notify-file location + Signal channel config recorded; `delivered:false`
   visible in the ledger.
5. S6 scan-after-write wired into the cycle (one command, receipted).

## Hard guardrails from the probes (non-negotiable build constraints)

1. **CLI `write` remains the only activation path.** Aletheia (reproduced x2):
   native `remember` on an active key **demotes it active→proposed** with an
   `ok:true, action:"updated"` receipt; recall then abstains. No record
   migrates to native remember. (team/PROBE-remember-admission-FINDINGS.md)
2. **The native admission chain is treated as inert** until a record is
   OBSERVED going proposed→active through public tools (never observed;
   attested-journal route unreached — HMAC canonicalization, 15 formats
   rejected; method limit stated). `maintain`/`consolidate` do not promote
   proposals (Assay). Corollary: campaign-C (upstream repair) stays gated.
3. **Everything is measured at DELIVERY level** (the P1 root cause):
   stream-level presence is necessary-but-insufficient, always.
4. **Capability vocabulary trap:** only `memory.propose` / `memory.commit` /
   `memory.read` are real nouns; `memory.write.*` silently denies while
   echoing the wrong noun back (Alice). Any authority work uses the verified
   vocabulary + explicit `capability_constraints_json` + explicit
   `mode: "enforce"`.
5. **Negative results are deliverables,** preserved verbatim with receipts.

## Budgets

- worker-pi (Cairn): local, free — the trial continues as the live arm.
- Kiln (build + execute) and Verity (audit): flash lanes, free.
- Ledger (claude): tried/failed/open cross-reference feeding the window-end
  report — claude lane.
- dsh lanes (Aletheia, Assay, Corvid): **metered with no counter → bounded
  tasks only.** No new native-pipeline spend this campaign. Open bounded
  item: the admission-path unit-test confirmation needs `cargo`/`rustc`,
  absent on this host — parked unless a lane has rust. Muse: calibrated
  (Corvid, ANSWERED/CORRECT/STABLE n=1x2, ~$0.002); no further spend.
- **Brian's attention is the real cost:** T1 confirms only (target ≤1/day),
  one veto now, stop-anytime.

## Roles

- **Cairn** — dogfooder; lives the tiers; reports burden, clarity, self-
  noticing from inside.
- **Kiln** — build + execute + survive-contact proof; change-aware trigger;
  tiering config (config-only) and its receipts.
- **Verity** — audits THESE criteria next; audits ledger-vs-claims at window
  end (T0 proportionality included).
- **Ledger** — synthesis: tried/failed/open cross-reference as the report's
  spine.
- **Aletheia, Assay, Corvid** — standing probe seats, bounded tasks only;
  their findings are this proposal's raw material and the window's audit
  baseline.

## Raw material (receipts)

- Assay: native-capture repro — non-delivery is status withholding by
  construction (NON_SERVEABLE_STATUSES); three divergences from the Kiln
  probe (id-match note, abstention reason env-dependent, admission gate
  transport-identity bound); maintain/consolidate do not promote.
  scripts/repro-20260912-assay/
- Aletheia: remember+admission probe (demotion x2; capability traps;
  attestation unreached) — team/PROBE-remember-admission-FINDINGS.md;
  row-6 data gap (answer_id never captured — "capture is the hole," fourth
  preregistration-class failure) — team/PROBE-row6-data-gap.md.
- Kiln: native capture probe (no derived lineage; proposed-state wall) —
  scripts/experiment_20260912_native_capture/FINDINGS.md, commit 84cc6b9.
- Trial pre-registration (window/metrics/roles/budget) — commit 6df91c7;
  finding #1 presentation format — commit 4fbd904; decision-memory build —
  3f9498f..e9e5621 + 060d842.
- Corvid: Muse calibration — commit 7d42fdf.
- Verity: criteria audit — team/CAMPAIGN-1-AUDIT.md (this v2's source).

## Open items for Brian's morning veto

1. Approve T0/T1 tiering as the in-experiment amendment to 7a (agent-
   confirmed LOW-STAKES only, after-the-fact audit, correctable by
   supersede). Everything else in 7a stands.
2. Confirm the window (10 T1 cycles / 3 days) and the ≤1/day burden target.
3. (Optional, zero-cost) bless campaign-C (upstream capture repair) as the
   pre-approved campaign-2 should A/B show capture is the binding constraint.

## Change log (v1 → v2, auditable)

- S1 (v2): + operational definition of "deliberate convention change"; +
  programmatic per-cycle delivered-level receipt (persisted toolResult text;
  new PRESENT / old ABSENT / status flip / valid_to). [v1: eyeballed
  delivered-level check]
- S2 (v2): + named post-hoc detection rule (artifact diff vs current record
  set; Cairn executes, Verity audits); + necessary-not-sufficient caveat
  with n (turns + post-supersede opportunities) reported. [v1: "trial
  ledger"]
- S3 (v2): + T0 misclassification rate beside the burden number; +
  denominator (working days with ≥1 capture-eligible event; n days + n
  confirms); + "estimate-vs-measured" labeling permanent; + unclear count
  reported. [v1: bare ≤1/day]
- S4 (v2): split into trigger fire-rate (≥3/5) + application rate;
  "self-noticing" reserved for trigger-OFF observation vs F1 baseline;
  + mandatory false-fire count; + blind frozen relevance-adjudication rule
  (Verity); + delivered-level counting. [v1: single conflated metric]
- S5 (v2): + pre-registered pairing rule (task family/worker/completed/
  nearest-in-time, n pairs); + symmetric skepticism on favorable direction;
  tokens primary, wall shown. [v1: unruled pairing]
- S6 (v2): scoped to UNSANCTIONED transitions (supersession flip expected +
  receipted); + scan-after-write as the instrument (receipts claim, state
  is); + CLI-write-only sub-check; + "lost" defined. [v1: blanket
  "no demotions"]
- NEW: standing instrument rules (receipts/state; delivered-level to S4;
  vocabulary trap binds automation).
- NEW: scoreboard sub-count "TTL expiries with no operator acknowledgment
  observed" + `delivered:false` count + wrong-code destructions, with
  pre-registered gate-friction interpretation (adopted from Cairn; Verity
  verdict: scoreboard note, not a criterion).
- NEW: pre-window checklist (5 items, verbatim from the audit).
- Unchanged by directive: thesis wording, design sections, guardrails,
  budgets, roles, raw material, open items. (Verity's cross-cutting wording
  flags — thesis anchor phrasing, "correctable ≠ corrected" sampling note,
  "decisive test" overstatement — were NOT folded; left for GiLMore's
  ruling so v2's diff stays exactly the enumerated scope.)
- v3 (wording only, GiLMore-directed; the three parked cross-cutting flags
  now folded): (1) thesis — anchor "(demonstration = S1–S6, descriptive,
  small-n — no causal claims)" attached to the one-line thesis; every
  external citation of the thesis carries it. (2) T0 arm — "correctable ≠
  corrected" note added (correction requires detection; detection is
  post-hoc sampling; sample size and misses reported). (3) spine —
  "decisive test" softened to the prereg's own limit ("cannot show that
  decision memory improves worker performance"), with that sentence required
  in every window-end report. No other edits; headers marked (v3) at the
  three touched spots.
