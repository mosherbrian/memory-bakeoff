# Assay — second-driver spot-check: Intelligence Directive landscape numbers

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0 (public web)
**Thread:** Assay — second-driver re-derivations.
**Subject:** the headline numbers left unverified in
`team/CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §6 /
`team/ALICE-INTELLIGENCE-DIRECTIVE-SECONDCHECK.md` (Alice verified StreamMemBench,
MemSecBench, AMA-Agent).
**Verdict:** **all five checked here reproduce exactly from the primary abstracts.**

## Checked

| directive claim | primary source | verdict |
|---|---|---|
| Agent Zero Memory: **95.60% LongMemEval**, **93.60% LoCoMo** | [arXiv:2608.29606](https://arxiv.org/abs/2608.29606) abstract, 30 Aug 2026: "95.60% on LongMemEval and 93.60% on LoCoMo, improving … by +0.73 and +1.10 points" | **CONFIRMED exact** |
| LongMemEval-V2: **451 questions**, histories up to **500 trajectories / 115M tokens** | [arXiv:2605.12493](https://arxiv.org/abs/2605.12493) abstract: "451 manually curated questions"; "up to 500 trajectories and 115M tokens" | **CONFIRMED exact** |
| LME-V2 coding-agent context gatherer: **72.5%** with high latency | same: AgentRunbook-C "achieves the best performance with 72.5% average accuracy … coding agent based methods have high latency costs" | **CONFIRMED exact** |
| BEAM: up to **10M tokens**, **100 conversations**, **2,000 validated questions** | [arXiv:2510.27246](https://arxiv.org/abs/2510.27246) abstract: "long (up to 10M tokens) …"; "BEAM … 100 conversations and 2,000 validated questions" | **CONFIRMED exact** |

All are the authors' own reported figures; none is an independent replication.

## One comparability flag (worth attaching before any citation)

The directive lists Agent Zero's **95.60% on LongMemEval** and LME-V2's **72.5%
average accuracy** near each other, but they are different referents:

- Agent Zero is scored on **LongMemEval** (the original benchmark) under its own
  protocol/judge;
- LME-V2's 72.5% is **LongMemEval-V2**, a *different benchmark* (451 curated
  questions over environment-experience histories) under a **context-gathering**
  formulation, and the paper itself notes the coding-agent method's high latency.

So 95.60 and 72.5 must not be read as one leaderboard. This is the fleet's
recurring "one name, several referents" class (cf. the five "LongMemEval"
referents in the claims ledger) — bind each to its version and metric before
citation. The directive's own conclusion ("protocol-local until independently
reproduced under the bake-off harness") already covers this; this just names the
specific pair at risk.

## Sources

- [Agent Zero Memory (arXiv:2608.29606)](https://arxiv.org/abs/2608.29606)
- [LongMemEval-V2 (arXiv:2605.12493)](https://arxiv.org/abs/2605.12493)
- [BEAM / Beyond a Million Tokens (arXiv:2510.27246)](https://arxiv.org/abs/2510.27246)

## Limits

Abstract-level only; three papers opened, no PDF/table reads. The remaining
directive numbers (SWE-Gym 2.4K/11, the Aug-12 cost study, Memora) were not
checked. No repo or team file modified except this note and the RD log.

— **Assay** (`worker-glm-dsh2`).
