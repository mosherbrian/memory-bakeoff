# Reading note c67 — Laya's own evaluation, and whether the 46-trial probe design is fair

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 67.**
Skeleton first; single queue; no model calls, no Mac connection, no script execution (saved
arrays/scripts read only). My fair-design charge: **label independence, primitive semantics,
threshold/calibration limits** — then ready or one blocking issue. Carried: imported Jev scores
are not a matched comparison; output shape and price do not establish accuracy or calibration.

*(facts, resolution, verdict, probe disposition appended below)*

## Laya's own evaluation (author-published; README limits; intake + Tern card cross-checked) `[read]`

**The 0.213-vs-0.081 resolution:** BENCHMARKS.md puts ECE **0.213 on the
`laya-typed-decisions` checkpoint**; the calibration table reports **0.466→0.081 for `laya`** —
**different checkpoints/aggregates. The intake shorthand "0.213→0.081" is not a paired
improvement on one population; do not present it as one.** Worse for the pitch: base
typed-decisions accuracy ≈**0.36 versus 0.461 majority** — the base checkpoint sits **below its
own majority baseline**. Author-stated limits: weak base-checkpoint zero-shot transfer, collapse
past ~20 options (Banking77 0.425 vs Jev 0.870), ordinal scoring and option-label sensitivity.
The Jev comparisons are imported numbers against a **never-published black box**, not
head-to-heads.

**Independent local evidence (saved arrays, read only — no model call):** my AUCs on the stored
question-sweep arrays: **0.537–0.641** across four questions — q3 is near chance. The saved
client retracts its own no-complaint-as-negative label assumption; checkpoint/temperature
identity is unrecorded. The keep/replace inventory adds a named failure: **laya ranked three
populations backwards** where a mechanical jargon check ranked them as Brian does. Negative
evidence from the Jev family: the SQuAD gating test removed **zero** hallucinations and cost
correct answers, with 0.82–1.0 confidence on wrong ones — a checker sharing the reader's errors.

**Verdict: a real, cheap, local mechanism with author-published calibration on a specific
checkpoint, weak-to-negative independent evidence on anything adjacent to Brian's questions —
approve the plumbing test, import nothing.**

## Fair-design review: label independence, primitives, thresholds

**Label provenance: independent but surface-derivable.** Labels were declared pre-run by trial
kind — independent of the tested model. But I verified the whole-token rule equals gold **46/46
across all four families**: gold is a deterministic function of query-token presence. The probe
therefore **cannot show classifier value**; its ceiling is the rule. Valid readings: endpoint
works, deviation profile vs the rule (FP = harmful-retirement candidates), probability shapes.
**Invalid: "the classifier can do supersession."**

**Primitives: binary choice is inside the design space** — the >20-option, ordinal, and
label-sensitivity limits do not bite. But the served checkpoint/temperature identity is unknown;
results attach to that instance only.

**Threshold/calibration: n=46 with 13 positives cannot support any calibration claim** (the
manifest agrees); fixed p≤0.1/p≥0.9 selective bands with no threshold selection — correct;
ties→yes slightly favors the minority class; note it.

**Two controls the fair probe needs:** (1) rule and majority baselines reported **per family**,
so an always-no collapse is visible against the 13 genuine-updates; (2) raw probabilities and any
identity fields logged verbatim before any banding — else the run is unattributable.

**Disposition: READY** — fair as a capped plumbing sanity check with honest baselines; the
framing requirement above is mandatory, not a blocker.

**Confidence: high on the ECE resolution and rule-gold equivalence (verified locally), high on
the weak-discrimination reading of the saved arrays (computed), medium that the negative Jev-
family evidence transfers to Laya's binary supersession question (different task, same
mechanism-class).**

## Addendum — final fair-design disposition (before the authorized 46 calls)

**READY — no blocking design issue.** Two panel findings fold in cleanly: Kiln's envelope
resolution (only `row[request]` transmitted, shape-checked, labels remain outer) closes label
leakage; Corvid's confirmation that the request uses the **Choice** name-definition primitive —
not ordinary Noul — matches this note's "binary choice is inside the design space" reading, so
the >20-option/ordinal limits stay non-binding. Standing requirements for the run, unchanged:
(1) rule and majority baselines reported **per family**; (2) raw probabilities and any identity
fields logged verbatim before banding; (3) **the served checkpoint stays explicitly unknown** —
results attach to this instance only; (4) valid readings are endpoint-works, deviation-profile-
vs-rule, and probability shapes — **not** classifier-can-do-supersession (gold is surface-
derivable, rule == gold 46/46 verified locally); (5) no calibration claim at n=46.

## Addendum 2 — run result reconciliation (post-run, no new claims)

**27/46 vs majority 33/46 vs rule 46/46; 13 FN, 6 FP; zero high-confidence; 159 ms median.**
This is the **always-no collapse the per-family reporting was designed to expose**: 33 correct
nos minus 6 FPs = 27, so **all 13 genuine updates were missed** — the classifier retired nothing
and missed every real supersession in the set. The plumbing worked (46 calls, finite latency);
the mechanism showed **negative value against the majority baseline** on this set, exactly the
reading boundary this note drew. Accepted caveats: the bad complaint labels **invalidate my
saved-array AUC interpretation as a task claim** — those numbers stand only as descriptive
shapes of the served outputs; binary-set performance does not prove label robustness on wider
primitives; received confidence/action fields differ from Jev docs and only `noul` was scored,
so field semantics remain unresolved. Nothing here upgrades or downgrades the ECE resolution or
the rule-gold equivalence, both verified locally.

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md,
team/EXTERNAL-CHEAP-CLASSIFIER-GATING-20260919.md, team/KEEP-REPLACE-INVENTORY-20260920.md,
~/laya/ saved scoring material (read-only), probes/laya-supersession-20260926/.