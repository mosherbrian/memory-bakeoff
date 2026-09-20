# CORVID-S7-1G-VERIFY — gate S7-1G verified PASS, 2026-09-17 15:2x PDT

Verifier: corvid-dsh (clock read at write). Author of the gate: plumb-fable —
corvid authored neither the gate nor S7-1's artifact; independence holds.
Claimed 15:19 PDT, verified from the declared artifact and the row text only.

## What the row demanded, and what was run

1. **Declared check exits 0.** `python3 team/S7-BM25-PREFILTER/check.py --selftest`
   → rc 0: "2 conforming fixtures accepted, one of them an honest refutation; a
   receipts-only directory, an unreadable prior and 29 mutants each rejected by
   exactly their own markers, no traceback." The selftest enforces the row's
   both-holds requirement in code: conforming → rc 0 with no markers; every
   mutant → rc 1 with EXACTLY its named marker set, the `S7-1 gate findings: N`
   line, and no traceback. Accept-loose / reject-nothing cannot pass it.
2. **Exit contract on the REAL path, not only fixtures.** Clean run on the
   artifact → rc 0 with the recomputed summary. Adversarial dirty copy (my own,
   beyond the selftest): real artifact copied to /tmp, verdict flipped to
   `artifact-confirmed` over the refuting data → rc 1,
   `[VERDICT-CONTRADICTS-RULE] abstain_correct is 0 and the declared rule needs
   3`, the findings line, no traceback. 0/1/marker/never-traceback all hold
   where it matters — on the artifact the fleet actually shipped.
3. **Substance, not file-counting.** The gate recomputes the prior measurement
   from `team/S6-SELECTIVITY` rather than trusting any number in the artifact;
   sha-binds every results row to the declaration bytes (post-run stopword edit
   = `RESULTS-NOT-BOUND`); orders control before re-run and requires per-case
   reproduction; proves the prefilter ran by comparing query_tokens values
   (applied / non-vacuous / never emptied); and derives the verdict from the
   declared rule over recomputed scores. The selftest's receipts-only case
   (all files present, content empty → rejected) proves file presence alone
   cannot pass. "Reject a deliberately non-conforming fixture" is covered 29
   ways, each named.
4. **Files required vs the row text.** The gate requires the three
   claim-bearing files the row text supports (declaration.json, results.jsonl,
   verdict.json; MISSING-FILE tested), byte-checks a local corpus.jsonl against
   the frozen prior when present. design.md / run_prefilter_rerun.py were first
   named in kiln's post-build close — after the gate landed 13:40:46 (mtime;
   artifact files 13:50:22–24) — so requiring them would have broken the
   pre-artifact property the row exists to protect. Reading accepted as
   faithful to "from the row's text alone".
5. **Verifier's own re-derivation (independent of the gate's code).** From the
   raw files: prior bm25 = 0.500 mean set-F1 / 5 retrieve / 0 abstain; control
   `bm25-nofilter` reproduces it per case 10/10; `bm25-prefilter` = 0.400 / 4 /
   0 with the single delta sel-003 (helpful r2 → distractor r4). Matches the
   gate's clean summary and kiln's S7-1 close note. The gate's arithmetic is
   right against the bytes on disk.

## Non-blocking findings (not this row's artifact)

- `team/tools/check_checker_exit_contracts.py` reports **INCOMPLETE: 4 live
  guard(s) uncovered** — `check_no_pipes_in_seats`, `check_plain_language`,
  `check_r2h_rater_blind`, `check_r2h_smoke_receipt` (the two R2H checkers and
  the D-9 duty checker were added without exit-contract controls). The driver
  is fail-closed about it (rc 1 — verified without a pipe masking the code),
  so the guard set still reads honestly; the gap is that those four guards'
  0/1 contracts are currently unproven by the driver. Control fixtures are
  owed by whoever owns those rows; the S7-*G gates live in artifact
  directories by design and are outside the driver's sibling-set, so this
  receipt proves their contract directly instead.
- First run of the driver in this verification printed rc 0 because a pipe
  (`| tail`) masked the driver's exit code — verifier error, corrected above;
  recorded because "rc 0 behind a pipe" is exactly how a fail-closed instrument
  gets read as green.

## Verdict

S7-1G **VERIFIED PASS** — done: corvid-dsh 2026-09-17 (claimed 15:19) —
artifact `team/S7-BM25-PREFILTER/check.py` as landed 13:40:46 PDT, sha
recorded below; receipt `team/CORVID-S7-1G-VERIFY.md`.

sha256(check.py) at verification:
9ad03aac1aa70c94b25ce6e54ffc50a26a802cba9e872585b429f181bc196616 — the
selftest and the dirty-path run above were executed against exactly these
bytes.
