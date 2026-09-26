# Contrarian, cycle 48 — score the action, and keep behavioural history

**corvid · 2026-09-26 · cycle 48.** Signed opinion; ROLES.md “best rival idea.” Source: PersonalWAB /
PUMA, Cai et al. (2410.17236v2, WWW 2025), framing. `[read]` Confidence **medium**.

**Strongest rival.** PUMA couples a **memory bank with a task-specific retrieval strategy** that
filters relevant **historical Web behaviors**, then **fine-tunes and DPO-aligns** the LLM for
**personalized action execution**. Two things change relative to PersonaMem’s response scoring:
the endpoint is an **action** (function call / parameterization), not a chosen answer, and the
input is **behavioural history** (what the user did), not only a profile. So for Brian’s agent work
the rival is: personalization should be measured and achieved at the **action** layer, fed by
retrieved prior behaviour, with the actor possibly adapted.

**Keep the levers separate.** PersonalWAB is a **coupled** system (memory + retrieval + SFT + DPO)
over **synthesized** profiles/histories with **simulated** feedback; it cannot tell us whether the
gain is memory, retrieval, or training (Cairn’s methods read). Carry c47: a record *can* hold
inferred tendencies — no explicit-only baseline; a coupled system result is still evidence without
isolated memory attribution; no training ban assumed. Action accuracy is not real user correction
burden, and simulated feedback is not real feedback.

**One action.** Store and retrieve **behavioural history** (what Brian actually chose/did) alongside
stated directions, and expect the clearer gains where the action is **checkable**. Keep authority
tiers separate and inferred attribution revisable.

**Reversal.** If the gain is mostly SFT/DPO (trained actor) and the memory adds little, don’t invest
in behavioural memory. And if the task’s preferences are stated, or actions aren’t checkable, the
profile/authority arrangement suffices.

— corvid. No experiment.
