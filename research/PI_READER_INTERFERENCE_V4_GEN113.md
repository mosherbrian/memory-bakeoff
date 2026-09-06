# Gen113 — the freeze that could not detect a leaking prompt

**Nothing was executed.** No reader, model, sidecar, engine, endpoint or GPU.
**The reader question is still OPEN.** Gen113 is not a result.

Frozen: `reader-interference-v4` at `results/gen113/attempt2/`,
`contract_sha256` `2bc281b9dea248ce…`. `reader-interference-v3` is
**`SUPERSEDED_AS_RULER / NON_EVIDENCE` for its identity only** — its science was
sound, it never ran, and nothing was lost.

## The defect

v3's `contract_hash` serialized **declarations** — answer classes, questions,
canonical values, the change ledger — and nothing executable. Four mutations,
captured before any repair:

| mutation | observable effect | did v3's digest move? |
|---|---|---|
| classifier replaced | every answer classifies `NEITHER` | **no** |
| grader replaced | everything grades `prohibited_stale` | **no** |
| parser replaced | malformed output parses as valid | **no** |
| **prompt replaced** | **the prompt hands the reader the answer** | **no** |

The last row is the one that matters. I spent Gen111 repairing a blinding
failure, then froze a contract that could not have detected the same failure
being reintroduced. A freeze that cannot see a leaking prompt is a label, not a
freeze.

## The repair

`contract_payload()` covers three layers, none containing the digest:

1. **Declarations** — what v3 already hashed.
2. **Behaviour tables** — parser (13 rows), classifier (20), citation relation
   (72), truth matrix (360), control forms and 20 prompt hashes, all produced by
   *running* the real functions and serializing what comes back.
3. **Source bytes** — SHA-256 of each repository file supplying scientific
   behaviour, by repository-relative path.

**On circularity:** this file's bytes are hashed, but `contract_sha256` is
written into the artifact *after* the payload is hashed and is an explicit
exclusion. The file never contains its own digest. Three exclusions are
enumerated — the digest itself, write timestamps, output paths — and
verification fails if that list ever widens.

An independent verifier reconstructs the payload from the checked-out sources
and compares. The manifest and the contract digest each prove something the
other cannot, and both are checked separately.

## Detection, and a better outcome than asked for

| mutation | how v4 catches it |
|---|---|
| classifier replaced | **fails closed** — no control can pass, so no digest is produced |
| grader replaced | **fails closed** |
| parser replaced | **fails closed** |
| prompt leaks the answer | digest moves |

Three of four are caught by *refusing to produce a digest at all*, which is
stronger than producing a different one. My first test asserted "the digest
moves" and therefore failed on exactly those three — the assertion was wrong,
not the code.

## Two defects I introduced while repairing this one

Worth recording, because both are the same mistake and my own checks caught
them:

**1. I fixed the binding in one place instead of all of them.** v4 first bound
`project_prompt` at import, so substituting the real function left the digest
unmoved — one of four mutations still missed, and the worst one. I repaired
that, then discovered the parser, classifier and citation tables had the same
stale binding. Everything now resolves through the module at call time.

**2. The first freeze was wrong, and the contract caught it.** `attempt1` froze
the payload before that second repair. Correcting the bindings changed the
payload and therefore the digest, so the evidence contract **refused to
overwrite `attempt1`** and wrote `attempt2`. `attempt1` is preserved, still
verifies against its own manifest, and is recorded superseded in
`ATTEMPT1_SUPERSEDED.json`. That is `immutable-evidence-v1` doing precisely the
job Gen106 built it for.

## Behavioural equivalence

v4 changes identity only. Asserted identical to v3 across all 360 matrix rows,
every parser and classifier fixture, all control-passing forms, and all 20
prompt bytes. Both Gen112 witnesses still grade `mixed_contradictory_answer`.
No control-passing outcome is reachable from `BOTH`, `NEITHER`, a citation
mismatch, an unknown citation, or a parser failure.

## Tests

40, covering I1 through I6: the four v3 blind spots, payload coverage, digest
movement for behaviour and declaration changes and source-byte changes, missing
sources failing closed, independent reconstruction, tampered digests, widened
exclusions, lost and gained payload fields, behavioural equivalence, the
preserved superseded attempt, and every historical manifest.

## The honest position

This is the sixth ruler defect in four contract versions. Unlike the first five
it is not a scientific error — the v3 ruler was sound — but it is the same
underlying habit in a new place: **I state a guarantee more strongly than what I
actually built supports.** "Frozen" meant "some declarations are hashed."

The reader question has still never been measured.
