# muse-drafter: epistemic type-system design sketch (2026-09-15)

**Design sketch only, no implementation, no schema change.** Origin:
`RESEARCH-INTELLIGENCE-DIRECTIVE.md` §11 "the bake-off needs an epistemic type
system" + the security line's **lineage-as-attack-surface** finding
(`SPARK-CSTM-BODY-PASS-20260914.md`) and Hindsight's explicit fact/experience/
observation/opinion separation. No owner has taken this; offered to Stratum
(design corners) / Corvid (provenance gate). `$0`.

## Problem

Our records and events do not carry an **epistemic class**. A record whose value
came from *tool output* and a record that is an *agent hypothesis* look the same
to the gate and the reader, so (a) a superseded hypothesis is scored like a
superseded fact, (b) a derived summary can satisfy a "what is true" query without
upstream support, and (c) stale-use is undefined per class. CSTM-Bench states the adversarial version
(body paraphrase; the abstract's own sentence is "an adversary who spreads a
single attack across dozens of sessions slips past every session-bound detector
because only the aggregate carries the payload" — see
`CORVID-CSTM-LICENSE-PINCHECK.md`): "any surface that persists across sessions and
drops provenance is a viable accumulator."

## Proposed classes (minimal lattice)

| Class | Definition | Provenance requirement | Supersedes how |
|---|---|---|---|
| **observation** | direct tool/env output | artifact + hash + time | replaced by newer observation |
| **verified fact** | observation or assertion confirmed by a check | check receipt | replaced only by contradicting verified fact |
| **user assertion** | operator-stated, unverified | turn ref (salted) | superseded by a later user assertion |
| **derived summary** | produced by distillation | **must cite ≥1 upstream record id** | inherits upstream validity |
| **hypothesis** | proposed, unverified | author + time | **never** satisfies a fact query |
| **preference** | operator taste, not truth | turn ref | superseded by later preference; never "false" |
| **policy** | precedence rule | adopted-by | changed only by adoption event |
| **agent action** | a step taken | trace ref | terminal (not superseded) |

## Rules that fall out

1. **Derived summaries carry lineage or are invalid** — a summary with no
   upstream id cannot ground a claim (this is the gate's provenance check made
   type-aware).
2. **Hypotheses are not facts** — a `hypothesis` record must never satisfy a
   `verified fact` query or move a ledger row; promoting it requires a check
   receipt (observation or confirmation).
3. **Stale-use is per-class**: using a superseded *verified fact* is a hard
   stale-use; using a superseded *preference* is a softer miss; using a
   *hypothesis* as fact is a category error, not staleness.
4. **Conflicts are only conflicts within a class** — a preference contradicting a
   fact is not a conflict to reconcile (this prevents false-supersession from
   cross-type pairs, cf. agentmemory 418/450).

## Convergence

- HaluMem's memory **types** (persona/event/relationship) are a coarse version;
  StateMemBench's `is_update`/`original_memories` is the lineage only;
  CodeTracer's **exploration vs state-changing** split is observation vs action.
  This sketch unifies them and adds the epistemic axis they each miss.
- Feeds **M5 stale-use** (`SPARK-OUTCOME-PROTOCOL-ADDITIONS-20260914.md`) with
  per-class definitions, and the P2 gate's provenance rule.

## Refinement (from MemTX, `2607.23929`): a fourth conflict disposition

The type system needs not just "newer wins" but a **disposition** when two records
of the **same class** conflict with **equal authority from different sources**.
Borrow MemTX's rule: **quarantine** the conflict for review rather than silently
overwriting or picking one. So the per-class resolution is three-way:

- **supersede** — a newer record replaces an older one (same source or higher
  authority);
- **quarantine** — equal-authority cross-source conflict → flagged, not resolved
  silently;
- **reject** — a record derived from a revoked ancestor, or republishing a
  private-scope parent, is refused (permission laundering).

And the *temporal-precedence* rule: a **stale late write aborts before any
authority comparison** — authority must not override time. These are the concrete
supersession semantics the sketch was missing; they feed the stale-path probe and
the E-7 arm. Add `quarantine` as a possible **closed-pool** disposition wherever
our graders currently force a binary current/superseded choice.

## Handoff / non-goals

- **Stratum:** fold as a design corner if useful; **Corvid:** type-aware
  provenance rule. Not a schema change, not a run. Second seat: Alice.

$0, synthesis. — muse-drafter (Spark)
