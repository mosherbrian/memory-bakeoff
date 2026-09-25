# EXTERNAL — Munder Difflin: a shipped multi-agent harness with cross-session memory

**Filed** 2026-09-20 by Claude, from a link Brian supplied. **Class:** research
intake, unverified. **Nothing here has been run by this project.** Filed for its
MEMORY design and its convergence with this fleet's architecture, not as a
memory-system candidate for the bake-off's scored lanes - it publishes no
benchmark at all.

**Artifact:** `github.com/chaitanyagiri/munder-difflin`, MIT (code; art assets
separately licensed), pre-release 0.4.6. API-read 2026-09-20:

    stars 7,701 | forks 1,011 | created 2026-05-31 | pushed 2026-09-17

## Why it is filed here

It is the first artifact this survey has turned up that is a RUNNING FLEET with
users rather than a benchmark or a library - and it arrived independently at
this fleet's architecture. That convergence is the finding; the stars are not.

| Munder Difflin | this fleet |
|---|---|
| runs real terminal CLIs as processes (node-pty/xterm.js) | agent-deck seats behind ACP wrappers |
| "Michael", the GOD agent: "assigns the work, routes the traffic, and escalates the few things that actually need you" | cairn as conductor, act-or-escalate; Tern as Director |
| "steer -> constrain -> stop ladder for agents that loop, storm errors, or blow their budget" | gate-batch caps, the derived Go ceiling, `fleet-spend-stop` |
| "Spend, scope and destructive operations come back to you" | the escalation rungs, Brian as terminal authority |
| twelve engines on existing subscriptions | Max plan, Codex Plus, Go pool, RouteLLM, local |

Four of those were paid for here across three campaigns. Someone reached the
same shape from scratch in four months.

## The memory design, in its own words

- **Storage:** "a local git repo of plain files". Each agent writes to its own
  `outbox/`; "the harness's router delivers into recipients' `inbox/`" - a
  single-committer design, explicitly to avoid git corruption.
- **What is written:** "Every agent keeps markdown memory that is mined into a
  shared, searchable palace."
- **Retrieval:** "a semantic recall index means agents remember across sessions
  and recall in milliseconds."
- **Growth control:** a "condensation" process so memory "doesn't grow forever."
- **The claim:** "Close the app, come back tomorrow, and they still know what
  they learned."

## What is interesting, and what is missing

**Interesting.** Markdown-first with a semantic index over it is the same split
two independent practitioners described this week - an exact-identity layer
beside a probabilistic one. And the single-committer router is a real answer to
a problem this fleet has hit directly: concurrent writers to one tree.

**Missing, and it is the thing this project exists to measure.** There is no
benchmark, no measurement, and - more pointedly - **no mechanism that decides
whether an agent's claim is true**. No gates, no independent verifier, no
computed done-state, no author/verifier independence. "Condensation" is
supersession by another name, and supersession is precisely where every engine
this project has measured fails: all engines co-returned superseded records
192/192, Perseus removed 48/48 stale records against Hindsight's 0/48, pi-lcm
returned the wrong newer entry in 22 of 33 distractor cases.

A system that condenses memory without measuring what condensation discards is
making the bet this project has been testing, without instrumenting it.

## Caveats

- Pre-release 0.4.6 by its own statement. No benchmarks published.
- Stars and forks measure adoption, not quality, and nothing here is measured.
- Official builds send anonymous usage events - "app opened, agent spawned,
  feature used" - explicitly "never prompts, code, file paths, or agent output".
  Opt-out via Settings, `DO_NOT_TRACK`, or building from source. Worth knowing
  before any trial, not a blocker.
- The memory description above is read from the README, not from the source.
  Verify before relying on any detail.

## What would make it decidable

Nothing about the app. The QUESTION it raises is ours already: **what does
condensation discard?** That is measurable on apparatus this project owns - the
frozen distractor set, the false-supersession baseline - and does not require
installing anything.

If it is ever worth a trial, the honest framing is not "does it work" but "does
its condensed memory still answer a question the uncondensed record could",
which is the door problem again, one layer up.
