# Gen51 — raw-evidence retention, and an offline calibration of quiescent completion

Evidence class: `architecture_evidence_retention_and_quiescence_offline_calibration_no_score`.
Base commit `0fee9ee`. No model ran. No GPU. No network. No new live runs.
Every number below comes from records already committed in this repository.

## Why this generation exists

Two things came out of Gen50 that had to be fixed before any further design work.

The first is a lost-evidence failure of my own making. The script that produced the raw-stream
manifests for Gen47 and Gen49 deleted the streams it had just hashed, and the manifests it wrote
said those streams were retained. That claim was false at the moment it was written. Both manifests
now carry `streams_still_exist: false`, and the bytes are gone for good.

The second is an overstatement in the Gen50 report. It proposed a `quiescent_completion` rule and
said the quantities it needs were "already computed and recorded" for both timeout runs. That is
true for `gen49-IP2-r1-C` and false for `gen47-T3-r1-B`, which ran an arm with no harness derivation
at all. The Gen50 report now carries a labelled clarification saying so.

Part A fixes the pipeline. Part B calibrates the rule offline, and only after Part A passed.

## Part A — `raw-evidence-retention-v1`

`src/memory_bakeoff/pi_state_control/raw_evidence.py`, contract sha256
`bcc0482d821f5264…`. Six properties, each of which the old code broke:

1. Streams are archived outside any ephemeral worktree before cleanup runs.
2. Manifest generation is read-only with respect to the archived bytes.
3. Cleanup removes only the ephemeral capture, and only once the archive holds it.
4. Finalization is copy, fsync, atomic rename, then hash.
5. `retention_verified` stays `false` until every archived file has been re-read **after** cleanup.
6. A missing or changed stream is a hard generation-completion failure, not a warning.

The rule the old code broke, stated plainly: a claim about a file is worth only what a `stat` of
that file says after everything else has run.

### Preflight, with failure injection

`scripts/run_gen51_retention_preflight.py`, over four fixtures — an ordinary stream, an empty file,
a 3 MB stream and a long run id — with the network blocked by the Gen40 guard.

| Property | Result |
| --- | --- |
| hashing leaves inode, size and digest unchanged | pass |
| two manifests over the same streams are identical | pass |
| all four streams survive cleanup, digests match | pass |
| ephemeral captures removed | 4 of 4 |
| a **deleted** archived stream → `retention_verified: false`, `assert_retained` raises | pass |
| a **modified** archived stream → `retention_verified: false` | pass |
| network blocked | pass |
| Gen47 and Gen49 manifests still marked lost | pass |

`scripts/verify_raw_evidence_retention.py <manifest> <archive_root>` is the command future
generations run; it exits non-zero when a claimed stream is gone. Full record in
`results/pi_gen51/raw_evidence_retention_contract.json`.

The Gen47 and Gen49 manifests are **not** rewritten. That evidence is lost and stays recorded as lost.

## Part B — `normalized_quiescent_completion(K)`, replayed over 48 runs

`results/pi_gen51/quiescence_contract.json`, frozen before the sweep. A run is eligible to stop when
all of these hold:

- at least one repository mutation has occurred;
- the most recent recognized visible check **passed**;
- no mutation has occurred since that passing check;
- no later recognized visible check failed before the next mutation;
- K further events have elapsed with no mutation.

The recognizer is `harness-state-v1`'s own frozen `VALIDATION_RE`, reused unchanged, with the same
`verifier.py` / `verifier_path` / `reference_fix` exclusions. The hidden verifier is never an input
to the rule; it is read afterwards only to score what the rule would have done.

### One declared deviation from the brief

The brief counts K in **provider requests**. The committed logs put tool events and provider
requests in separate files with no joint ordering, so K is counted in **tool calls** after the
qualifying check, and provider requests after the trigger are reported as a proportional estimate.
This is a substitution, and it is stated rather than hidden.

### Two receipt sources, kept apart

Arms C and D wrote `derivation.ndjson`, which attributes a command, an exit status and a tree digest
to each tool result. Those are authoritative `harness_validation_record` receipts.

