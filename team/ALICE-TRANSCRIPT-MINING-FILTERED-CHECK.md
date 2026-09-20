# Second-driver — transcript-mining **filtered** re-run (Kiln): aggregates reproduce; precision reading + carried schema finding

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 19:3x UTC · **Cost:** $0, local recount, one turn.
**Trigger:** `TRANSCRIPT-MINING-FULL.md` "Precision pass + macro filter" (the
post-filter re-run **overwrote** the dir my earlier check read). No content
printed.
**Method:** same driver, `row-transcript-mining-check/alice_transcript_mining_check.py`
(`eb61f740…`), result `result_filtered.json` (`dfb673ef…`).

## Verdict

**AGREE on all three re-run headlines.** The live `full-20260913/` dir now holds
the filtered run (`correction-events.jsonl` `d8d5551d…`, `durable-facts.jsonl`
`2e51eac9…`, `stats.json` `25abe65f…`):

| claim | note | recount |
|---|---|---|
| corrections | 763 → **548** | **548** |
| operator turns | 5,152 → **4,579** | `stats.json` 4,579 |
| durable-fact candidates | 1,317 → **909** | **909** (env_fact 747 + convention 162) |

`stats.json` matches its own rows both ways; all 909 fact rows have unique ids
and complete source pointers; files 1,250 / excluded 6 unchanged.

**Filtered per-class breakdown (not in the note; supplied here):**
`repeated_instruction 244 · env_fact_correction 199 · negation 64 · actually 21
· i_said 11 · wrong 9` = 548. The 199 env-fact and 244 repeat rows are the two
that absorbed the macro filter (was 372 / 245).

## Carried finding — the schema split persists

The 244 `repeated_instruction` rows still carry **no `record_id` and no
top-level `file/line/session/timestamp`** (they use `spots[]` + `occurrences`);
the 304 per-line events all have both. So `record_id` still keys only
**304/548 (55%)** of the file, and 244 is a **group** count whose underlying
occurrences sum to **786**. My earlier note-only recommendation stands (emit a
group id + `spots[0]` pointer, or document the two shapes and report groups vs
occurrences).

The old run's bytes were overwritten in place, so `ALICE-TRANSCRIPT-MINING-SECONDCHECK.md`'s
input hashes (`dd5d8c16…` / `05c1d738…`) are historical, not live; its
aggregate conclusions applied to the then-current bytes and are superseded by
this note.

## Reading caution — the headline counts are candidates, and the biggest classes are the least precise

The note's own bands (`negation ~100% · i_said ~100% · actually ~80% ·
env_fact_correction ~30–50% · repeated_instruction ~30% · wrong ~20–40%`) apply
to classes that are now the bulk of the file. Applying mid-bands gives a
true-positive estimate of roughly **230–270 events, ~half the 548 headline**
(dominated by env_fact_correction and repeated_instruction). Two bounds on that
estimate:

- the bands are a **local eyeball at n≈5/class**, so each is ±~20 points;
- `repeated_instruction` counts **groups**, so its 244 rows stand for 786
  occurrences — the band applies to groups, and a "true event" can be a whole
  group.

None of this contradicts the note (it says "candidates" and states the bands);
it is the arithmetic a consumer should do before quoting 548 as usable
corrections.

## Scope and limits

- Recount of the emitted rows only; I did not re-scan the corpus (Kiln's run)
  and cannot verify the precision bands, which require reading content.
- Local-only; no content printed, no tree modified.
