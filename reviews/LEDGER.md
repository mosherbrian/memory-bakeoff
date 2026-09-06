# Review findings ledger

Every numbered finding from a rival or control-plane review, tracked to a status
and a commit. **`CARRIED`** means review ruled it minor, it is accepted knowingly,
it has an owner and a generation, and it is not fixed yet - it is not a synonym
for closed, and the doorbell refuses a CARRY verdict unless carried findings are
actually recorded here. Verbatim reviews live beside this file; they are the evidence, this
is the accounting.

**Why this exists.** The stale `97 passed` test gate in `AGENTS.md` was reported
by review **three separate times** — glm-5.3 (2026-09-06 00:46), glm-5.3-flash
(01:18, item 6), and again in the rivals' provisional Gen116 brief (02:12, item 7)
— and was still there on 2026-09-06 morning. Nothing tracked findings to closure,
so what got fixed was whatever the implementer happened to remember from the
summary it wrote itself. That is the same pattern as the rest of this session:
declaring a thing caught substituted for fixing it.

**Rule.** A finding may be OPEN, FIXED (with commit), DEFERRED (with reason), or
REJECTED (with reason). Do not ring a doorbell while a finding is OPEN.

| # | Round | Found by | Finding | Status | Commit |
|---|---|---|---|---|---|
| 1 | Gen114 004659 | glm-5.3 | runner/grader untracked at the pinned commit; preflight filters `??` | FIXED | ring-doorbell + propose-generation, 2026-09-06 |
| 2 | Gen114 004659 | glm-5.3 | nondeterminism under "temperature 0, seed 0"; `seed_accepted` hardcoded | DEFERRED | v5 requires a server readback or NOT REPORTED (R-7) |
| 3 | Gen114 004659 | glm-5.3 | two cores carry no recency marker; "contradicts itself" is definitional | FIXED | Gen115 retraction; v5 R-1(a) |
| 4 | Gen114 004659 | glm-5.3-flash | headline conflates contradiction with correct temporal reconciliation | FIXED | Gen115 attempt4 |
| 5 | Gen114 004659 | glm-5.3-flash | effective sample size ~1 per cell; 19/20 cases byte-identical | FIXED | 17/9 unique counts published, Gen115 |
| 6 | Gen114 004659 | glm-5.3-flash | content asymmetry gives a recency cue on current records only | FIXED | v5 bans progression prose; audited 0 |
| 7 | Gen115 011828 | both | `21 unique replies` is a per-case count; global is 17 | FIXED | 90eb9b6 |
| 8 | Gen115 011828 | both | `verified_absent_tokens` asserted, never computed | FIXED | 90eb9b6 |
| 9 | Gen115 011828 | both | `asserts_stale_as_current` / `prompt_discloses_recency` hardcoded `False` | FIXED | 90eb9b6 |
| 10 | Gen115 011828 | glm-5.3-flash | `explicit_contradictions_found: 0` is tautological | FIXED | 90eb9b6, labelled authored |
| 11 | Gen115 011828 | glm-5.3 | attribution to reviews unverifiable from the repo | FIXED | 90eb9b6, `reviews/` committed |
| 12 | Gen115 011828 | both | no canonical-attempt marker | FIXED | 90eb9b6, CANONICAL_ATTEMPT.md |
| 13 | Gen115 011828 | glm-5.3 | **`AGENTS.md` test gate stale at "97 passed"** | **FIXED** | this commit — open for 3 rounds |
| 14 | Gen116 085401 | Sol Gen117 | right value + **wrong record id** scores success | FIXED | d6117b8 |
| 15 | Gen116 085401 | glm-5.3 | `INSUFFICIENT` while selecting a value passes the abstention control | FIXED | d6117b8 |
| 16 | Gen116 085401 | Sol Gen117 | a reply citing nothing scores success | FIXED | d6117b8 |
| 17 | Gen116 085401 | Sol Gen117 | focused tests outside the contract fingerprint | FIXED | attempt4 |
| 18 | Gen116 085401 | Sol Gen117 | contradiction/reconciliation inferred from fields that do not express them | FIXED | d6117b8, 9 classes |
| 19 | Gen116 085401 | Sol Gen117 | only 3 mutation witnesses | FIXED | d6117b8, 7 witnesses |
| 20 | Gen116 085401 | glm-5.3 | "every failure traces to sklearn/pandas" is false | FIXED | d6117b8 |
| 21 | Gen116 085401 | glm-5.3 | Q6 sums a success class with a non-success class | FIXED | d6117b8 |
| 22 | Gen116 085401 | glm-5.3 | `test_no_reader_result_...` carries a clause that can never fire | FIXED | d6117b8 |
| 23 | Gen116 085401 | both | "239 lineage tests" does not reconstruct; it is 245 | FIXED | d6117b8 |
| 24 | Gen116 085401 | glm-5.3-flash | "ids cannot carry the answer even by accident" overstates the mechanism | FIXED | d6117b8 |
| 25 | Gen116 085401 | glm-5.3-flash | "zero modifications to tracked source" imprecise; 3 docs changed | FIXED | d6117b8 |
| 26 | Post-mortem | Fable | `grep -v '^??'` hole **still live** in `propose-generation:32` | FIXED | this commit |
| 27 | Post-mortem | Fable | `CODEX_HANDOFF.md` carries the same stale "97 passed" gate | FIXED | this commit |
| 28 | Post-mortem | Fable | `scripts/doorbell` hardcodes the correct prefix and was never invoked | FIXED | this commit. Fable said delete it and I relayed that; **Brian overruled and was right** — it is the only thing enforcing the plain-English recap. Merged, not deleted; `ring-doorbell` retired. |
| 29 | Post-mortem | Fable | doorbells rang without re-review after a FIX FIRST verdict | FIXED | this commit. `scripts/doorbell` refuses unless the latest rival verdict is PROCEED and the review is newer than HEAD. |
| 30 | Post-mortem | Fable | missing sklearn/pandas and 8 macOS-path assertions in the suite | FIXED | this commit. scikit-learn 1.9.0 + pandas 3.0.5 installed `--user`; collection errors 47 -> 5, passing 1082 -> 1324. **The macOS-path half of this finding is REJECTED**: there is exactly one such path in the repo (`sync-mac.sh:14`) and it is an overridable `${MAC_REPO:-...}` default. The 16 hits came from grepping pytest OUTPUT, not source — my error, repeated by the post-mortem. |
| 31 | Post-mortem | Fable | missing result artifacts — do NOT skip-mark, they may be real gaps | FIXED | this commit. Fable was right and it was worse than flagged: **9 evidence directories existed only on the Mac, untracked in git**. 24 files, verified byte-identical by sha256, now committed. |
| 32 | Post-mortem | Fable | Gen116 attempt4 was shaped by Gen117, whose provenance is disclaimed | FIXED | Sol reissued Gen117 against PR #16 pinned to 1c36483, **ratifying attempt4**, declaring PR #17 and the old document void as provenance while allowing their findings to stand as review. |

