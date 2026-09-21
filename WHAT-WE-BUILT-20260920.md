# What we built

Written 2026-09-20. Everything here was checked against the running system on
that date, not recalled.

These documents live at the repository root, deliberately outside `team/`. The
indexer only scans `team/`, so writing them here does not add three documents
to the corpus whose composition we are currently measuring.

## The short version

The goal was a research fleet: several AI seats that run memory experiments
against each other, unattended, while Brian sleeps. The science is a bake-off
between memory systems. The machinery is everything built to make a fleet of
language models produce trustworthy evidence without a human watching.

The science produced real results. The machinery produced more machinery.

## The research, which is the point

Twenty experiment directories, eleven with a signed verdict. Eleven external
candidate cards. Six answer pages. The findings that survived independent
verification:

| Question | Answer | Evidence |
|---|---|---|
| Does memory improve real work? | Not established. Every experiment so far measures retrieval and delivery, never task outcome. | all verdicts |
| Can BM25 decline an irrelevant question? | The corpus-coverage rule rejects 5/5 irrelevant queries and loses 0/5 useful ones, on small constructed sets. Earlier filter and margin rules failed. | `S11-ABSTAIN3` |
| Does BM25 plus pi-lcm beat BM25 alone? | No. Set-F1 stays at 0.60. | `S7-COMPOSE` |
| Does the key-equality protection layer help? | No. It makes false replacement worse: 22/33 becomes 33/33. | `S11-LAYER-HIST` |
| Is the failure to decline specific to BM25? | No. Five implementations all score 0/40 on the external benchmark. | `S7-KD-WORLDS`, `S10-KD-CROSS` |
| Can competing text push useful evidence out? | Yes. At 600 characters of query-adjacent pressure, evidence presence falls from 100% to 20%. | `S9-DOOR-RUNG2` |

Two of those are negative results about things we built ourselves, published
against our own interest. That is the part worth keeping.

The corpus: 827 documents labelled by a local model, 1,519 role labels,
finished 2026-09-20 18:15 for no money. The role distribution is not yet
quotable, because the control that would show whether the labeller is reading
the documents or guessing from the filenames has not been run.

## The steampunk mechanics

This is the honest name for it. What follows is a real inventory, not a
caricature.

**79 executable scripts** in `~/.config/agent-deck`, plus about 100 more
backup and retired copies in the same directory.

**A 2,388-line bash poller**, in two copies that have diverged from each other
at least once.

**A 3,857-line Python web server** for the conductor chat interface.

**A 1,470-line status computer** and a 1,379-line billing-rules engine.

**112 checker scripts** in the research repository, plus 22 per-experiment
gates.

**Roughly 20 systemd timers** that belong to the fleet, on top of another 25
belonging to the household assistant that shares the machine.

**18 registered seats**, of which 5 were running today.

### The contraptions, and what each was built to prevent

Each of these exists because something went wrong once. That is both the
justification and the diagnosis.

- **The dispatch ledger** — an append-only file recording which seat was woken
  to produce which row. It exists because authorship used to be parsed out of
  a sentence an agent wrote about itself, which let a seat verify its own work.
- **Computed row state** — a machine column in the board, written only by the
  poller from file existence and exit codes. It exists because a finished row
  stayed open forever for want of the literal word `done:`.
- **The gate pair** — one seat writes a test from the row text alone, a
  different seat verifies it. It exists because on Sprint 6 the same seat wrote
  both the work and the test that proved it.
- **The escalation ledger** — append-only, with acknowledgements appended
  rather than edited. Built today, after the discovery that nothing read the
  alarms.
- **The stall detector** — asks one question, "has any work output been written
  recently", and deliberately knows nothing about gates, seats or quotas, so it
  has no predicate to get wrong. Built today.
- **The overseer** — a Claude session subscribed to the escalation channel that
  fixes what it can and acknowledges what it did. Built today. Within five
  minutes of starting it found and fixed a defect in my own repair from two
  hours earlier.
- **The quota ladder** — `fleet-failover`, `fleet-quota`, `fleet-codex-quota`,
  `fleet-credits`, `fleet-spend-stop`, `go-budget`. Six components to answer
  "can this seat afford to run".
- **The window** — the fleet raised and lowered on a timer to match a free
  promotional period for one model provider. That promotion expires today.

### What it cost to run

Today's spend, from the live budget tool: **$0.51 of a $2.58 daily
allowance**, with $33.35 remaining of $60 over eleven days. The fleet is cheap
now. It was not always: a 13-seat configuration measured on 2026-09-15 spent
$21.65 in a day and produced three lines of product code, with 58% of that
going to seats polling to ask whether anything had changed.

The token meter has recorded **29.6 million input tokens, 25.1 million output
tokens and 6.0 billion cache reads**. It has recorded **$0.00**, because the
dollar field was never populated and the meter stopped writing on 2026-09-14.
Cost discipline runs entirely through a separate tool.

## What today looked like

Thirty escalations raised, all on one day, because the ledger was built that
morning. Twenty defects found and fixed. Eight of the twenty were found because
Brian asked a question. Four were found by an automatic check. Four were found
by a reviewing seat. Four I found while reading nearby code.

Zero research rows completed.

## The honest summary

What works: the evidence discipline. Negative results get published. A verdict
by the author does not count. A gate the verifier rejected gets rewritten. The
corpus labelling ran 827 documents to completion without supervision, for free.

What does not: the coordination layer around that discipline has grown faster
than the research it protects. Twenty defects in one day, in eight mechanical
families, none of which the existing alarms could detect, because every alarm
tests a named condition and these were all failures of the instruments
themselves.
