# S7-3 design — false supersession: pi-lcm native vs a trivial state layer

Row S7-3 (sprint 7, BACKLOG-NEXT rank 4). Author: kiln-flash, 2026-09-17.
The binding declaration is `declaration.json`, written before any receipt and
sha-bound into all of them; the trial list and the thin layer are frozen by
sha256 inside it. This file is the prose companion. $0, local, no LLM, no
score import.

## Prior measurement, per the standing re-measurement rule

- **pi-lcm**: no false-supersession measurement exists — none exists. Stated
  in declaration and verdict per the rule; this row is the first.
- **agentmemory** (the protected comparison point):
  `research/AGENTMEMORY_FINDINGS.md` — under the `/remember` Jaccard write
  path, the 500-record stress store superseded **418 of 450 stress
  distractors (92.9%)**. The distractor shape documented there is reused:
  deliberately distinct facts sharing the fact-type template, scoped to
  different repos/services (a delta redis migration vs a fjord redis
  migration, Jaccard 0.75–0.9). Per-trial jaccard is recorded in
  trials.jsonl.

## Trials (frozen before the run)

44 trials, deterministic, in fleet voice: **32 distractor** (same template,
different scope — the original must NOT be superseded) and **12 update**
(same scope and fact-type, genuinely newer value — the original MUST be
superseded). Sanity before declaration: each original alone answers its own
query as the top hit in the real pinned store; a trial that cannot is
malformed and stops the run before anything is frozen.

## Arms (controls first)

1. `never-supersede` — control: supersedes nothing (the 0%-false trap the
   gate's update trials close).
2. `always-supersede` — control: supersedes everything.
3. `pi-lcm-native` — the real pinned store reader wrapped in the tool-level
   exact-then-bounded-relaxation query behavior (the S4-14/S6-2 pin), fresh
   store per trial, original+newer both present. The store has no write-time
   consolidation, so supersession is operationalized as **retrieval
   displacement**: the original's own query, re-issued with both records in
   the store, returns the newer write as its top hit.
4. `thin-layer` — `thin_layer.py`, the probe: key equality on
   (scope, fact_type). A newer write with the same key supersedes the
   original; anything else leaves it alone. ~35 code lines, sha-pinned in the
   declaration, inside this directory (the roadmap's Phase-G ban: measure the
   deciding property before building any state layer).

## Decision rule (frozen in declaration.json before the run)

`layer-helps` iff the false-supersession rate drops by at least **0.50**
(pi-lcm native → thin layer) AND the layer misses at most **0.10** of the
real updates (at most 1 of 12); else `layer-does-not-help` — which is a PASS:
Gate F asked for the number, not for a layer.

Pre-registered expectation (honest, recorded before the run): pi-lcm's
exact-AND gate matches a distractor only if the scope token matches, so the
native false-supersession rate is expected LOW; then the drop cannot clear
0.50 and the verdict is `layer-does-not-help` — pi-lcm does not have
agentmemory's disease, and a state layer adds nothing. If native
false-supersession turned out HIGH, the key-equality layer would drop it to
~0 while missing 0 updates, and the verdict would be `layer-helps`. Either
number decides Gate F; the measurement, not the outcome, is the deliverable.
