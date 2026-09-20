# muse-drafter: MemTX body pass — "a memory write is not a belief commit" (2026-09-15)

Body read of `arXiv:2607.23929v2` ("MemTX: Transactional Belief Commit for
Stateful Agent Memory"). Top theory-fit candidate from watchlist delta #2.
Grounding only — **preprint under review, vendor numbers uncited, no score
import.**

## Thesis (directly ours)

**A memory write is not a belief commit.** Recording an observation and
committing a belief are distinct events; systems that treat every accepted write
as immediately actionable truth let a polluted result, stale update, or
teammate's half-finished note drive an **irreversible action**. This is our
epistemic-type-system sketch and supersession-as-transaction, stated as a
protocol.

## Model (what to borrow)

- **Record schema:** entity/attribute/value + **source with authority weight** +
  **permission block** (owner, reader/writer roles, private/shared/public scope) +
  **derived-from edges forming a derivation DAG** + **type** (belief / summary /
  profile / index / shared-copy / tool-action) + **validity interval** vs a
  logical clock + writer confidence.
- **Eight-state lifecycle:** raw → tentative → validated → committed →
  action-safe, plus branch states quarantined / **superseded** / revoked.
- **Five isolation levels** (raw-read … action-safe-read); **four risk tiers**
  (low/medium/high/external-action), tier = trusted harness config, not agent
  output.
- **Commit pipeline (4 checks):** evidence (confidence ≥0.6 unless authority
  ≥0.9) · validity (interval contains now) · **semantic-conflict adjudication** ·
  dependency-stability (no pending-revocation ancestor).
- **Conflict rule (precise):** temporally disjoint values coexist; a candidate
  whose rival committed after the snapshot is a **stale late write and aborts
  *before any authority comparison*** (authority never overrides temporal
  precedence); else higher authority supersedes, lower aborts, **equal authority
  from different sources is quarantined**. Also blocks records derived from
  revoked parents and private→wider republication (**permission laundering**).
- **Action gating** on irreversible tools; **typed cascading repair** walks the
  derivation DAG (beliefs revoked; summaries/profiles/index/shared-copies
  quarantined; tool actions compensated or logged as leaked).
- **Two machine-checked invariants** (action-safety gating; cascade-repair
  completeness) over 5.5M states, zero violations.

## Six corruption families (a taxonomy we lack)

tool-result pollution · stale late writes · dirty reads of tentative state ·
semantic conflict · **permission laundering** · cascading-rollback failure —
evaluated on a 90-case conformance suite (60 traps + 30 controls) + 56 hardened,
pure-rule grader, downstream-harm pipeline.

## Transfers / recommendations

1. **Supersession rule:** "stale late write aborts before authority; equal
   authority conflicts are quarantined" is a concrete rule our E-7/supersession
   arm could adopt, and *quarantine-not-overwrite* matches our epistemic-type
   caution.
2. **Provenance-to-action-time is the named open problem:** "declarative lineage
   has nothing to inspect" when an agent transcribes without declaring the
   parent — exactly our provenance-gate worry; the paper says the fix is
   **provenance that follows content to action time**.
3. **Permission inheritance to derived records** = our scope-leakage/security arm.
4. **Recommend a candidate card** (owner call); body pass complete here. Code
   `lxy1134/MEMTX_` — license **ARR** per prior pass; paper **CC BY 4.0**.

## Limits

Preprint (under review), single author-list, results on a purpose-built
conformance suite; all rates vendor, **not citable**. Method/mechanism is the
value, not the numbers. Second seat: Alice.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
