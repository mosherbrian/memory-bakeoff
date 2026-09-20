# Second-driver: full-corpus mining numbers vs the committed outputs

**Seat:** Alice (`worker-glm-dsh` / lane `alice-dsh`) · **Date:** 2026-09-14 05:0x UTC · **Cost:** $0, local, counts-only
**Serves:** Alice's standing rule — re-derive one load-bearing number per session.
**Target:** `team/TRANSCRIPT-MINING-FULL.md` (Kiln, consolidated 2026-09-13), the
Brian-facing scale-up numbers, checked against the artifacts it names
(`~/.local/share/memory-bakeoff/transcript-mining/full-20260913/{stats.json,
correction-events.jsonl,durable-facts.jsonl,digest.md,corrections-digest.md}`).
**Method:** `team/row-transcript-mining-rederive/alice_full_corpus_rederive.py`
(sha256 `9bc7d200aaf70405bf7a717d766c1a3582b45aa69aad93f0defeabbb608d098b`),
a counts-only recount — no `excerpt` is read into memory or printed, no writes.

## Verdict

**Most final numbers reproduce exactly; three Brian-facing figures do not**, and
they are the kind that get quoted (file scale, repeat-event count, the excluded
pile). The digest totals and every turn/correction/fact total are sound.

## Reproduces exactly ✔

| Claim in the note | Re-derived |
|---|---|
| Operator turns extracted 4,353 | `stats.turns_before_dedupe` = 4,353 |
| Continuation copies removed 255 | `stats.duplicates_removed` = 255 |
| **Unique operator turns 4,098** | `stats.user_text_turns` = 4,098 |
| Personal-life turns excluded 230 | `stats.personal_turns_excluded` = 230 |
| 270 per-event corrections (env 169, negation 61, actually 21, wrong 9, i_said 10) | JSONL per-event rows: 169/61/21/9/10, sum **270** |
| 26 repeated-instruction groups | JSONL `repeated_instruction` rows = **26** |
| 324 candidates (env_fact 311, convention 13) | JSONL rows: 311/13 = **324** |
| Digest deduped to 318 unique groups | `digest.md`: `candidates: 324 │ unique: 318` |

## Does NOT reproduce ✘

**1. "Files scanned … 1,250 (6 open files excluded …)" — the tree says 1,260 / 5.**
`stats.files_scanned` = **1,260**; `len(stats.scan_by_file)` = 1,260;
`sum(by_project.files)` = 1,260; `files_excluded_open` = **5**, with exactly 5
names. So the note's own "(scanned+excluded total is 1,256)" is short by 9
versus the committed **1,265**. The 1,250/6 pair is from an earlier iteration.

**2. "26 repeated-instruction groups (240 events)" — the rows sum to 144.**
The 26 rows carry `occurrences` values of 2–44 and **sum to 144**; there is no
`events` field. `stats.repeated_instruction_groups` = 26 (count only). The
corrections digest is internally consistent with the fresh state
(`candidates: 296` = 270 per-event + 26 groups). **240 is Kiln's earlier
pre-dedupe correction figure** ("repeat groups = 240 (not 21)"), carried into
this line after the dedupe re-run replaced the number.

**3. "the claude-mem-observer dir's 573 turns" — stats reports 0 user turns there.**
`by_project["-var-home-bmosher--claude-mem-observer-sessions"]` =
`{'files': 580, 'user_turns': 0}`; 573 is not a structural value anywhere in
`stats.json` (it appears only as a digit-substring). If the observer's pipeline
records were counted in some earlier stage, that stage's count is not in the
committed stats, so the note quotes a number no artifact here supports.

**Minor, same class:** "Project coverage: 12 of 13 dirs contributed turns" —
`by_project` lists **12** projects, of which **11** have `user_turns > 0` (the
observer is listed with 0). The 13-dir universe and the 12-with-turns split are
not reproducible from `stats.json`.

## Propagation

`(240 events)` also appears in Stratum's `COLDREAD-20260913-sprint2-outline.md`
(line 24); the `SPRINT-2-OUTLINE.md` itself does not carry it. The 1,250 and 573
figures appear only in `TRANSCRIPT-MINING-FULL.md`.

## Minimal fix (owner Kiln)

In `TRANSCRIPT-MINING-FULL.md`:
- file row → **1,260 scanned / 5 open excluded** (total 1,265), matching
  `stats.files_scanned` / `files_excluded_open`;
- "(240 events)" → drop it or replace with **144 occurrences** (or just the 26
  groups, which is the gated number);
- drop or qualify the observer **573** (stats says `user_turns: 0` for that
  project) and reword "12 of 13" to the reproducible `by_project` form.
Then the COLDREAD line inherits the corrected figure.

## Limits

I did **not** re-run the miner over the raw transcripts; this is an independent
recount of the committed outputs the note's numbers rest on, so it can catch a
stale/mixed line but cannot validate scanning or classification correctness.
Nothing was written; no transcript content was read into or printed by the
script.

— **Alice**. $0, one turn.
