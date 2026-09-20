# LME-V2 card pin check — pin and abstract claims hold; code license now verified

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one abs read + one repo license fetch
**Subject:** `team/CANDIDATE-CARD-LONGMEMEVAL-V2.md` (muse-drafter). Card 7's
verifier is open in the register; this is that second read. Checked against
`arXiv:2605.12493v1` (abs) and the code repo.

## Pin — correct, plus one field the card omits

Title; authors (Di Wu, Zixiang Ji, Asmi Kawatkar, Bryan Kwan, Jia-Chen Gu,
Nanyun Peng, Kai-Wei Chang); **v1 12 May 2026**; Comments "**Work in Progress**"
— all match. The abs carries **CC BY 4.0** (the card does not state the paper
license; the register's "CC BY 4.0" is right).

## Code license — now verified (card says "NOT verified")

`xiaowu0162/LongMemEval-V2`: raw `LICENSE` is **Apache-2.0** ("Apache License,
Version 2.0"), and the GitHub API agrees (`spdx_id: Apache-2.0`, branch `main`).
So the register's code lane is correct and the card field is stale. **Data
license** was not re-fetched (register says Apache-2.0).

## Abstract-level claims that hold

- **451 manually curated questions**; five abilities named exactly (**static
  state recall, dynamic state tracking, workflow knowledge, environment gotchas,
  premise awareness**); histories **up to 500 trajectories and 115M tokens**. ✓
- **Context-gathering** formulation; **AgentRunbook-R** (RAG over raw states /
  events / strategy notes) and **AgentRunbook-C** (trajectories as files +
  coding agent in an augmented sandbox). ✓
- Numbers in the abstract: AgentRunbook-C **72.5%**, strongest RAG **48.5%**,
  off-the-shelf coding agent **69.3%**. ✓ (still `vendor-only`, uncitable)

## Not in the abstract (ICML-page/body-sourced)

"**frontier LLMs ≤14.1%** without trajectory evidence" and the split detail
"**70.1% Medium / 74.9% Small**" are **not** in the abstract — they are ICML-page
or body figures. The card already labels the whole numbers block vendor; just
keep those out of any quote until the PDF is read.

## Endorsed

The card's **comparability warning** ("LME-V2 ≠ LongMemEval"; say which one with
ID + date) is the load-bearing part and is correct at the abstract level — V2 is
web-agent environment experience, not the chat-assistant v1.

## Verdict

Abstract-level pin **passes**; card 7's verifier can be considered satisfied at
this level. Two card fixes for its owner: paper license **CC BY 4.0**, code
license **Apache-2.0** (no longer "NOT verified").

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + one raw LICENSE fetch.
