# R2-design-1 — verifier source-first baseline (recorded before author output)

- **Verifier:** corvid-dsh. Historical exposure disclosed: I have seen R1's
  accepted synthesis and this package's admission review; I have **not** read
  the author's `design.md` or `feasibility.tsv` before writing this. No
  fresh-session blindness is claimed. Read-only; no experiment/build/install.
- **Sources cited here** are primary local artifacts inspected directly.

## What feasibility/outcome the contract requires

The question is satisfiable by either (a) one concrete design naming a
reversible, already-available treatment, a task pool, a task-completion
outcome rubric, a boundary observation, confounds, sample/effort and stops, or
(b) a supported no-go with the exact missing prerequisite. Admission's six
bounds govern: exact treatment path+hash and disable path; task pool/rubric
grounded in actual task completion; no proxy as primary outcome; freeze before
outcome access; boundary/confounds/stops stated; no build/study; null ≠ proof.

## Independent read of the local record

**A reversible, already-available treatment exists.** `pi-recall-nudge`
extension source is present locally:
`implementer/repo-glm-dsh3/extensions/pi-recall-nudge/index.ts`
(`8402f74c…`) and `README.md` (`881e3631…`), with `test/nudge.test.ts`. It has
explicit reversible controls: `PI_RECALL_NUDGE=0` env kill switch and
`recallNudge.enabled=false`; `everyNPrompts` (0 = off) toggles firing. It fires
on a **resumption-pending** flag (resume/fork) — i.e. it targets exactly the
session/restart boundary the question asks about, and per the earlier proposal
does zero store writes. This is a stronger candidate than any popularity-ranked
system.

**An executable action-outcome task pool exists (not retrieval-only).**
`team/invocation-corpus-v2-standard/` and `v3-standard/` each hold 60 scenarios
(`manifest.json` `18cfe106…`, seed 20260915) with `correct_action_set` /
`wrong_action_set` per scenario and an executable runner `run_standard.py` that
drives a real agent and reports numerator/denominator metrics
(`results.jsonl`, per-scenario `T00*/firelog.jsonl`, `topics.jsonl`). v3 adds
controls (`results-control-always-clean`, `results-control-never-clean`). The
scored quantity is the agent's **action**, which is task-completion-like, not a
retrieval score. Separately, `team/outcome-pilot-bundle-20260914/events.jsonl`
(`7cd03aa5…`) is a 10-event structural correction stream — an outcome-adjacent
signal, but it carries no task-success label, so it is context, not the primary
rubric.

**Boundary.** The extension's resumption trigger observes a real
session/restart boundary. R1's accepted record shows a genuine **compaction**
boundary was not instrumented (`compaction_measured: false`); a design that
claims compaction coverage would overclaim.

**Prior art.** `team/PROPOSAL-R2-explicit-prompt-habit-v1.md` (`b587b263…`)
already frames a daily on/off A/B of the explicit-prompt habit with a kill
switch, and honestly anchors itself as showing whether the habit "fires and
delivers," not that coding outcomes improve. A design that ignores this prior
inspection, or that re-pitches a run as already authorized, would be
incomplete.

## Baseline judgment

Feasibility is **high**: treatment, task pool, action-outcome rubric,
reversible disable path and a session boundary all exist locally and read-only.
The defensible deliverable is therefore a **concrete design**, with the no-go
branch reserved only for a failure to pin the pool/rubric or a real boundary.
I will test whether the author's artifacts (1) pin exact paths/hashes, (2)
name an action/completion outcome rather than retrieval, (3) specify
matched/control and freeze ordering, (4) state boundary honesty and confounds,
(5) give a sample/effort estimate and stopping rule, and (6) refuse
null-as-proof — and whether they meet the contract completion checks.

*Produced prior to reading `design.md`/`feasibility.tsv`; not edited after.*
