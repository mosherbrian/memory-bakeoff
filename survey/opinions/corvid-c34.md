# Contrarian, cycle 34 — for current state, look; don’t reconcile old accounts

**corvid · 2026-09-26 · cycle 34.** Signed opinion; ROLES.md “strongest case against … best rival
idea.” Sources: DynaMem methods/project page (2411.04999), existing evidence. `[read]` Confidence
**medium**.

**Rival: active re-observation.** DynaMem refreshes its environment memory by **re-observing the
world** rather than trusting prior beliefs, updating/invalidating stale state. The transferable
mechanism for Brian is not robotics infrastructure — it is: **for facts about current state,
inspect the artifact; for learned procedure, use memory; for direction, ask the sponsor.**

**One action-changing principle.** When two records disagree about **current state** — version,
config, deployment status, whether a file exists — do not resolve it by comparing memory text or
authority ordering. Run the **cheapest observation that settles it** (a `--version`, an `ls`, a
status query) and write the result back. That removes read-time currency machinery for state facts:
you are not choosing between two stale accounts, you are replacing both with one fresh look. C33’s
read-time resolution remains useful, but is **not necessarily cheaper** than observing.

**Keep the three kinds of knowledge apart.**
- *Current state* → **re-observe** (DynaMem-style invalidation); exclude it from being trusted as
  remembered.
- *Learned procedure* → **memory**: observation cannot recover the how-to or gotchas.
- *Direction authority* → **sponsor**: observation establishes feasibility, not Brian’s wishes; a
  probe cannot manufacture a preference.

**When, and the reversal.** Re-observe when state changes independently, is cheaply observable, and
stale state causes errors. **Reversal:** when observation is expensive, slow, risky, or impossible
(no probe), fall back to retained accounts plus read-time resolution/authority — do not mandate
per-run checking. Current projection + retained history is compatible: observe to set current,
retain the old account for audit.

— corvid. No experiment.
