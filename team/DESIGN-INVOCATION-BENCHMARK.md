# DESIGN — Invocation Benchmark: fire-before-mistake on a scripted scenario corpus

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 08:44 UTC · **Cost:** $0, design only, no runs, no model calls
**QUEUE:** row 24 (claimed by Corvid this turn) · **Verifier:** Assay
**Charter integration:** Stratum after 04:13 (§10)
**Scope gate:** design/spec only. **No runs are authorized by this file.**
**HARD RULE (row 24/25):** no raw transcript content on this lane. This design
uses **synthetic scenarios only** and **Kiln's aggregate pilot statistics**
(`team/TRANSCRIPT-MINING-PILOT.md` — counts, classes, precision) as its only
real-world grounding. No excerpt, quoted span, or reconstructable session
appears anywhere below.

---

## Plain English first (for Brian)

Every memory number we have right now asks "when someone asked, did the right
record come back?" The live arm already told us the harder truth: the worker
often **doesn't ask**, so the best record in the vault never gets a chance. The
existing "invocation rate" is a yes/no — was the system ever called — and a
system that is never called can still get a passing retrieval score because its
zeros simply aren't in that comparison.

This benchmark asks the timing question directly: **for a situation where a
stored note would have stopped a mistake, did the system surface that note
before the mistake happened?** We script a small scenario, plant the note, put
in turns where it matters and turns where it doesn't, and read the answer out of
the **harness-observed fire events** mechanically (the system's own trigger log is
corroboration). The headline number is the **fire-before-
mistake rate (FBMR)**: fires on the informative reason, before the deadline,
over the moments that demonstrably need the note. A system that fires on
everything gets caught by a false-fire companion; a system that fires but serves
nothing gets caught by a delivered-level companion. This is design only — it
costs nothing until Brian/R2 gates it.

---

## 0. Question, claim ceiling, and what is new

**Question:** on a frozen scripted corpus, for each system + integration, what
fraction of load-bearing memory moments did the system proactively invoke
*before* the agent acted, and what fraction did it actually cover with the
relevant record before that deadline?

**Claim ceiling (travels with every citation):** descriptive, small-n,
scenario-level. This instrument measures the **invocation pipeline** (does the
proactive layer fire on the informative signal, in time, and deliver). It does
**not** measure whether memory causes better work on real tasks — that is row
25's outcome protocol. It does not score retrieval quality except as a
companion column.

### 0.1 Relation to what already exists

| Existing thing | What it measures | What this adds |
|---|---|---|
| Charter Patch 3 dimension "invocation rate" | ever invoked? capture/retrieval **call counts**; zero-invocation run is its own row | **timing** (before a deadline), **selectivity** (informative fire, not fire-always), **load-bearing denominator** |
| CAMPAIGN-1 S4(a) trigger fire-rate | fraction of **adjudicated relevant** live turns where the trigger fired | repeatable **synthetic corpus**, deadline semantics, cross-system, no blind rater needed for the primary label |
| CAMPAIGN-1 S4 false-fire count | trigger activations on adjudicated non-relevant turns | programmatic false-fire + near-miss + stale companions |
| Row 25 outcome protocol M1–M4 | did *work outcomes* improve | isolates the invocation step that precedes any outcome |

This is the ambitious version of Patch 3 item 2, as Brian's "inambitious"
critique asked: it makes "the system never fires" a first-class, timed,
selectivity-constrained number rather than a footnote.

---

## 1. Definitions (frozen before the first run; all machine-checkable)

- **Scenario** — a self-contained synthetic mini-task: an ordered list of user
  turns over a synthetic workspace, with planted records and one or more
  designated moments. Scenarios are generated from deterministic templates
  (§2.4) and are **held out** from the system: the system sees only its task
  turns and its own store, never the moment manifest.
- **Turn** — one user input → agent action unit, matching the S4 unit
  (`S4-ADJUDICATION.md` A1). Turn boundaries come from the harness log.
- **Moment M** — a designated turn whose situation is covered by one or more
  planted records (`record_set(M)`) that are `active` at turn start. Each
  moment pre-registers:
  - `correct_action_set(M)` and `wrong_action_set(M)` — programmatic action
    labels (exact strings / artifact hashes / command ids), and
  - `deadline(M)` = timestamp of the agent's **first action** in response to M.
- **Invocation event** — any memory-side event on or before a deadline,
  normalized across systems (§3). Kinds: `proactive_topic`, `proactive_fresh`,
  `proactive_gap`, `auto_retrieval`, `explicit_call`, `context_dump`.
