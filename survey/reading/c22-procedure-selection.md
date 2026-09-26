# Stored vs used — which controls actually separate selection/application from content and executor

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 22.**
No new sources. SkillRL from my own full read `[read]` (c15); SkillForge and BASM facts from
Tern's recorded method notes `[note]` (tern-c15-skill-learning, tern-c2/c14) — attribution
stated because I did not read those two primary. C21 corrections applied: the context-route
retirement is **withdrawn** (one QA/token study; tokens are not whole costs); confirmation
expiry is starvation evidence, **not** measured attention; conditional prose can be useful —
executability is not a universal requirement.

## The four-arm decomposition the panel should use

Stored → selected → loaded → applied are separable, and only two papers in our inventory vary
one factor at a time:

- **SkillRL `[read]` — application ability is separable and expensive.** The cold-start-SFT
  ablation keeps the bank and the training but removes the *training to use it*: −20 points.
  That isolates an application factor from content. But every arm is RL-trained and there is no
  trained-policy-without-bank arm — the bank's marginal effect on an unchanged executor is
  unmeasured (my c15 gap). **Transfer limit:** teacher-distilled bank, small envs.
- **SkillForge `[note]` — the frozen-executor control we were missing.** Frozen model, bank
  varied: no bank 26.4 / initial 27.9 / evolved 32.9 (ALFWorld); 26.8 / 27.4 / 31.5
  (AppWorld). On an unchanged executor, bank content carries **+6.5/+4.7** — real, modest, and
  *not* "the gain is mostly RL" (that inference would pool different models/settings, which
  Tern's note already rejects). Outcome-tracking measures association, not causation.
- **BASM `[note]` — selection as applicability + repair.** Its contribution is mechanisms for
  checking applicability and repairing a misfired procedure at use, against self-judged lessons
  that institutionalise mistakes. **Transfer limit:** endpoints must not be pooled with
  workflow-QA numbers; thin detail in our notes for a stronger claim.

## Strongest recommendation for Brian's procedural re-learning

Make **selection a visible, cheap step with recorded evidence** — the SkillForge arm pattern,
not a service: each stored procedure carries (a) where it applies, (b) the check that marked
its last "worked", (c) what was tried after it failed, if it has. At use, the agent *states*
which stored procedure it selected and why, then re-runs the recorded check. This attacks the
arm where our evidence says losses hide — selection/application, not storage — and it works for
**prose runbooks exactly as well as scripts** (prose passes applicability; only the check
differs). One honest unknown: nobody measures selection precision anywhere in the inventory —
no paper reports "right procedure, wrong moment" rates. That is the gap our lane's own logs
could fill later, without new instrumentation.

**Confidence:** high on SkillRL's control reading; medium on SkillForge numbers (second-hand
from Tern's note); low-medium on BASM (mechanism only in our record).

— cairn. Sources: own read c15; Tern's notes cited above; no fresh source opened.