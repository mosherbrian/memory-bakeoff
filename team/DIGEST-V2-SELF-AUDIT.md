# DIGEST-V2 self-audit — seed list is over-generous (spark pulse)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local
**Target:** the 32 `seed` rows in `team/DIGEST-V2.md`, ahead of Cairn's 20-row spot-check.
**Method:** read all 32 rewrites, graded against "crisp declarative, vault-ready as written".

## Verdict: keep 10, demote 22

The fact-residual rule kept session-local status lines, log excerpts, and
meta-conversation. Proposed demotions (DIGEST-V2.md itself left frozen so
Cairn checks a stable target; apply if he concurs):

**→ probe-corpus (11):** #152 (systemctl output), #161 (deploy error line),
#162 (dbus error text), #164 (sudo command), #171 (draft-timing log),
#193, #200, #236, #243 (server/slot log excerpts), #211 (tuned-profile log),
#297 (benchmark table paste). All machine material, some already flagged by
the log-dump rule but slipped through on first-line shape.

**→ drop / question (2):** #143, #291 (both open questions).

**→ drop / fuzzy (9):** #106 (vague intention), #108 (rambling opener),
#117 ("I have a few questions…"), #123 (bare file path), #216 ("Addendum 3
is excellent"), #248, #251 (meta-conversation), #300 ("I am logged in
now"), #312/#313 ("Revision 2 is materially better" ×2, no referent).

**→ drop / session-local (4, borderline):** #136 (fragment), #163 (one-off
incident path), #233 (deploy status line), #318 (screenshot path).

**Keep (10):** #110 (iommu=pt test-representation requirement), #134 (vulkan
build spec-type constraint), #159 (model location decision), #228
(slot-swap on cancel observation), #288 (fleet routing state — time-bound,
needs date qualifier before seeding), plus #106? No — #106 demoted above.
Keeps needing qualifiers before any vault write: #288 (as-of date), #228
(single observation, n=1).

## Lesson for the lane

A residual "everything else is fact" rule over-seeds. The classifier needs a
positive fact test (stable subject + timeless predicate + no first-person
frame), not just probe/question/fuzzy carve-outs. If Brian orders a v3 pass,
that rule goes in first. Net seed estimate after demotions: **~8–10/318**,
not 32 — the machine-probe skew is even stronger than DIGEST-V2 reports.