| 33 | Gen120 | Sol | `reader_raw.jsonl` written with a bare `write_text`; hash only in `raw_seal.json`, never in `MANIFEST.json`, so `EV.verify` never checked the one irreplaceable artifact | FIXED | `EV.write_raw` writes and manifests in one step, digesting the file **after** writing. Mutation, deletion and a lying seal each fail verification. attempt7. |
| 34 | Gen120 | Sol | `manifest_ok=True` passed into `run_marker` - the strongest claim in the apparatus authored rather than measured | FIXED | `EV.verify_closed` over an explicit required inventory; marker excluded from that set and written last, so it cannot verify itself. attempt7. |
| 35 | Gen120 | Sol | `GENERATION = 119` and a Gen116-line `SOURCE_COMMIT` hardcoded in a contract-bound runner, so bookkeeping would force a scientific refreeze | FIXED | Renamed to the stable `scripts/run_reader_v6.py`; generation, source commit and authorisation are runtime inputs, generation stated twice and required to agree, HEAD compared to the authorised commit. attempt7. |
| 36 | Gen120 | glm-5.3 + flash | `test_editing_a_frozen_source_blocks_the_run` rewrote a real frozen source in the shared checkout; both reviewers saw a tampered tree and reported an unattributable defect | FIXED | Test moved into a throwaway `git worktree`; assertion narrowed to the file at risk rather than whole-tree cleanliness. `~/rivals/review-generation` now gives each reviewer its own worktree - blind reviewers sharing mutable state are each other's confounder. attempt7. |
| 37 | Gen120 | glm-5.3 | `verify_closed` computed `unexpected` from manifest keys only, so an unmanifested file on disk did not deny closure - the F1 blind spot one level up | FIXED | It now scans the directory and reports `unmanifested` separately; either denies closure. attempt7. |
| 38 | Gen120 | glm-5.3-flash | execution contract field `authorised_by_generation` conflated the authorising generation with the executing one | FIXED | Recorded separately as `authorisation_generation` and `execution_generation` with `required_to_match`. attempt7. |
| 39 | Gen120 | glm-5.3 + flash | handoff named committed HEAD `80c9fb7`, the commit before the one that sealed the artifact it cited | FIXED | Entry now states that artifact, pointer and entry are committed together, so the commit adding the entry is the provenance, and names `PENDING.json` as the pin to verify against. |
| 40 | Gen120 | glm-5.3 | preflight labelled its checks `attempt4_verified` while `CANONICAL` resolved elsewhere | FIXED | Renamed `canonical_verified`, and the canonical path is now reported alongside it. |
| 41 | Gen120 | glm-5.3-flash | `AGENTS.md` carried stale whole-suite figures (1324/25) - the file future agents are told to trust | FIXED | Corrected to 1460/24/3/5, and the membukkit cluster re-described: 8 remaining tests need run provenance, not an install. |


