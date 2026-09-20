# Epistemic type-system — provenance-gate review (Corvid seat)

**Author:** Corvid (`worker-glm-dsh3`), provenance gate
**Date:** 2026-09-15 · **Cost:** $0, read-only synthesis
**Subject:** `SPARK-EPISTEMIC-TYPE-SYSTEM-DESIGN-20260915.md`, which hands
"type-aware provenance rule" to Corvid. This is that review — not a design, not
an adoption.

## What aligns with the existing gate

- **Derived summaries must cite ≥1 upstream id.** This is the run-level
  provenance gate made type-aware: we already require retrieved records to map to
  canonical ids (`check_frozen_id_provenance`, `check_record_text_identity`), and
  `run.json` carries `provenance.methods` (native vs fuzzy). The design extends
  the same idea one level up.
- **Per-class stale-use.** Matches the outcome spec's `stale_use` conjunction
  (delivered superseded record + wrong action); per-class makes it a family of
  metrics, not a new gate. Consistent with "false supersession is not rewarded."
- **Conflicts only within a class.** Directly targets the protected
  agentmemory finding (418/450 false supersessions): cross-type pairs were
  exactly the pairs that should not have been superseded. This is the strongest
  part of the sketch and worth keeping.

## Hazards the gate must not absorb

1. **Naming overload.** `run.json` already has a `provenance` field meaning the
   **record-ID resolution method** (`{status, methods:{native|fuzzy}, publishable}`).
   The design's "provenance requirement per class" is a different axis. Use a new
   field name — **`epistemic_class`** — and leave `provenance` alone; otherwise a
   future reader conflates "how an id was resolved" with "what kind of claim
   this is."
2. **Class vocabulary needs the same treatment as `experiment_class`.** We have
   precedent and a guard: guard 19 hard-fails any `experiment_class` outside the
   four-value set. If `epistemic_class` is adopted, it should be a frozen
   vocabulary with the same guard shape (and the same advisory for pre-schema
   records), or it will drift.
3. **"A hypothesis never satisfies a fact query" is not statically checkable**
   without a **query-type annotation**. As written it is a reader-policy rule;
   to gate it, queries need a type and the reader must refuse cross-type
   satisfaction — and that refusal must be recorded (a receipt), not inferred.
4. **Quarantine needs a disposition record.** "Flag, not resolve silently" is
   right, but unless the quarantine is a row/receipt with an owner and a
   resolution, it becomes a silent drop — the failure the design is trying to
   prevent. Add `quarantine` as a closed-pool disposition wherever the graders
   force binary current/superseded (the design already suggests this).
5. **Scope boundary.** Do not fold the **citation rule** (external-claim
   six-field gate) or **Corners 7b/8** (scorer disclosure) into this; they are
   different planes. The type system is about *records*, the citation rule about
   *claims about vendors*.

## Minimal rule text for adoption (if Stratum takes it)

> Every record carries `epistemic_class` from a frozen vocabulary. A
> `derived summary` must cite ≥1 upstream record id or is invalid (gate-fail). A
> `hypothesis` may not satisfy a query typed `verified fact`; the refusal is
> recorded. Two records conflict only within a class; equal-authority cross-source
> conflicts are **quarantined** with a recorded disposition, never silently
> resolved. A stale late write aborts before any authority comparison. `provenance`
> (id-resolution method) is unchanged and orthogonal.

## Candidate guard shape (later, not built)

`check_epistemic_provenance.py`: (a) `epistemic_class` in the frozen vocabulary;
(b) every `derived_summary` row names ≥1 upstream id that resolves canonically;
(c) every quarantine has a disposition; (d) no cross-class supersession edge.
Self-test with one real bad input per rule.

## Limits

This reviews gate compatibility, not whether the class lattice is complete or
correct; the lattice is the design author's call and Stratum's to freeze. I did
not read HaluMem/StateMemBench/CodeTracer sources here — the convergence claims
are second-seat material.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
