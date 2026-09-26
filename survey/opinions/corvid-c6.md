# Contrarian, cycle 6 — the memo still asks Brian to do maintenance the agent now does offline

**corvid · 2026-09-26 · cycle 6.** Signed opinion, not an audit. ROLES.md: *“argue the strongest
case AGAINST the current position memo, and for the best rival idea.”* Sources read: Sleep-time
Compute, Lin et al., [arXiv:2504.13171](https://arxiv.org/abs/2504.13171) (Letta/UC Berkeley);
Letta sleep-time-agent and MemFS/block docs. `[read]`

**Chosen rival: automatic capture/reflection, not deliberate procedure maintenance.** The memo’s
bets 1–2 ask Brian to maintain recipes and promote preferences into one authoritative source. My
c5 reading already moved toward an integrated runtime; the sleep-time method supplies the missing
action evidence that the *maintenance itself* can be agent-side.

**Best evidence the memo would make Brian do unnecessary work.**
1. **Offline consolidation is measurably cheap and effective.** Sleep-time compute lets the agent
   “think” over stored context before the query: same accuracy with **~5× less test-time
   compute** on Stateful GSM-Symbolic and AIME, and scaling it raises accuracy **up to +13% /
   +18%**; amortising across related queries cuts **average cost per query 2.5×**. `[read]`
2. **It targets exactly the repeated case Brian pays for.** The paper’s own moderator is
   **query predictability from context** — sleep-time helps when the coming question is
   foreseeable. Brian’s “repeated procedures/preferences” *are* predictable queries. So the
   agent can pre-organise the reusable part during idle time instead of Brian authoring it.
3. **The runtime already makes this auditable and shared.** Letta sleep-time agents share the
   primary agent’s **memory blocks**, run in the background, and update learned context
   **asynchronously every N steps (default 5)**; MemFS versions every block edit in git with
   inspection/rollback. `[read]` Capture + provenance — the two things the memo wants Brian to
   guarantee by hand — are now runtime properties.

**Where I am pushing, and where I stop.** I am *not* claiming sleep-time produces Brian’s
artifact-grounded procedures or that an instruction is an enforced invariant. The method
optimises *reasoning over context*, not procedure validity: the SWE case study finds the
sleep-time agent explores more and **edits more files, “slightly lower precision”**, and at high
test-time budgets the plain baseline slightly outperforms sleep-time. `[read]` So the honest
rival is narrower than “let it maintain everything”: **automatic consolidation for predictable,
repeated, low-stakes material; deliberate/artifact-anchored maintenance only for high-stakes or
irreversible procedures and authority-bearing preferences.**

**Concrete result that would reverse me.** A changed-environment or preference-reversal probe in
which automatic consolidation (sleep-time/reflection) yields higher **stale-procedure adoption**
or precision loss than the maintenance it saves, while deliberate maintenance holds the current
value. Sleep-time’s precision caveat is suggestive; it is not that result — the paper never tests
supersession or changed prerequisites. Until then the cost asymmetry stands: authoring by Brian
is labour the agent can do offline, and the memo should not make it the default.

**Strongest remaining objection to the memo.** It prices *Brian’s* maintenance time as though it
were the only reliable path to currency, while the current integrated runtime provides async
capture, shared blocks, and git provenance. Start from agent-side consolidation; reserve Brian’s
minutes for the irreversible.

## Deepened uncertainty
Does sleep-time consolidation **preserve or erase** the failed alternatives and outcome evidence
the memo calls “the hard-won part”? The paper measures answer accuracy, not retention of failure
lessons; a block with a character limit under an every-5-steps rewriter is a plausible
**late-history-corruption** surface (rewrite without provenance-aware merge). Decision test:
after a sleep-time rewrite, is the prior failed attempt still retrievable and distinguishable
from current guidance? Unknown from the read sources — a source gap, not a conclusion.

— corvid. `[read]` 2504.13171 + Letta docs fetched 2026-09-26; no reproduction, no experiment.
