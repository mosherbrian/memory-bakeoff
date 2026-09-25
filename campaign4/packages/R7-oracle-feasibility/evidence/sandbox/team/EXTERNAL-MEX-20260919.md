# EXTERNAL — mex: a repo-local code graph plus a living Markdown wiki

**Filed** 2026-09-19 by Claude, from a link Brian supplied. **Class:** research
intake, unverified. **Nothing here has been run or reproduced by this project.**

**Source:** r/AIMemory, "My Claude Code kept rereading the same repo instead of
preserving what it learned…", posted by `DJIRNMAN`, 2 days before reading.
https://www.reddit.com/r/AIMemory/comments/1wjtloc/my_claude_code_kept_rereading_the_same_repo/
**Artifact:** https://github.com/mex-memory/mex — open source, v0.8.0, ~1,200
GitHub stars. Post is locked and archived; three comment threads exist.

## Why this one was filed as a card when the r/LocalLLaMA thread was not

It carries an artifact, stated numbers, a named baseline and an author-stated
limitation. The other carried one practitioner's habit. That is the difference
the intake bar should turn on — not the subreddit and not the star count.

## What it claims to be

The stated problem is the project's own M3: "coding agents keep rereading the
same repository every session, relearning the architecture, and then throwing
most of that knowledge away."

Two parts, deliberately separated:

- A **living Markdown wiki inside the repo**, written by agents as they work,
  holding architecture, conventions, decisions and patterns.
- A **deterministic local code graph** — Tree-sitter parsing into SQLite, no
  service, no embeddings. `mex graph scope "trace the authentication flow"`
  returns a neighbourhood of functions, callers, callees, imports and
  relationships rather than whole files.

The connection between them is the part worth attention: Markdown claims point
at exact code symbols, so when a function changes, moves or disappears, the tool
can name which prose is now suspect. Its own framing: "the code is the source of
truth, Markdown is the explanation, the graph keeps them connected."

Languages: TypeScript/TSX, JavaScript/JSX, Python, Rust.

## The numbers, as stated

Benchmarked **on the mex repository itself**, six retrieval tasks:

- 10.74x less returned context than `grep` top-3, about 90.7% smaller
- 100% expected-symbol recall
- 5/5 real-agent tasks completed correctly, 0/5 needed a fallback Read or Grep

## CAVEATS — read before citing any number above

1. **Self-run, self-selected, one repo.** The benchmark is the author's, on the
   author's own codebase, over six tasks. This is the same shape the
   KnowledgeDrift card already flagged as a field-wide pattern.
2. **"100% expected-symbol recall" is recall against symbols the author
   expected.** A recall figure is only as strong as the expectation set, and
   that set is not published in the post.
3. **The baseline is weak.** `grep` top-3 returns whole matching lines and
   files; returning less context than grep is close to definitional for any
   graph-scoped retriever. It establishes a floor, not a competitor.
4. **The author states the limitation themselves**, which is unusual and worth
   recording: "This is a small benchmark on one repo and task set, not a claim
   that mex universally cuts total agent token usage by 90%." We should hold
   them to that scope rather than the headline.
5. **Drift detection scores health, it does not prevent bad writes.** Asked in
   comments how LLM-generated wiki churn and hallucination are stopped from
   propagating, the author describes `mex check` / `mex sync`: twelve checkers,
   minus 5 per problem and minus 3 per warning, prompting a sync below a
   threshold. Those weights are unexplained and unvalidated, and the mechanism
   is detection after the fact, not prevention at write time.
6. **The graphify comparison is the author's own reverse-engineering**, and they
   explicitly decline to claim superiority: "i wouldnt claim that now, we have
   testing going on."

## Where it touches open questions

- **M3, redundant re-discovery.** This is the only external artifact seen so far
  that targets M3 directly. Its claim is a context-size reduction, not a
  rediscovery count, so it does not supply an M3 measurement — but it is a
  candidate intervention for one.
- **Staleness and supersession.** Symbol-linked prose gives a mechanical
  staleness signal that does not depend on an LLM judging its own notes. The
  bake-off has measured false supersession as a live failure; this is a
  different approach to the same hazard.
- **Deterministic beside probabilistic.** A second practitioner this week
  describing the same split - an exact-identity layer next to a retrieval layer.
  Two anecdotes are not evidence, but the convergence is worth noting.

## What would make it decidable

Run `mex graph scope` against this project's own corpus and compare returned
context and symbol recall to the existing BM25 and pi-lcm arms on the SAME
tasks. Local, no service, no API spend. That is a measurement this project can
make; the author's benchmark is not one we can cite.
