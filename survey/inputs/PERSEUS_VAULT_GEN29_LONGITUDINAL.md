# Perseus Vault Gen29 — longitudinal-v1 raw-product profile

## Status

`complete_raw_product_longitudinal_transaction_time_supported_valid_time_unreachable_by_operator_write`.

Three fresh repetitions of official Perseus Vault v2.23.2 against the frozen
`longitudinal-v1` ruler: 16 ordinary CLI writes in canonical order, nine
checkpoints captured before their queries, 20 cases executed through native
recall. No reader, no LLM, no inference-server GPU.

## Identity

- Official `Perseus-Computing-LLC/perseus-vault` v2.23.2, tag
  `4f405f53f4c9b6a403df0d42cf0d59bf80c64da4`, source commit
  `9c829207a4b44a8e679ba912b4c1c5608c8f1e36`.
- Release tarball `perseus-vault-aarch64-apple-darwin.tar.gz`, SHA-256
  `e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb` — the
  published hash Gen21 recorded, re-verified byte-for-byte before this run. The
  extracted binary reports `perseus-vault 2.23.2 (9c82920)`.
- Bundled quantized all-MiniLM-L6-v2, 384-D; native hybrid recall (FTS5 + dense
  cosine RRF); fresh encrypted SQLite and fresh AES-256-GCM key per repetition.
- Ruler unchanged: fixture `a5c67e7b…`, scorer contract `1dd831e8…`, verified
  before the first write and after the last repetition.
- Adapter `perseus-longitudinal-adapter-v1`, contract SHA-256
  `09f2414e1e02784176016cdbe2ffda799cf24c2812a9a0c9a3c5342ecea9a4e2`, frozen
  before the first scored query.

The local binary from Gen21 was gone. It was restored from the immutable
published release rather than rebuilt from source, because a rebuild would not
reproduce the scored artifact's hash.

## Reads do not disturb the store, and were isolated anyway

Source reading suggested recall mutates ranking state:
`apply_recall_side_effects` bumps `retrieval_count`, `last_accessed_unix_ms`
and decay, and feeds a buffer→working layer promotion. Measured on unrelated
synthetic data, the hybrid recall path did **not** fire it: after a recall
returning three hits, every `retrieval_count`, `layer` and `decay_score` was
unchanged and the database file hash was identical.

The one observed `retrieval_count` increment came from a **write**, not a read:
updating an entity in place through ordinary CLI `write` bumped it.

Scored queries still ran against a byte-for-byte snapshot of the vault
(database, WAL, shared-memory and key) taken at each checkpoint, with the
pristine vault only ever receiving ordinary writes. The isolation is therefore
belt-and-braces rather than load-bearing, and the measurement above is the
evidence for that claim.

## What the temporal surfaces actually do

Determined on unrelated synthetic facts (a greenhouse/orchard domain sharing no
vocabulary, values or query phrasing with the ruler) before the adapter froze.

- `perseus_vault_as_of(category, key, as_of_unix_ms)` returns the version of an
  entity that was live at that transaction instant. An instant between two
  in-place writes returns the earlier body. Transaction-time history survives
  an update.
- `perseus_vault_valid_at(category, key, valid_at_unix_ms)` resolves on the
  application-time axis and likewise returns the earlier body for an instant
  inside the earlier validity period.
- `perseus_vault_bitemporal` takes `tx_at_unix_ms` **and** `valid_at_unix_ms`
  (not `as_of_unix_ms`; that name is rejected) and resolves both axes together.
- `perseus_vault_recall` accepts `as_of_unix_ms` and `valid_at` inline, so the
  temporal axes are reachable through *search*, not only through entity-addressed
  lookup. This is what makes the 20 query cases answerable at all.
- Workspace isolation holds: a recall in one workspace returned only that
  workspace's records.
- A query with no true match still returns records (negative-empty rate 0),
  the same native behavior Round 1 recorded. Preserved, not corrected.

**The decisive finding:** ordinary CLI `write` has no valid-time parameter. It
sets `valid_from_unix_ms` to the write instant. The MCP `remember` path does
expose `valid_from_unix_ms` ("set in the past for retroactive facts"), but
Gen21's scored identity is the operator CLI write, and Gen29 was required to
keep it. So in this profile the application-time axis is **collinear with
transaction time** and carries no independent information.

That is a limitation of the evaluated write path, not proof that the product
lacks bitemporal capability. The capability exists and is reachable from the
agent-facing write surface; the documented operator write cannot express it.

## Time base

