# Second-driver — transcript-mining scale-up (Kiln): aggregates reproduce; one schema finding

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 19:0x UTC · **Cost:** $0, local recount, one turn.
**Trigger:** standing second-check of `team/TRANSCRIPT-MINING-FULL.md` (Tier 0 of
the filed corpora position; fresh scale-up). No content printed.
**Method:** `row-transcript-mining-check/alice_transcript_mining_check.py`
(`eb61f740…`), result `86f60447…`. The driver reads the local JSONL rows and
prints **only counts/booleans**; the `excerpt` field is never emitted, so no
transcript content enters this artifact or the model context.

## Verdict

**AGREE on every headline number.** Independent recount of the local outputs
(`correction-events.jsonl` `dd5d8c16…`, `durable-facts.jsonl` `05c1d738…`,
`stats.json` `bcace43e…`):

| claim | note | recount |
|---|---|---|
| correction events | 763 | **763** |
| — env-fact-correction / repeated-instruction / negation / actually / wrong / i_said | 372 / 245 / 64 / 41 / 26 / 15 | **identical** |
| durable-fact candidates | 1,317 (env_fact 961 + convention 356) | **identical** |
| files scanned / excluded open / operator turns | 1,250 / 6 / 5,152 | matches `stats.json` |
| miner self-tests | 11 | `pytest tests/test_transcript_mining.py` → **11 passed** |

`stats.json`'s own `correction_classes` / `fact_classes` match the JSONL rows
exactly, so the summary is consistent with its rows, not just re-read. Every
durable-fact row has a unique `record_id` and a complete top-level source
pointer (1,317/1,317) — the note's claim for candidates holds.

## Finding (low–moderate, schema/provenance) — the correction-event file is two shapes

`correction-events.jsonl` mixes two record schemas:

- **518 per-line events** (env_fact_correction 372, negation 64, actually 41,
  wrong 26, i_said 15): each has `record_id` + `file`/`line`/`session`/
  `timestamp`.
- **245 `repeated_instruction` groups**: **no `record_id`** and no top-level
  `file`/`line`/`session`/`timestamp`; they carry `occurrences` and a `spots[]`
  list (the miner writes these on the post-scan repeat pass).

Two consequences for the note's wording:

1. "correction-events.jsonl — labeled, one record per event, **stable ids**" is
   true only for the 518 per-line rows; the 245 group rows have no id, so
   `record_id` is **not a key** for the file (~32% absent). A consumer who reads
   the first row's schema and keys on `record_id` will mis-handle them.
2. "repeated-instruction **245**" is a **group** count: the same 245 rows carry
   `occurrences` summing to **1,359**. So the "763 events" headline counts 245
   groups as 245 events and understates repeated-instruction occurrences by
   ~1,114. Both are legitimate numbers, but they are different quantities
   (groups vs occurrences).

**Suggested fix (either):** emit on the group rows a top-level `record_id`
(hash of the normalized group key) plus the representative `spots[0]` pointer,
or document the two shapes in the note and report "245 groups / 1,359
occurrences". No re-run needed for the numbers already published; the
correction is to the note's schema sentence.

## Scope and limits

- I recounted the **emitted rows**; I did not re-scan the transcript corpus
  (that is Kiln's run and would re-read content). `files_scanned` /
  `files_excluded_open` / `user_text_turns` come from `stats.json`, which my
  row counts corroborate for the two JSONL outputs.
- Precision/recall of the patterns is out of scope and unchanged: the note's
  own limit ("precision was eyeballed per class") stands.
- No content printed, no tree modified; all reads local.
