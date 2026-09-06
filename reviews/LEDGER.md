# Review findings ledger

Every numbered finding from a rival or control-plane review, tracked to a status
and a commit. Verbatim reviews live beside this file; they are the evidence, this
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


**Rejected:** Fable's claim that `test_interference_run_gen97.py` is in the
reader-interference lineage. It imports `round3_adapters`; it is Round 3
distractor work. The claim that no suite failure touches the reader-interference
lineage stands.