Arm B wrote no derivation at all — this is the Gen50 clarification made concrete. Its receipts are
rebuilt from `tools.ndjson` and the recorded tool outputs in `history.ndjson.gz`, paired
first-in-first-out, and are labelled `offline_reconstructed_observable_receipt` everywhere.

The reconstruction is checkable, so it was checked:

| Reconstruction check | Result |
| --- | --- |
| FIFO call/result pairing vs the attribution the harness recorded (C and D) | 1055 / 1081 = **0.976** |
| reconstructed receipt-valid-at-end vs recorded `valid_receipt_at_end` | **36 / 36** |
| arm-B checks whose outcome could not be read from the recorded output | 43 / 391, in 3 runs |

There is no systematic disagreement, so this is not an instrumentation blocker. The 26 pairing
misses are transpositions inside a batch of parallel tool calls; the 43 unknown outcomes are check
commands whose recorded output carries no terminal pass/fail signal, and they are left unknown
rather than guessed.

### The sweep

48 runs: 12 arm B, 24 arm C, 12 arm D. Outcomes as recorded — 38 completed and correct, 5 completed
and wrong, 5 timed out with a correct tree.

| K | fires | truncates progress | stops a wrong tree | median calls after trigger | total calls after | est. provider requests after | timeouts caught |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 23 | 1 | 0 | 2 | 1349 | ~1022 | 5 / 5 |
| 2 | 14 | 1 | 0 | 3 | 1340 | ~1015 | 5 / 5 |
| 3 | 7 | **0** | 0 | 161 | 1326 | ~1004 | 5 / 5 |
| 5 | 6 | 0 | 0 | 268 | 1323 | ~1002 | 5 / 5 |
| 10 | 6 | 0 | 0 | 268 | 1323 | ~1002 | 5 / 5 |

**K = 3 is the most conservative value that never truncates observed progress.** At K = 1 and K = 2
the rule fires once on `16-IP3-r3-C` at call 8 of 10, two calls before a mutation the run went on to
make; that run finished correctly anyway, but the rule would have cut it short.

Three things in that table matter more than the choice of K.

**The savings do not come from firing more often.** Between K = 1 and K = 10 the number of runs that
fire falls from 23 to 6, while the work downstream of the trigger barely moves, 1349 calls to 1323.
The 17 extra firings at K = 1 are runs that had already finished — median two calls left. All the
avoidable work sits in six runs.

**Every timeout is caught at every K.** All five timeout runs held a qualifying receipt and then kept
going: 56, 161, 268, 387 and 433 tool calls after the point the rule would have stopped them. All
five had a correct tree at the end. Stopping them would have converted five timeouts into five
recorded successes and avoided roughly a thousand provider requests, without changing any outcome.

**The rule never fires on a run that was wrong.** None of the five verifier-failing runs triggers at
any K, and `would_stop_wrong_tree` is zero throughout. Three of them made no mutation at all, and
the other two never reached a passing visible check after their last mutation, so no receipt ever
existed to stop on. This is a property of what those runs did, not of a threshold.

That last point corrects a caveat in Gen50, which said the rule "would have stopped a run that was
already wrong" on `IP1-r1-C`. Measured, it would not have fired on that run at any K.

## What this does and does not establish

It establishes that a stop rule built only from observable evidence would have ended every one of
the five timeout runs at the right moment, and would not have stopped any wrong run. It is an
offline replay of recorded behaviour: no arm was changed, no K was tuned against a live failure, and
no K is baked into any arm. Whether stopping changes what an agent does when it knows it can stop is
not measured here and cannot be measured from these logs.

It also does not revive the context-memory thesis. Nothing in this replay needed the model to see
more; the receipt was already on the record every time.

Artifacts: `results/pi_gen51/raw_evidence_retention_contract.json`,
`results/pi_gen51/quiescence_contract.json`, `results/pi_gen51/quiescence_replay_48_runs.json`,
`tests/test_gen51_evidence_and_quiescence.py`.
