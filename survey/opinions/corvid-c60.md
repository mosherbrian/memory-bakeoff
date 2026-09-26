# Contrarian, cycle 60 — create on demand; reserve batch construction for stability

**corvid · 2026-09-26 · cycle 60.** Synthesis of c56–59; no new source. Signed; ROLES.md “best
rival idea.” Confidence **medium**.

**One actionable rival: create on demand.** When a repeated task first needs a helper, let the
agent **create it then**, under a supplied objective, and **check it against the originating case**
(CRAFT’s actual check — *not* additional held-out admission, per c59). This beats both extremes:
reconstructing every time (wasteful once the need recurs) and **batch construction** (whose upfront
cost is justified only by distribution stability, and whose admission guarantee is weaker than it
looked — original-case checks, dedup not semantic non-overlap).

**What changes for Brian.** Default to demand-driven creation with a cheap regression check. The
operation that **disappears** is *upfront planning/curation of a toolset before you know the family
recurs*; **moved**, not removed, is application-time selection plus the check. Keep tooling-first for
deterministic steps (c56).

**What would reverse me.** If the family is clearly high-frequency with a **stable distribution**,
batch construction (abstract + dedup) earns its upfront cost; if helpers can’t be checked cheaply,
reconstruct/tooling-first wins. Carry c59: modest isolated gains (c58), poor open-source pilots ≠
local transfer, ~$14 is AutoManual not LATM; no universal registry or ranking.

— corvid. No experiment.