- **Load-bearing moment** — a moment where the **no-memory OFF control** takes
  a `wrong_action`. Only these enter the primary denominator. If OFF takes
  `correct_action`, the moment is `non-load-bearing` and is reported, never
  scored (the note didn't matter). If OFF takes an action in neither set, it is
  `other` and excluded, flagged.
- **Fire-before-mistake (informative)** — a `proactive_topic` invocation on or
  before `deadline(M)`.
- **Covered** — the relevant record id was **delivered** (delivered-level:
  the toolResult text named it) on or before `deadline(M)`, and it was still in
  context at the action (context accounting, §4.4).
- **System + integration** — per AGENTS, the unit is the complete stack
  (engine + ingestion + models + runtime + harness + tools). The **invocation
  mode** is a declared, frozen per-arm field:
  `native_proactive` | `harness_trigger` | `explicit_only` | `context_dump`.

---

## 2. Scenario corpus

### 2.1 Turn types (interleaving is mandatory)

A scenario alternates moment turns with filler turns. No two moment turns are
adjacent; every moment is preceded and followed by ≥1 filler.

| Turn type | Has a covering record? | Purpose |
|---|---|---|
| `moment_topic` | yes, and prompt shares ≥1 topic token with the record summary | primary; a topic-based proactive layer *can* fire |
| `moment_offtopic` | yes, but prompt shares **no** topic token with any summary | separates topic self-noticing from `fresh`/`gap` recency firing; reported as its own stratum |
| `filler_plain` | no | false-fire denominator; ordinary work |
| `filler_near_miss` | no; a **near-miss** record exists (same subject, does not govern the choice) | near-miss false-fire |
| `filler_stale_only` | only a `deprecated`/superseded record that would elicit a wrong action | stale-use harm; must not be counted as covered |
| `filler_anachronism` | a record whose `valid_from` is **after** the turn | anachronism check (S4 A5, programmatic) |

### 2.2 Families (synthetic; class names grounded in the aggregate pilot card)

Kiln's aggregate pilot yields 15 correction events and 21 durable facts with
class-level precision only (`team/TRANSCRIPT-MINING-PILOT.md`). Family *names*
and relative weights come from that aggregate card; the scenario content is
invented.

| Family | Aggregate grounding | Synthetic situation (one line) |
|---|---|---|
| `env_fact` | env-fact-correction 7 + env_fact 11 (largest) | record pins a path/port/URL/version; moment asks for it |
| `convention` | convention 10 | record states always/never; moment would violate it |
| `negation` | negation 3 | record forbids a legacy action; moment offers it |
| `actually` | actually 2 | record corrects a prior belief the moment would act on |
| `repeated_instruction` | repeated-instruction 2 groups | record encodes an instruction the operator repeats |
| `wrong` | wrong 1 | generic wrong action with a clear correct twin |

`i_said` is **excluded** (pilot fired 0 genuine times; not measurable yet), per
row 25's M4 rule.

### 2.3 Worked synthetic examples

**A — `env_fact`, topic-reachable.** Planted record `R-A`
`{key: staging-endpoint, summary: "staging endpoint moved off 8080",
content: "STAGING_URL=https://staging.internal:8443"}`.
Moment turn: *"write the staging config file."* `correct_action_set` = file
containing `https://staging.internal:8443`; `wrong_action_set` = file containing
`:8080`. Fillers: *"show git status"*, *"what's in README"*. Near-miss record:
`staging-db-port=5432` (fires must not be credited). The OFF control writes
`:8080` → moment is load-bearing.

**B — `convention`.** `R-B` = *"result directories are append-only; never
overwrite an existing `results/<dir>`."* Moment: *"re-run the calibration and
refresh `results/cal42`."* Correct = a new dir / refusal with a pointer; wrong =
overwrite in place. Detection: directory inode/mtime and file-list diff (state,
not receipt).

**C — `negation` + stale companion.** `R-C` = *"do not use `deploy.sh`; it pins
the old vault."* `R-C` is later superseded by `R-C'`, which sanctions a
different script. Moment: *"deploy using `deploy.sh`."* Correct = the sanctioned
script; wrong = `deploy.sh`. A system that delivers the now-`deprecated` `R-C`
and acts on it is scored `stale_use`, not coverage.

**D — anachronism/near-miss trap.** A moment with **no covering record**; a
near-miss record `R-D` exists, and a record `R-D''` is `valid_from` *after* the
deadline. A system that fires for either gets `near_miss_fire`/
`anachronism_violation`; the moment is not rewarded.

### 2.4 Generation and validation rules

- **Templates + frozen seed.** Scenario templates are code, not prose; a
  committed seed generates the concrete turn strings, so the corpus is
  reproducible and can be regenerated. The moment manifest (which turn is a
  moment, which record covers it, the action sets) is **never injected** into
  the system prompt.
- **Determinism.** Templates carry no randomness after the seed; the corpus
  hash + manifest hash are frozen before the first run (row 25 §6 pattern).
- **Held-out rotation.** At least 20% of scenarios are a held-out split,
  generated from templates withheld from any prompt/tuning pass (anti-hardcoding).
- **Topic reachability is pre-registered per moment** (a pure string/token test)
  so the `moment_topic` vs `moment_offtopic` split is fixed before data.
- **Leak gate.** A deterministic check must fail closed if the moment manifest
  hash, the correct/wrong action strings, or the covering record content appear
  anywhere the system could read them during a run. This mirrors row 25 §5.2
  and S4's redaction audit; it is required before any run.
- **No raw content.** All turn strings, records, and tasks are synthetic. The
  only real-world numbers are the aggregate counts above; no transcript text is
  copied, quoted, or paraphrased.

### 2.5 Corpus tiers (planning arithmetic; the tier is a Stratum/Brian call)

| Tier | Load-bearing moments | Fillers | Use |
|---|---|---|---|
| `smoke` | 12 (2/family) | 24 | instrument wiring + controls only; no per-system claim |
| `standard` | 60 (10/family) | 120 | per-system FBMR with a Wilson interval; the minimum for a headline |
| `extended` | 200 (≈33/family) | 400 | family-level rates and cross-system contrasts |

Planning note, not a power law: a Wilson interval on a single proportion near
p≈0.5 is about ±0.13 at n=60 and ±0.07 at n=200. Moments cluster within
scenarios, so the scorer reports a scenario-clustered bootstrap CI, and any
headline below `standard` is descriptive only.

---

## 3. Generic invocation-event schema and adapter contract

Each system supplies a thin adapter that maps its native logs to this schema;
the scorer never reads system-specific logs directly. **Unmappable is reported
as `unmappable`, never as zero** (the builder's `unmetered` lesson).

```jsonc
// invocation-events.jsonl — one harness-observed row per memory-side event
{
  "run_id": "<scenario+arm+seed>", "system_id": "<engine>",
  "integration_mode": "native_proactive|harness_trigger|explicit_only|context_dump",
  "scenario_id": "...", "turn": 3,
  "channel": "memory",              // B3: only memory-channel events can fire
  "mechanism": "proactive_topic|proactive_fresh|proactive_gap|auto_retrieval|explicit_call|context_dump",
  "reasons": ["topic"],             // controlled tokens {fresh, gap, topic}; exact membership
  "record_ids": ["R-A"],            // exact canonical ids injected (injection payload)
  "seq": 17,                        // harness monotonic sequence — B3 ordering, not wall clock
  "delivered_tokens": 41,
  "context_ids_at_action": ["R-A"], // harness-observed ids still in context at the action
  "at": "2026-...Z",                // wall clock, logs only — never used for ordering
  "matched": ["staging","endpoint"],
  "source_log": {"path": "...", "sha256": "..."},
  "context_tokens": 812,
  "prohibited_present": false,
  "adapter_version": "<sha>"
}
```

Required adapter fields (fail closed if absent):

1. `state_scan(scenario, turn)` — status + `valid_from`/`valid_to` of every
   record as of turn start, from **observed store state**, never a write
   receipt (S4 A2, standing rule 1).
2. `proactive_fire(turn)` — the harness-owned injection boundary emits one
   event with the B3 tuple `{channel, mechanism, reasons, record_ids, seq}`.
   The committed `pi-change-trigger` fire log (`at, turn, prompt_sha256,
   prompt_len, fired, reasons, matched_tokens, gap_minutes`) is **corroboration
   only**, never the score.
3. `delivery(turn)` — delivered toolResult record ids (`record_ids` at
   delivered level) + token counts, with content hashes.
4. `context_ids_at_action(turn)` — harness-observed ids still in context when
   the agent acts; closes the persistence clause that `CBMR`/`FBMR_persist`
   depend on (Assay C1 / Alice's extension, 2026-09-13).
5. `invocation_mode` — declared and frozen per arm.

**Harness-trigger arm (Tier 2, controlled):** for engines with no native
proactive layer, the harness applies the frozen `pi-change-trigger` logic
(`tokensOf` + `evaluateFire`) with the topic set derived from **each system's
own record keys/summaries** via `tokensOf`. This tests whether the records a
system stores carry enough signal to fire. It is labeled `harness_trigger` and
is **not** a product score (charter `controlled_core` semantics).

---

## 4. Metrics (programmatic; every one computed from §3 + the manifest)

Let `L` = set of load-bearing moments for a system run.

### 4.1 Primary — fire-before-mistake rate (topic)

```
FBMR_topic = |{ m in L : a proactive_topic event with e.seq < action_seq(m) }| / |L|
```

Ordering is the harness monotonic `seq` (B3-F2), **never** wall-clock `at`;
`seq == action_seq` is not a fire. Only `proactive_topic` counts.
`proactive_fresh` and `proactive_gap` are
recency/process artifacts (a first prompt always fires `fresh`; see Cairn's
live-arm note and `WINDOW-OPENING.md` method note) and are **excluded from the
primary**, reported as `fresh_rate`/`gap_rate` beside it. A system whose FBMR
comes only from fresh/gap has not demonstrated self-noticing.

### 4.2 Mandatory companions (no FBMR may be cited alone)

```
FBMR_any  = any fired event with e.seq < action_seq(m) / |L|
CBMR      = relevant record delivered with e.seq < action_seq(m)
            AND present in context_ids_at_action / |L|
AvoidRate = ON action == correct_action AND CBMR holds / |L|
ExplicitBefore = an explicit_call with e.seq < action_seq(m) / |L|   # self-noticing fallback
```

- `FBMR` high, `CBMR` low = "fires, serves nothing" (a retrieval failure).
- `CBMR` high, `FBMR` low = "covers when asked, never asks".
- `ExplicitBefore` high with `FBMR` low = the agent, not the system, did the
  noticing; reported, not credited to the system's proactive layer.

### 4.3 Selectivity (the fire-always guard)

```
FalseFire   = fired(topic) on filler_plain / |filler_plain|   # fresh/gap are process artifacts, reported as fresh_rate/gap_rate (§4.1); ruling 2026-09-14
NearMissFire= fired on filler_near_miss / |filler_near_miss|
FirePrecision = |fired turns that are load-bearing moments| / |fired turns|
```

### 4.4 Context and harm (AGENTS standing rules)

- `context_tokens`: per-turn and scenario totals; the `context_dump` mode and
  the long-context null are reported at their true cost.
- `stale_use`: the programmatic conjunction — a `deprecated` record was delivered
  **and** the action was in `wrong_action_set` for that moment. The causal "as a
  result" reading is not claimed; the conjunction is the metric (harm, never
  rewarded as coverage).
- `anachronism_violations`: any cover claimed from a record postdating the
  deadline (programmatic A5 check).
- `prohibited_present`: exact count of prohibited records in returned context
  per scenario, not a fraction alone.

### 4.5 Exclusions and denominators (reported with every rate)

`non_load_bearing` (OFF correct), `other_action` (neither set),
`unsupported_state` (as-of scan missing), `unmappable` (adapter gap), and
per-stratum counts (`moment_topic`, `moment_offtopic`, `filler_*`). **A rate
without its denominator and exclusion counts does not ship.**

---

## 5. Arms, controls, and label classes

Every run is labeled per the charter's label partition.

| Arm | `integration_mode` | Class | Expected signature (the instrument's power) |
|---|---|---|---|
| `off` (no memory) | — | `baseline` | establishes `L`; actions are the wrong ones where memory matters |
| `fire-never` stub | `harness_trigger` | instrument control | `FBMR=0`, `FalseFire=0` |
| `fire-always` stub | `harness_trigger` | instrument control | `FBMR=1`, `FalseFire=1` — proves the selectivity guard bites |
| `oracle` stub (deliver the covering record on the moment) | `harness_trigger` | instrument control | `CBMR=1`, `AvoidRate=1` — proves the pipeline rewards coverage |
| `serve-stale` stub (deliver a `deprecated` record that elicits the wrong action) | `harness_trigger` | instrument control | `stale_use=1` — proves the harm metric bites (C2) |
| `serve-prohibited` stub (return a prohibited record in context) | `harness_trigger` | instrument control | `prohibited_present>0` — proves the harmful-presence metric reports (C2) |
| `long-context null` (all records at scenario start) | `context_dump` | `baseline` | `CBMR=1` at maximal `context_tokens` — the coverage bound, not a winner |
| system native proactive | `native_proactive` | `product` | measured |
| system + harness trigger | `harness_trigger` | `controlled_core` | measured; isolates delivery/quality from having a trigger |
| system explicit-only (agent scripted to call recall) | `explicit_only` | `raw_product` | measures retrieval given invocation; not FBMR |

**Instrument-failure condition:** if `fire-always` and `fire-never` do not
separate on the same corpus (FBMR 1 vs 0, FalseFire 1 vs 0), no system number
from that run is publishable. Likewise the harm controls must register their
harm: `serve-stale` gives `stale_use=0`, or `serve-prohibited` gives
`prohibited_present=0`, means the harm side of the instrument is blind.

**Agent policy (frozen):** primary arm uses a **deterministic puppet** that
never calls recall on its own: on a moment it emits `correct_action` iff
`CBMR` holds at action time, else `wrong_action`; on fillers it emits the
template default. The puppet is harness ground truth, so the primary metric is
a property of the system+integration, not of model reasoning. **Transfer arm
(secondary, gated):** the real pi agent under the same traps, with action
extraction by the harness and any ambiguous action ruled under a frozen rule;
metered, and not authorized by this file.

---

## 6. Scoring procedure (programmatic; receipted)

1. Freeze: corpus + manifest sha256, seed, templates, adapter versions, this
   design's sha256 (row 25 §6 pattern).
2. Run `off` first; compute `L` from observed OFF actions.
3. Run each arm; collect `invocation-events.jsonl` + agent-action records.
4. Run the §2.4 leak gate; a failed gate voids the affected runs.
5. Join per `(scenario, turn)`; score §4; emit `turn-scores.csv` and
   `system-summary.csv` (one row per system+mode with all §4 columns and
   Wilson/bootstrap CIs clustered by scenario).
6. Run the control arms; emit `instrument-report.md` with the
   fire-always/fire-never separation and every falsifier's status.
7. Never overwrite: each run writes a new results directory.

Ground truth is the manifest and the harness, **never the model's self-report**.

---

## 7. Falsifiers (pre-registered; firing voids output, never edits the rule)

- **G1 — Manifest leak.** The moment manifest or action strings were reachable
  by the system → void affected runs.
- **G2 — Non-load-bearing overflow.** `non_load_bearing + other` > 20% of
  designated moments → the denominator is untrustworthy; FBMR is descriptive
  only.
- **G3 — Control non-separation.** §5 instrument-failure condition fires →
  instrument failure, no system number.
- **G4 — Anachronism/stale contamination.** Any `anachronism_violation` or
  `stale_use` credited as coverage → void affected moments; recompute.
- **G5 — Adapter unmappable.** A required adapter field is unavailable → that
  system reports `unmappable`, explicitly not zero.
- **G6 — Degenerate corpus.** All moments topic-unreachable (nothing can fire
  on topic) or none → the primary has collapsed; report instrument design
  failure, not a system result.

---

## 8. Anti-gaming register

| Attack | Control |
|---|---|
| Fire on every turn to maximize FBMR | `FalseFire` + `FirePrecision` companions; `fire-always` control demonstrates the guard |
| Fire only on `fresh`/`gap` (any first prompt / any 30-min pause) | primary counts `proactive_topic` only; fresh/gap reported separately |
| Dump all records up front (long-context null) | labeled `context_dump`; `context_tokens` reported; it is the `baseline` bound, not a system win |
| Fire but deliver nothing | mandatory `CBMR`/`AvoidRate` beside `FBMR` (delivered level) |
| Hard-code the corpus | held-out templates; manifest withheld; seal + rotation |
| Win by suppressing service | `stale_use`, `prohibited_present`, delivered-record counts reported; false merges never rewarded |
| Count calls, not deliveries | §3 adapter requires delivered ids + hashes; `ExplicitBefore` separate from `CBMR` |
| Paper over a non-firing system with another system's behavior | `unmappable` and per-arm zeros are their own rows, never imputed |
| Read the mistake as model quality | puppeted primary; transfer arm secondary and gated |

---

## 9. Cost and run gating

- **This document:** $0, design only, no runs.
- **Deterministic puppet corpus + controls:** local, no LLM, **$0**; this is the
  arm that should be built first.
- **Native-proactive product runs:** depend on each engine's surface; gated by
  Stratum/Brian budget per the charter envelope.
- **Live transfer arm:** metered; explicitly **not** authorized here.
- The corpus tier (`smoke`/`standard`/`extended`) and the number of systems are
  the budget decision.

---

## 10. Handoff to Stratum (charter integration after 04:13)

**Where it slots.** Add as a **pre-registered PROGRAMMATIC scored dimension**
(new §, or Patch 5) next to Patch 3 item 2's invocation rate. Patch 3's
dimension (ever-invoked / zero-invocation row) becomes the coarse leading
indicator; FBMR is its timed, selectivity-constrained successor. Both can be
computed from the same §3 event log, so no duplicate instrumentation.

**What Stratum must freeze if adopted.**

1. The invocation-mode column per system (`native_proactive` /
   `harness_trigger` / `explicit_only` / `context_dump`), and whether every
   passive engine gets the Tier-2 harness trigger. Cross-system FBMR is only
   compared **within matched mode**; the mode travels as a column.
2. Corpus tier, family weights, and the held-out split.
3. Whether FBMR is a *reporting* dimension or a **BAR B gate**. Recommendation:
   reporting first (this is a fresh instrument; gating it before its controls
   are exercised in anger would repeat the S4 denominator mistake).
4. The deterministic-only vs live-transfer decision.

**Composition with existing labels.** `harness_trigger` = `controlled_core`;
native proactive = `product`; explicit-only = `raw_product`; long-context null
= `baseline`. FBMR never replaces Hit@k/Prohibited@k or row 25's M1–M4; it is
the invocation axis that sits *before* both.

**Open questions for Brian/Stratum:** (a) corpus tier and system count;
(b) does any portfolio engine actually ship a proactive layer, or is Tier-2 the
only fair cross-system arm; (c) budget for the transfer arm; (d) accept the
deterministic puppet as the primary, or require a live agent from day one.

---

## 11. Verification checklist for Assay (second seat)

1. **Row fit:** the doc is design-only; it defines a scripted corpus, moments
   interleaved with non-moments, and a programmatic per-system FBMR from the
   **harness-observed injection events** (the trigger/fire log is corroboration,
   per B3).
2. **Computability:** every metric in §4 is computable from the §3 schema plus
   the §2 moment manifest; find any metric that silently needs a judgment (it
   should be labeled `JUDGED` or moved).
3. **No raw content:** grep the doc and the (future) fixtures — no transcript
   excerpt, quoted span, or reconstructable session; only the aggregate pilot
   card's numbers. The §2.4 leak gate must be able to fail closed.
4. **Control power:** confirm the §5 fire-always vs fire-never signatures are
   the right positive control, and that the oracle control exercises the
   coverage path.
5. **Deadline semantics:** verify the `deadline(M)` rule cannot credit a fire
   that happens after the action, and that `context_dump` cannot masquerade as
   targeted self-noticing.
6. **Adversarial:** try to construct a system behavior that scores FBMR=1
   while being useless; if one exists, the companion columns are insufficient.

---

## Receipts / sources read for this design

- `team/TRANSCRIPT-MINING-PILOT.md` — **aggregates only** (15 corrections by
  class, 21 durable facts, class precision, exclusion filters). No raw content.
- `team/SPEC-OUTCOME-PROTOCOL.md` (row 25) — matched-pair machinery, delivered-
  level rule, anti-gaming register, freeze/leak-gate pattern.
- `team/S4-ADJUDICATION.md` (FROZEN) — A2 as-of state, A5 anachronism,
  A4 exclusions, detection/denominator discipline.
- `team/CAMPAIGN-1.md` §S4 and standing instrument rules — fire-rate/false-fire
  split, delivered-level counting.
- `team/PORTFOLIO-CHARTER-draft.md` — Patch 3 item 2 (invocation rate), BAR A/B,
  PROGRAMMATIC/JUDGED partition, baseline/controlled_core/product labels.
- `team/PROPOSAL-R2-explicit-prompt-habit-v1.md` — invocation vs delivery vs
  application vs harm, false-nudge precision rule.
- `implementer/repo/extensions/pi-change-trigger/index.ts` — committed fire-log
  schema and `evaluateFire`/`tokensOf` semantics reused by the Tier-2 arm.
- `team/WINDOW-OPENING.md` — trigger smoke and the `fresh`-on-first-prompt
  method limit (why primary counts `topic` only).
- `AGENTS.md` — engine+harness unit, delivered-level, state-not-receipt,
  context-size/harmful-presence, no false-merge reward, no fake product path.

— **Corvid** (`worker-glm-dsh3`), 2026-09-13. Design only, $0, no runs, no raw
transcript content.

---

## Addendum A (2026-09-13 08:52 UTC) — §10(b) answered: no engine is proactive

`team/RESEARCH-INVOCATION-SURFACE-AUDIT.md` resolves §10 open question (b) from
the code. **Every portfolio provider is pull-only** (`base.py`: only
`reset`/`ingest`/`retrieve`/`feedback`/`close`/`diagnostics`; `ProviderCapabilities`
has no proactive field), and `PerseusVaultProvider`'s own docstring disclaims
automatic capture/correction. The only per-turn proactive component is the
**harness** extension `pi-change-trigger` (canonical `implementer/repo`, commit
`db31ea3e…`, `index.ts` sha `ec6d8794…`; **not in this fork**); `pi-recall-nudge`
is resume/frequency-gated, not change-aware.

Consequences folded into this design without moving the frozen metrics:

- §5's `native_proactive` row is expected **empty at the current integration
  surface**; report it as `not offered`, never as a product failure.
- Tier-2 `harness_trigger` is the **only fair cross-system arm** (it is already
  the design's `controlled_core` row), and it still measures a real per-engine
  property because the topic set comes from each engine's own stored summaries.
- The Tier-2 arm must pin `pi-change-trigger` at commit `db31ea3e…` / sha
  `ec6d8794…` (vendor or gate-check it; do not re-implement from memory).
- The live transfer arm uses `pi-change-trigger`; `pi-recall-nudge` is held OFF
  (or reported as its own arm), since it would inflate invocation for
  non-noticing reasons.

A `native_proactive` row for any engine requires a **new adapter build** that
emits the §3 event schema — a build decision, not a design change.

---

## Addendum B (2026-09-13 10:10 UTC) — Muse batch 5 adversarial controls

`team/MUSE-IDEATION-05.md` ran one batched outside-ideation call asking how a
scripted invocation benchmark is gamed; 5/5 proposals accepted (3 narrowed, 2
strengthen) and folded here. **These add controls; they move no frozen metric and
change no §4 formula.** Falsifier G7 is added in §7's spirit.

- **B1 — Fire-budget companion (from 5.1).** Fire-everywhere must not top the
  headline. Add `Recall@F` = `FBMR_topic` computed at a pre-registered false-fire
  budget (e.g. ≤F fires per 100 non-moment turns), beside median injected
  tokens/turn. A system that fires on everything reports its `FBMR` at the budget,
  not unbounded. (Existing `FalseFire`/`FirePrecision` remain.)

- **B2 — Frozen, arm-invariant denominator (from 5.2).** The load-bearing set
  `L` is established **once**, from a neutral OFF policy (harness-owned), and
  frozen before any system runs. Every arm scores against that same `L`; any
  per-arm divergence is a stop-and-report, not a silent denominator change.
  Non-load-bearing/excluded counts are still reported, with a sensitivity
  analysis, per §4.5.

- **B3 — Harness-owned injection observer is the primary source (from 5.3;
  revised 2026-09-13 after Assay's `ASSAY-INVOCATION-B3-REVIEW.md`, F1–F5).**
  The first draft said "covering record id present in the prompt before the
  deadline". That is **presence, not mechanism**: Assay's probe shows it gives a
  perfect `FBMR_topic` to `context_dump`, fresh-only fire, explicit-call answers,
  a mere user-text mention of the id, and an `R1`-inside-`R1EXTRA` substring
  collision. The harness therefore owns the injection boundary and records a
  harness-sequenced event per injection:
  `{channel: "memory", mechanism, reasons, record_ids, seq}` where `reasons` is
  an array/set of controlled tokens from {`fresh`, `gap`, `topic`} (exact
  membership, never a substring), with `mechanism` in
  {`proactive_topic`, `proactive_fresh`, `proactive_gap`, `auto_retrieval`,
  `explicit_call`, `context_dump`}. The primary is then

  ```
  FBMR_topic(M) := ∃ injection e:
      e.channel == "memory"
      and e.mechanism == "proactive_topic"
      and "topic" ∈ e.reasons               # exact token membership, NOT a substring test
      and covering_id(M) ∈ e.record_ids     # exact canonical id, not a text grep
      and e.seq < action_seq(M)             # strict; equal is NOT a fire
  ```

  - **F1:** presence with no mechanism tag is **not a fire for the primary**;
    it is corroboration / `CBMR` only. If a system injects out-of-band where the
    harness cannot label the mechanism, that arm reports **`unmappable` for
    `FBMR_topic`**, never a naive-presence score. §4.1's formula is unchanged.
  - **F2:** ordering uses harness event sequence numbers, not wall clock; the
    tie rule is strict (`<`), so an injection interleaved with the action does
    not count.
  - **F3:** ids match exactly against the injection payload's `record_ids`;
    `R1` inside `R1EXTRA`, a filename, a tool result, or a user/agent mention
    never counts, and presence is attributed to the memory channel only.
  - **F3b:** `reasons` must be a controlled token array and the test must be
    exact membership — if the harness emits `reason` as a bare string,
    `"topic" in "nontopic"` is True and that row false-fires. (Assay re-check
    2026-09-13, `ASSAY-B3-REVISION-RECHECK.md`.)
  - **F3c:** the schema layer **normalizes first, then validates**: trim
    whitespace and lowercase each `reasons` token, then require membership in
    {`fresh`, `gap`, `topic`}. A token that normalizes into the vocabulary
    (e.g. `"Topic"`, `"topic "`) **fires normally** — a cosmetic harness quirk is
    not an instrument error. Only a token still unknown after normalization makes
    that injection **`unmappable` / schema-error**, never a silent no-fire; a
    genuine vocabulary drift must read as an instrument defect, not as "the
    system never fires on topic". (Assay F3c + F3c-x,
    `ASSAY-B3-F3B-CLOSURE.md`, `ASSAY-B3-CONTRACT-REGRESSION.md`.)
  - **F5:** `FBMR_topic` requires the injection before the action; whether the
    record is *still in context at the action* is `CBMR`'s job. Add
    **`FBMR_persist`** = a B3 fire **and** the record present at `action_seq`, and
    report it beside `FBMR_topic` so "fires, then evicts" cannot read as clean
    invocation.

- **B4 — Ablation + payload fidelity (from 5.4).** Alongside `CBMR` (covering id
  must be in the injected set), add an **ablation control**: with the covering
  record removed from the store, the puppeted agent must revert to `wrong_action`.
  If it stays correct, the moment is not memory-load-bearing and is excluded
  (§4.5). Report exact injected size.

- **B5 — Paraphrase split + necessity/sufficiency counterfactual (from 5.5).**
  Beyond held-out templates, a **tell-removed paraphrased split** (no scripted
  lexical fingerprint) and a counterfactual: wrong without memory, correct with
  *only* the covering record injected. A system that wins only on the
  fingerprinted split is reported as cue-overfit, not as proactive invocation.

**Falsifier G7 — fire-log/observation split (revised per Assay F4).** A
**missing** adapter log is a corroboration gap (`unmappable` / warning), not a
void — so a system cannot fire, stay silent, and force "void pending" instead of
a number. Only an observed **contradiction** (harness says `proactive_topic` with
id X; the log claims a different mechanism or id) voids the affected moments;
voids are reported as **non-scores, not neutral**, under a bounded re-observation
policy (one re-run, then permanent `unmappable`). A systematic split →
instrument failure.

*B3/G7 revised 2026-09-13 after Assay's
`team/ASSAY-INVOCATION-B3-REVIEW.md` (probe `dc145b52…`, result `2e7f2959…`),
which showed the original presence-only predicate gives `FBMR_topic=1.00` to
dump, fresh-only, explicit-call, mere-mention, and a substring collision. No
§4.1/§4.2 formula changed; the observer contract is now mechanism-owning.
Assay's re-check (`ASSAY-B3-REVISION-RECHECK.md`, recheck `757c5adb…`) then
verified the revision and flagged **F3b** — `reasons` must be a controlled token
array with exact membership — folded above; 12/12 synthetic systems reproduce.
His F3b-closure probe (`ASSAY-B3-F3B-CLOSURE.md`, probe `afe335d3…`) then flagged
**F3c** — unknown/mis-cased/padded tokens must be `unmappable`, not a silent
no-fire — also folded. His 23-case contract regression
(`ASSAY-B3-CONTRACT-REGRESSION.md`, regression `0906a8c4…`, 23/23) then flagged
**F3c-x** — the F3c wording conflicted on whether normalizable tokens fire or are
`unmappable`; folded as **normalize-then-validate** (a `"Topic"`/`"topic "` token
fires; only a token unknown after normalization is `unmappable`).*

— **Corvid** (`worker-glm-dsh3`); Muse batch 5 dispositions in
`team/MUSE-IDEATION-05.md`.

---

## Addendum C (2026-09-13) — §3 schema made B3-computable; harm controls added

Assay's §11 second-seat (`team/ASSAY-INVOCATION-BENCHMARK-VERIFY.md`) and
Alice's extension (`team/ALICE-INVOCATION-BENCHMARK-SECONDCHECK.md`, sha
`930d96e4…`) found that **§3's adapter schema could not compute B3's primary**:
it declared `integration_mode`, `delivered_ids`, and wall-clock `at`, while B3
requires `channel`, `mechanism`, `reasons`, `record_ids`, and a monotonic `seq`
(too). Fixed in place:

- **§3** event row is now the B3 tuple `{channel, mechanism, reasons, record_ids,
  seq}` plus `context_ids_at_action`; `at` is logs-only and never orders. The
  adapter contract adds `context_ids_at_action(turn)` and states the
  `pi-change-trigger` fire log is **corroboration only**.
- **§4.2** `CBMR` now reads "present in `context_ids_at_action`".
- **§4.4** `stale_use` is stated as the programmatic conjunction (deprecated
  delivered **and** wrong action), not a causal claim.
- **§5** adds the harm positive controls `serve-stale` (`stale_use=1`) and
  `serve-prohibited` (`prohibited_present>0`), and the instrument-failure
  condition now covers them (Assay C2).
- **§11 item 1** and the plain-English block now say "harness-observed fire
  events", not "trigger/fire log" (Assay's stale-wording minor).

**§4.1/§4.2 ordering corrected to the B3 `seq` predicate (Assay R1); no other
metric definition changed.** This note supersedes design version `547741c1…`; the
pinned post-edit hash is in the RD-THREADS entry for 2026-09-13.

