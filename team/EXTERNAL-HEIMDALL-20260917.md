# External: Heimdall — candidate discovery, 2026-09-17

**Found by Brian**, alongside the Agent Memory Atlas, from the daily report's
cited sources. New to this repo. **Source:** `github.com/ArihantDeva/heimdall`,
**MIT**, npm `@arihantdeva/heimdall` v0.2.0, 111 stars, 174 commits on main.

**Status: CANDIDATE DISCOVERY. It publishes no evaluation** — see the bottom.

## What it is

A CPU-only persistent memory system for coding agents, maintaining a ranked
knowledge graph across repositories. TypeScript/Node ≥22.5 plus Python and bash;
vendors Graft (Apache-2.0) and graphify (MIT). Integrates via MCP into Claude
Code, Pi, Codex, Cursor and Windsurf.

- **Stores:** a SQLite journal at `~/.heimdall/journal.db` — file metadata
  (hash, size, mtime, depth), symbol definitions from tree-sitter AST parsing,
  and cross-file call edges.
- **Retrieves:** hybrid ranked search over a per-repo code graph plus global
  `bge-m3` embeddings computed **on CPU**, with results **verified against the
  live filesystem** and labelled **STRONG / WEAK / REBUILT / STALE**.
- **Claims** *"zero token spend"* for indexing, *"CPU only — never an LLM
  call"*, and that *"ranked retrieval is trustworthy enough to act on"*.

## Why it is interesting to us, and it is not the ranking

**THE STALENESS LABEL IS THE IDEA.** It verifies a retrieved result against the
live filesystem at retrieval time and returns a confidence label rather than a
bare hit. Every engine we have measured returns records as if they were equally
current; the whole G2 supersession problem is that a stale record and a current
one are indistinguishable at the point of use. Heimdall's answer is to check at
read time and say which it is. Whether it works is unmeasured — but the DESIGN
answers the question our instrument keeps asking.

**Zero-token indexing is directly comparable to our cheapest arm.** bm25 beat
both memory engines in our own measurement, and bm25 is also free. Heimdall is a
richer free retriever - AST symbols and call edges rather than word overlap - and
it costs no model calls either. It belongs in the same bracket as our bm25
baseline, not in the bracket with Mem0 and claude-mem.

## Goal mapping

- **G2 supersession** — the STRONG/WEAK/REBUILT/STALE label is a supersession
  signal delivered at retrieval time. This is the most direct external attempt
  at G2 we have seen.
- **G3 invocation** — a ranked retriever with a verification step is an
  invocation design, not just a store.
- **Roadmap R-PF Gate F (adopt / compose / build)** — a candidate for the
  ADOPT column, and a plausible compose partner for the S7-2 bm25-behind-an-
  abstention-gate attempt.
- Advances **G1 and G4 not at all**, said plainly.

## What it lets us stop building

Possibly the retrieval-time staleness check we would otherwise design from
scratch for G2. "Possibly" is doing real work in that sentence — see below.

## What NOT to trust

- **IT PUBLISHES NO BENCHMARK NUMBERS AT ALL.** It names *"LongMemEval-S
  baseline 0.740"* as a **target, not a result**. So every claim about it is a
  design claim. This is the cleanest example in our register of a system to
  place in the vendor-only class with no measured entry.
- **"Trustworthy enough to act on" is an assertion with no instrument behind
  it.** That is precisely the sentence our whole project exists to test, and it
  arrives here unmeasured.
- **The evidence of it working is one machine.** *"~12,800 live nodes with a
  166-test suite"* on the author's own machine. A test suite measures the code,
  not the retrieval quality.
- **Claims are from a summariser reading the README**, not from our own read of
  the repo. Before any adoption, read the code at a pinned commit — which is
  exactly the method the Agent Memory Atlas card recommends.

## What this changes

1. **A candidate for the ADOPT column of Gate F**, which the S6-3 roadmap map
   says is the unmade decision. It is the first ADOPT candidate with a
   supersession story.
2. **A possible compose partner for S7-2.** That row puts bm25 behind pi-lcm's
   abstention gate; Heimdall's labelled output is a third arm worth costing
   before the sprint reaches it.
3. **Do not measure it yet.** It has no published number to check and no claim
   to falsify, so a run would produce our number against nothing. Read the code
   first, then decide whether a run is worth a slot.
