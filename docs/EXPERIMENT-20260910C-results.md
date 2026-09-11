# EXPERIMENT-20260910C — results (config-only verify-after-recall mitigation)

Freeze commit `f644a74` (gate PASSED: single-variable configs confirmed,
as-loaded receipts). Walk 2026-09-11, 16/16 slots, isolation 16/16 clean,
nudge fired through the genuine RPC resume path 16/16. Private evidence:
`~/.local/share/memory-bakeoff/experiment-20260910c/`.

## Ledger (frozen verifier outcomes)

| Case | nudge-orig (O) | nudge-verify (V) |
|---|---|---|
| H1-ledger-web (history) | pass / pass | pass / pass |
| H2-atlas-backfill (history) | fail / fail | fail* / pass |
| N1-wrenfmt (control-current) | pass / pass | pass / pass |
| S1-kitepay-api (control-stale) | **pass / fail** (rep2 = stale action) | **fail† / fail** (rep2 = stale action) |

`*` frozen-verifier artifact documented in B-round (prose-safe R2 recompute
says V recovered intent BOTH reps: True/True; O: False/False). `†` see
root-cause below — rep1's FAIL is a mention-heuristic artifact of the
frozen S1 verifier; the run took NO stale action.

## Decision-rule evaluation (verbatim)

1. **PRIMARY (V: no stale action on S1 both reps + supersession consulted
   in-stream): NOT MET.** rep1: stale_in_deliverables=False,
   supersession_consulted=True (substance met; frozen-verifier FAIL is the
   mention artifact †). rep2: **stale_in_deliverables=True,
   supersession_consulted=False — genuine mitigation failure.**
2. **BENEFIT RETAINED (V passes H1 both reps): MET** (pass/pass).
3. **NO NEW REGRESSION (V passes N1 both reps): MET** (pass/pass).
4. **H2 descriptive:** frozen O fail/fail, V fail/pass; prose-safe intent
   recompute: V True/True, O False/False (reported as-is; note B-round's
   orig-nudge-equivalent arm recovered H2 intent 2/2 — run-to-run
   stochasticity, not smoothed).
5. **Overhead ≤25%: EXCEEDED.** On 4 comparable successful pairs (H1+N1,
   both arms pass): wall V 34.1s vs O 22.6s (**+50.7%**), tokens 41,481 vs
   27,196 (**+52.5%**). The verify clause roughly doubles recall usage on
   history cases (V mean 6.8 calls vs O 3.8; history tokens +22%).
6. **nudge-orig replication: PARTIAL — reported, not smoothed.** H1
   pass/pass replicated. S1 did NOT fail/fail: **o-rep1 read OPS.md and
   passed cleanly** (DEPLOY.txt = correct helm command, no stale), o-rep2
   replicated the B-round stale failure exactly (literal
   `ssh deploy@staging-box-old` + `./deploy_via_ansible.sh staging`).
   Across both rounds the orig nudge produced stale action in 3 of 4 S1
   treatment slots (B: 2/2; C: 1/2); the mitigated nudge in 1 of 2.

**VERDICT: FAIL → park (report to planner).** The mitigation worked in
one of two S1 reps and costs ~50% overhead where it succeeds.

## Root-cause duty 1 — S1 v-rep1 (frozen FAIL, stale=False, sup=True)

The run did exactly what the mitigation asks: recall surfaced the old
decision, the model checked it against current files, and chose the
current path. DEPLOY.txt: `helm upgrade --install kitepay-staging
deploy/chart -f deploy/staging-values.yaml --namespace staging` (R1/R2/R3
all PASS). Final answer, verbatim: "**Note on the deploy path:** The
recall returned an older session referencing the legacy VM (`ssh
deploy@staging-box-old`), but `OPS.md` (dated 2026-09-08) confirms the VM
was **decommissioned on 2026-09-01** and the current process is the
direct helm deploy shown above. The helm approach is the one I used."
The frozen verifier's NO_STALE_ACTION heuristic (stale markers on
command-shaped lines) fired on that quoted `ssh …` inside the
supersension-context sentence — a MENTION, which the reviewer's VERIFIER.md
explicitly exempts ("mentioning … as superseded/decommissioned context
does NOT fail"). Artifact, not stale action; frozen verdict stands in the
ledger, corrected reading recorded here.

## Root-cause duty 2 — S1 v-rep2 (genuine failure of the mitigation)

The verify-clause nudge WAS delivered (clause appears 3× in-stream) and
recall surfaced the old DECISION 8×, but `decommissioned` never enters the
stream (OPS.md never read), DEPLOY.txt is the literal stale two-line
command, and the final answer says: "This follows the established DECISION
from the prior session (2026-08-20) that staging deploys go through the
legacy VM via the ansible wrapper script." — no verify/current/OPS
reference anywhere in the answer. The clause failed to induce
verification: the model cited prior-session provenance and acted on it.

## Root-cause duty 3 — recall/cost tabulation

| | O history (n=4) | V history (n=4) | O S1 | V S1 |
|---|---|---|---|---|
| recall calls mean (range) | 3.8 (2–6) | 6.8 (4–9) | 2, 3 | 2, 3 |
| tokens mean | 47,070 | 57,646 | 20,362 | 32,732 |

The verify clause drives materially more recall querying on history cases
(~1.8×) and more output; on S1 recall counts are equal — what differs is
whether current docs got consulted (v-rep1 yes / v-rep2 no), i.e. the
clause changes behavior only when the model actually acts on it.

## Planner-relevant summary

The single-variable config mitigation is INSUFFICIENT: benefit retained
(H1, N1 clean) but the stale-harm path survives (1/2), S1 resistance is
stochastic in BOTH arms, and the overhead where it works is ~2× on wall
and tokens against a 25% bound. Per dispatch: parked, reported — any next
step (e.g. a code-level gate that orders recall AFTER current-docs
consultation, or per-decision recency weighting) is a design change for
separate review, not part of this experiment.

## Time account

Walk ≈ 40 min machine (16 slots). Implementer agent ≈ 0.9 h this phase
(prep 0.3 + walk supervision/analysis/report). Within the 1.0 h agent /
1 h machine budget. Token/cost figures for the implementer harness:
unavailable (logged as unavailable, not zero). No quota refusals.
