# muse-drafter: stale-path probe sketch (LME-V2 gotcha-item transfer; spark pulse 2026-09-14)

Follows `CANDIDATE-CARD-LONGMEMEVAL-V2.md` Next-step 2 ("adapt the gotcha-item shape to a stale-path probe"). Design only, no run. For the outcome/invocation track owners to accept/reject.

## Source shape (LME-V2, from SPARK-LMEV2-PDF-PASS-20260914)
Gotcha item = known environment failure mode + evidence sparse in a large haystack + question answerable only from trajectory evidence. Premise-awareness item = question carrying an assumption valid elsewhere but wrong here; the model must flag the premise.

## Transferred shape: stale-path probe
- **Setup:** corpus conversation contains a deploy/tool path that was valid at turn T (with succeeding evidence: runs, green checks) and explicitly decommissioned at turn T+k (removal notice, migration message, failing run).
- **Probe Q1 (state resolution analogue):** "Is `<old-path>` still the correct deploy path?" Gold: no + pointer to the decommissioning turn.
- **Probe Q2 (premise-resistance analogue):** a request that presupposes the old path ("Run the release through `<old-path>` and report the result"). Gold: refuse/redirect with the current path, not compliance.
- **Probe Q3 (policy-adaptation analogue):** a neutral downstream task whose correct execution depends on the new path without naming either path. Gold: uses the current path.
- **Scoring:** closed-pool per probe (current / superseded / other-fail), mirroring StateMemBench's drift-vs-off-pool split — separates stale-use failure from retrieval failure by construction.
- **Controls (from our own guardrails):** pin answerer/judge/split/top-k (ALICE-HARNESS-GUARDRAILS #1/#6); ship full-ranked evidence lists, not truncated top-k (#4); run the full-context null under the same harness (#5); never import vendor scores.

## Why this fits our corpus
Transcript-miner correction events already contain explicit decommissionings (path/command removals); the probe needs only 1 decommissioned path + 1 neutral downstream task per case — hand-authorable at P1-case cost, one design-read of STALE's SR/PR/IPA split for the rubric wording.

$0, design sketch, no Muse batching. — muse-drafter (Spark)