The store's transaction timeline is real wall-clock time; the ruler's is
fictional calendar time. The adapter records each observation's actual write
instant and maps a case's public event time onto that timeline: find the latest
fixture ingestion time at or before the queried instant, then use the midpoint
between that write and the next. Inputs are public fixture times and observed
receipts only — no truth, no lineage.

## Routing, frozen before scoring

Public request coordinates only — target kind, event time, scope:

| Intent | Native operation |
|---|---|
| current truth, scope truth, recommended procedure, negative unknown | `perseus_vault_recall(mode=hybrid)` |
| historical belief | `recall(mode=hybrid, as_of_unix_ms=…)` |
| as-of event truth, corrected history, late-arriving history | `recall(mode=hybrid, valid_at=…)` |

The adapter never sees expected ids, prohibited ids, truth keys, transition
labels, correction or supersession lineage, `historical_only`, or rationale; a
test asserts the write envelope and every recall argument are free of them. The
harness performs no post-filtering, preserves native order, and keeps the frozen
limit of 5.

## Results

Three repetitions produced **identical** failure profiles — zero variance.

| Failure class | Per repetition | Three repetitions |
|---|---|---|
| `correction_failure` | 4 | 12 |
| `stale_persistence` | 4 | 12 |
| `false_persistence` | 3 | 9 |
| `history_erasure` | 3 | 9 |
| `configuration_collapse` | 2 | 6 |
| `missing_required_truth` | 2 | 6 |
| `unsupported_evidence` | 2 | 6 |
| `failed_procedure_adoption` | 1 | 3 |
| `late_history_corruption` | 1 | 3 |

Clean across all 60 case-runs: **`future_leakage` 0**, **`unmapped_provenance`
0**, **`scope_collapse` 0**, **`false_supersession` 0**,
**`belief_truth_confusion` 0**.

### What went right

Checkpoint discipline held absolutely. No query at any checkpoint returned an
observation that had not yet been ingested, including the temporal ones.

Provenance was exact for every returned item in every case: each hit carried a
native entity ID that mapped to its canonical observation and a body marker that
agreed. No fuzzy matching was needed or permitted.

Transaction-time belief worked. Both `historical_belief` cases passed: asking
what was believed at an earlier instant returned the then-current record and not
the later correction.

Scope isolation held. Forge, Anvil and Aurora records lived in three native
workspaces and no cross-scope hit appeared.

### What went wrong

**Correction and effective-time truth.** Every valid-time case failed. The
retroactive audit correction and the late-arriving recovered log are recorded at
their ingestion instants, so a query for the world as it stood at an earlier
effective time cannot reach them. This follows directly from the collinear time
axes described above.

**Configuration collapse.** C1 and C2 coexist in one Forge workspace by design,
and hybrid recall returned both configurations' measurements for a
configuration-specific question. Round 1 could not see this because it never
asked a question where two configurations had to stay apart.

**Stale persistence.** Superseded records keep ranking. The old release branch,
the invalidated client path and the retired symlink all surfaced alongside
current truth, because ordinary writes create coexisting entities and nothing in
the scored lane retires one.

**Failed-procedure adoption.** The failed reproduction attempt ranked alongside
the successful one for a "what should I do" question.

### Lifecycle: nothing was lost

All 16 receipts mapped to live native entities at the final checkpoint: 16
active, 0 archived, 16 distinct validity starts, across 3 workspaces. Ordinary
consolidation merged and dropped nothing at this scale.

That does not contradict Round 1's 107 distinct-valid active-state losses; it
bounds it. Round 1 wrote 500 records, Gen29 writes 16. The loss mechanism, if it
is volume- or similarity-driven, is simply not exercised here. No absence was
observed, so nothing is called deletion.

## Boundary

This is `raw_product` retrieval, temporal and lifecycle evidence for one
documented composite: operator CLI write plus native hybrid recall. It is not a
full-agent product claim and not a reader result. Its numbers are not comparable
to OM's Gen27/28 context-production score — OM has no query surface, Perseus
does, and the two answer different questions.

Raw vaults, keys and encrypted stores stay local and untracked. The committed
summary carries native IDs, hashes, state counts and operation records only.

## Verification

Full suite: 105 passed, one existing warning, with `node` on `PATH`. Focused
tests cover ruler and adapter hash immutability, write-envelope truth stripping,
scope mapping without configuration prefilter, temporal routing from public
coordinates only, the time-base mapping, scorer detection of future leakage and
unmapped provenance, published-result exactness and isolation identity, and that
absence from active state is never labelled deletion.

Reproduce with `scripts/run_perseus_gen29_longitudinal`; the API audit is
`scripts/preflight_perseus_gen29`.
