# R20 admission review — corvid-eval, read-only

- **Verdict: ACCEPTED** (with bounded coverage conditions, below).
- **Reviewer:** corvid-eval; qid R20-admission-1; receipt started 2026-09-25T19:22:21Z,
  deadline 19:32:21Z. Read-only: this file is the only write; no host effects, no
  network/Signal/services, no R19 or production change.
- **Contract pin:** receipt `contract_sha256` `f6934033…` equals `sha256(package.md)`. ✓
- **Scope pin:** `scope-decision.json` = `SCOPED_AUTHOR_AND_ACTIVATION_HELD`, ceiling 200,
  activation gated on R19 complete + baseline/candidate independent PASS + bounded release.

## 1. Tier2+4 contract feasibility

- Tier2 (loop change) and tier4 (descriptive measurement) are separated as required:
  tier2 is the versioned stamp artifact on agent-loop task surfaces; tier4 is the
  before/after measurement with a script, no model judging, no daemon.
- Authoring is safely bounded and gated: this release activates **admission only**;
  baseline/implementation require prospective receipts, and activation waits until R19
  participant execution and outcome review finish. Nothing here mutates the running
  contract ("existing active tasks remain on their original contract").
- Evidence deliverables and the isolated real-process witness are all offline/private;
  private capabilities and message secrets are explicitly excluded from export.
- Feasible with the stated sources; the risky parts (source-branch provenance, unknown
  denominators) are already required to be failed/labelled rather than guessed.

## 2. Authority and terminal semantics

Coherent and consistent with the campaign's separations:
- Worker declares completion; never selects its verifier or grants authority.
- Contract/config selects routing/owners; the stamp cannot dispatch work, extend a grant,
  authorize a page, or override a sponsor stop. Proposed vs authorized vs actually-started
  are kept distinct; `measurement(e)` independently checks real starts.
- Terminal: explicit terminal disposition, director-owned, no fabricated next research job;
  blocked open work gets a concrete bounded recovery action. No partial terminal commit;
  a bad/missing/malformed/oversized/routing-wrong stamp refuses advancement **before**
  mutation and opens an owned bounded fault, preserving artifact+reason and never silently
  waiting.
- Honest failure is protected: failed/incomplete work may still be filed with a blocking
  issue for the existing escalation owner. Completion exception is explicit (submitting the
  claim/stamp is allowed; executing commands drafted inside it is not). The R19 delivery
  contradiction is retained as a read-only regression fixture.

## 3. Baseline coverage (verified against live records, read-only)

Window `[2026-09-24T19:00:00Z, 2026-09-25T19:00:00Z)` is **exactly 24h**, matching the
post-activation comparison. Available coverage is real but **partial**, and the package
already commits to labelling holes rather than extrapolating:
- agent-loop SQLite `events`: 147 in-window rows (types start/authorize/admit/publish/
  decision_task/decide/verify_pass/verify_fail/interrupt), but the earliest in-window row is
  `2026-09-25T01:17Z` → **~6.3h at window start has no loop ledger**.
- `RESEARCH-PRIORITY-HISTORY.jsonl` begins `2026-09-25T03:45Z`; `REST.jsonl` begins
  `2026-09-25T04:33Z`; `RESEARCH-STREAMS.json` gives A/B only.
- `control-events.tsv` is **stale since 2026-09-24T03:53Z** and is unusable for this window;
  the per-seat `acp-stream/*.jsonl` files are thin/instruction-only, not a reliable turn log.
- `escalations.jsonl` exists (613 lines) and contains wiring-test pages that must be
  excluded from production incidents, as the package requires.
- Consistent SQLite snapshot is feasible via a read transaction (`mode=ro` URI); the DB was
  opened read-only here and no WAL assumptions were needed.

Consequence: formulas (b)/(c)/(e) are computable only over the covered interval with explicit
unknown denominators and censoring; (a)/(d) likewise. This is feasible, but it is the main
bounded risk: the baseline report must state the uncovered interval and observed lower bounds,
not a full-day estimate. `Q-DELIVERY` is a registered question (rank 4) with no prior
active packages, so "same-stream" for (c) needs an explicit scope (campaign-wide over A/B, or
an explicit Q-DELIVERY binding) — a clarification, not a blocker.

## 4. 200-minute arithmetic

`10+20+60+25+20+15+15+10+15+10 = 200` exactly, equals the fixed ceiling; no hidden reserve,
automatic extension or repair. Tier split is an estimate and labelled as such. ✓

## Bounded conditions (not blockers)

1. Baseline report must quantify the `19:00Z→01:17Z` uncovered interval and mark (a)-(e)
   denominators unknown where the ledger is absent; no extrapolation.
2. State the (c) same-stream scope explicitly (Q-DELIVERY has no stream registry entry).
3. Keep the R19 late-review/protocol-deviation visible in accounting (as R19 already requires)
   and do not combine it into a retroactive success.

## R19 non-interference

No R19 file, dispatch, task/packet, frozen prompt, order or grading is read-modified here;
R20 activation is gated after R19 completion, and R20 uses R19 only as read-only evidence.
This admission neither alters nor delays R19.

*Reviewed read-only: package.md, scope-decision.json, admission-receipt.json,
RESEARCH-PRIORITIES.json, RESEARCH-STREAMS.json, RESEARCH-PRIORITY-HISTORY.jsonl, REST.jsonl,
control-events.tsv, agent-loop campaign4.db (read-only), escalations.jsonl, acp-stream/*,
R19 package/checkpoint/delivery-amendment-acceptance.*
