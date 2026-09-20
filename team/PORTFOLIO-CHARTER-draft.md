> ## APPROVED by Brian, 2026-09-16
>
> **Approved with a stated caveat: several portions are now outdated.** The
> fleet was furloughed to three seats on 2026-09-15 (cairn conducting, kiln
> doing, corvid reviewing; everyone else parked until the OpenCode Go weekly
> window resets), the conductor moved from a metered GLM seat to a local $0
> seat, and the Z.ai Lite contract limits the fleet to ONE request in flight.
> Any part of this charter that assumes the wider roster, the old conductor, or
> parallel worker execution should be read as superseded by that arrangement,
> not as authority.
>
> **What the approval grants:** the charter's structure and its campaign, so the
> fleet no longer waits on Brian to originate work. **What it does not grant:**
> the roster or the concurrency the document was written against.
>
> **Required follow-up, not optional:** a reconciliation pass naming which
> sections are stale and what replaces them. Until that lands, cite this
> charter for its structure and its named systems, and check the live roster in
> the QUEUE header before assuming anyone is available.
>
> The spend envelope stays as Brian set it elsewhere; this approval does not
> raise it.

# PORTFOLIO-CHARTER (DRAFT) — parallel evaluation of memory systems on one conflict benchmark

**Status:** DRAFT, design only, no runs, no spend. Written 2026-09-12 by
Stratum (worker-glm) on GiLMore's dispatch, answering Brian's challenge of
tonight: *"why am I the only driver?"* On approval this becomes the fleet's
second originated campaign (campaign-1 was Brian-challenged; this one is
fleet-originated). **The one ask: Brian approves this charter and a spend
envelope. Everything else runs without him.**
**Patch 1 (2026-09-12, post-Verity criteria pass — she passed it, no
re-open):** programmatic/judged label partition made explicit + dispute
sample on judged labels feeding the primary; envelope arithmetic line;
drop-by-name extended to instruments; recommendation bar and portfolio bar
split into distinct criteria. Four folds, nothing else touched.

**Patch 2 (2026-09-12, post-G0 pre-P2, per Corvid's survey + Brian's
go-ahead relayed by GiLMore):** agentmemory upgraded to IN-PORTFOLIO
(row 7), with its known false-supersession failure carried as a
pre-registered PROGRAMMATIC scored dimension — see §"Scored dimension:
false-supersession rate (agentmemory)". License row CLEARED per Corvid's
frozen-commit verification (P1 satisfied by pinned-blob receipt; Kiln's
supporting fetch receipt: `docs/PORTFOLIO-P1-DISCOVERY.md`). Two folds +
one table-row update, nothing else touched.

**Patch 4 (2026-09-12, price ruling from Brian relayed by GiLMore —
amendment-of-record under G0 authority):** official lane prices recorded and
the P2 worst-case arithmetic line printed in binding form — see §Patch 4.
Two folds, nothing else touched.

**Patch 3 (2026-09-12, POST-G0 BRIAN DIRECTIVE — amendment-of-record under
G0 authority, relayed by GiLMore):** three folds, envelope arithmetic
re-printed, decision log updated (all below, §Patch 3 detail).

1. **BASELINES LOCKED.** Two explicit arms join the long-context null as
   locked portfolio baselines: **pi-lcm** (the store-reader arm, rows 1–2 —
   previously PENDING build, now a locked arm) and
   **pi-lcm-with-long-multi-session-memory-no-memory-system** (the
   multi-session-history null: pi-lcm's long multi-session store presented
   as raw history, no memory-system machinery — the null built on the same
   store the live arm uses). Both are local and metered-spend $0.
2. **NEW PRE-REGISTERED PROGRAMMATIC SCORED DIMENSION — invocation rate.**
   Per system, from run logs: was the memory system EVER invoked for capture
   or retrieval during its assigned runs (capture-call count, retrieval-call
   count). A system with zero invocations is a ZERO-INVOCATION RUN: reported
   as its own outcome row, never imputed from other systems' behavior, and
   excluded from Hit@k comparison only in the sense that its numbers are its
   own zeros. LABEL CLASS: PROGRAMMATIC (deterministic count over run logs).
   Rationale carried from the live arm: self-noticing is the measured
   weakness — a system that is never called cannot help, and that must be a
   number, not a footnote.
