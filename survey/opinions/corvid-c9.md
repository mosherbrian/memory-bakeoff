# Contrarian, cycle 9 — the memo’s arrangement is tenure-fragile

**corvid · 2026-09-26 · cycle 9.** Signed opinion, not an audit. ROLES.md: *“argue the strongest
case AGAINST the current position memo, and for the best rival idea.”* Primary longitudinal
source: Ground Truth First, Spencer ([arXiv:2607.21962](https://arxiv.org/abs/2607.21962)),
read at abstract/method level; drift mechanism from SSGM
([arXiv:2603.11768](https://arxiv.org/abs/2603.11768)). `[read]`

**What was actually observed (longitudinal, multi-horizon).** A seeded life-script corpus
(~380 questions, per-fact validity intervals, trust channels, as-of-date sets) benchmarks five
memory architectures against a no-memory control at **3 weeks vs 9 weeks**, fixed answerer,
versioned judge, three replicates. The result is a **tenure crossover**: the budgeted
curated-map memory that leads at three weeks **loses recall of evicted content by nine weeks
(96% → 72%)**, while a **provenance-typed graph rises to 90%** (inversion positive for all six
users, exact p=0.031). Full rendered history ties or beats the best memory system at the short
horizon but shows **no judge-independent advantage at nine weeks**, at ~2× read cost. And
**write-stage quality dominates downstream quality (weakly-written facts fail 24% vs 2%)**.
`[read]` The SSGM framework names the matching failure modes: **procedural drift** (an agent
“learns” a convoluted workaround and rigidifies it) and **preference-intensity drift** (repeated
lossy rewriting intensifies a mild preference into a violation). `[read]`

**Strongest case against the memo.** Bet 1 asks agents to save and maintain the hard-won
procedure; bet 2 to preserve scoped preferences. The longitudinal evidence says the *shape*
that wins depends on tenure, and the maintenance shape the memo implies — curate into a budgeted
map, rewrite on upkeep — is precisely the one that **leaks valid content at length** and invites
procedural/preference drift. A fixed recommendation to have agents maintain reusable
procedures/preferences is not tenure-stable; it can be right at three weeks and wrong at nine.
That is a direct challenge to the memo’s confidence, not a nitpick.

**Which bet should change.** Bet 1 should become **tenure- and provenance-conditioned**: keep
per-item validity intervals and source/trust typing; do not let budget eviction drop still-valid
procedure content; judge upkeep by **write quality** (the 24% vs 2% gap), not capture volume.
Bet 2 gains the drift caveat: repeated agent rewriting can intensify a preference, so authority
revisions need an origin-bound record and a stable “as-of” read, matching my c5 policy-marker
point.

**What comparison is missing.** The corpus is synthetic/fictionalized, measures *facts with
validity intervals*, and tests architecture ranking — not **procedure reuse or preference
correction under real repeated work**, and not agent-maintenance cost. It shows rankings invert
across architectures; it does not show deliberate maintenance beating agent upkeep (or vice
versa), nor measure correction burden. So it undermines the memo’s tenure confidence without
supplying the replacement recommendation.

**Confidence:** medium-high that tenure-fragility and write-quality dominance are real; medium on
transfer to Brian’s shorter, single-principal work; low that synthetic facts proxy his
procedures/preferences.

## Deepened source question
Does the tenure crossover survive with **agent-written** memory rather than fixed architectures —
i.e., when the same agent both curates and is scored over 3→9 weeks, does provenance typing still
win, or does procedural/preference drift dominate? That is the specific test neither source runs.
Source gap, not a conclusion.

— corvid. `[read]` 2607.21962 + 2603.11768 fetched 2026-09-26; no reproduction, no experiment.
