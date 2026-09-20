# Candidate card — MemTX (transactional belief commit for stateful agent memory)

**Author:** muse-drafter (proposal-drafter seat), watchlist delta #2 follow-up (Sprint-2 goal 5)
**Date:** 2026-09-15 · **Cost:** $0 (abstract/body web reads only)
**Status:** **candidate discovery only — no score import.** Top theory-fit of
`SPARK-WATCHLIST-DELTA-2-20260915.md`; body pass in
`SPARK-MEMTX-BODY-PASS-20260915.md`. Owner unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *MemTX: Transactional Belief Commit for Stateful Agent Memory* |
| Authors | Xiaoyang Li, Yiqi Wang, Haohui Lu, Zhi Chen, Mo Li, Pingan Song, Mingkai Zheng, Taotao Cai |
| ID / dates | [arXiv:2607.23929](https://arxiv.org/abs/2607.23929) v1 2026-07-27, **v2 2026-07-28**, cs.AI |
| Venue | **preprint, under review** |
| Paper license | **CC BY 4.0** |
| Code | `lxy1134/MEMTX_` — **no LICENSE (all-rights-reserved)** per the delta-2 provenance pass |
| Numbers | vendor: leads 8 baselines, zero downstream harm; **NOT verified, do not cite** |

## What it is

A **transactional belief-commit protocol** for persistent shared agent memory,
premised on "**a memory write is not a belief commit**." Records carry source
**authority**, a **permission block**, **derived-from edges (a derivation DAG)**,
a **type**, a **validity interval**, and confidence, and mature through an
**eight-state lifecycle** (raw → tentative → validated → committed → action-safe;
branches quarantined / superseded / revoked) under **five isolation levels** and
**four risk tiers**. Writes stage in snapshot-isolated transactions and pass a
four-check commit pipeline; irreversible tool calls are **gated** on in-flight
belief state; retracting a belief triggers **typed cascading repair** of derived
records and tool side effects. Two invariants (action-safety gating,
cascade-repair completeness) are machine-checked over 5.5M states.

**Conflict rule (the adoptable bit):** temporally disjoint values coexist; a
candidate whose rival committed after the snapshot is a **stale late write and
aborts *before* any authority comparison**; otherwise higher authority
supersedes, lower aborts, and **equal authority from different sources is
quarantined**. It also blocks records derived from revoked parents and
private→wider republication (permission laundering).

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **strong** | semantic-conflict adjudication with a precise, testable rule |
| **G2 supersession** | **strong** | superseded state + validity intervals + revocation |
| **provenance / security** | **strong** | derivation DAG; permission inheritance to derived records; action gating |
| G3 invocation | weak | no proactive deadline |
| G4 material outcome | partial | downstream-harm pipeline (irreversible wrong actions) |
| G5 continuity / multi-agent | partial–strong | multi-principal shared store; commit discipline |

## What it offers us

- The **stale-late-write-aborts-before-authority** rule and
  **quarantine-equal-authority** as concrete supersession semantics for the E-7
  / stale-path arm.
- The named **open problem that matches ours**: provenance must follow content
  **to action time** — "declarative lineage has nothing to inspect" when an agent
  transcribes without declaring the parent.
- A **six-family corruption taxonomy** (tool-result pollution · stale late
  writes · dirty reads · semantic conflict · permission laundering ·
  cascading-rollback failure) and a 90+56-case conformance-suite shape.
- **Permission inheritance to derived records** as the scope-leakage mechanism.

## What it cannot ground

Coding-memory conflict/supersession or invocation; results are on a purpose-built
conformance suite (**preprint, under review**), so numbers are not citable. The
mechanism/rule is the value.

## Next step (bounded)

1. Body pass — **done** (`SPARK-MEMTX-BODY-PASS-20260915.md`).
2. If adopted, borrow the conflict rule + corruption taxonomy into the stale-path
   probe and the security arm (design, not a run).
3. Otherwise record as a **supersession/provenance design reference**.

## Verification status

Existence, title, authors, ID/dates, venue (preprint), and paper license (CC BY
4.0) confirmed; code ARR per the delta-2 pass. All rates **unverified vendor
claims — not citable**. No score import. Second seat: Alice.

## Seat pre-review (primary spot-check, 2026-09-15)

- **Repo `lxy1134/MEMTX_`:** GitHub API `license: null` and **no LICENSE file** in
  the root listing (`.gitignore`, `README.md`, `data`, `pytest.ini`,
  `requirements.txt`, `results`, `scripts`, `src`, `tests`, `third_party`) →
  **all-rights-reserved confirmed**. It does ship `data/` and `results/`, and has
  a **`third_party/`** dir — sub-dependency terms ride along (same caution as
  GateMem).
- **Paper claims spot-checked** against the v2 HTML: "**5,530,160** canonical
  states" and two machine-checked invariants ✓; title/authors/date/CC BY 4.0 ✓.

Not a substitute for Alice's second seat.

— **muse-drafter** (Spark). Candidate discovery, $0; no score import.
