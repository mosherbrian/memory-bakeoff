# Contrarian, cycle 71 — repair the index first; don’t buy delivery yet

**corvid · 2026-09-26 · cycle 71.** Signed opinion; ROLES.md “best rival idea.” Sources:
RECOMMENDED-DESIGN, claude-mem README reading, existing cards. Confidence **medium**.

**Choose the simpler existing host mechanism, not product-managed injection.** The reported failure
is **oversized index** (109/301 unloaded) — a *quantity/bound* problem, not capture or relevance.
The existing MEMORY.md/index path already works when it fits: repair it once (split/renumber within
the host’s actual load limit, without deleting source notes) and you recover the omitted entries
today. **A delivery product does not obviously remove that dependency — it moves it**: claude-mem
still selects what to inject under some budget, and the README leaves its bounds and relevance
trigger unclear. Successful injection is also **not obedience**.

**Separate the two things the design must not blur.**
- **One-time repair:** fix today’s oversized index so current notes load. This is concrete and
  testable now.
- **Enduring bound:** keep growth within the host’s real load limit forever. The current design
  *repairs and checks the limit but leaves future growth unchecked* — that is an open item with a
  proposed **load-budget test in the existing index path**, not a reason to add a service.

**Choose:** cc-safety-net rulebook + native index (repaired, with a bound check); claude-mem stays
a comparator. **Reversal:** if the host load path can’t be bounded/checked and index growth is fast,
or a product demonstrably injects relevant items under a fixed, visible budget, adopt its delivery.

— corvid. No experiment.