3. **NEW GATE CRITERION (BAR B amendment).** No system is recommended unless
   actual outcomes improve MATERIALLY over the no-memory baseline arms
   (long-context null AND the two pi-lcm baseline arms): **Hit@3 alone does
   not pass BAR B.** Operationalization proposed by the executor for
   Verity's rule check: (i) penalized Hit@3 (stale-use penalty applied) must
   exceed the BEST baseline arm's penalized Hit@3 by more than that
   baseline's recorded run-to-run band; (ii) outcome measures (stale-use
   penalty, Prohibited@k) must not regress vs that baseline. "Materially" is
   defined by (i)+(ii) or by whatever v2 Verity freezes — a bare Hit@3
   advantage is not adoption evidence.

**Envelope arithmetic re-print (Patch 3 — run counts changed by +2 baseline
arms).** G0 rule stands: total metered spend = Σ(repeats × per-run lane
price) over the run matrix, worst case (full matrix × most expensive lane)
≤ **$5 all-in**; touching $5 = stop + report. Re-print with the two new
arms:

- **pi-lcm reader arm and pi-lcm multi-session-history null arm are LOCAL
  and metered-$0**: store reads are local sqlite; the null arm is local
  history passthrough. Neither adds metered storage or retrieval cost.
- Metered draw grows ONLY by their reader/eval passes on metered lanes:
  +2 arms × tasks × repeats, drawn from the SAME ≤$5 pool (no top-ups).
  Worst-case all-in allowance at the most expensive named lane
  (deepseek-direct, $0.60/1M) = **≈8.3M tokens for the entire campaign**;
  at muse pricing (~$0.002/task) the allowance is ~2,500 tasks. The P1 run
  matrix must size task counts so the Σ lands inside the pool, and the
  arithmetic line is re-printed with actual task counts at P2 entry.

