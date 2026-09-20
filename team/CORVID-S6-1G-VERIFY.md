# CORVID-S6-1G-VERIFY — gate verification for row S6-1G

Verifier: corvid-dsh, 2026-09-17 09:53 PDT. I authored neither the gate
(plumb-fable) nor the artifact it gates (kiln-flash). Prior measurement cited:
kiln-flash's S6-1 close note on QUEUE.md ("declared check → clean, rc 0; gate
selftest also green: 16 single-defect mutants + rank table + missing-file roots
all rejected") — my run below is an independent re-execution of the same
declared check plus adversarial mutants of my own construction, not a re-use of
kiln's numbers.

## Verdict: VERIFIED PASS

## What was checked

1. **Declared check** (`python3 /home/bmosher/memory-bake-off/team/S6-CORRECTION/check.py --selftest`):
   exit 0. Output: conforming fixture accepted; 16 single-defect mutants, a
   rank table, 4 missing-file roots, dirty and hostile CLI roots all rejected
   by name, no traceback.
2. **Clean run on the real artifact**: exit 0, `S6-1 gate: clean`.
3. **Independence is structural** (the row's mtime test): gate mtime
   2026-09-17 07:32:54 PDT vs earliest mtime among kiln's four declared
   artifact files: note.md 08:16:07 (numeric-claims.json 08:16:36,
   review.json 08:16:55, publication.json 08:17:10). The gate predates every
   artifact file by ~43 minutes, so "written from the row text alone" holds on
   evidence, not instruction. (The directory also holds the gate's own
   `check.py` and `__pycache__/`; the comparison above is against kiln's
   declared files, which is the sense the row intends.)
   Gate sha256 `40db8308c147a7a5…5aee`.
4. **Content enforces what row S6-1 demands** (source read, check.py lines
   58-270): all four declared files required (`MISSING-FILE`); partition
   arithmetic total=60 and nonempty+empty=total (`PARTITION-SUM`) — the check
   that catches the original 19/60-vs-37 contradiction class; every scenario
   count in note.md must be one of the three partition numbers unless the
   sentence marks it retracted (`SCENARIO-COUNT-DISAGREES`, with a
   retraction carve-out so quoting the old wrong 37 as wrong does not trip);
   both counts must actually be stated (`SCENARIO-COUNT-MISSING`); fixture
   dating must be explained with a cause, not merely present
   (`DATING-ABSENT`/`DATING-UNEXPLAINED`) and the 90-day window claim must be
   addressed (`TEMPORAL-CLAIM-UNADDRESSED`); ranking language banned in prose
   and tables unless negated, and the absence of ranking must be stated
   explicitly (`ENGINE-RANKING`/`NO-RANKING-STATEMENT-MISSING`); cause must be
   retrieval configuration, not measurement error (`CAUSE-MISSING`);
   "verifying the arithmetic did not validate the experiment" required
   (`TRANSFERABLE-FINDING-MISSING`); FirePrecision must be distinguished from
   retrieval precision when named (`FIREPRECISION-CONFLATED`);
   review.json needs reviewer ≠ author (`REVIEW-NOT-INDEPENDENT`);
   publication.json needs a real revision and destination
   (`PUBLICATION-RECEIPT`).
5. **Exit contract** (per `team/tools/check_checker_exit_contracts.py`
   dialect): 0 clean / 1 with named `[MARKER]` lines and the
   `S6-1 gate findings: N` summary / never a traceback — including a hostile
   root (note.md replaced by a directory, JSON files replaced by non-object
   JSON) in the gate's own selftest, re-run by me.
6. **Adversarial mutants of my own, not the gate's fixtures** (copies of the
   real artifact, one defect each):
   - 41→37 in note.md → REJECTED (`SCENARIO-COUNT-DISAGREES` +
     `SCENARIO-COUNT-MISSING`), rc 1.
   - appended "pi-lcm ranks above claude-mem" → REJECTED (`ENGINE-RANKING`), rc 1.
   - dating cause replaced with "remains unexplained" → REJECTED
     (`DATING-UNEXPLAINED`), rc 1. (First attempt was a no-op — I replaced the
     gate's fixture text instead of kiln's actual sentence; re-ran with an
     asserted anchor. Recorded because a verifier's own false alarm is a
     finding about the verifier.)
   - reviewer set equal to author in review.json → REJECTED
     (`REVIEW-NOT-INDEPENDENT`), rc 1.
   - every claim source set to "TBD" → REJECTED (`NUMERIC-CLAIMS`), rc 1.

## Stated limit (the gate declares this itself; confirming it)

The gate proves the document agrees with itself and makes the row's
distinctions. It cannot prove the explanation is true or that the counts match
the pinned results — that remains the S6-1 artifact verifier's job (kiln's
note re-measures both counts from `results-pi_lcm_store_reader_toollevel/topics-derivation.jsonl`; the file-level
re-derivation of those numbers belongs to the S6-1 verification, not this gate
check).

## Result

Row S6-1G: artifact exists, declared check exits 0, independence structural,
gate rejects defective documents by name. VERIFIED PASS.
