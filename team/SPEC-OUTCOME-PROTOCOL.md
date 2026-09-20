# SPEC — Outcome-Measurement Protocol (QUEUE row 25)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, design only, no runs
**Verifier:** Corvid (`worker-glm-dsh3`, independent) · **Charter integration:** Stratum, after 04:13
**Scope gate:** design/spec only. No paired runs are authorized by this file.
**HARD RULE (inherited from row 24/25):** **no raw transcript content on this
lane.** The transcript-mining corpus stays local. This spec consumes only
aggregate statistics and de-identified, pattern-level correction events.

**Plain English first (for Brian):** right now every memory metric we have asks
"did recall return the right record?" This spec asks the harder, more honest
question — "did the work go better?" It defines how to compare two otherwise
identical pieces of real work, one with memory and one without (or two systems
against each other), and score four outcomes: how long it took, how many errors
were made, how often the agent re-discovered something it already knew, and how
many times the operator had to correct it. It also defines the clean interface
by which Kiln's transcript-mining correction events can become labelled test
cases for that fourth metric later — with raw transcript text never crossing
into this lane.

---

## 0. Question and claim ceiling

**Question:** on matched real work, does an agent operating *with* memory beat
the same agent *without* it (design A), or does system X beat system Y
(design B), on four outcome measures?

**Claim ceiling (anchor travels with every citation):** descriptive, small-n,
paired. This protocol can show direction and magnitude on the matched pairs it
ran. It cannot show that decision memory *causes* better coding outcomes, and
no report may phrase it that way.

This is distinct from retrieval metrics. Retrieval metrics say what was
returned; these outcome metrics say what the worker then did. Both are
reported; neither substitutes for the other.

---

## 1. Unit of analysis: the matched task pair

Definitions, frozen before data:

