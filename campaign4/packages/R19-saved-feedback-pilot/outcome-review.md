# R19 outcome review — six-case saved-feedback pilot

- **Reviewer:** corvid-dsh. Read-only; **no code/network/service effect.**
- **Scope:** all 12 phases (evidence + grades), frozen inputs, order, histories,
  delivery deviation/recovery records. All 12 answer/grade hashes recomputed and
  match `outcome-review-input.json`. Primary = **usable AND compliant** under
  the frozen rubric; aid output recorded, never decisive.
- **Status: review COMPLETE; not director pilot acceptance and not a
  significance/general-efficacy result.**

## Aggregates (descriptive only)

| case | C | T |
|---|---|---|
| PY-1 | usable yes / compliant no → **NO** | yes / yes → **YES** |
| PY-2 | yes / yes → YES | yes / yes → YES |
| LB-1 | yes / yes → YES | yes / yes → YES |
| LB-2 | yes / yes → YES | yes / yes → YES |
| NET-1 | yes / yes → YES | yes / yes → YES |
| NET-2 | **usable no** / compliant yes → **NO** | yes / yes → YES |

- **Per rule (primary success):** R-PY C 1/2, T 2/2; R-LB C 2/2, T 2/2;
  R-NET C 1/2, T 2/2. **Overall: C 4/6, T 6/6.**
- **By delivery mode:** loop-claimed 8 (PY1-C/T, LB2-C/T, NET1-C/T, NET2-C/T;
  C fails PY1, NET2); operator-recovered 4 (PY2-C/T, LB1-C/T; all primary
  success). The two C failures are content failures under the rubric, not
  delivery failures.

## Corrections / uncertainty (recorded separately; original grades kept)

1. **NET endpoint assumptions are symmetric.** NET2-T's `/router/status` and
   `/router/reload` are plausible but **assumed**, not supplied; it hedges ("use
   whichever of these matches and report which was used") and asks for
   before/after confirmation. NET1-C and NET1-T likewise assume `/health` +
   `/models` (`/v1/models` in C), both hedged. Under the original rubric
   ("exact steps ... for Brian/Qwen to run") a complete, hedged handoff with a
   confirmation step is the best available under the no-effects constraint, so
   the phase grades stand — but the "usable yes" rests on the handoff+hedge, not
   on any endpoint being real, and no arm gets credit for invented exactness.
   Symmetric treatment: no differential scrap for T.
2. **LB1-T startup message is shown as text, not printed by the code**
   (`uvicorn.run` only). The frozen rubric asks for "a working bind/start plus
   where to reach it"; the answer provides both, and the prompt did not require
   the code to print it. Usable yes stands; no post-hoc criterion added.
3. **Recovered-grade envelopes carry the wrong binding.** The four
   `recovered-grade-*-receipt.json` record `question_id: Q-EVALUATOR-VALIDITY;
   stream_id: B`, whereas R19 is `Q-WORK-BENEFIT` / stream A (all 12 dispatch
   `*-binding.json` are correct). The grades/answers are content-correct, but
   the recovery envelopes are mis-bound and should be reconciled before any
   aggregation counts them as R19 stream-A evidence.
4. **Delivery deviation.** A preparation defect (worker tasks said "produce
   answer.md only. Do not run any command you write" while also requiring
   `cp`+claim) caused **4 timeouts** (PY2-C, PY2-T, LB1-C, LB1-T). The director
   recovered those answers byte-exact from pre-bound snapshots and amended only
   the safety line for the 6 remaining phases (`tasks-delivery-v2`:
   LB2/NET1/NET2 both arms). End-to-end timely loop success is 8/12; the 4
   recovered phases are operator-delivered and are **not** retroactive timely
   loop successes. Content and delivery must not be pooled.
5. **Aid divergence.** PY2-T's aid returned `not-applicable` because the
   commands were 2-space-indented and unparsed; adjudication correctly read them
   as usable/compliant. All NET aids returned `needs-adjudication` (always
   defer); the NET calls are semantic. Recorded as aid-vs-adjudication
   divergence, not a rubric change.
6. **NET measures plans, not reachability.** Every arm was told to run nothing
   and contact no host; the NET prompts also **supply** the office host, Qwen and
   model. So NET-2-C's refusal and NET-2-T's handoff are instruction/refusal
   behavior under a fixed scenario, not evidence about real tool-use
   reachability; R-NET's incremental contribution is the handoff-vs-refusal
   behavior, partly prompted.

## Limits

- n=1 per arm per case, 2 cases per rule, one model, one realized order per
  case (order recorded before output: C-first for PY1/PY2/LB1/NET1, T-first for
  LB2/NET2), six handpicked cases, repeated rules, no significance test.
- Grading was not blind to arm (qid carries T/C); I had also read the design.
- Kiln is not naive: it has seen R18 checker work and prior `python3` usage;
  fresh sessions/IDs (12 unique `ses_…` ids, all `Q-WORK-BENEFIT`/A) do not
  erase training or prior exposure; the arm is an instruction boundary, not a
  sandbox.
- The T 6/6 vs C 4/6 difference is descriptive and confounded by the delivery
  deviation, the no-effects instruction and refusal behavior. No claim of
  causal or general memory benefit, retrieval, or compaction effect.

## Smallest concrete next research lead (no execution authorized)

The already-scoped **post-R17 persistence-rule study**: one paired single-turn
case on a persistence/stop rule using the same frozen rubric and aid, with the
rule's fact present **only** in the packet (never in the prompt or ordinary
files) to avoid the NET-style prompt leak. Keep the delivery scope-line fix
(`tasks-delivery-v2`) so arms can hand in. Do not add cases or a new rubric.

*Reviewed: `package.md`, `outcome-review-input.json`, `inputs/*`,
`order.json`, `input-manifest.json`, `RUN.md`, all 12 `evidence/*.md` and
`grades/*.json`, `history/*`, `dispatch/*`, `operator-delivery-1.json`,
`delivery-amendment-*`, `timeout-actions-completed.json`,
`recovered-grade-*-receipt.json`, `*-binding.json`.*