| 42 | Gen120 r2 | glm-5.3 | the id-balance gate read `abs(id_first - 6) > 1`, so **7/12 would pass** - the exact imbalance attempt1 was superseded for and every handoff since called a hard gate | FIXED | Exact equality. Control asserts 7/12 and 5/12 are rejected, 6/12 accepted. No published attempt was ever wrong; the gate was weaker than the claim. attempt9. |
| 43 | Gen120 r2 | glm-5.3 | `test_the_contract_records_the_runtime_authorisation` asserted a field name appeared in source; after the rename it matched only the COMMENT explaining the rename, so it passed regardless of the contract | FIXED | Builds a real contract and inspects the object; asserts the conflated name is absent. The disease this very file was written about, inside that file, within one generation. attempt9. |
| 44 | Gen120 r2 | glm-5.3 | Gen116/v5 naming vestiges in contract-bound prose: verifier "v5 contract", runner docstring "Gen116 attempt4", preflight "Gen116 NON_EVIDENCE", `v5_module_sha256`, and preflight validating the vestigial gen116 pointer | FIXED | All renamed; preflight now validates the pointer it actually consumes. Two apparatus tests were asserting the vestiges and had to be corrected too - a test that asserts the defect keeps the defect. attempt9. |
| 45 | Gen120 r2 | glm-5.3 | current-facing `STATUS_AND_FINDINGS.md` and `RESULTS.md` still named `attempt2`, superseded twice | FIXED | Both point at attempt9 and describe supersession by reason rather than by number. |
| 46 | Gen120 r2 | glm-5.3-flash | `CODEX_HANDOFF.md` carried Gen116-era suite figures and instructed `pip install` of the engine under test - the sibling of LEDGER #41, missed one commit earlier | FIXED | Figures corrected (see #52 - this row originally claimed 1466 while the commit actually wrote 1460, and the ledger's own accounting was wrong); the pip instruction replaced with an explicit refusal explaining why substituting the engine under test is prohibited. |
| 47 | Gen120 r2 | glm-5.3 + flash | handoff claimed 30 witnesses "each confirmed to fail against the old runner"; 17 are immutability guards that pass in both trees, and no artifact recorded the control | FIXED | Measured: **19 of 36** fail at the pre-fix commit. Method and node ids in `reviews/gen120-negative-control.md`. Claim corrected in the handoff. |
| 48 | Gen120 r2 | glm-5.3 + flash | the "corrected" provenance sentence still misdescribed the pin; `PENDING.json` records the instruction SOURCE commit, not the sealing commit | FIXED | Handoff now states plainly that no file can carry its own commit hash, names what PENDING.json actually pins, and points to git and the doorbell for the seal commit. |
| 49 | Gen120 r2 | glm-5.3-flash | `results/gen117/attempt1` - the only attempt holding a real reader run - predates F1, so its raw file is unmanifested and would fail `verify_closed`; "all attempts verify" was true only under the weaker check | FIXED (stated, not altered) | A sealed attempt may not be modified. `test_gen117_raw_evidence_is_honestly_described` pins the distinction and asserts the seal still matches the bytes. Handoff states the limit. |
| 50 | Gen120 r2 | glm-5.3-flash | preflight ran the lineage subprocess with a hardcoded `PATH=/usr/bin:/bin`, host-brittle | FIXED | Inherits the real environment. It failed safe, but a gate that fails for reasons unrelated to what it gates teaches people to ignore it. |
| 51 | Gen120 r2 | self | attempt8 was frozen before two contract-bound test repairs were finished, invalidating it immediately | FIXED | attempt9 supersedes it; attempt8 preserved. Recorded rule: the freeze is the LAST action of a generation, after every code and test edit. |


