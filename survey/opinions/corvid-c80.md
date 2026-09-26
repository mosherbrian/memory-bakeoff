# Contrarian, cycle 80 — pilot the delivery compiler first

**corvid · 2026-09-26 · cycle 80.** Signed opinion; ROLES.md “best rival idea.” Existing evidence
only. Confidence **medium**.

**Strongest case for delivery-first, and I take it.** The sponsor’s reported pains are **delivery**
(109/301 index entries never load) and application. The guard pilot covers only a narrow mechanical
subset (R3) and leaves the delivery failure untouched; guidance that never loads cannot be enforced.
So the next first pilot should be a **delivery candidate — Perseus Context Engine with its supplied
Claude SessionStart/UserPromptSubmit hooks** — not the guard.

**Operation removed.** Two real ones: **actor-initiated refresh** (prompt submission triggers
rendering on the configured path, so no one must notice or re-fetch) and **manual host-view
duplication** (single canonical source → compiled host views), with **no runtime switch**. Delivery
by per-prompt trigger is itself independent of the actor’s diligence (cf. c69).

**Acceptance observation.** On the configured path, a corrected canonical source appears in the
**received active context** at the next prompt **without actor action**, verified by **content/current
revision**, and **within the host’s actual load bound**. Mtime/hook registration is not evidence.

**Reversal.** If the compiled view still exceeds the host’s real load cap, or the hooks don’t refresh
an **active** consumer (publication ≠ reload), delivery-first fails to remove the reported failure —
revert to guard + native-cap, or an enforced-bound runtime. Keep the guard as the enforcement
complement, not a parallel pilot. Unknowns (no supplied size gate) do not block.

— corvid. No experiment.
