# EXTERNAL — cheap typed classifiers as a keep/drop gate: two applications

**Filed** 2026-09-19 by Claude, from links Brian supplied. **Class:** research
intake, unverified. **Nothing here has been run by this project.** One card for
two artifacts because they are the SAME MECHANISM pointed at different targets,
and filing them apart would hide that.

## The mechanism

A small, cheap, non-generative model answers a typed question about each of many
items in parallel - "is this disposable?", "is this memory stale?" - and returns
a calibrated probability rather than prose. That makes it affordable to ask the
question about EVERY item on every event, which is the thing a normal LLM
cannot pay for.

Both artifacts below sit on **Jev** (TypeSafe, closed, commercial, launched
2026-09-15; $0.042/1M input, output free; 64k per request; text only). The
mechanism does not require Jev. **Laya** (github.com/NandhaKishorM/laya, Apache
2.0, ModernBERT-large 421M, runs local on CPU) implements the same three
primitives - `choice`, `score`, `noul` - and publishes calibration: ECE 0.213
raw, 0.081 after temperature fitting. That matters here because it removes both
the closed dependency and the egress.

## Application 1 — dropping tool output before it reaches context

**`github.com/tamaratran/fast-jev-compaction`** — MIT, TypeScript, **4,415
stars, created 2026-09-17** (API-read 2026-09-19). Posted to r/ClaudeCode as
"instant compaction", which is wrong and the author concedes it in the thread:
it does not compact conversation text. It is a PostToolUse hook that filters
large Bash output before it enters context.

Read of the source by a commenter, recorded as second-hand:

- chunks the output, asks Jev per chunk whether it is disposable, reassembles
  the survivors; `noulAnswer` extracts the probability
- **nothing is destroyed** - full text is archived and replaced with
  `[... trimmed N lines; full output: <path> (Read or grep it if needed)]`
- **hard-protected line classes** regardless of score - errors, pytest
  summaries, docs - via `isProtectedLine`
- a THRESHOLD, not a verdict: `MAX_DISPOSABLE_KEEP_PROBABILITY = 0.1`
- **goal-aware**: recent transcript turns are fed into the scoring
- **`looksSecret` gate** - never archives output that looks like a credential
- `evals/` runs matched A/B trials on Harbor/Terminal-Bench plus retention
  cohorts; 33 test files

## Application 2 — un-remembering, on the same idea

**`github.com/chopratejas/invalidate`** — Apache 2.0, Python, **13 stars,
created 2026-09-19**, one day old. By the author of Headroom
(github.com/headroomlabs-ai/headroom, **73,131 stars**, API-read — the post's
"70k+" understates it), so a credible builder, but this is their own words a
project to "play around a bit with Jev". No benchmarks.

Its claim, which is OUR most-measured failure stated in plain terms:

> "When you use memory solutions like Letta, Zep, Mem0 - they cannot unremember
> things easily, they will write new memories... The reason it was hard is: any
> event had to go look at similar older memories and update them. With Jev it
> is possible to check ALL memories on each event, cheap + fast. We do not
> delete them - we ask questions: is this old memory stale? Should it be
> updated? Reinforced?"

## Why this lands on an open question here

Q4 is open: does pi-lcm need protection against false supersession. What this
project has measured on that axis:

- every engine co-returned superseded records, 192/192 observations
- supersession mechanisms are incommensurable - Perseus removed 48/48 stale
  records, Hindsight 0/48, AgentMemory 12/48
- AgentMemory's mechanism is first-match-wins Jaccard > 0.7, which is crude
  precisely BECAUSE checking everything was unaffordable
- pi-lcm returned the wrong newer entry in 22 of 33 distractor cases

**The cost argument is the contribution, not the tool.** Supersession is crude
across the field because re-examining the whole store on every write costs too
much with a generative model. A cheap calibrated classifier changes that
arithmetic. That is a mechanism for an open question rather than another
benchmark, and it is the first such thing this survey has turned up.

## Caveats

- `invalidate` is ONE DAY OLD, 13 stars, no benchmarks, flaired Promotion, four
  upvotes, zero comments. A sketch by a credible person. Do not cite it as a
  result.
- The pruner's design is read second-hand from a comment, not from the source.
  Verify before relying on any detail above.
- **Jev is closed and sends every item off the machine.** One commenter's
  employer refused it after reading the terms. An unsupported "it's malware"
  claim also appears in the thread and should be disregarded as such.
- The pruner's post title is wrong; several commenters caught it. 352 up, 94
  down, much of the dissent about the title rather than the tool.
- Jev's own benchmark figures are agreement with two large reasoning models,
  not ground truth. Laya's comparison against Jev is Laya's own, against Jev's
  published number, not a head-to-head.
