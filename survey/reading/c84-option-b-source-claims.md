# Reading note c84 — source-checking option B's three live claims: two hold with wording, one cannot be checked

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 84.**
Skeleton first; **explicit sponsor commission**: adversarial review of
`inputs/DESIGN-OPTION-B-20260926.md` as a candidate, not a decision; Claude is co-author, not
independent evidence; sponsor file preserved unchanged. Claims checked: (1) "Agent-confirm tier
ON, so drafts cannot expire" (Vault v2.23.2, native vs Pi wrapper); (2) "@profile sets a budget
per model" (Context Engine 1.0.26); (3) Ledger mutable-writer independence (existing c78 source
note sufficient). One direct source trace used (@profile, pinned wheel); resolved
@budget/render seam not re-read; no release sweep, no runtime.

*(findings + ratings appended below)*

## Claim 1 — "Agent-confirm tier ON, so drafts cannot expire" — **UNVERIFIABLE from pinned
artifacts; first unsupported guarantee**

Vault v2.23.2 is described as "our Linux build"; **no Vault artifact exists in the pinned
source root** (only `perseus-ctx` 1.0.26 and `perseus-ledger` 1.2.4 wheels). Per commission, I
state unknown and do **not substitute identities**: the Pi decision wrapper in this session
(`project_perseus_*`) shows drafts carry a draft_id + one-time confirmation code, but its draft
lifetime is not observable from the tool contract, and wrapper behavior is not native Vault
2.23.2 evidence. The word **"so"** additionally asserts a causal mechanism (confirm-tier ⇒
no-expiry) that nothing shown establishes. **Rating: unsupported-as-written** — not disproven;
checkable if the build's source is pinned.

## Claim 2 — "@profile sets a budget per model" — **supported as declared config, with one word
to keep**

Direct trace (wheel, pinned): profiles are keyed by model name and carry
`context_target: int — **advertised** context budget for the model`, plus memory posture
(on_demand/relevant/always) and `inject_limit`. Unknown names fall back to default
deterministically; first `@profile` wins. So the design's sentence is true **as configuration**.
The field's own name — *advertised* — keeps the resolved seam intact: enforcement remains the
separate `prompt-size` gate; a profile does not itself fail a render. The design does not claim
otherwise; reviewers should not read more into it than "sets".

## Claim 3 — Ledger mutable-writer independence — **conditional, not supplied by hashing**

Existing c78 source note (sufficient per commission): **hash chains prevent neither edits nor
certify truth.** The design's own fleet principle — "a file an agent can write is not evidence
about that agent" — therefore bites its own row: the Ledger is an independent witness **only if
the store sits outside the agents' write path**; hashing records sequence, it does not bind the
writer. The design half-sees this (it invokes the principle) but the row's headline ("hash-chained
record of what the automated steps did") reads as stronger than the mechanism.

## Requirement implications

- **Req 2:** per-model **declared** budgets exist (`context_target`); enforcement unchanged and
separate. No new cell; record wording "advertised".
- **Req 3:** Ledger protection/evidence status **conditional on store write-restriction outside
agents** — partial, not hash-supplied.
- **Req 7:** the Ledger "is the label history for retraining" inherits the same conditionality:
labels written by a writer who can write the store are not independent evidence.
- **Req 10 (evidence integrity):** mechanism (chain) yes, independent attestation no — partial.

**First unsupported guarantee, named: the agent-confirm ⇒ drafts-cannot-expire claim (Vault
artifact absent; causality asserted).** Everything else in the three checked claims survives
source contact with the quoted wording kept.

**Confidence: high claim-2 facts (direct wheel trace), high Vault-artifact-absent (root listed),
high on the c78 ledger limitation being the binding condition (carried source finding), medium
that no Vault source is pinned anywhere else (searched scratchpad only — named unknown).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, panel-response-c83.md,
systems/perseus-context-engine.md, systems/perseus-ledger.md, CAPABILITY-MATRIX.md.