**Plain English first:** the program's own decision memo
(`implementer/repo/DECISION_MEMO.md`) says the recommendation ("which memory
system, on what evidence") cannot close until three defined questions are
answered — and two of the three measuring instruments are already BUILT and
never run. This charter proposes to run the portfolio: about a dozen memory
systems (ours and open-source), the same frozen conflict benchmark, one
harness, seeded runs, blind scoring, on lanes and models that cost Brian
nothing new beyond a small pre-approved envelope. His total calendar cost:
two decisions (approve this; adopt-or-refuse the result) plus a stop switch
he already holds.

## Origination duty (the explicit answer to the critique)

Brian has been the only driver because asks arrived as prose, and prose
needs a driver to become work. From this charter forward, the standing duty
is: **the fleet originates, Brian gates.**

1. Every retro round, any seat may propose one originated campaign; GiLMore
   aggregates and lands at least one shaped proposal per cycle — question,
   candidates, envelope, phase gates, stop switch, decision points — in the
   campaign format this file establishes.
2. Brian's role is defined by negation: he does not assign tasks, break
   ties between seats, or attend execution. He approves envelopes, receives
   gate reports, issues verdicts at named gates, and holds the stop switch.
   A gate report longer than one page is a defect.
3. Nothing in this duty authorizes unapproved spend or unapproved scope:
   origination without a gate is exactly the "decisions dying in limitation
   sections" failure in reverse. Shaped ask, gated execution.
4. This charter is the duty's first exercise — proposed by the fleet, from
   the record's own backlog, at Brian's challenge rather than his assignment.

## Why this campaign, and why it is pre-justified

DECISION_MEMO.md's rule: a generation that does not fill a row is
unjustified. Three required rows are open, and this campaign is scoped to
fill them and nothing else:

- **Row 4** — does ANY memory system beat putting the history in the
  context window? Instrument BUILT, never run:
  `src/memory_bakeoff/longcontext_null.py`. Intake calls it highest-priority
  and the cheapest item ("a configuration of the harness we already run").
- **Row 5** — do the four unmeasured local engines change the picture?
  Unmeasured: Habitus, agentmemory, Hindsight, MemBukkit (row 3 measured
  Perseus, Mem0, bm25 only).
- **Row 6** — what does each system DO with a stale record it returns,
  scored as a penalty? Metric BUILT, never applied:
  `src/memory_bakeoff/stale_use_penalty.py` (FAMA, arXiv:2606.27472).

Anchoring numbers already frozen (row 3, Gen38, held-out 27-persona slice):
Hit@3 on **dynamic** conflict — perseus 0.434, mem0 0.419, bm25 0.226.
Both engines roughly double the lexical baseline and both sit below 44%
absolute. The category is not flattering to itself; the portfolio asks
whether anything in it is.

## Candidates (in-orbit first; license and adapter cost stated honestly)

Cost classes: **none** = measured already; **low** = config or store-reader
work in the harness we run; **medium** = provision/verify a shipped harness;
**high** = write a new adapter and operate a service. License marks: ✅ =
stated in a receipt we hold; ⚠ = named from general knowledge, verify
before adapter work; ❓ = unknown, verify. (License verification receipt is
P1, owned by Stratum.)

| # | System | Class | License | Adapter cost | Where it stands today (receipt) |
|---|---|---|---|---|---|
| 1 | **pi-lcm** (store reader) | in-orbit — **LOCKED BASELINE ARM (Patch 3)** | Brian's own (`projects/pi-lcm-bun`), private | none — read-only reader exists (`extensions/pi-project-recall`, 12/12 tests) | in daily use; R2-lineage measured the recall question, not conflict quality |
| 2 | **pi-lcm tool variants** (`lcm_grep`/tool-level vs raw store) | in-orbit | same | low | within-conversation only; A/B of reader paths is a config |
| 3 | **Perseus vault** (decision memory + bake-off engine) | in-orbit | this program's own | none — memconflict adapter frozen (`627f812d`), Hit@3 0.434 dynamic | measured; best-in-portfolio so far, below 44% absolute |
| 4 | **native capture** (pi native remember/admission) | in-orbit | pi's (`@earendil-works/pi-coding-agent`) ⚠ | low — probe scripts exist | measured INERT as an admission path (`team/PROBE-remember-admission-FINDINGS.md`, DO NOT MIGRATE); included only so the portfolio's "ours" column is complete; stays out unless campaign-C repairs it |
| 5 | **mem0** | external | Apache-2.0 ⚠ | none — adapter frozen (`920f496b`), Hit@3 0.419 | measured; unavailable in one pinned profile (row 2) — recheck at P1 |
| 6 | **habitus** | external | upstream `munch2u-a11y/Habitus-AI`, pinned `f93b770e`; license NOT stated in `vendor/habitus/UPSTREAM.md` ❓ | none — vendored, blob-hash-verified | measured on core5 (row: Hit@5 0.875, Useful>harmful 0.923); unmeasured on memconflict |
| 7 | **agentmemory** | external — **IN-PORTFOLIO (Patch 2)** | ✅ Apache-2.0 at pin (Corvid, frozen-commit receipt) | none — in harness | measured core5 + lifecycle; **known-bad carried as scored dimension:** falsely retired 418/450 distinct stress memories at write-time supersession, 92.9% (`STATUS_AND_FINDINGS.md`) |
| 8 | **hindsight** | external | ❓ | none — in harness | measured; supersession mechanism present but 0/48 on row 2's lineage test |
| 9 | **membukkit** | external | ❓ | none — in harness | measured core5 (Hit@5 0.958, MRR 0.525); row-5 candidate |
| 10 | **claude_mem** | external | ❓ | none — in harness | measured (`results/claude_mem_compare_core/`) |
| 11 | **bm25 / tfidf / dense_lsa / hybrid_rrf** | baselines | home-grown | none | frozen baselines; bm25 is row 3's anchor |
| 12 | **letta (Letta/MemGPT)** | external | Apache-2.0 ⚠ | medium — benchmark SHIPS an upstream harness; provisioning, not writing | never run here; needs a server process |
| 13 | **langmem** | external | MIT ⚠ (LangChain) | medium — upstream harness shipped | never run here |
| 14 | **a_mem** | external | ❓ | medium — upstream harness shipped | never run here |
| 15 | **memobase** | external | ❓ | medium — upstream harness shipped | never run here |
| 16 | **memos (MemOS)** | external | ❓ | medium — upstream harness shipped | never run here |
| 17 | **Zep** | external | community edition ⚠ | **high** — NOT in the benchmark's shipped harness list (a_mem, langmem, letta, memobase, memos, mem0); new adapter + server dependency | **stretch, parked by default.** Named by GiLMore; included for honesty, gated on G0 explicitly admitting it |
| 18 | **long-context null** | arm | n/a | none — BUILT (`longcontext_null.py`), never run | row 4's instrument; the null the whole portfolio must beat |

Prerequisites, stated: `external/MemConflict` is gitignored and absent — the
182 MB pinned dataset must be materialized (disk only, free, pinned at
upstream `ec51d5d`, dataset sha `8ef9ec…` already frozen in the Gen38
contract). The six upstream harnesses come from the benchmark's own release
— we provision, we do not write them.

## Shared harness spec (one interface, seeded runs)

1. **One adapter interface** — the existing bake-off provider interface
   (the `--providers` list is already ten systems long). Every candidate,
   in-orbit or external, enters through the same interface: ingest the
   prepared conflict corpus, answer the same queries, emit raw results to
   opaque ids. No system gets a bespoke metric path.
2. **Benchmark of record:** `memconflict-benchmark-v1` (contract
   `05212108…`, dataset `8ef9ec…` frozen at Gen38) — primary slice the
   held-out 27 personas no adapter was tuned on. Secondary: the harness's
   own longitudinal/conflict tasks for the engines the external benchmark
   cannot load. Lanes never combined (intake rule).
3. **Seeded runs:** pin seeds wherever the serving lane supports it; where
   sampling is unseeded (qwen, recorded Gen44), alternate and repeat per
   the R2 alternation rule and report band-widths, never single draws.
   Persona/run identity discipline per the Gen36-38 frozen procedure; every
   run re-asserts contract + dataset + adapter pins before writing.
4. **Metrics (all pre-registered, none invented mid-run):** Hit@3 dynamic
   conflict (row 3's basis, primary); the harness table columns (Hit@5,
   MRR, All-relevant@5, Prohibited@5, Useful>harmful, Mean ctx chars);
   **stale-use penalty** (row 6's BUILT metric, applied to every system's
   delivered results); **long-context null** as the arm every system must
   beat (row 4). Overhead columns (tokens, wall) reported, not scored.
5. **Standing instrument rules carry over:** receipts claim, state is;
   delivered-level counting; negative results are deliverables (a system
   that scores zero is a row, not a footnote).

## Budget envelope (free/metered lanes ONLY — zero GLM window draw)

- **Eval-workload inference** (the model calls that exercise the systems):
  `deepseek-direct` (Brian-named tonight, $0.15–0.60/1M — **verify with a
  price receipt before first spend**), `muse` (already calibrated by Corvid,
  ~$0.002/task, receipt `7d42fdf`), `InferX` (Brian-named tonight, free —
  smoke receipt before reliance). **No GLM window draw for any evaluation
  inference.**
- **Envelope arithmetic, shown at G0 (Verity fold):** total metered spend =
  Σ(repeats × per-run lane price) over the run matrix, computed and printed
  as a line item before G0 — worst case with the full matrix and the most
  expensive lane must still land ≤ **$5 total**. Sub-caps: ≤$1 per metered
  task per dsh seat (existing cap discipline). **All-in-or-not:** Brian
  approves the whole envelope once at G0; there are no mid-run top-ups —
  touching $5 stops the campaign and reports.
- **Proposed envelope for Brian to set at G0: ≤$5 total metered spend**
  (matches the standing metered-lane cap). Runs inside it proceed without
  him; touching it stops the campaign and reports.
- **Seat labor:** free flash lanes (Kiln, Verity, Stratum) as today; dsh
  lanes (Aletheia, Assay, Corvid) bounded tasks inside their existing $5
  caps; Ledger/fsync (claude) as today; Cairn (local pi) free.
- **Non-spend prerequisites:** 182 MB dataset materialization (disk); any
  external-server processes (letta et al.) run locally, free.

## Per-seat assignment map

| Seat | Assignment | Lane/cost |
|---|---|---|
| **Kiln** | harness integration: adapter interface conformance, provisioning the six upstream harnesses, per-adapter unit receipts, run execution | flash, free |
| **Verity** | adjudication ONLY (rule-writing + blind labels) — assigned no adapters, ever, for independence | flash, free |
| **Aletheia (Alice)** | verify the two BUILT-but-never-run instruments (`longcontext_null.py`, `stale_use_penalty.py`) behave as claimed before first exposure — her standing seat, artifact-level | dsh, bounded, ≤$1 |
| **Assay** | one external-claim reproduction from the upstream harnesses (identity discipline check), null results early | dsh, bounded, ≤$1 |
| **Corvid** | muse-lane extension calibration + edge-case cache (refusals, timeouts, off-by-ones) for the run matrix | dsh, bounded, ≤$1 |
| **Ledger** | synthesis spine: map every result to DECISION_MEMO rows 4–6; nothing enters the report unanchored | claude |
| **Cairn** | optional, bounded: does benchmark conflict behavior match what the live loop actually suffers? (relevance sanity, not scoring) | local pi, free |
| **fsync** | standing utilization watch (existing QUEUE row 8) | claude |
| **Stratum** | this charter's maintenance; license-verification checklist (P1 receipt); cold-read of the report before it reaches Brian; caveat-travel duty on every cited number | flash, free |
| **worker-codex** | reserve: cold-seat drill (QUEUE row 4) or one adapter port if a lane frees | outside |
| **GiLMore** | aggregation, blind-map holder, Brian interface, gate reports (≤1 page) | conductor |

## Pre-registered criteria + blind adjudication (Verity pattern)

**Two bars, stated separately (Verity fold).** They answer different
questions and neither implies the other:

- **BAR A — portfolio bar (category verdict, row 4's question):** does ANY
  memory system beat putting the history in the context window? The
  portfolio passes BAR A iff ≥1 candidate clears BAR B *and* also beats the
  long-context null on the same slice under the same penalties. If no
  system clears both, the campaign's answer is "on this workload, memory
  systems do not yet earn retrieval" and the recommendation becomes a
  configuration (the null), not a product. This is a field-level finding —
  it survives even if every product fails.
- **BAR B — recommendation bar (per-system, G5 adoption):** a system is
  recommendable iff, on the held-out 27-persona dynamic-conflict slice:
  Hit@3 ≥ bm25's 0.226 **with the stale-use penalty applied**, AND its
  overhead stays within the harness's reported band (overhead is reported,
  not gated), AND it carries no unremediated license blocker at P1. A
  system that beats bm25 only by co-returning poison fails the bar — that
  is row 6's whole point. A system that clears BAR B but not the null
  comparison is "best product, still loses to the null" — reported as such,
  never rounded up to a win.

**Label partition (Verity flag 1).** Every scored label is declared, before
first run, as exactly one of:

- **PROGRAMMATIC** — deterministic verifier output over delivered results
  (Hit@k, MRR, Prohibited@k, stale-use penalty computed from results vs
  ground truth, overhead totals). Sha-pinned code, no judgment, no judge;
  these feed the bars directly.
- **JUDGED** — labels requiring reading (e.g., attribution of an acting line
  to a recalled line where the verifier cannot decide; UNDECIDABLE
  resolution). Verity labels blind under the frozen rule (below). A judged
  label is a citation with a name on it, never a bare number.

**Scored dimension: false-supersession rate (agentmemory; Patch 2,
pre-registered before P2).** LABEL CLASS: PROGRAMMATIC — deterministic
verifier over stored state, no judge. Definition: after a system's ingest of
the prepared corpus (including the 450-record deliberate-distinct stress
slice), false-supersession rate = (records retired by that system's own
write-time supersession without a genuine replacement in the corpus) ÷
(records ingested). Measured from the system's own lifecycle/scan surface —
the same observed-state instrument as S6 — never from a write receipt.
Recorded prior from the Gen33-38 lineage: **418/450 = 92.9%** on
agentmemory's stress slice (`STATUS_AND_FINDINGS.md`). Reporting duty: the
rate is printed beside every agentmemory BAR B number, in the summary table
as its own column for any system with write-time supersession, and in the
P4 report's caveats. It does NOT gate BAR B arithmetic — the stale-use
penalty already penalizes the retrieval-side consequence; this dimension
makes the write-side cause visible beside it. Adoption weighting is Brian's
P4 call, informed by the dimension.

The partition table per metric ships with the adjudication rule; a metric
that turns out to need judgment where this charter said programmatic is
itself a P3 finding, reported — not silently reclassed.

**Dispute sample (Verity flag 2).** Judged labels feed the primary only
with a check attached: a second rater (Assay, or Corvid per the S4-B5
reserve pin — named at rule-freeze, before any data) re-labels a
pre-registered random sample (≥20% of judged items, drawn by committed
seed). Pre-registered interpretation: disagreement ≤10% → judged-fed
primary stands with the rate printed beside it; disagreement >10% → the
judged component is declared unreliable for the bar, and the primary is
reported PROGRAMMATIC-ONLY beside the disputed version — the bar is never
carried by contested labels alone. If the programmatic-only and judged-fed
versions of BAR B disagree about any system's pass/fail, that system's
result is reported as contested, not averaged.

1. **Blind scoring mechanics:** anything programmatic scores itself
   (verifier columns, sha-pinned contracts — no judgment, no judge).
   Anything JUDGED goes to Verity under a rule written and frozen BEFORE
   first run — the R2H pattern just shipped
   (`team/R2H-ADJUDICATION.md`): anonymized system identities, arm-strip
   prep, labels frozen before the map joins, falsifiers inside the rule,
   results in a worksheet never in the rule. The benchmark's
   `upstream_llm_judge` is `requires_reader_authorization` — no LLM judge
   runs without Brian's explicit yes, and the default design uses none.
2. **Pre-named outcome branches (now against the two bars):** (a) BAR A
   passes → rows 5/6 fill, memo can close, G5 verdict names the system(s);
   (b) BAR A fails → the field-level finding lands as the result — the
   long-context configuration becomes the default recommendation, which is
   a publishable answer, not a failure; (c) penalties flip the BAR B
   ranking → row 1's co-return problem is the deciding variable and
   supersession mechanisms (row 2's incommensurability) become the
   portfolio's real axis; (d) BAR B passes for some system but BAR A fails
   → "best product still loses to the null" — adoption question answered
   honestly in the negative at G5.

## Phase gates

| Gate | What | Brian? |
|---|---|---|
| **G0** | approve this charter + the ≤$5 envelope (+ explicitly admit or park Zep) | **YES — decision 1 of 2** |
| **P1** | materialize dataset; provision upstream harnesses; license-verification receipt; lane smoke receipts (deepseek price, InferX free, muse balance); per-adapter unit tests; Alice's instrument verification (fail → drop-by-name per Method limits) | no |
| **P2** | seeded runs inside envelope; contract pins re-asserted per run | no |
| **P3** | programmatic scoring + blind labels under the frozen rule; labels frozen, then map joined | no |
| **P4** | report (≤1 page gate form + anchored annex); DECISION_MEMO rows 4–6 filled; adopt/refuse/veto | **YES — decision 2 of 2** |
| any | envelope touched → automatic stop + report. Brian stop-anytime, as always | standing |

## What Brian must approve vs what runs without him

**Approves (exhaustive):** G0 charter + envelope number + Zep in/out; any
envelope increase; any use of his real project data (none is planned — the
benchmark is third-party and pinned); any LLM-judge authorization (default
design uses none); the P4 verdict.
**Runs without him:** everything else — adapters, provisioning, license
checks, smoke receipts, seeded runs, scoring, adjudication, the report.
His total calendar: two decisions and a stop switch. That is the answer to
tonight's question, priced.

## Method limits, inside the charter

- Design seat ran nothing; every number above is cited (Gen38, core5
  tables, DECISION_MEMO, intake). Band-widths, not certainties.
- License marks ⚠/❓ are honest ignorance with an owner and a phase (P1
  receipt), not assumptions. **Drop-by-name applies to instruments too,
  not just candidates (Verity fold):** a candidate whose license forbids
  our use, an upstream harness that will not provision, or an instrument
  that fails Alice's P1 verification (or cannot apply to some systems'
  output formats) — each is dropped BY NAME at P1, the candidate table and
  criteria re-issue before P2, and the DECISION_MEMO row that dropped
  instrument was going to fill stays OPEN and says so in the report. A
  quietly substituted instrument is the one move this charter forbids.
- deepseek-direct and InferX were named by Brian tonight and are unverified
  on this host; they get smoke receipts before any reliance.
- Benchmark evidence class only: this portfolio can say which system wins
  THIS benchmark under THIS harness. It cannot say which system improves
  Brian's actual mornings — that question stays with campaign-1's live arm
  and the R2 habit arm, and the three are never pooled.
- A generation that fills no DECISION_MEMO row is unjustified: this
  campaign fills 4, 5, and 6 or it reports why it did not.

*Design seat: Stratum (worker-glm). Sources: DECISION_MEMO.md,
research/PHASE2_CANDIDATE_INTAKE.md, research/MEMCONFLICT_GEN38_FULL_RELEASE.md,
results/current_core5/summary.md, vendor/habitus/UPSTREAM.md,
README.md (providers list), CAMPAIGN-1.md (lane budgets), QUEUE.md,
GiLMore dispatch 2026-09-12 (lane names, candidate list, Brian's critique).*

## G0 — APPROVED (Brian, 2026-09-12 ~16:1x PT, relayed by GiLMore)

Verbatim: "Cool! Here are some other things I want... Go, Zep parked."
- Charter approved at sha256 prefix 6e7f7d8df1a73878 (this file at freeze).
- Envelope: ≤$5 all-in metered, arithmetic line stands, touch-$5 = stop+report.
- Zep: PARKED per Brian.
- Verity criteria pass: filed (flags 1-5 patched pre-freeze, see Stratum's patch turn).
- Phase 1 (build) starts now. P4 gate form due at close.

---

## Patch 4 — OFFICIAL PRICE TABLE + P2 WORST-CASE ARITHMETIC LINE (Brian price ruling, 2026-09-12 ~18:5x, relayed by GiLMore)

**Ruling (verbatim from the relay):** official prices = the measured table in
POLICY — deepseek-direct $0.15/$0.60 per 1M (off-peak), muse $0.10/$0.20 per
1M, InferX $0, local GPU $0. The worst-case arithmetic line (repeats ×
per-run lane price, summed) prints at P2 entry and **must be ≤$5**.

**Provenance:** deepseek-direct's rates match the measured POLICY table
(`~/.local/share/agent-deck/conductor/POLICY.md:190` — "$0.15/M in,
$0.003/M cached, $0.60/M out", measured 2026-09-11 with the live keys).
muse/InferX/local recorded from the ruling. Off-peak noted as given; a
peak-price receipt is owed before any peak-hour run, per the charter's
"verify with a price receipt before first spend" rule — now satisfied for
off-peak.

**Official price table (binding for all envelope arithmetic):**

| Lane | $/M input | $/M cached read | $/M output |
|---|---|---|---|
| deepseek-direct (off-peak) | 0.15 | 0.003 | **0.60** |
| muse | 0.10 | — | 0.20 |
| InferX | 0 | 0 | 0 |
| local GPU (pi) | 0 | 0 | 0 |

**The P2-entry arithmetic line (binding form):**

> **0.15·T_in + 0.60·T_out ≤ 5.00** (dollars, off-peak),

where T_in / T_out = total millions of input / output tokens summed over
the full run matrix — every system × task × repeat — on the **most
expensive metered lane** (deepseek-direct). Cached reads price at $0.003/M
and are excluded from the worst case. Equivalent flat bound: **≤ 8.33M
output-equivalent tokens all-in** (matches Patch 3's ≈8.3M under the new
split pricing).

Worked task-level form for the P2-entry re-print (fill actual counts):

> Σ_over matrix ( repeats × N_tasks × (0.15·t_in + 0.60·t_out) / 1000 ) ≤ 5.00,

with t_in / t_out in thousands of tokens per task as measured by the
lane-meter (which now counts cache-correct tokens for every reader family —
builder, RD-THREADS 18:4x; prices remain the missing half until this
ruling, now supplied).

**Task-budget translation (from Patch 3, unchanged by this patch):** at
muse's ≈$0.002/task the allowance stays ~2,500 tasks; on deepseek-direct the
8.33M-token allowance is the binding one. The re-print at P2 entry uses
actual task counts from the run matrix, and the standing rule is unchanged:
**all-in-or-not, no top-ups, touching $5 = stop + report.**

**Cross-references:** this patch supplies the prices the anchor map named as
the envelope hole (`team/ANCHOR-MAP-RD-20260912.md`); the Corner 1 (BAR A
budget parity) and Corner 2 (capture-burden column) pre-registrations from
`team/DESIGN-CORNERS-1.md` remain PROPOSED (Verity rule-check pending) and
should ride the same P2-entry turn as this line's first re-print.

— Stratum, charter maintenance. Patch 4 filed under the ruling's authority;
nothing else in the charter moved.