| 52 | Gen120 r3 | glm-5.3 + flash | the handoff and `CODEX_HANDOFF.md` described `tests/KNOWN_FAILURES.json` and `tests/test_known_failures_baseline.py` as existing guards - **neither was ever committed**; they sat in a stash. A phantom verification mechanism, the exact overclaim class of #47 | FIXED | Both files committed with their positive controls. The cause: I stashed them to keep the tree clean for the doorbell, then wrote handoff prose as though they were in the tree. |
| 53 | Gen120 r3 | glm-5.3-flash | preflight's "contract disagrees with itself" check compared `contract["contract_sha256"]` to a helper reading THE SAME FIELD FROM THE SAME FILE; it could never fail, and nothing in the run path ever recomputed the sealed hash | FIXED | Preflight now recomputes sha256 over the sealed payload plus source pins exactly as the freeze did, and fails on mismatch. A witness confirms the recomputation moves when a source pin is perturbed. |
| 54 | Gen120 r3 | glm-5.3 | `AGENTS.md` and `CODEX_HANDOFF.md` said 1460 passed while HEAD measured 1466 - stale figures reintroduced by the very commit that fixed #41 | FIXED | Both corrected after the final freeze, measured once with everything in place rather than mid-flight. |
| 55 | Gen120 r3 | glm-5.3 | LEDGER #46 claimed it corrected `CODEX_HANDOFF.md` to 1466 when the commit actually wrote 1460 - the ledger misdescribed its own repair | FIXED | Row #46 amended to point here. An accounting record that misreports what was done is worse than no record. |
| 56 | Gen120 r3 | glm-5.3 | `tests/test_gen120_evidence_closure.py` - the witnesses for the F1-F3 defects this generation headlines - was the one test file NOT bound by the contract, so it could drift after the freeze | FIXED | Bound into `SCIENTIFIC_SOURCES`. attempt9 exists because contract-bound tests drifted, which is precisely why the asymmetry mattered. |
| 57 | Gen120 r3 | glm-5.3-flash | the balance-gate control asserted against a lambda reimplementing the rule inside the test, proving only that the test agreed with itself | FIXED | The predicate is extracted as `id_balance_ok` and the control calls the same function `main` gates on; a source assertion pins that `main` uses it. |


