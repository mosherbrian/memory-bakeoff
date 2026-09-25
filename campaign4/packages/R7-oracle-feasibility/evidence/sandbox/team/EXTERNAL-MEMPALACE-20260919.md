# EXTERNAL — MemPalace: verbatim local memory with a bitemporal graph

**Filed** 2026-09-19 by Claude, from a link Brian supplied. **Class:** research
intake, unverified. **Nothing here has been run or reproduced by this project.**

**Artifact:** https://github.com/mempalace/mempalace — MIT, Python. Repository
figures read from the GitHub API on 2026-09-19, not from the README:

    stars 59,162 | forks 7,563 | open issues 742
    created 2026-04-05 | last push 2026-09-18 | not archived

Five months old and the most adopted artifact this project has surveyed. That
is an adoption fact, not a quality one, and is recorded as such.

## What it is

Conversation history stored **verbatim** - explicitly no summarisation or
paraphrase - with semantic retrieval over it. Hierarchy of "wings" (people and
projects), "rooms" (topics) and "drawers" (original content), so searches are
scoped rather than run against a flat corpus. Pluggable backends: ChromaDB by
default and embedded, SQLite with exact NumPy vectors, a Rust-native vector
search, or Milvus / Qdrant / pgvector as servers.

Also ships a **temporal entity-relationship knowledge graph with validity
windows**, and 45 MCP tools. Auto-save hooks for Claude Code, Codex CLI and
Cursor. Local-first: "nothing leaves your machine unless you opt in."

## Where it touches open axes here

**1. Effective time.** Gen75 closed the temporal line with Perseus keeping
transaction-time history while its effective-time capability was recorded
NOT_DEMONSTRABLE - the store had no caller-settable validity coordinate. A
system advertising validity windows is a direct candidate on that axis, and it
is the only one surveyed that claims one.

**2. Verbatim against distillation.** This project's measured failures cluster
in what happens to a record after it is written - false supersession, stale
records co-returned, a correction that retires more than it should. Storing the
original and never rewriting it is the opposite bet, and it is testable.

**3. It is in Brian's harness.** Claude Code and Codex CLI hooks, not a research
prototype needing an adapter written for it.

## THE CAVEAT THAT MATTERS MOST HERE

Every headline number is **retrieval recall**:

    LongMemEval  R@5  96.6% raw, no LLM, no API key
                 R@5  98.4% hybrid v4, held-out 450q, tuned on 50 dev questions
    LoCoMo       R@10 60.3% no rerank, 88.9% hybrid v5
    ConvoMem     92.9% average recall
    MemBench     R@5  80.3%

This project has measured TWICE that retrieval recall is not the binding
constraint. S9-DOOR-RUNG2: competing text displaces useful evidence at a
600-character limit. Corroborated independently on 2026-09-19 by adebench at a
2,400-character budget on a different corpus. R@5 says the right chunk was in
the top five; it says nothing about whether it survived composition and the cut
into the model's context.

So the most adopted system in the space reports on the axis we have already
established is not decisive. That is not a defect in MemPalace - it is the gap
this project is unusually equipped to measure.

## Other caveats

- **They flag their own overfitting**, which is worth recording as a credit:
  "the last 0.6% was reached by inspecting specific wrong answers", self-labelled
  as teaching to test.
- **They decline side-by-side comparisons** against Mem0, Mastra, Hindsight,
  Supermemory and Zep, by stated choice. Honest about cherry-picking; also means
  no competitor context.
- 98.4% was tuned on a 50-question dev set. Small.
- 742 open issues on a five-month-old project.
- 45 MCP tools is a large surface for a fleet that has had MCP reliability
  trouble.
- Termux unsupported; GPU image x86_64 only; first embedding download is ~80 MB,
  or ~300 MB multilingual, and needs network.

## What would make it decidable

Not a re-run of its benchmarks - those are on the axis we have already
discounted, and reproduction commands and full result files are committed, so
re-deriving them teaches us nothing new.

**Measure it at the door.** adebench's author asked on 2026-09-19 for "a third
system measured the same way", and stated the adapter is one class. MemPalace
is a 59k-star system with hooks into the harness Brian actually uses, and
nobody has measured what it DELIVERS under a budget and under competing-context
pressure. That is a measurement no one else is making, on the most adopted
system in the field, using an instrument this project has already validated
against its own finding.

Local, no service required for the raw path, $0. Whether it is worth a row is
the Director's, and it belongs inside the agenda audit rather than ahead of it.
