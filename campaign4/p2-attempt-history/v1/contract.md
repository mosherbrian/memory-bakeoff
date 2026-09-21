# Frozen work-package contract

**Freezes:** `ACCEPTED-ARCHITECTURE.md` §3 (sha256 `cf390ce0…ad11c2b5c`),
as amended in scope by `CHARTER.md` and bounded by `director-decisions.md`.
**Replaces:** `CONTRACT-TEMPLATE.md` (provisional transcription — retired).
**Baseline:** installed agent-deck v1.16.4; P1 v1 accepted
(`b7279897…11eea9`). No redesign; compactness is a requirement, not an
aspiration — *"There is no bespoke schema or gate-authoring exercise for each
package."*

## The contract (every package carries exactly this)

```text
Task or question — and the decision it informs
Inputs and expected output
Completion check, or named judgment reader
Worker, verifier and duty owner
Time/spend limits
Permitted data, tools and writes
```

The controller generates IDs, timestamps and hashes. Standard environment
settings and limits inherit from named, versioned defaults; a package cites
the defaults by version and states only its deltas.

## Work-type extensions (one row applies, chosen by the Director, checked once by the reader)

| Work type | Additional contract |
|---|---|
| Experiment | Metrics, controls, thresholds, exclusions, comparison method; registration (criteria, bar with a number, pinned inputs) committed as its own commit **before** any scored execution — ancestry, not a hash, is the evidence of order, plus disclosure of prior exposure |
| Implementation | Required behavior, regression evidence, permitted changes; no source change without an independently admitted implementation package |
| Judgment | Named reader, bounded effort, required disposition; no artificial numeric bar — the recorded disposition is equally visible alongside mechanical results |
| Higher-risk action | Explicit permissions and recovery requirements |

## Admission and budget defaults (inherited unless a package deltas them)

- **Admission** produces either an accepted contract or **one bounded
  explanation of what is missing** — not a negotiation, not unlimited rounds.
  Author and validity-reviewer must differ; whoever materially repairs a
  contract cannot certify that repair.
- **Budget:** one initial execution plus one repair. Every execution and
  verification activity also carries a wall-clock deadline and resource limit;
  expiry does not spend a repair. The budget follows the question (stable
  `question_id` across renames/amendments), never the row id.
- **Attempt binding:** the controller binds attempt identity at dispatch
  (launcher-recorded actor: seat + model + version — never agent self-report)
  and binds collected artifact bytes at verification. Two linked ledger events
  per attempt: a **start** (durably written before execution, carrying the
  declared deadline) and an **end** (output hashes, cost, reason for ending).
  Artifacts publish before transitions that depend on them; missing artifacts
  or mismatched hashes block the affected claim.
- **Trust boundary (shared host):** session metadata read by the controller
  establishes the configured session, not cryptographic proof of authorship or
  execution. Worker hashes, identity-file paths and pane collection do not by
  themselves prevent another same-filesystem process from supplying those
  bytes. Cross-boundary claims are payload, never attribution.

## What the contract does not do

It does not authorize another package (finishing ≠ starting); it does not set
controller code, upgrades, or migrations; completion (`COMPLETE`) is stored
separately from outcome (positive / negative / inconclusive finding) — a
valid negative experiment finishes the job, an invalid measurement is not a
null because execution ended.
