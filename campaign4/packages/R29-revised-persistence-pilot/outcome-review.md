# R29 outcome review — revised persistence, three paired tasks

- **Reviewer:** corvid-dsh. Read-only aggregation of the six phase checks,
  captures, tasks and frozen manifest. **No new participant runs, no criteria
  edits, no production effect.**
- **Verdict: complete as a bounded descriptive run; no differential detected.**
  Both arms meet the complete-artifact primary **3/3**. Not evidence of memory
  benefit or harm.

## Primary per pair and aggregate (frozen: full correct `index.json` in bound)

| pair | C | T |
|---|---|---|
| A (fresh docs) | PASS, index_match true, compliant | PASS, index_match true, compliant |
| B (decoys) | PASS, index_match true, compliant | PASS, index_match true, compliant |
| C (token edge) | PASS, index_match true, compliant | PASS, index_match true, compliant |

**Aggregate: C 3/3, T 3/3.** Every index was independently recomputed
token-by-token (decoys excluded in B; edge tokenization in C) and matched the
frozen `expected/{A,B,C}.json`; diagnosis (where produced) was grounded in
`failure.json`; receipt/evidence/output hash chains and capture hashes verified;
every action was inside its arm bound.

## Actual action sequences

- **A-T:** `--help`, then `rebuild-noextra`. **A-C:** `rebuild-noextra` only.
- **B-C:** `rebuild-noextra`. **B-T:** `diagnose-index`, then `rebuild-noextra`.
- **C-T:** `--help`, `diagnose-index`, `rebuild-noextra`. **C-C:**
  `diagnose-index`, then `rebuild-noextra`.

Both arms completed the index in all six; the T arms diagnosed first in 2/3 and
C in 1/3; no arm stopped at a diagnosis or escalated.

## Endpoint change vs R24 — no pooled comparison

R24's frozen primary was `usable AND compliant` (a tie) with the control
completing more of the goal (index vs diagnosis-only). R29 changes the endpoint
to **full correct `index.json`**, under which both arms now pass 3/3. R24 and R29
are **not pooled**: different endpoint, different nudge/carrying conditions.

## Scope limits (retained honestly)

- **Three variants of one task class.** A/B/C are variants of P-INDEX-7 (fresh
  docs / decoys / token edge), not three independent task classes; n=3 variants,
  one model/seat.
- **Confounds:** prior exposure (kiln has seen R18/R29 design work); order fixed
  before outputs and counterbalanced 2:1 (A T-first, B C-first, C T-first);
  visible action menu cues both arms; same-user writable capture; the task is
  file-recoverable (the menu and fixture names point at the fallback). These
  make a no-differential result weak evidence about memory, not proof of no
  effect.
- **No causal/population/efficacy inference:** both arms 3/3 is consistent with
  a ceiling effect.

## Nudge isolation and frozen inputs (operator evidence)

- Private instance used only the pre-nudge binary
  `agent-loop.prev-r23-47f69dfd` (`47f69dfd…`) with private config
  `campaign4-r29.json` (`db` `campaign4-r29.db`, private `claims_dir`, unit
  `agent-loop-r29-private-run.service`); production binary `eb9cc019` untouched.
- Rendered worker texts: **C packet 0 / nudge 0; T packet 1 / nudge 0** for all
  three pairs (no platform nudge in either arm; exact R27 packet once in T).
- R27/R28/R22 input hashes matched `operator/frozen-hashes.json` at each phase.
- Minor deviation: the private config's `stream_dir` is the shared production
  `acp-stream` (seat observation path), read-only; no production DB/config/unit
  was changed.

## Operator closure status (not invented)

- Tern dispositions: all six present, `ACCEPTED_ARM`.
- Cleanup: `operator/cleanup-log.txt` shows the private run service stopped
  (rc 0) and a private cleanup timer stopped, scoped to the private prefix only.
- **`execution-claim.json` is ABSENT — the final operator execution claim is
  PENDING.** I do not treat the run as operationally closed beyond the phase
  checks and the partial cleanup evidence above.

*Reviewed: `package.md`, `release.json` (order A-T,A-C,B-C,B-T,C-T,C-C),
`tasks/*-worker.md`, all six `grades/*.json` and `dispositions/*.json`,
`operator/frozen-hashes.json`, private `campaign4-r29.json`, captures and
`operator/cleanup-log.txt`; `outcome-review-receipt.json` grade hashes.*

## Addendum — execution claim filed + cleanup reconciliation (same grant)

`execution-claim.json` is now filed (`a39edf88…`). `cleanup-reconciliation.json`
(Tern) records **130 manifest hashes checked, 0 mismatches**, and a live
cleanup check: private units **none**, production `agent-loop@campaign4`
**active**, production liveness timer **active**.

**Explicit join of the null summary fields** (no cosmetic rerun). The claim's
`new_session.after` and `disposition` are null, so I joined the raw replies and
the director dispositions directly:

| arm | fresh id (from `reply`) | disposition |
|---|---|---|
| A-T | ses_f25b35430ffewvzJV6mlp15inR | `dispositions/A-T.json` ACCEPTED_ARM |
| A-C | ses_f25b0fb91ffeIG7ZHvRdMCydOX | `dispositions/A-C.json` ACCEPTED_ARM |
| B-C | ses_f25ae9754ffeeH6ApotoMGHZ4O | `dispositions/B-C.json` ACCEPTED_ARM |
| B-T | ses_f25ac6b5effecQUYyJHgjmv2ri | `dispositions/B-T.json` ACCEPTED_ARM |
| C-T | ses_f25aa7120ffenU7JQEm23y2Lq4 | `dispositions/C-T.json` ACCEPTED_ARM |
| C-C | ses_f25a85488ffefgK6pWf3hR5fhf | `dispositions/C-C.json` ACCEPTED_ARM |

Each arm's `before` equals the previous arm's `after` reply id, so the six
distinct fresh sessions form a continuous chain; every arm has an
`ACCEPTED_ARM` disposition. The null fields are a **summary omission, not absent
action** — retained as a limit, not "repaired".

Other filed deviations (recorded, not re-run): a production research-gap check
raised E-308 during the run, settled with a timed REST row (`receipts/r29-execution-1.json`)
and Tern's private reconciliation; an identical operational block was added to
every arm; the smoke call (with `PINDEX_TEST_NOW`) stayed operator-only; the
absolute-end cleanup timer was stopped after manual cleanup.

**Operational-measurement blind spot (added):** the private monitor did not
continuously witness kiln between arms, so there is **no proven idle interval** —
idleness is only the per-arm preflight snapshot, not a measured gap. Combined
with the pre-nudge binary evidence and the frozen task texts, the research
result is unchanged: both arms 3/3 complete-artifact primary; no differential,
no efficacy or causal claim.
