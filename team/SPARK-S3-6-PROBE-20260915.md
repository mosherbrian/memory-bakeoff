# S3-6 probe — SKILL.state vs pi-blackhole compaction, fit verdict (muse-drafter, 2026-09-15)

**Row:** QUEUE S3-6 (owner "Corvid + muse-drafter"; this is the muse-drafter half).
**Scope:** design only, no score import, $0. **Verifier: Stratum.**
**Blocker (stated up front):** pi-blackhole does not exist in this workspace —
`grep`/`find` across the tree and `$HOME` return no `blackhole` module or `compile()`
(only `QUEUE.md` names it). So the **code-fit half and the row-36 toy run cannot be
done from this seat**; they need the pi-blackhole tree (likely Corvid's lane / the
work machine). What follows is the **paper-side** half plus an explicit fit verdict.

## Pin — SKILL.state

| Field | Value |
|---|---|
| Title | *SKILL.state: Scalable Long-Horizon Agent Skills* |
| Authors / affiliation | Sanket Badhe, Priyanka Tiwari, Jonghyun Chung — **Google LLC** |
| ID / date | [`arXiv:2608.26263`](https://arxiv.org/abs/2608.26263) — **v2 2026-08-28 read here**; **v3 2026-09-02 is current** (Corvid pin, 2026-09-15); cs.AI/cs.MA; **accepted, EMNLP** |
| License | **CC BY 4.0** (read from the v2 HTML; matches the abs license link) |
| Artifact | **none surfaced** (no repo/HF link in the HTML) |

## What it is

A runtime that replaces **append-only conversational history** with an **explicit,
mutable structured execution state**. Per step the model sees only the immutable
**skill specification**, the **current structured state**, and the **latest
observation**; **intermediate reasoning is discarded immediately after producing a
validated state update**, which prevents prompt growth with history. Reported:
higher task accuracy with substantially lower cumulative tokens, architecture-
agnostic. The authors state one boundary themselves: when the task objective is
*the historical trajectory* (auditing, debugging provenance, explaining past
actions), interaction history is the target and this design does not serve it.

## Fit verdict against our threads

| axis | SKILL.state | our thread | fit |
|---|---|---|---|
| compaction | **deterministic structured state** (not a summary) | DIGEST/compaction arm | **good design point** — a third pole beside Cliff (lossy typed) and ACM (lossless offload) |
| epistemic class | state update is **validated** before commit | "verified fact" with a check receipt | **partial** — a validation gate, but the state is **mutable/overwritten** |
| lineage / supersession (G2) | **none** — no prior-state versioning | supersession/lineage, S6 | **weak** — a mutable state is the opposite of our retired-not-deleted ledger |
| provenance / replay | **discards reasoning** by design | correction-event miner, replay, M4 | **conflicts** — the authors concede this; it would destroy the trace our lane needs |
| cost / tokens | strong reduction (vendor) | cost/break-even | promising, uncited |
| cache-miss cost | smaller context → lower **cache-miss** cost (miss ≈ context × $0.10/M, per `BILLING-CORVID.md`) | our miss-dominated bill | **cost-axis plus** (Corvid, S3-6 co-owner half) |
| worker burn | not measurable here (needs blackhole) | row asks "cost worker burn" | **blocked** |

**Verdict:** a strong *compaction-shape* reference (explicit state beats history for
latency and context growth) but a **poor provenance/lineage match** — it is the
architectural inverse of our "retired, not deleted" discipline and of the
correction-event lane. Adopt only as a **third compaction pole**; do **not** adopt
for any lane that needs the historical trajectory. **Added by the co-owner half
(Corvid):** the same small-context property is a **cost-axis plus** — a smaller
context shrinks the **cache-miss** cost (`miss ≈ context × $0.10/M`), so on our
miss-dominated bill SKILL.state's shape is structurally cheaper, independent of its
provenance flaw.

## Comparison (three compaction poles, all reuse-green except SKILL.state)

| | when to compress | lossiness | lineage |
|---|---|---|---|
| Compaction Cliff (Apache-2.0 + DUA) | event/trigger | lossy, typed lanes | none |
| ACM (MIT) | **agent decides** | **lossless** (disk offload) | query on demand |
| SKILL.state | every step | **discard reasoning**, keep structured state | none (mutable) |

## Open (for Corvid / the blackhole owner)

1. **Code fit** — read pi-blackhole `compile()` + ledger schema: does it keep a
   retired-not-deleted ledger (our shape) or a mutable state (SKILL.state's)? That
   distinction decides whether the comparison is same-axis or cross-axis.
2. **Worker burn + toy run** — row-36 smoke with pi-lcm as audit floor: not run
   here (no blackhole, live smoke); defer unless a conductor wants it on the work
   machine.
3. **Prompt-growth numbers** — vendor-only, uncited.

$0, web reads + local search; no score import; no blackhole tree touched. —
muse-drafter (Spark)

## Code half — pi-blackhole 0.5.5 read (2026-09-15, unblocked)

Tarball `/tmp/opencode/pi-blackhole-review/pi-blackhole-0.5.5.tgz`, extracted
read-only (never installed). It is a **TypeScript** extension (MIT,
`k0valik/pi-blackhole`) that **layers two upstreams**, both vendored unmodified:
`sting8k/pi-vcc` (the `compile()` summariser) and
`elpapi42/pi-observational-memory` (the OM ledger).

### `compile()` — `src/core/summarize.ts`

`compile()` = normalize → `filterNoise` → `buildSections` → `mergePrevious`, with
OM content and recall-notes stripped before merge. It is **summarize-and-merge
over a `previousSummary`**, i.e. **lossy carry-forward compaction**, not a
deterministic state machine. (So the row's "deterministic compaction" describes
the *chain/ledger* layer, not the summary text.)

### Lineage — **strong fit** (better than SKILL.state)

- `src/core/compaction-chain.ts` validates an **`ActiveSegmentChain`** of
  `PiVccCompactionDetailsV2` segments with coverage (`firstKeptEntryId`,
  sequence/append checks) and refuses malformed chains (`invalid-chain-entry`,
  `latest-not-append`, `missing-chain-start`). Compaction has a **checked
  lineage**, not just loss.
- `src/om/ledger/types.ts`: `Observation{id, content, timestamp, relevance,
  sourceEntryIds, tokenCount}`, `Reflection{id, content,
  supportingObservationIds}` — observations link to **source entry ids** and
  reflections to **supporting observation ids** (provenance links).
- **Tombstones / retired-not-deleted:** `om.observations.dropped` records
  `observationIds`; `fold.ts` computes `activeObservations` vs `observationsById`
  (which **retains dropped**), and `projection.ts` exposes `droppedOnlyInFull`.
  Dropped observations survive in the full fold — the same discipline as our
  "retired, not deleted" ledger.
- `src/core/lineage.ts` is thin (active session-branch entry ids), i.e. session
  lineage, not fact lineage; the fact-level lineage is the ledger's source ids.

### Epistemic class — **partial fit**

Observations carry a **`relevance`** enum (low/medium/high/critical) and
reflections carry supporting ids, but there is **no truth-class lattice** (no
observation / verified-fact / hypothesis split) and no verified-fact receipt.
So blackhole gives us **salience + provenance**, not our epistemic classes.

### Verdict (S3-6)

| question | answer |
|---|---|
| lineage fit | **good** — validated compaction-segment chain + source-id provenance + tombstones |
| epistemic-class fit | **partial** — relevance enum, no truth classes |
| deterministic compaction? | **mixed** — `compile()` is lossy summarize-and-merge; determinism is in chain validation + ledger folding |
| vs SKILL.state | blackhole is the **lineage-friendly** pole; SKILL.state is the lineage-free latency pole |
| worker burn | not measured (would need a run) |

**Fit verdict:** pi-blackhole's ledger is a **useful positive reference for our
retired-not-deleted + provenance discipline**, and its compaction chain is a shape
we could borrow for validating segment lineage. It does **not** supply epistemic
truth classes (add those ourselves, per
`SPARK-EPISTEMIC-TYPE-SYSTEM-DESIGN-20260915.md`).

### Toy run — not done (stated, not silently skipped)

The row's "toy run on row-36 smoke with pi-lcm as audit floor" was **not run**:
the package is explicitly **not installed**, and the run needs the live row-36
smoke + pi-lcm floor. Design-only, no score import; if the conductor wants the
run, it needs an install/worker-burn decision, not a seat call.

$0, read-only extraction; no install; no score import. — muse-drafter (Spark)

## Toy-run plan (ready to execute; blocked on install approval)

The row asks for a toy run on row-36 smoke with pi-lcm as the audit floor. It is
**not executed** because pi-blackhole is present as a **download only** ("NOT
installed", Brian's constraint) and the run needs a Pi runtime + the row-36 smoke
corpus. Rather than install unilaterally, here is the exact plan so a conductor
can approve/run it:

**Prereqs**
1. Install `pi-blackhole@0.5.5` from the pinned tarball into an **isolated
   prefix** (not the shared runtime) — install approval is the gate.
2. Row-36 smoke corpus + harness (`team/CAIRN-ROW36-SMOKE-RUN-PLAN.md`), closed
   sessions only.
3. pi-lcm store-reader as the audit floor
   (`src/memory_bakeoff/providers/pi_lcm_store_reader.py`, contract suite).

**Steps**
1. Run the row-36 smoke **without** blackhole (baseline context) and **with**
   blackhole compaction + OM enabled; capture `compile()` output and the folded
   OM ledger per run.
2. Assert from the ledger: the compaction **segment chain validates**
   (`ActiveSegmentChain.ok`), **tombstones present** for dropped observations,
   and every observation's `sourceEntryIds` resolves to an entry.
3. Audit floor: replay the same queries through pi-lcm and confirm the
   compacted-context answer set is a **subset/equal** of the uncompacted answer
   set on the audited slice (no facts silently lost beyond declared tombstones).
4. Record: context tokens before/after, cache-miss-sensitive context size, chain
   ok/not, tombstone count, provenance-resolution rate, audit-floor result.

**Expected outcome / what it would falsify**
- Confirms (or not) that blackhole's summary compaction is **lossy as declared**
  (chain valid, tombstones recorded) and that pi-lcm sees no undeclared loss.
- A provenance-resolution failure or a chain-invalid run would **block adoption**
  of the chain shape.

**Decision needed:** install approval (Brian/conductor) + worker-burn budget.
Until then S3-6 stays **design-only**; no score import.

$0, plan only; no install; no run. — muse-drafter (Spark)
