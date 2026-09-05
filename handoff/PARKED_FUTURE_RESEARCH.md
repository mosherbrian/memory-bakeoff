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

### Sharpened 2026-09-05 by P2, §1

P2 clarifies what the Pi quality-gate work (Gen43-47) actually was: a
**SKILL.state-like operational-state architecture, not a general semantic memory
system**. Read P1's "independent overlap" through that lens. Gen47 is evidence the
mechanism is **implementable and promising**, not evidence for a general
production extension.

---

## P2 — Observational semantic state, and the three-layer architecture

**Status:** PARKED. **Raised by:** Brian, 2026-09-05, from a disposable ChatGPT
whiteboard discussion after Round 2.
**Effect on the current round:** NONE. Round 3 is unchanged; no experiment starts
from this. **P1 remains** — this note sharpens it and adds a distinct adjacent
idea.

### 1. What the Gen43-47 Pi extension actually is

The successful harness-maintained Pi state/control extension is fundamentally a
**SKILL.state-like operational-state architecture**, not a general semantic memory
system. Its important idea:

- do **not** use the accumulated transcript as the authoritative representation of
  execution state;
- mechanically derive **bounded current state** from observable events where
  possible;
- expose the model to that current state, the control phase, the latest
  observations, and a small recent conversational tail;
- retain **full historical evidence separately** for provenance and recovery;
- gate authoritative transitions such as validation or completion on
  **machine-checkable evidence**, never on model assertion.

This stays a distinct architectural research direction.

### 2. The adjacent idea: genuinely observational semantic state

Most systems called "observational memory" still perform **smarter compression of
conversation history** — observe turns, summarise, fold, and hand the model a
better textual history.

A more interesting architecture for long-running coding agents would instead
construct a **provenance-backed materialised view of the project** from the
event stream.

Worked example. Evidence over time: *"Use Redis for the cache."* → the Redis
deployment fails → *"Switch to SQLite."* → the implementation changes →
validation passes.

Rather than retaining a compressed narrative containing all of that, an
observational semantic-state layer would maintain something like:

| field | value |
|---|---|
| cache backend | SQLite |
| Redis decision | superseded |
| reason for change | deployment problem |
| implementation status | validated |
| provenance | links to the source conversation and tool events |
| prior belief | recoverable, **not presented as current truth** |

**The goal is not "the agent can search old memories."** It is that the agent
**continuously knows** the current project state, decisions, constraints,
supersessions, unresolved questions and validated conclusions — without
reconstructing them from narrative history.

### 3. Three concepts, kept separate

- **Operational structured state (SKILL.state-like)** — objective execution phase
  and machine-observable state; ideally mechanically derived. Validation receipts,
  current tree, modified files, workflow progress.
- **Observational semantic state** — higher-level inferred project beliefs:
  architecture choices, constraints, conclusions, failed approaches, open
  questions, superseded decisions. Inferred from evidence but represented
  **explicitly**, not as narrative summary.
- **Conversation/history systems (pi-lcm, OM)** — preserve or compress what
  happened; useful as evidence, provenance, and recovery of what is not in active
  state.

**These may be complementary rather than competing.**

### 4. Candidate long-term Pi architecture

```
pi-lcm / lossless event history      -> authoritative evidence substrate
+ structured operational state       -> mechanically derived execution state
+ observational semantic state       -> compact canonical beliefs/decisions
+ (optional) semantic retrieval      -> obscure, on-demand long-tail recall
```

The active model receives **the two state views plus a bounded recent interaction
window**. Full history stays accessible for provenance and recovery rather than
continuously occupying working context.

### 5. The critical authority rule

**Do not let an LLM freely rewrite canonical semantic state.**

Round 2 and the Pi quality-gate work both argue for separating **evidence
generation** from **authoritative judgment**. A future semantic observer should
produce *proposed* observations carrying at least:

- source provenance;
- type;
- effective / current status;
- supersession relationship where relevant;
- confidence or uncertainty where inference is involved.

Promotion into authoritative state uses **deterministic constraints** wherever
possible, with **explicit ambiguity** rather than silent replacement.

> **LLMs can interpret evidence and propose state. The harness owns canonical
> truth, provenance, and the state-transition rules.**

### 6. Research implication — broader than P1

Eventually compare at least five arms:

1. accumulated / preserved conversational context (pi-lcm style);
2. compressed observational narrative (OM-like);
3. structured operational state;
4. structured operational **plus** observational semantic state;
5. hybrid state plus on-demand historical retrieval.

**The dependent variable is long-horizon coding-agent continuity and correctness —
not compression ratio.**

Questions to answer:

- Does the agent preserve current decisions across very long work?
- Does it avoid **resurrecting superseded approaches**?
- Does it retain explicit unresolved questions and constraints?
- Can it recover obscure historical evidence when needed?
- Can every important state item be **traced to evidence**?
- What happens when the semantic observer makes a **wrong inference**?
- Does structured semantic state outperform increasingly sophisticated transcript
  compression?

### 7. Rules it inherits when opened

The four Round-2 rules apply unchanged, and the Gen96 treatment applies to the
arms: audit whether each arm's budget and context window are the **same quantity**
before any number is compared across them. Five arms with different context
mechanics are that trap at greater scale than P1's three.

One further note from Round 3, relevant to §5: **"resurrecting superseded
approaches" is measurable, and we are already measuring it.** Stale-version
interference replicated in 192 of 192 observations across four independent
neighbourhoods (Gen99), and Gen100-102 are establishing whether a native
supersession mechanism removes it. Whatever that concludes is a direct input to
this hypothesis.

### 8. Status

Parked. Round 3 is unchanged and no experiment starts from this. A durable
architectural hypothesis to survive until we deliberately return to the Pi
long-horizon architecture line.
