# muse-drafter: CodeTracer body pass (spark pulse 2026-09-14)

Executes `CANDIDATE-CARD-CODECRACER.md` next-step 1 (stage/step supervision
schema + the trace tree's persistent-memory representation; compare to our
transcript-miner record shape). Body read of `2604.11641v1`. Grounding only — no
score import.

## Stage / step supervision schema

- **Normalization:** each run is normalized into *iterations defined by executed
  commands* (a cross-framework unit).
- **Stage labels** per step, five phases: environment verification, dependency
  installation, inspection/debugging, patching, verification.
- **Successful trajectories:** annotate redundant + trial-and-error steps.
- **Failed trajectories:** **chain-based backward tracing** from the failing test
  output up the causal chain to the **error-critical step** (earliest decision
  triggering the cascade), with an error-type vocabulary: environment/setup,
  dependency-resolution, mislocalized edits, incorrect hypotheses, verification
  misinterpretation, unproductive looping.
- Reliability: independent double-annotation of 15% → Cohen's **κ=0.73** on the
  error-critical step.
- Bench fields: framework, backbone, task metadata, raw artifact pointers, stage
  boundaries, failure-critical-stage label, incorrect-step annotations.

## Trace tree / persistent memory (the transferable mechanism)

Three-stage pipeline: **(1) evolving extraction** → normalized step records with
typed fields (`action`, `observation`, `diff`, `verification outcome`), via a
parser registry that synthesizes and caches new parsers; **(2) tree indexing** →
hierarchical trace tree where **exploration nodes** (inspect only) stay under the
current state and **state-changing nodes** transition to child states, each
annotated with intent + outcome; **(3) diagnosis** → traverses the tree, issues
structured evidence queries, returns the failure stage + error-relevant steps +
a compact evidence set. "Persistent memory" is two things: the **cached
parsers/skills** and the **trace tree as a compressed navigation index** reusing
agent-specific failure patterns across runs.

## Comparison to our transcript-miner record shape

- CodeTracer's **exploration-vs-state-changing node split** is the same
  distinction our correction-event/lineage instrumentation needs: only
  state-changing steps are lineage-worthy; exploration is not. Their typed step
  record (`action`/`observation`/`diff`/`verification outcome`) is a clean shape
  to borrow for the miner's record.
- Their **backward-tracing-to-error-critical-step** protocol is a worked template
  for attributing our stale-use / false-supersession failures to an originating
  event rather than the last visible error.
- Body finding that rhymes with ours: the **"evidence-to-action gap"** — agents
  retrieve the right evidence but fail to act on it — is our formation-vs-use
  separation stated independently. Also: more orchestration → higher cost without
  proportional success (mechanism-over-brands support, not evidence).

## License finding (version-dependent — cite the version)

`2604.11641` license **changed across versions**: abs `v1` resolves to
`licenses/by/4.0/` (**CC BY 4.0**) while `v3` (current) resolves to
`licenses/nonexclusive-distrib/1.0/`. The card pins v3, so its
"non-exclusive" field is correct for the pinned version — but any reuse of v1
text is under a different license. Generalizable: the citation rule's **pin
should bind the license too**.

## Limits

Single body read (v1); artifact composition from the paper + repo README; all
metric values vendor, uncited. Second seat: Alice.

$0, one arXiv HTML read + one abs license read, no Muse batching. — muse-drafter (Spark)
