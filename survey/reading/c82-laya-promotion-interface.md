# Reading note c82 — laya.evals: what the learning loop ships versus what promotion needs

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 82.**
Skeleton first; **requirements 1/7 integration, sponsor-requested learning loop**; bounded
primary read of `NandhaKishorM/laya` — README plus the directly named evaluation/calibration
interfaces only. No code run, no dataset generation/download, no model calls, no training, no
public benchmark sweep. Deliver: what `laya.evals` actually supplies for a custom binary
held-out set, recall/calibration reporting, checkpoint comparison and temperature fitting;
**supplied primitives vs automatic promotion/rollback (neither assumed)**; source revision; the
**missing integration named, not a new framework**.

*(interface map + verdict appended below)*

## Supplied evaluation primitives (HEAD `4066d5d5fbf0`, 25 Sep 2026)

**Custom held-out set:** `Dataset.from_jsonl` + `laya-evals validate <dataset>` — labelled JSONL
is the contract. **Reporting:** pluggable `Evaluator` classes (accuracy/MAE/within/confidence),
`ece()` calibration error, `EvalReport` with per-slice aggregation (language/model/qid/tag).
**Checkpoint comparison:** `EvalReport.compare(baseline, tolerances)` + CLI `--baseline`,
`--min-accuracy/--max-ece/--min/--max`, **exit code 1 when a threshold or tolerance fails** —
README: "laya.evals scores a labelled dataset and **gates a build on it**". `--model` pins a
checkpoint explicitly.

## Not supplied (neither assumed)

**No automatic promotion or rollback.** The gate is an exit code; acting on it is the caller's
script. **No temperature fitting in the evals path** — the runtime only *loads* fitted
temperature files; fitting lives in the Kaggle fine-tuning notebook, and the README states both
shipped checkpoints are over-confident and `laya-multilingual` has **no fitted temperatures at
all** — "fit them before relying on these numbers". **No built-in binary recall/precision** — a
flag/keep task needs a small custom `Evaluator` subclass (the extension point exists).

## The missing integration, named

Four pieces, none a framework: **(a)** a labelled held-out JSONL of Brian's own corrections —
the c67 label budget, generation is ours; **(b)** a custom binary `Evaluator` mapping
`answer_confidence` → flag/keep against gold (a few lines at the supplied extension point);
**(c)** a promotion script: run `laya-evals` with `--baseline` + thresholds, swap the checkpoint
directory only on exit 0 — **the exit code is the seam; the script is unbuilt glue**; **(d)** a
**local** temperature fit on a calibration split before any confidence threshold means anything
— the supplied fitting path is the Kaggle notebook, i.e. hosted training egress, which the
sponsor's local-first constraint says to port; porting is training-adjacent work, not an
existing command.

**Opinion:** the learning loop's *measurement* half is genuinely supplied and machine-gateable;
its *decision* half (promote/rollback) and its *calibration* half (local fit) are integration we
own. Nothing here changes the pilot order: the promotion script is worthless before (a) exists,
and (a) is the same label budget c67 already priced.

**Confidence: high on supplied/not-supplied split (direct reads of evals.py, evals_cli.py,
README sections), high that exit-code-gating is the intended seam (README wording + CLI codes),
medium that a local temperature port is the only hosted-training dependency (notebook internals
not read — named unknown).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c81.md, OPTION-B-CASCADE.md, OPTION-B-LEARNING-LOOP.md,
systems/laya-correction-prefilter.md.