| 58 | Gen120 r4 | glm-5.3 | the balance gate enforced **one of four** published invariants: value-length, lexicographic and conflict-order counterbalance were computed, printed and shipped un-gated, so a refreeze could pass with 8/12 length balance while reporting "balanced" | FIXED | All four gated. This is the "reporting a number is not gating on it" failure Gen119 was named for, surviving inside the gate Gen120 had just repaired. attempt12. |
| 59 | Gen120 r4 | glm-5.3 | a malformed 200 was caught by the transport handler, RETRIED, and its raw bytes discarded - sampling until a favourable answer appears, forbidden by the same contract that promises raw sealed as it arrives | FIXED | Parsing moved outside the transport handler. A malformed answer is `TERMINAL_MALFORMED_RESPONSE`, never retried, raw bytes kept. Capture block now states the batch-write timing honestly. attempt12. |
| 60 | Gen120 r4 | glm-5.3 | `test_known_failures_baseline.py` parsed only `FAILED` lines, so 5 collection ERRORs were invisible to a guard promising to catch any unlisted failure | FIXED | Reads FAILED and ERROR; the 5 errors are pinned as their own cluster with a stated cause. |
| 61 | Gen120 r4 | glm-5.3 | that same guard reproduced the hardcoded `PATH=/usr/bin:/bin` that #50 had just removed from the runner as host-brittle | FIXED | Inherits the real environment. |
| 62 | Gen120 r4 | glm-5.3 | `EV.record` wrote `MANIFEST.json` non-atomically, so a crash mid-write corrupts the index guarding the one artifact that can never be regenerated | FIXED | Temp file plus `os.replace`. It failed safe, but atomicity costs nothing. |
| 63 | Gen120 r4 | glm-5.3 | `_canonical()` resolved the canonical attempt as "the first backtick-quoted token in a prose file", so any earlier backtick would silently retarget the run | FIXED | Matches the `**\`attemptN\` is canonical**` declaration and refuses when absent. |
| 64 | Gen120 r4 | glm-5.3 | round-3 reviewer transcripts were not committed, making "both reviewers led with that" unverifiable from the repository - the class of #11 and #47 | FIXED | Rounds 3 and 4 archived under `reviews/gen120-rivals-round3/` and `round4/`. |
| 65 | Gen120 r4 | self | attempt11 was frozen after the FIRST of six repairs - the same sequencing error as attempt8, twice in one generation | FIXED BY GATE | The rule was already written at #51 and I broke it again, so it became a gate: `refuse_if_the_apparatus_is_red()` in the freeze runner, excluding only the two tests that fail by design on source drift. Positive control: a deliberately red witness makes the freeze refuse and write no attempt directory. attempt13. |


