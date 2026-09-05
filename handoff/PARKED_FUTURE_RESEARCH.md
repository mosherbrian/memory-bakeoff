# Parked future-research notes

Questions deliberately deferred. **Nothing here changes the current round's plan.**
A note is parked so it survives subsequent generations without competing with the
work in flight; it is picked up only when a generation explicitly opens it.

---

## P1 — Structured operational state vs accumulated conversational history

**Status:** PARKED. **Raised by:** Brian, 2026-09-05, during Round 3 (Gen96).
**Effect on the current round:** NONE. Round 3 remains interference/scale,
unchanged, as designed in Gen95 and Gen96.

### The external evidence, attributed

Brian revisited **SKILL.state (arXiv:2608.26263v3)**. Its long-horizon
experiments are cited as strong external evidence that **validated structured
execution state can outperform accumulated, sliding-window or compressed
conversational history** — reported as **~0.94 accuracy at both 100 and 200
steps** in the cited experiments.

**This is recorded as a citation, not as a result of ours.** The bake-off has
**not** replicated SKILL.state, has not run its fixtures, and makes no claim
about those numbers. They are here because they motivate the question, and they
are labelled so a later reader cannot mistake them for something this repository
measured.

### The independent overlap that makes it worth testing here

Earlier **Pi quality-gate** work independently exercised parts of the same
architecture, without reference to that paper:

- harness-owned **canonical state**;
- explicit **provenance** on every claim;
- **supersession** and current-truth handling;
- state **mechanically composed from measured evidence** rather than from
  narrative context.

Round 2's closure is itself an instance of the last one: `round2_closure`
composes its synthesis from the modules that measured each number, and a test
asserts the composition rather than the values, so the summary cannot drift from
its evidence.

### The experiment to run later

A dedicated three-arm comparison:

1. **preserved / pi-lcm context** — accumulated conversational history;
2. **structured canonical state** — validated, harness-owned, provenance-carrying;
3. **hybrid** — both.

### The architectural hypothesis to preserve

> **Structured operational state as the working source of truth, with lossless
> historical context and evidence retained for provenance and on-demand
> recovery.**

Not "state instead of history" — state *as the working surface*, history *kept
whole underneath it* so any claim can be traced back and any lost detail
recovered on demand.

### Rules this experiment inherits when it is opened

The four Round-2 rules apply and are not renegotiated: prove every failure class
reachable before interpreting a zero; never read a harness choice as a product
capability; never mix layers; decompose a pooled failure by mechanism before
comparing arms. The three arms would also need the Gen96 treatment — an explicit
audit of whether each arm's budget and window are the same quantity before any
number is compared across them.
