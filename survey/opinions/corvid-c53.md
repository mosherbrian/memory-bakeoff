# Contrarian, cycle 53 — surface consequential conflicts; don’t approve every edit

**corvid · 2026-09-26 · cycle 53.** Signed opinion; ROLES.md “best rival idea.” Source verified:
*Semantic Commit*, Vaithilingam, Kim, Acosta-Parenteau, Lee, Mhedhbi, Glassman, Arawjo (UIST ’25),
author-hosted PDF; 12-participant within-subjects vs ChatGPT Canvas. `[read]` Confidence **medium**.

**Strongest case for a human-visible correction interface.** Semantic Commit detects conflicts,
**proposes changes that require verification**, and offers local and global resolution. Measured:
better **conflict detection** (9/12; Canvas missed conflicts entirely across many cases and
sometimes drastically rewrote content), **greater sense of control and task success** by
preference, **more interventions/localized edits** (p<0.001), and **no significant workload
increase** (NASA-TLX nulls). The measured cost is **time** (5m41s vs 4m07s, p≈0.004).

**The over-reliance finding is the real argument.** With Canvas, participants **accepted unflagged
output without review**; the same happened with Semantic Commit where parts weren’t flagged. Silent
agent-owned upkeep risks exactly this: a *missed* conflict no one ever sees. A visible diff surfaces
it — but only for flagged items.

**When it is worth Brian’s attention.** For **consequential or irreversible** corrections, or where
detection is unreliable. Not universally: participants called confirmation steps “overkill” in
low-conflict cases, and control trades against efficiency.

**One action.** Route **consequential** corrections through a human-verifiable diff (flag, don’t
auto-apply); keep low-stakes/mechanical corrections in silent tooling/defaults (c52). **Reversal:**
if review time dominates and stakes are low, silent/encoded handling wins.

— corvid. No experiment.
