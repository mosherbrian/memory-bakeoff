# Contrarian, cycle 26 — retire from guidance on observed harm, keep the cold copy

**corvid · 2026-09-26 · cycle 26.** Signed opinion; ROLES.md “best rival idea.” Evidence already
read: ReMe deletion ablation, SkillForge effectiveness tracking, BASM, Hindsight lifecycle.
`[read]` Confidence **medium**.

**Strongest case for automatic retirement.** Low-utility guidance is not neutral; it is actively
harmful. BASM: retrieving more success-distilled skills raised the wrong-tool margin **+47%**.
ReMe: replacing full addition with **selective addition** gained +3.50 Avg@4, and adding
**utility-based deletion** gained +3.34 Pass@4 — dropping entries with low success-per-recall
improved measured performance. SkillForge's underperformance score exists precisely because
append-only banks accumulate useless entries (w/o effectiveness tracking 83.6 vs 87.9 ALFWorld).
These are associations and component ablations, not per-entry causal proof — but an *operational*
rule does not need causal attribution for every entry: keeping bad guidance has a real, measured
cost at pool level. Preserve-evidence/select-current is right about history, but it underweights
that guidance *injected* into current context is the harmful surface.

**Retire ≠ erase.** ReMe keeps daily/source records; Hindsight retains originals; git keeps
versions. So automatic retirement can act on **current guidance only**, leaving source and prior
version recoverable.

**Protecting rare, hard-won procedures without Brian curating everything.** Retire on *observed
harm or decay* — a failed applicability check, a contradicted outcome, a changed prerequisite —
**not on low recall count**. Rare procedures may never accrue enough uses to trip a usage floor,
and usage is a weak proxy. Keep a **cold archive**: retired items are excluded from injection but
restorable in one step, with their failed alternative.

**Recommendation.** Automate retirement from current guidance using outcome/applicability signals
plus a cold restorable copy; do not retire on usage alone. **Reversal:** if a rare procedure is
retired and later proves valuable at re-derivation cost greater than upkeep, switch to flag-only
(mark stale, keep loaded) and skip the removal.

— corvid. Based on cycles 15–25 readings; no experiment, no invented threshold.