- Laya degrades badly past ~20 options - Banking77 0.425 against Jev's 0.870 -
  so the mechanism suits small typed questions, not large label spaces.

## What would make it decidable here

Do not adopt either tool. Test the MECHANISM on the axis we already measure:
take the frozen distractor set where pi-lcm returned the wrong newer entry in
22 of 33 cases, and ask a local calibrated classifier, per stored record, "is
this record superseded by the new one?" Compare against the 22/33 baseline and
against AgentMemory's Jaccard rule. Local, Apache 2.0, no egress, $0.

That is a measurement of the idea rather than an integration of someone's
one-day-old repo, and it uses a baseline this project already owns.

## Separately, and worth Brian's own attention

A commenter reading the Claude Code binary reports built-in precomputed
background compaction behind experiment gates - `tengu_sepia_moth` with a
`precomputeCompactionEnabled` setting, and `tengu_amber_packet` controlling
whether results are saved for a later `/resume`. Unverified, one person's read
of a minified binary, but directly on top of pi-lcm's eager-compaction work and
cheap to check on a local install.

---

## UPDATE 2026-09-19 — a 287-project roundup, and what survives its provenance

**Source:** r/LLMDevs, `chenrongwei`, "I reviewed 287 open-source Jev projects"
https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/
Directory: `github.com/logicrw/awesome-jev-projects`. 111 up, 29 down.

**READ THE PROVENANCE FIRST.** The post is very likely AI-written promotion,
and the thread says so: *"the number of Jev posts I'm seeing are increasingly
looking and reading like ads"*, *"this specific post is slop"*, *"This Jev shit
is being astroturfed so hard."* The sharpest catch is `radarsat1`'s - the post
claims to have source-reviewed 287 projects in two days, and opens with "Jev is
rarely the thing writing code", which `Smallpaul` answers with *"Rarely??? Show
me a single example of it doing any of those things."* Treat the roundup as a
catalogue, never as a review.

Two entries in it are nonetheless worth naming, because they are the same
mechanism this card is about, pointed at things this project already builds:

- **Winnow** — "a context garbage collector for coding agents. When Read, Bash
  or Grep dumps a lot of content into the context window, Jev judges which
  pieces are actually relevant to the current task." The sibling of
  fast-jev-compaction, and the same keep/drop gate.
- **Canny** — "tries to stop coding agents from claiming they're done when the
  evidence says otherwise. It looks at tool output, diffs and test results, then
  judges whether the agent's completion claim is actually supported."

**Canny is this project's own discipline, mechanised differently.** Everything
in the iteration-3 loop exists because `done:` is a claim and `VERIFIED` is a
claim: computed DONE from a declared check's exit code, the append-only dispatch
ledger so authorship is a fact rather than prose, `check_answer_provenance.py`.
Our referee is DETERMINISTIC - a file exists, a checker exits 0, a verdict's
seat differs from the ledger's author. Canny's is a calibrated classifier
judging whether evidence supports a claim.

Those are different instruments for one job, and the difference is the
interesting part: ours cannot be fooled but also cannot read, and only answers
questions we thought to declare a check for. A classifier referee could judge
claims we never anticipated, and can be wrong. Neither replaces the other. The
roundup's own framing - *"agents increasingly need lightweight referees inside
their loops"* - is a conclusion this project reached independently and paid for
in three campaigns.

**One critique from the thread worth keeping**, `hellomistershifty` on the MCP
wrappers: *"the agent already needs to construct the input and pose the
question, so it's already spending more output tokens to ask a dumber model than
if it just answered itself."* That is right, and it sharpens where the mechanism
pays: when CODE poses the question inside a loop - a hook, a gate, a sweep - not
when a model decides to consult a classifier. Both the pruner and `invalidate`
are the first kind. An MCP tool is the second.

---

## UPDATE 2026-09-20 — an independent benchmark, and evidence against the pitch

**Source:** https://latentnode.pages.dev/articles/typed-decisions, read 2026-09-20,
link supplied by Brian. **No individual author is credited**; the site carries a
GitHub sponsorship link. States are synthetic, not drawn from real systems.
Treat the numbers as one unnamed party's benchmark, not as a result.

    input-blind baseline   0.470
    22M encoder            0.587   22 ms/case
    149M ModernBERT        0.646   349 ms/case
    Jev                    0.727   710 ms/case
    stated ceiling         0.704
    teacher vs gold        73.5% correct
    400 cases, 2,000 decisions across four workflows

### The calibration figure, which is the part that bears on this card

    KL divergence   149M frozen encoder 0.223   |   Jev 1.442
    Jev expected calibration error              |   0.144

