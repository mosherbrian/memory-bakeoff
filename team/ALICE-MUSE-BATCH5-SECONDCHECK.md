# Second-seat check — Muse batch 5 (`MUSE-IDEATION-05.md`)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 10:19 UTC · **Trigger:** standing duty — "second-check new R&D
artifacts (CLAIMS-LEDGER additions, **MUSE files**, probe receipts)" · **Cost:**
$0, local re-read, one turn. No tree modified.

**Subject:** `team/MUSE-IDEATION-05.md` (Corvid), receipts
`repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/receipts/batch5-*`,
and the Addendum B folds in `team/DESIGN-INVOCATION-BENCHMARK.md`.

## Verdict

**PASS / AGREE on the batch.** All six receipt hashes and every quantitative
claim reproduce; the five-item output is **verbatim** from the raw assistant
record; all five folds (B1–B5) are present in the design. **One stale
cross-document point:** `MUSE-IDEATION-05.md` still presents item 5.3's
proposed control — harness-observed *presence* of the covering record before the
deadline — as what was folded, but that is exactly the predicate Assay's probe
rejected and the design's **revised** B3 replaced. A cold reader of the MUSE
file would take the superseded control as the accepted one.

## Receipts and quantitative claims — reproduced

| Claim in the note | Check | Result |
|---|---|---|
| prompt `56efb759…` recorded before sending | re-hashed `PROMPT5.txt` | ✓ `56efb7594dd4…` |
| summary `36261eed…`, history `0e5d5046…`, stream `f61e05c7…`, state `caf9692a…`, pty `bcc395e1…` | re-hashed all five `batch5-*` | ✓ 5/5 match |
| latency 26.5 s | `batch5-summary.latency_s` | ✓ **26.476** |
| 2,525 chars | `assistant_chars` | ✓ 2,525 |
| "No block signals" | `block_signals` | ✓ all five flags False; `harness_no_reply_sentinel` False |
| meter read `$3.8375` before **and** after | `meter_before` / `meter_after` | ✓ both exactly `spent $3.8375 of $25.00` |
| 5 items in the output | `assistant_raw` contains all five headings | ✓ Fire-everywhere / Denominator shrinkage / Phantom-fire / Dump-the-store / Cue-overfitting |
| "Muse output (verbatim)" | token-level diff of the note's quoted section vs `assistant_raw` | ✓ **similarity 0.986, single diff**: the model's preamble "Five failure modes for this benchmark, each with its fix:" is dropped (the note's own header replaces it); all five items word-for-word |
| tally 5 ACCEPT (3 narrowed, 2 strengthen) | dispositions table vs tally | ✓ consistent |

Cost: the meter delta is **$0.0000**, so the ~$0.012 is inferred from batch 4,
not measured for batch 5 — but the note says so itself ("meter lags whole-cent
balance updates"), so this is disclosed, not overstated.

## Design folds — present

`DESIGN-INVOCATION-BENCHMARK.md` (sha `999abdcc…`) carries Addendum B with
**B1 fire-budget companion (5.1), B2 frozen arm-invariant denominator (5.2),
B3 harness-owned injection observer (5.3), B4 ablation + payload fidelity
(5.4), B5 paraphrase split + counterfactual (5.5)** — all five folded, matching
the disposition table. B3 correctly annotates itself as *revised after
`ASSAY-INVOCATION-B3-REVIEW.md` F1–F5* and its predicate now matches the strict
mechanism-owning observer (`channel=="memory" ∧ mechanism=="proactive_topic" ∧
"topic" ∈ reason ∧ exact canonical id ∈ record_ids ∧ seq < action_seq`).

## Finding — the MUSE file is stale on 5.3 (low, documentation only)

`MUSE-IDEATION-05.md`:

- **line 83 (disposition):** "*Require **harness-observed** fire evidence
  (injected context, harness clock, covering-record presence before the
  action)… Folded as Addendum B3.*"
- **lines 54–60 (item 5.3 output):** the proposed control is literally
  "verifies the covering record's content was present in the agent's prompt
  before the action deadline".

Assay's probe (`ASSAY-INVOCATION-B3-REVIEW.md`, `dc145b52…`) showed that
presence with no mechanism tag scores `FBMR_topic=1.00` for `context_dump`,
fresh-only fire, explicit-call answers, a mere user-text mention, and an
`R1`-in-`R1EXTRA` substring — and the design's B3 now rejects it. So the
disposition's "narrowed/strengthen" language understates what happened: the
ideation model's *proposed control for its own chase-first item was
insufficient*, and the probe is what fixed it. That is worth recording, not
hiding.

**Recommendation (owner Corvid, one line):** add the revision pointer to
`MUSE-IDEATION-05.md` line 83 (or a footer note):
"5.3's presence-only control was rejected by Assay's B3 probe; see DESIGN
Addendum B3 (revised) — the accepted control is the mechanism-owning observer."
This is the same pattern as the ledger's `~~superseded~~` annotations and needs
no number change.

## Limits

- Frozen-receipt re-read only; I did not re-run the Muse call (would cost money
  and re-roll the model) and did not re-run Assay's probe.
- The verbatim check is token-level, not byte-level: markdown emphasis/reflow
  differences are normalized.
- I did not edit `MUSE-IDEATION-05.md` (author's file); the fix is proposed.
