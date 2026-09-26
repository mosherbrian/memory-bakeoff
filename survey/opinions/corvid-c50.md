# Contrarian, cycle 50 — make preference memory example-induced and action-grounded

**corvid · 2026-09-26 · cycle 50.** Synthesis of c46–49, no new source. Signed; ROLES.md “best
rival idea.” Confidence **medium**.

**One consequential action to change.** The preference bet should stop treating stated directions
as the only capture unit. Add: **when examples reveal a useful distinction, the agent induces an
editable rule and stores the behavioural examples, then applies them at the action endpoint** —
TidyBot (frozen executor + induced rule), PUMA (behavioural history + action), PersonaMem-v2
(implicit preferences). Keep **authority tiers separate**: an explicit direction binds regardless
of inferred habits.

**Strongest surviving rival.** The **trained reader/actor** (PersonaMem-v2 RL reader; PUMA
SFT/DPO). It is the real alternative where *reasoning* is the bottleneck or the executor itself
must change; coupled-system gains exist, but training cost/transfer to Brian is unestablished and
no equal-compute comparison exists.

**Work removed vs relocated.** Removed: hand-authoring rules and per-query whole-history replay.
*Relocated*: applicability/selection/validation to the agent, and correction cost to whoever owns
the rule. No measured correction-burden saving from any of the four.

**One reversal.** If examples reveal no generalizable distinction, or the executor must change,
induction fails and training (or clarification) is needed; and if Brian’s real cost is *stated*
direction repetition, inferred rules don’t address it.

— corvid. No experiment.
