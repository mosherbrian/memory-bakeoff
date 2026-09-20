# Assay — second-driver verification: P2 entry run (queue row 28)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, no LLM
**Subject:** `results/p2_entry_20260913/`, commit `40d71e3` (HEAD), canonical
`implementer/repo`; author Kiln (row 28, "not certifying my own run").
**Verdict:** **PASS.** Every recomputable number reproduces; the two nulls'
identity is semantic; the raw `0.0` is confirmed a retrieval-null.
**Sealed receipts:** `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-p2-entry-run/`.

## Provenance

- HEAD is exactly `40d71e3`; `results/p2_entry_20260913/{per_question.jsonl,pins.json,summary.json}`
  and the runner are **tracked** at it, with **no worktree diff** on those paths,
  so the verified bytes are the commit's, not a dirty tree.
- Committed `summary.json` sha256 `c7dc90a1…`; `pins.json` sha256 `e749e73e…`
  (dataset `8ef9ec85…`, upstream `ec51d5d3…`, composition `controlled_core`/`baseline`).

## 1. Deterministic re-run to a scratch OUT — IDENTICAL

Ran the committed runner with `OUT` monkeypatched to `/tmp/p2entry-assay-scratch`
(the committed result dir was never written):

- `summary.json`: **byte-identical**, same sha256 `c7dc90a1…`;
- `pins.json`: **byte-identical**;
- `per_question.jsonl`: **13,404/13,404 rows identical ignoring `wall_ms`** (the
  only non-deterministic field; it is timing and is excluded from `summary.json`).

## 2. Hand-recompute of `first_support_rank` — 22/22 AGREE

Own session-identity scorer (`p2_entry_hand_recompute.py`; it does **not** call
`M.first_support_rank`): for a deterministic sample of **22 questions across 22
personas**, re-ran the tool-level arm's retrieval and re-derived rank from
`Unit.session_id ∈ gold.support_sessions`. Sample covers every rank class
(1,2,3,4,5), `measured_zero` (0), and `unmeasured` (None).

- **rank, rank_status, offered, relaxed_with all agree 22/22**, 0 mismatches.
- Aggregate re-derived from the committed raw ranks: dynamic ConfHit@3
  = **586 / 2631 = 0.2227**, exactly the headline.

## 3. Chronology discipline — 12/12 clean

For 12 further sampled questions, re-ran retrieval with sessions `0..i` only;
the maximum session index of any returned unit was **≤ the question's session in
every case** (0 violations). Structurally, the runner appends session `i` then
asks session `i`'s questions, and `gold_for` reads only session `i`; the
all-units `unit_by_id` is used only to map returned ids, never to retrieve.

## 4. The two null arms — identity is semantics, not shared state

`pi_lcm_history_null` (`PiLcmHistoryNullProvider`) and `longcontext_null`
(`LongContextNull`) are distinct classes in distinct modules, instantiated
separately per arm/persona.

- Per-question comparison: **3351/3351 identical** on `rank`, `rank_status`, and
  `offered` (not merely identical aggregates).
- Both `offered` distributions are the whole allowed history (348–442 items),
  so the shared result is the shared *rule* ("return everything, score by
  session identity"), not a shared mutable store.
- Dynamic ConfHit@3 = 0.0 for both; overall Hit@3 = 0.0147 (47/3189).

## Headline numbers confirmed

| arm | measured | dynamic Hit@3 | overall Hit@3 |
|---|---|---|---|
| `pi_lcm_store_reader_toollevel` | 3189 | **0.2227** (586/2631) | 0.1875 |
| `pi_lcm_store_reader` (raw) | 3189 | **0.0** | 0.0 |
| `pi_lcm_history_null` | 3189 | 0.0 | 0.0147 |
| `longcontext_null` | 3189 | 0.0 | 0.0147 |

- n = 3,351 questions (3,189 measured / 162 unmeasured); dynamic slice 2,631
  matches Gen38's slice.
- **The raw `0.0` is real, not a scoring artifact:** the raw arm returned
  `offered = 0` on **all 3,351** questions (retrieval-null under strict-AND, no
  relaxation), so all 3,189 measured cases are `measured_zero` by construction.
- Relaxation fired **2,986 / 3,351** turns, matching the commit message.

## Limits

- Part 1 re-ran the committed code; parts 2–4 re-ran the arm's retrieval
  (`tool_level_retrieve` / the providers) but scored with an independent rank
  function. The raw arm and the null scoring path were verified from the
  committed rows plus the `offered=0` census, not re-retrieved row-by-row.
- `wall_ms` is non-deterministic by design and excluded.
- No deviation from the row's expected results; no tree modified (scratch OUT only).

— **Assay** (`worker-glm-dsh2`).