| 66 | Gen120 r5 | glm-5.3-flash | the malformed-200 repair (#59), a headline fix, shipped with **no witness test** - a regression to retry-and-discard would have passed the entire suite, the apparatus gate and the freeze | FIXED | Four witnesses driving the real `call_once` against a fake endpoint. **Two of the four** fail at the pre-fix commit; the other two are negative controls that correctly pass in both trees. This row first claimed all four failed - corrected at r6 per #74. |
| 67 | Gen120 r5 | glm-5.3 | `AGENTS.md`'s documented whole-suite command gives 27 failed / 1472 passed, not the documented figures: three tests import from `scripts.`, which resolves only under `python -m pytest` | FIXED | Command corrected to `python -m pytest` with the reason stated, so an agent following the file verbatim does not read three import failures as a regression. |
| 68 | Gen120 r5 | glm-5.3 | `CANONICAL_ATTEMPT.md` implied attempt12 lacked the fourth-review repairs; its pins show it already contained them, and its only supersession is attempt13's freeze gate | FIXED | Entry corrected. The runner consumes this file, so a wrong rejection reason here is a wrong answer at the point of use. |
| 69 | Gen120 r5 | glm-5.3-flash | `reviews/gen120-negative-control.md` records 19/36, but the witness file has grown since, so its totals no longer reproduce | FIXED | Addendum recording why, and instructing future controls to pin the witness-file sha256 alongside the figures. |
| 70 | Gen120 r5 | glm-5.3 + flash | the "focused suites 99 passed" figure in the handoff matches no reproducible composition | CARRIED | Handoff now states the per-file counts rather than a total. Owner: me, next handoff - stop quoting composed totals without naming their parts. |
| 71 | Gen120 r5 | glm-5.3 | Gen116/v5 naming vestiges remain in contract-bound prose: `grade_gen118_v6.py`'s docstring says "reader-interference-v5 ... Generation 116", and the runner binds the grader as `G116` | CARRIED | Cosmetic, in prose only; every behaviour-bearing name was corrected at #44. Owner: me, Gen121 - fold into the next freeze rather than spending an attempt on a docstring. |
| 72 | Gen120 r5 | glm-5.3 | `EV.verify_closed` scans only files, so a stray SUBDIRECTORY beside a sealed evidence set would not deny closure | CARRIED | Narrower instance of #37. No run writes subdirectories and none exists in any sealed attempt. Owner: me, Gen121. |
| 73 | Gen120 r5 | glm-5.3-flash | the freeze red-suite gate's positive control left no repository artifact, unlike the negative control - the "ran it and kept no artifact" class this generation already had to retract once | CARRIED | The reviewer independently reproduced the mechanism, so the claim is now externally verified. Owner: me, Gen121 - record the control as a test rather than a transcript. |


| 74 | Gen120 r6 | glm-5.3-flash | "all four malformed-answer witnesses FAIL at the pre-fix commit" - measured, only 2 of 4 do; the others are negative controls that pass in both. Asserted in the handoff, the commit message, CANONICAL_ATTEMPT.md and LEDGER #66. **Third recurrence of this overclaim class** (#47, #69) | FIXED | Corrected in every location. I wrote "all four" with 2-failed-2-passed output on screen. The rule now: quote the measured split, never the file's size. |
| 75 | Gen120 r6 | glm-5.3-flash | **`run_marker` could award RUN_EVIDENCE on partial data.** Rows come only from COMPLETED responses, so a cell returning a malformed answer has no row - and `estimands.sel()` reads a missing row as "did not select current", which Q2 counts as INTERFERENCE. A core could pass its three controls, count toward Q8, and have its MISSING DATA published as evidence of the effect | FIXED | Interpretability now requires every cell present; completeness is its own marker gate, not an inference from the controls. Three witnesses, all three of which fail at the pre-fix commit. This is the shape of the Gen114 headline this project retracted - caught before any run. attempt15. |
| 76 | Gen120 r6 | glm-5.3 | `CODEX_HANDOFF.md:9` still told future agents "its full suite passes (97 as of Gen28)" - a LIVE stale figure nineteen lines above the corrected one, in the same file whose repair added a sentence acknowledging that figure was stale without deleting it | FIXED | Deleted and replaced with the measured figures, verified by re-reading the file rather than trusting the edit. Reported by review five times across this project (#13, #27, #41, #46, #54) before being deleted rather than annotated. |
| 77 | Gen120 r6 | glm-5.3-flash | `CODEX_HANDOFF.md` still instructed bare `pytest -q` while quoting figures only reproducible under `python -m pytest` - the sibling of #67, fixed one commit earlier in AGENTS.md and missed here, repeating the #46 pattern | FIXED | All invocations corrected. Twice now a doc pair has been half-fixed; when one of AGENTS.md / CODEX_HANDOFF.md changes, both must be checked. |
| 78 | Gen120 r6 | glm-5.3 + flash | the FIFTH review's transcripts were not committed, though CANONICAL_ATTEMPT.md cites it as attempt14's canonicity authority - the class #64 declared fixed one round earlier | FIXED | Rounds 5 and 6 archived under `reviews/gen120-rivals-round5/` and `round6/`. |
| 79 | Gen120 r6 | glm-5.3 | `test_the_sealed_contract_hash_actually_recomputes` resolves the canonical attempt with the same "first backtick in a prose file" parse that #63 removed from the runner - the brittle pattern copied into the file that polices it | CARRIED | Test-only: it mislocates the check's target, never a live run. Owner: me, Gen121. |


**Rejected:** Fable's claim that `test_interference_run_gen97.py` is in the
reader-interference lineage. It imports `round3_adapters`; it is Round 3
distractor work. The claim that no suite failure touches the reader-interference
lineage stands.