- **Task** — a bounded unit of work with an explicit DONE condition
  (e.g. "make test `X` pass", "produce artifact `Y`", "answer question `Z`
  from the record"). Ad-hoc exploration is not a task.
- **Task instance** — one execution of a task in one condition.
- **Matched pair** — two task instances produced under the two conditions and
  joined by the matching rule in §2. Every scored number is a per-pair
  quantity; unpaired instances are reported in their own list and excluded
  from paired statistics.
- **Condition** — design A: memory ON vs OFF for the same worker/system.
  Design B: system X vs system Y. The arm label is the *condition*, never the
  worker's or the system's self-report.

### 1.1 Designs

- **Design A — within-worker with/without memory.** One worker (or one system),
  arm toggled by a pre-committed rule (e.g. `PI_RECALL_NUDGE` per the R2
  pattern, or day/coin schedule frozen in advance). Strongest control of
  confounding; limited by novelty/learning effects (§8).
- **Design B — across systems.** Same task family, two systems, same corpus and
  query set. Assignment order counterbalanced (each system runs each matched
  task in both order positions where feasible, else randomize which runs
  first). Weaker control of per-system variance; the pairing still removes
  task-difficulty variance.

Both designs use the same four metrics and the same pairing machinery.

---

## 2. Matching rule (freeze before the first pair)

Pair on, in priority order:

1. **Task family** — reuse the frozen S5 rule (`infer_family` / `annotate_families`);
   explicit `TASK-x` / `QUEUE row N` wins, else objective rule match, else
   `unclassified`. Pairs must share a family key (day-scoped keys do not
   cross days; for this protocol family keys are **not** day-scoped — freeze
   that override explicitly in the prereg).
2. **Worker / system identity** — design A: same worker. Design B: the two
   named systems.
3. **Starting state** — same repo, same base commit/tree hash, same corpus
   version; any drift is a candidate-invalidating fact.
4. **Size/complexity band** — same pre-registered band (files touched, test
   count, expected artifacts). Bands and their boundaries frozen in advance.
5. **Time proximity** — nearest-in-time within the family, greedy-lexicographic
   tie-break by start time. The S5 finding stands: greedy is not
   minimum-total; pair *identity* must be reported, not just pair count, and the
   tie-break reported beside the result.
6. **No reuse** — a turn/instance is in at most one pair.

**Minimum n:** ≥ 8 matched pairs for a one-sided sign test at α=0.05 to be
reportable (7/8 gives p≈0.035; 8/8 gives p≈0.0039). Below 8 pairs, report
per-pair values and medians only, with no p-value and no "significance"
language. Wilcoxon signed-rank, if used, is secondary and also needs ≥6
non-tied pairs.

**Randomization / blinding:** condition assignment (design A) or run order
(design B) is frozen with a commit-reveal seed before the first instance. The
rater who labels correctness/corrections sees arm-stripped artifacts (condition
labels removed, sessions renamed opaquely) and never sees the arm map; arm-joined
numbers are computed only after labels freeze.

---

## 3. Outcome metrics (operational definitions)

Every metric carries: unit, start/stop, detection source, and the anti-gaming
rule. Follow the standing instrument rules: **receipts claim; state is**, and
**count at delivery level, never call level.**

### M1 — Time-to-complete

- **Unit:** seconds wall and tokens, per task instance; primary is **tokens**
  (wall is noisy across lanes), wall reported beside it.
- **Start:** first operator turn or harness marker that opens the task
  (timestamped in the session receipt).
- **Stop:** the DONE condition observed in state (test exits 0, artifact hash
  matches, operator accept), not the worker's claim of done.
- **Pair statistic:** per-pair log-ratio `log(t_mem / t_no_mem)` (design A) or
  `log(t_X / t_Y)` (design B); report median and IQR of ratios, plus raw
  medians. Report n, ties, and unpaired.
- **Anti-gaming:** a run that stops early without meeting DONE is a failure
  (M2), not a fast completion. Tokens counted from the harness `tokenUsage`,
  not self-report.

### M2 — Errors committed

- **Unit:** count of failure events per task instance.
- **Detectable event kinds** (frozen list; each must map to a receipt):
  test/CI failure attributable to the task; reverted or corrected edit for the
  same line; wrong-scope write (file outside the declared task scope);
  non-zero-exit command used as a task step; broken build left behind.
- **Detection:** programmatic first (test logs, diff/revert records, exit
  codes, scope-diff), then adjudication only for ambiguous kinds under a frozen
  rule. Self-reported "I made no errors" is **not** a source.
- **Pair statistic:** per-pair error count and total; report as counts
  (design is count data, not a rate with unknown denominator).
- **Anti-gaming:** do not collapse M2 into M4 — an error the operator never
  caught still counts here.

### M3 — Redundant re-discovery of facts already in memory

- **Unit:** count per task instance of facts the worker re-derived, re-asked,
  or re-discovered that a memory record **already held at task start**.
- **Operational rule:** a re-discovery is redundant iff
  (a) a stored record covering the fact existed at task start (state scan,
      record id + `valid_from/valid_to` + status at start, not a write receipt),
  and
  (b) that record's content was **delivered** to the worker before the
      re-discovery (delivered-level: the relevant toolResult text, not a call),
      or was available-but-not-delivered — two separate sub-counts:
      `redundant_delivered` and `redundant_available_only`.
- **Matching facts to records:** native canonical id or exact canonical marker
  only; fuzzy text matching may be reported but is `exploratory_only`, never
  publishable (inherits the fuzzy-subtext provenance rule).
- **Pair statistic:** count and `redundant per delivered record` per pair.
- **Anti-gaming:** false merges/supersessions are **not** rewarded here. A
  record that was never served does not make a re-discovery redundant; report
  the served-record count in the same table so a large "redundancy" number
  cannot be manufactured by suppressing service.

### M4 — Operator corrections needed

- **Unit:** count of operator correction events per task instance.
- **Detection classes** (consume Kiln's detector; classes from the pilot):
  `negation`, `actually`, `env_fact_correction`, `wrong`,
  `repeated_instruction`. Each event carries a confidence and a
  quoted-speech flag (§5).
- **Pipeline:** machine candidates → adjudication under a frozen rule. Report
  both **raw** and **high-confidence-only** counts, because pilot precision
  differs by class: negation/`actually` ≈100%, `env_fact_correction` ≈5/7
  (quoted third-party speech is the residual noise), facts ≈85–90%,
  `i_said` fired 0 genuine times. `i_said` is excluded until the full corpus
  makes it measurable.
- **Pair statistic:** count and per-pair delta; report detector precision (or
  its adjudicated estimate) beside the count — an unmeasured precision is a
  claim, not an instrument.
- **Anti-gaming:** repeated-instruction groups must be de-duplicated (normalized
  60-char prefix, ≥2 turns) so one correction is not counted N times; deliberate
  benchmark probes ("list the integers 1 to 60") are excluded by the frozen
  exclusion rules, and their exclusion count is reported.

### 3.1 Reporting table (shape, frozen before data)

Per pair: `pair_id, family, worker/system, n_M1_tokens, n_M1_wall,
n_M2_errors, n_M3_redundant_delivered, n_M3_redundant_available_only,
n_M4_corrections_raw, n_M4_corrections_high_conf`, then the deltas/ratios.
Arm purity (any violation of the assigned condition) and exclusion counts are
columns, never footnotes. Context size and harmful/prohibited presence from the
retrieval arm are reported in a companion table (per AGENTS: never rely on
prohibited fraction alone).

---

## 4. Instruments and receipts

- **State, not receipt:** every metric that depends on what memory held reads a
  store scan at task start and task end (ids, status, `valid_to`), not a write
  receipt.
- **Delivered level:** M3 counts deliveries (toolResult content), not retrieval
  calls.
- **Arm purity measured:** condition toggles are read from the extension/nudge
  logs and config receipts; intention-to-treat uses the assigned condition,
  with per-protocol numbers shown beside it, never instead.
- **Read-only assertion:** store sha256 + mtime at task start and end; any
  mismatch is a stop-and-report event for that pair.
- **Ground truth is the harness, never the model:** DONE conditions, test
  outcomes, and diffs are harness-owned. LLM/self-report may not supply M1/M2.

---

## 5. Consuming Kiln's transcript-mining correction events (later; aggregates only)

This is the interface row 25 requires the spec to be able to consume. **No raw
transcript content crosses into this lane.** The raw corpus stays local under
`~/.local/share/memory-bakeoff/transcript-mining/`; what crosses is a
de-identified, pattern-level event stream.

### 5.1 Input contract — an anonymized correction event

One JSON object per event; **no raw excerpts, no free text, no quoted spans**.
Text is represented only by a salted hash and structural metadata.

```json
{
  "event_id": "sha256(salt|source_session_pseudonym|turn_index|detector_version)",
  "schema_version": 1,
  "detector_version": "<pinned>",
  "source_session_pseudonym": "<opaque>",
  "project_pseudonym": "<opaque>",
  "class": "negation|actually|env_fact_correction|wrong|repeated_instruction",
  "subtype": "wrong|negation|... (nullable)",
  "turn_index": 0,
  "timestamp_bucket": "<hour or day>",
  "confidence": 0.0,
  "quoted_speech": false,
  "repeat_group_id": "<nullable>",
  "normalized_prefix_hash": "<salted sha256, not the prefix>",
  "env_fact_kind": "path|env_var|port|url|version|pin|other (nullable)",
  "evidence_span_length": 0,
  "correction_of_prior_same_fact": false,
  "exclusion_filters_applied": ["isMeta","tool_result","subagent_jsonl","continuation_summary","task_notification","seat_dispatch"],
  "extraction_run": "<pilot|scale-20260913|...>"
}
```

Explicitly **absent by construction:** raw `user`/assistant text, quoted spans,
file contents, secrets, hostnames, absolute paths with user identity. The
`normalized_prefix_hash` exists so repeated-instruction de-dup is checkable
without revealing the prefix.

### 5.2 Leak gate (required before any event crosses)

A deterministic self-test on the export bundle must fail closed:
- no field value contains a substring from the raw corpus beyond the agreed
  structural vocabulary;
- no value equals a raw excerpt prefix (bounded n-gram check against a
  local-only reference, result = boolean);
- event counts reconcile to the aggregate stats in
  `team/TRANSCRIPT-MINING-PILOT.md` (or the scale run's aggregate card).
A bundle that does not pass the gate is not consumable by this protocol.

### 5.3 Two uses

1. **Calibration cases for M4** — the labelled events (class + adjudicated
   truth) become the held-out set on which the M4 detector's precision is
   measured. The pilot's class-level precision is the baseline; the scale run
   should raise `env_fact_correction` precision by adding the quote-aware
   matcher before its numbers feed M4.
2. **Replay test cases** — each event is replayed through the M4 harness as a
   synthetic correction and must be counted exactly once, attributed to the
   right task/pair, with the right class. This is a *harness* test, not a
   re-run of the transcript; it uses the event record only.

### 5.4 What "aggregates only" means here

The pipeline may emit: counts by class, precision by class, per-project
breakdowns, confidence distributions, and the anonymized event stream of §5.1.
It may not emit: excerpts, example sentences, quoted spans, or anything that
reconstructs a session. Where the pilot says "local eyeball of excerpts", that
eyeball stays local; only its numeric result travels.

---

## 6. Pre-registration and freeze checklist

Before the first scored instance, freeze (sha256 each) and publish:

1. this spec (matching rule, bands, metric definitions, M4 rule, exclusion
   lists);
2. the assignment/order seed (commit-reveal; seed revealed at close);
3. the adjudication rules: DONE conditions, M2 failure kinds, M3
   record-existence test, M4 precision rule;
4. the analysis plan (§7) and the minimum-n statement (§2);
5. the leak gate (§5.2) and the de-identified event schema version.

No metric definition, band boundary, or exclusion may move after the first
instance; a needed change restarts the pair set and is reported as a restart.

---

## 7. Analysis plan

- **Primary:** per-pair ratios/deltas for M1–M4, pooled by family; report n,
  median, IQR, and every per-pair value.
- **Secondary:** exact sign test (one-sided, pre-registered direction per the
  question) at n≥8; Wilcoxon signed-rank only as secondary. No multiple-testing
  fishing: the four metrics are all reported, no "winner" selected after the
  fact.
- **Arm purity:** ITT primary; per-protocol beside it; violations listed.
- **Retrieval companion table:** delivered-record counts, context size, and
  harmful/prohibited presence, per AGENTS rules, so M3/M4 cannot be read
  without the service state.
- **Negative results are deliverables:** if memory shows no benefit, or makes
  outcomes worse, that is reported verbatim with the same receipts.
- **Outcome branches** (declared now): (a) consistent direction across a
  majority of pairs and metrics → report descriptive support; (b) mixed/no
  direction → report null; (c) memory worse → report harm, do not reframe as
  "overhead". None of these licenses a causal claim.

---

## 8. Confounds, threats, and anti-gaming register

| Threat | Control |
|---|---|
| Learning/novelty: second task benefits from the first regardless of memory | counterbalance order; pair only same-family; report order position |
| Selection: memory tasks are the ones that need memory | arm assigned by frozen schedule, not chosen by worker |
| Arm leakage: OFF day still nudged | purity measured from nudge/config receipts; ITT + per-protocol |
| Hawthorne: operator behaves differently when scored | blinding of raters; operator not told which metric is primary |
| Metrics reward volume, not quality | delivered-level counting; harmful/prohibited presence beside every number |
| False merge/supersession scored as good retrieval | M3 counts only served, state-verified records; false merges reported separately |
| Self-report as score | harness owns DONE/errors; model self-report never a source |
| Transcript lane leaking raw content | §5.1 schema + §5.2 fail-closed leak gate; raw corpus never leaves local |
| Greedy pairing not min-total | report pair identity + tie-break (S5 finding) |
| Small n read as significance | n<8 → medians only, no p-value, no "significant" language |

---

## 9. Boundaries

- Design only; **no runs are authorized** by this file. Execution is gated on
  Brian's budget/scope decision for R2 and Stratum's charter integration.
- **No raw transcript content on this lane** — at any stage, by any tool.
- No writes to any memory store under test; read-only arms asserted.
- No model-as-judge for ground truth; no fake product dependency substituted.
- The transcript-mining raw corpus remains read-only; only the §5.1 event
  stream and aggregate cards cross.

---

## 10. Handoff

- **Owner:** Assay. **Verifier:** Corvid (independent; check matching-rule
  completeness, metric definitions are computable from stated instruments, and
  the §5 interface cannot carry raw content).
- **Charter integration:** Stratum after 04:13.
- **Execution artifacts to produce later (not now):** prereg file with hashes,
  pairing harness (extend the frozen S5 machinery), M1–M4 metric collector,
  the M4 event replay/calibration harness, and the leak-gate script.
- **Open questions for Stratum/Brian:** (1) does design A run on the work
  machine or the fleet? (2) which two systems for design B? (3) token budget
  and n; (4) whether the scale-up transcript run is authorized before M4
  calibration.

---

## Receipts / sources read for this spec

- `team/TRANSCRIPT-MINING-PILOT.md` — **aggregates only** (pilot stats,
  correction classes, precision, exclusion filters, scaling plan). No raw
  transcript content read.
- `team/ASSAY-POWERCHECK-S5-PAIRING.md`, `team/ASSAY-POWERCHECK-S5-FAMILY.md`
  — frozen matching/family machinery and the greedy-not-minimum-total finding.
- `team/PROPOSAL-R2-explicit-prompt-habit.md` — arm assignment, blinding,
  ITT/per-protocol, read-only assertion patterns.
- `AGENTS.md` — evaluation rules (state not receipt, delivered level, no
  false-merge reward, context-size/harmful-presence reporting).

— **Assay** (`worker-glm-dsh2`), 2026-09-13. Design only, $0, no runs, no raw
transcript content.
