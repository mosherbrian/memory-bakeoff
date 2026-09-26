# Contrarian, cycle 70 — pick enforcement-first, one rule, one test

**corvid · 2026-09-26 · cycle 70.** Signed opinion; ROLES.md “best rival idea.” Source:
systems/cc-safety-net.md card. Confidence **medium**.

**Choose: one project-scoped cc-safety-net rulebook** as the first pilot. Rationale is c69: it is
the smallest change whose effect is **independent of the actor’s noticing/obedience** — the reported
application failure. It has a concrete host path (Claude Code/Pi adapters), additive custom rules,
diagnostics and decision logs; the contract, owner (Claude deployment, not upstream, not Brian) and
test are nameable now. **Scope it to ONE sponsor preference** (e.g. `python` not `python3`) with
positive/negative cases plus a **bad-config test** — because an invalid/legacy configuration can
leave rules inactive, so the pilot must prove the rule actually fires. Caveat (one line): the card’s
arrow reverses the sponsor’s example — fix that before writing the rule.

**Why not a coherent memory product first?** claude-mem/ReMe/Hindsight target **capture/delivery**;
they still require the actor to obey, and choosing one is a multi-component integration with
unverified local benefit. A product wins only if it removes more work on the *failed* operation —
not by bundling (c69 addendum); here that operation is enforcement, which products don’t supply.

**Explicit boundary (don’t overclaim).** The guard does **not** repair index truncation; the
one-page design must state the real delivery arrangement, and the index-cap check stays a separate
pilot assumption/test.

**Reversal.** If the custom-rule schema can’t express the chosen preference, or the covered path
can’t veto on the target hosts, switch the first pilot to a coherent **delivery/capture** product —
for removed delivery work, not for coherence.

— corvid. No experiment.
