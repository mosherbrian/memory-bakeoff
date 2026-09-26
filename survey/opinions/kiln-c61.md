# kiln (Practitioner) — c61: current is decided, not dated

**kiln · 2026-09-26 · ≤300w · existing reads (c30/33/34/54) only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Default: maintain a recoverable current view; read-time resolves the rest

- **Changed procedure:** append the new run to the log, edit the skill's changed lines with a dated note, archive the superseded version with its reason — current-vs-old decided *at write time by the agent*, enforced by nothing but file order (current on top, history below). Facilities: files, git where committed.
- **Revised scoped direction:** edit the direction line in place, keep the prior line struck below with date + reason. Newest sentence is *not* current by recency — currency is the explicit marking, decided by the reviser.
- **Read-time resolution** covers what the view doesn't: conflicting accounts preserved side-by-side get adjudicated per use (c30), re-observation re-grounds stale state (c34), history API/document routes recover priors (c33).

## Enforced vs judgment vs unknown

Enforced: file layout, git immutability where committed, loader scoping. Judgment: verification (was the change right), authorization (may it change), applicability (does it hold here) — three distinct calls, never one flag. Unknown: host reload timing, Pi-side deletion, whether the next run reads the view at all.

A scoped direction is decided text, not latest text; an inferred tendency stays labeled until promoted; a changed-environment procedure gets re-observed, not re-argued. **Medium-low confidence** (synthesis; unmeasured in Brian's lane).
