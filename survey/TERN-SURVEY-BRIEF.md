# Tern: new brief (2026-09-26) - read this first, then CHARTER-FIELD-SURVEY.md

You now lead the agent-memory field survey. You are not directing campaign4 packages any more.

## Your job
Build and keep an expert position on agent memory: broad (the whole field), critical (solid results vs hype), applied (what fits Brian: Claude Code, Pi, local models, admin/rollout/model-testing work; the team at work second). Think like a senior researcher writing a field review and a recommendation, not like a release auditor.

## How to think (the change)
- Breadth first. Read widely: papers, system docs, benchmarks, our own past results (bake-off, KnowledgeDrift ranking, research cards, R61/R68). Form views early, state confidence, revise.
- Rigor in proportion to the stakes. A landscape claim needs a source and a confidence level, not a checksum. Save hard proof for claims that will drive a rollout.
- Every cycle must change the memo or the register, or say plainly "no change, because...".
- No repair chains: fix a blocking tool once; after two fix steps without a result, stop and tell Claude.
- Critique asks "does this change the conclusion?" If not, log it and move on.
- Opinions are welcome. "Probably X (medium confidence) because A, B" beats "undetermined pending qualification".

## Outputs (all under ~/memory-bake-off/survey/)
- COVERAGE.md: one current table of explored and remaining systems, papers, benchmarks and native facilities, with status, cycle, note and takeaway; update within every cycle and end with prioritized next up. Preserve unresolved identities and reasoned deferrals from the roadmap/Gen125 intake.
- FIELD-MAP.md: taxonomy -> systems -> key results/benchmarks (known flaws) -> open problems; source + confidence per entry.
- POSITION-MEMO.md: one page; ranked bets for Brian; overrated things; frontier; what would change each position.
- QUESTIONS.md: open questions ranked by decision value x uncertainty / cost; each tagged literature / cheap probe / needs proof.
- PROBES.md: small experiments -> question -> memo change.
- READOUT.md: rewritten each cycle end, one screen, plain language: what changed, top 3 open questions, next step, confidence shifts. Then run: `/var/home/bmosher/.config/agent-deck/notify-claude <<< "[survey] cycle N readout updated: <one line>"`.

## Resources and limits
- Corvid can act as critic on request (grade flaws by whether they change a conclusion). Kiln/cairn can run cheap probes. Campaign4 machinery (R71/R72) is parked for rare Prove requests, which need Brian's approval.
- Model calls for probes: small and cheap; Go pool is shared ($60/month, no paid overflow).
- Deadlines: first POSITION-MEMO by 2026-09-29; stable position by 2026-10-14.

## First cycle (start now)
1. Inventory what we already have (bake-off results, research cards, external corpora recommendation, KnowledgeDrift v2, campaign4 R61/R68 findings) - skim, do not re-verify.
2. Sketch FIELD-MAP.md v0 from that plus your own knowledge of the literature; mark gaps.
3. Write POSITION-MEMO.md v0 (low confidence is fine) and QUESTIONS.md v0.
4. Write READOUT.md and notify Claude.


**Sponsor deliverable clarification,26September2026:** by29September deliver ONE one-page recommended design for Brian's stack, named components/contracts/operational owner/how-to-test, one named first pilot for approval, confidence and non-blocking open questions. Coherent design is the output shape, not a gate on every step. Actor-owned upkeep is the baseline. No exhaustive audit prerequisite; caveats matter only when they change the recommendation. Laya probe complete:46labels, majority+keyword baselines, one run; no rerun/framework/review rounds. See latest paragraphs of inputs/BRIAN-PRINCIPLES.md.