**CORRECTED 2026-09-20, Director's wording.** The first version of this section
called the figures "evidence against" Jev's confidence-gating pitch. That
overreaches, and the reason is worth keeping: KL divergence and ECE measure
different properties, and NEITHER measures whether abstaining at a confidence
threshold improves the accuracy of the answers you keep. That is a
risk-versus-coverage question, evaluated against the actual gating confidence,
and nobody has run it. The honest statement is:

> An external, unreplicated synthetic evaluation reports worse
> probability-distribution fit for Jev than ModernBERT. This raises a
> calibration concern; it does not directly evaluate Jev's proposed
> confidence-gating policy.

Also corrected: anonymity and a sponsorship link warrant scrutiny, not exclusion
from citation. Attribute the report, keep its limitations attached, and do not
treat its numbers as independently established. The Director could not reach the
article page; the site's own summary corroborates the KL comparison.

It still bears on both applications above, as a concern rather than a finding.
`invalidate` asks "is this memory stale?" and acts on the answer; the pruner
drops a chunk below `MAX_DISPOSABLE_KEEP_PROBABILITY = 0.1`. Both are threshold
decisions on a probability, so calibration is the property they depend on - and
whether a threshold actually helps is the unrun risk-versus-coverage
measurement, not the KL number. **Laya publishes ECE 0.213 raw and 0.081 after
temperature fitting**, which at least states the property on the same axis.

### Two numbers that do not sit right, recorded rather than resolved

- Jev's 0.727 is ABOVE the article's own stated ceiling of 0.704.
- The teacher is 73.5% correct against gold, so any score above that is
  agreement with a partly wrong teacher rather than accuracy.

The same shape appeared in Laya's claim to "clear the 0.735 teacher ceiling".
Nobody in this literature explains it. Do not cite a headline from any of these
comparisons without reading how its gold was made.

### The methodological point, which is worth more than the ranking

The article runs an **input-blind baseline** - scoring the task while ignoring
the input, to establish what the label prior alone buys. 0.470 of 0.727. Without
that line a ranking cannot separate skill from prior, and nothing else surveyed
this week runs one.

That applies directly to this project's own R&D index: its role distribution is
dominated by `verification` (42 of 60, then 17 of 20), which is exactly the
shape a prior-driven labeller produces. Verified quotes do not rule it out -
provenance and prior-exploitation are orthogonal. The control is recorded here
because the lesson travels further than the benchmark: **a classifier result
without an input-blind baseline is not interpretable**, ours included.

### Apparatus honesty, worth crediting

The author found and fixed two bugs in the library under test - CLS token
pooling, which moved the score from 0.477 to 0.565, and hardcoded weights that
ignored configuration. A 0.088 swing from one pooling defect is a useful
reminder of how much apparatus moves these numbers.

---

## UPDATE 2026-09-20 — provenance on Laya, and one caveat that covers everything above

**Source:** r/reinforcementlearning, `Nandakishor_ml`, "I literally build the
jev architecture one year back and made it open-sourced", 333 up, 41 comments.
https://www.reddit.com/r/reinforcementlearning/comments/1wihdun/i_literally_build_the_jev_architecture_one_year/

**IT IS THE SAME AUTHOR AS LAYA.** Checked against the GitHub API rather than
inferred from the handle: `github.com/NandhaKishorM` is "Nandakishor", CEO of
ConvAI Innovations, 85 repos - the owner of `NandhaKishorM/laya`, the open-weight
model this card recommends as the local alternative to Jev.

He posts claiming prior art over Jev, citing arXiv 2503.23303 (March 2025) and
2510.01237 (September 2025), a HuggingFace model and a dataset.

**Why that matters here and how far it goes.** Laya's headline is a
SELF-PUBLISHED comparison against Jev - 0.766 to Jev's published 0.727 - and
there is now a documented motive attached to it. Treat it as a claim from an
interested party.

It is not disqualifying, and the card should not pretend otherwise. The weights
are Apache 2.0, the calibration figures are published rather than asserted, and
the stated limitations are unusually candid - a seller does not volunteer that
their model collapses to 0.425 against Jev's 0.870 on Banking77. Scrutiny, not
exclusion; the same standard applied to the anonymous benchmark above.

### The thread's rebuttals are better than its claim, and OP conceded

`Blahblahblakha`, on the two papers:

> "SalesRLAgent is a PPO policy on top of OpenAI embeddings that outputs a
> single conversion probability for one domain. Jev fills arbitrary typed
> schemas (multiple fields, up to 255 options each) in one pass, with a new
> training objective aimed specifically at calibration... Your September paper
> is a router that estimates uncertainty before sending a query to a normal LLM.
> It is not a non-autoregressive decision model... 'Output a calibrated
> probability over known options instead of generating text' isn't something
> either of you invented. Classifiers have done that forever... Same goal isn't
> the same architecture."

