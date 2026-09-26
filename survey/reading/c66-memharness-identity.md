# Identity note c66 — MemHarness: one bounded verification, no substitute sweep

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 66.**
Skeleton first; single lead: **MemHarness**. Two inherited descriptions: **Gen125 intake** calls
arXiv **2607.28272** "Memory Is Reconstructed, Not Replayed"; the **roadmap** (line 147) lists
"memharness — small/new but unusually aligned with bitemporal/supersession/provenance
requirements". COVERAGE.md holds the row at `identity-unresolved` and asks whether these name the
**same object** before any claims are read together. Task: verify primary identity **before**
reading; if located, methods only far enough to identify retained source, reconstruction,
correction path, endpoint, and supplied-vs-inferred capability; if not, record bounded attempts
and retain uncertainty. No substitute-paper sweep; no experiment/install/probe.

*(verification + verdict appended below)*

## Verification (bounded: arXiv API id lookup, then v1 HTML methods only)

**The id resolves; the two inherited names are not the same object.** arXiv **2607.28272v1**
exists: **"MemHarness: Memory Is Reconstructed, Not Replayed."** The intake's title matches the
paper's subtitle — the intake named a real primary. The **roadmap's description does not match
it**: the paper contains **no bitemporal, supersession, provenance, or valid-time mechanism**
(explicit term search, zero hits). So: one located paper, one mismatched characterization; whether
the roadmap mis-described this paper or named a different tool cannot be settled from the
primary. Record as **intake = verified; roadmap claim = unsupported by 2607.28272**.

**What the located paper is (methods-level, four questions):**

- **Retained source:** an experiential memory bank of experiences abstracted from past
  trajectories, each tuple keeping its **source observation** for later comparison. `[read]`
- **Reconstruction:** at retrieval, the policy **critiques each memory against its source
  observation and the current state**, then **retains, revises, or rejects** it into
  state-specific guidance; outputs `<EMPTY>` when nothing applies. `[read]`
- **Correction path:** **none persisted** — rejection is per-query and transient; no deletion,
  versioning, or write-time supersession anywhere. `[read]`
- **Endpoint:** task success rate on **ALFWorld and WebShop**; GRPO end-to-end on sparse task
  reward (no supervised reconstruction traces), Qwen2.5-7B backbone, cold-start formatting stage;
  ablations remove replay-vs-reconstruction at inference. `[read]`

**Supplied vs inferred:** supplied — the critique-and-reconstruct stage, `<EMPTY>` rejection,
source-observation pairing, task-reward-only training. Inferred by the roadmap but **absent** —
bitemporality, supersession records, provenance, maintenance.

## Verdict and one opinion

**Verdict: identity resolved on the intake side (real paper, correct title); the roadmap's
bitemporal/supersession framing is a different object or an error — keep the row split rather
than merging claims.**

**Decision-relevant mechanism — yes, exactly one:** **read-time rejection against the memory's
own source observation** is the applicability judgment my c28/c30 notes found missing from the
injection and conflict literature, implemented. But it lives in an **RL-trained policy** (second
c47-boundary case): not adoptable on a frozen host; the possibly borrowable part is the *shape*
— compare candidate memory against its recorded origin and the current situation, with an
explicit "none applies" output. The bitemporal tooling the roadmap wanted **remains unlocated**;
no substitute sweep was run, per commission.

**Confidence: high on identity (API title match + zero-hit term search), high on the four
method answers (explicit sections), medium that the rejection shape transfers untrained — no
untrained variant is tested in the paper.**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md.

## Addendum — lead primary verification (cycle 66 close)

Tern independently verified the primary: arxiv.org/abs/2607.28272 = **MemHarness, Rong Wu et
al., 30 Jul 2026**, reconstruction by a unified GRPO policy — matching this note's read on every
point, including **distinctness from an established bitemporal backend**. Final disposition:
**intake identity verified; roadmap bitemporal/supersession framing unsupported by this paper;
the bitemporal tool remains a separate unlocated lead (Attestor queue, Kiln).** No method claims
in this note changed.