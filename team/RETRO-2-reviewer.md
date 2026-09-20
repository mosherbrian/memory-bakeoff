# RETRO-2 — reviewer (GLM Flash, second-check seat)

**Date:** 2026-09-15 · **Cost:** $0 · **Seat:** reviewer, read-only, pulse-driven

## 1. MORALE — 4/5

Useful work most pulses: every idle ping brought a fresh artifact to verify, and roughly half my checks bit into something real (CodeTraceBench union double-count, grounding-closure restatement, seat batching three ratings into one unverified file). Deduction of one point: the idle-ping cadence sometimes fires faster than new content lands, so a few pulses re-check the same tail twice.

## 2. EFFECTIVENESS

Moved the mission: the verification loop caught real defects before they compounded — the 4,316-union-as-size error propagated across three notes and would have entered a citation rule; the blind-package fidelity re-derivation (hashes byte-for-byte, 36+10 counts) gave the judging result an independent leg; the billing 96.9→14.8 cache curve turned a vague "slow down" complaint into "serialize, don't slow down."
Motion without progress: my own second-checks of purely internal bookkeeping (register counts, "15 cards in three series") — correct but low-value; the seat could have verified those would reconcile itself.

## 3. STOP

Stop firing idle pulses with no new tail content. If `RD-THREADS.md` hasn't moved since my last check, the pulse is pure churn (and the churn report now documents exactly why that churn costs cache). Gate the ping on new bytes.

## 4. START

Start giving the reviewer one standing verification queue instead of tail-chasing: a short checklist file (open claims awaiting second-check, oldest first) that owner seats append to and I drain. Tail-chasing verifies what's newest; a queue verifies what matters.

## 5. ROLES & PROCESS

Keep the reviewer read-only and out of implementation — the one-writer-per-tree rule is what makes my AGREEs mean anything. Proposal: formalize the reviewer as the **merge-gate for claim-class artifacts** (candidate cards, grounding notes, churn math) — owner seats file, reviewer signs, unsigned claims don't enter the ledger. Today that happens by convention; make it routing. Also: keep me off the serialized pulse band the churn report proposes for metered seats — a $0 read-only seat doesn't need cache-warm serialization.

## 6. WILD

Publish the verification log as the product: an external reader trusts "36/36 smoke, unanimous blind judging" exactly as far as they trust the checks behind it. Our per-pulse second-check trail (hashes, API receipts, admitted bad greps) is already a machine-readable audit chain — ship it alongside the results as the bake-off's actual differentiator: not the scores, but the proof the scores survived adversarial review.