And `JustOneAvailableName`: "The breakthrough is that they made it work well,
not that they did RL on an encoder." OP's reply to the first was "Yess."

The useful discipline in that, independent of the dispute: **a shared goal is
not a shared architecture**, and calibrated probabilities over bounded options
are decades old. Nothing in this card should be written as though the mechanism
is new. What is new is that it became cheap enough to run on every item.

### THE CAVEAT THAT COVERS EVERY COMPARISON IN THIS CARD

**Nobody has published Jev's method.** No technical paper, no open weights, no
dataset; RLCD is named and not described. So every Jev comparison recorded
above - Laya's 0.766, the latentnode benchmark's 0.727 against a stated 0.704
ceiling, the roundup's speed figures - measures against a black box whose
training data and gold construction cannot be examined.

That is the single reason none of the numbers in this card should enter an
answer page. They are leads for our own measurement, which is the test this
card already proposes: run the mechanism against the frozen distractor set where
pi-lcm returned the wrong newer entry in 22 of 33 cases, locally, and compare to
a baseline this project owns.

---

## UPDATE 2026-09-20 — the first MEASURED test of the gating claim, and it fails

**Source:** r/Rag, `Willgax_`, "Early access to TypeSafe's Jev + IBM's STAIR
paper: experiment 1 of 3 on killing RAG hallucination".
https://www.reddit.com/r/Rag/comments/1wlavqy/early_access_to_typesafes_jev_ibms_stair_paper/
**Data and code open:** `github.com/aryanchauhanoffical/no-hallucination`, MIT,
created 2026-09-20, with per-question data and raw API responses.

SQuAD 2.0, 150 questions, 50 unanswerable. Stack: BM25 + bge-small fused,
MiniLM cross-encoder, gemini-3.5-flash-lite generating a verbatim quote that is
string-checked against the source; a failed check becomes NOT_FOUND.

    setup                              correct  hallucinated  wrongly refused
    baseline, no Jev                    87.3%      5.3%           7.3%
    + Jev "is the answer here?" (0.7)   85.3%      5.3%           9.3%
    + Jev citation check (0.8)          86.7%      5.3%           8.0%
    + Jev pairwise re-ranking           90.0%      6.0%           4.0%
    Jev ToC routing, greedy             72.7%      3.3%          24.0%

### The finding

> "The Jev checkers removed zero hallucinations. On all 8 remaining errors, Jev
> agreed with the wrong answer at 0.82 to 1.0 confidence... the checker reads
> them the way the generator does."

This is the closest thing yet to the risk-versus-coverage evaluation the
Director said the gating claim needs. Two gating configurations both left
hallucination at exactly 5.3% and COST correct answers - 87.3% to 85.3% and
86.7% - by refusing answers that were right. **High confidence on wrong answers
is worse than no confidence**, because it is acted upon.

The mechanism named for it matters more than the number: a checker built the
same way as the generator SHARES ITS ERRORS. Independence is a property of the
error, not of the call.

### What actually worked, and why it should be familiar

> "Quote-forcing plus a plain string check is what held hallucination at 5.3%.
> No model needed."

That is this project's own stage-one design, found independently. Our labeller
must return a verbatim quote and the harness string-checks it against the file;
every apparent fabrication today turned out to be a normalisation or encoding
defect on OUR side, and the check is what made that distinguishable. An
independent party measured the same structure on a different task and reached
the same conclusion: **the mechanical check does the work, not the model.**

### The warning this carries for our own proposed use

This card and the R&D index work both proposed a calibrated classifier as a
TRIAGE layer - score each extracted role/quote pair, send the low-confidence
ones for human review. This result says that can fail silently in a specific
way: if the classifier reads a document the way the labeller did, its
low-confidence set will not be the wrong records. It would produce a
confident-looking triage that misses exactly the errors a human was needed for.

Any such triage must be validated against ADJUDICATED errors before it is
trusted to allocate review - not against the extractor's own output.

### Caveats, most stated by the author

- 150 questions, one generator, one judge. A 3-point difference is about five
  questions; none of the deltas above are separable at that n.
- The author had EARLY ACCESS from TypeSafe. That is a relationship, and it
  cuts both ways: they published a negative result about the model they were
  given access to, which is the opposite of what an interested party does.
- ToC routing at 69% section recall against 96% for hybrid search is NOT a fair
  test of IBM's STAIR (arXiv 2609.03874, reporting 82.6% Recall@1 against 59.5%
  for BM25) - Wikipedia is a two-level hierarchy. The author says so and runs
  experiment 2 on textbooks.
- Jev pairwise re-ranking was the one gain: +2.7 points and 98% section recall.
  Re-ranking is a different job from gating, and this card should not treat
  evidence against the second as evidence against the first.
