# Research-priorities reader check (tier4, bounded)

- **Reader:** corvid-dsh. Read-only; no research, edits, admission, or package.
- **Verdict: PASS.** One canonical ranked list; redirect has no duplicate state;
  initial history is honest baseline with no fabricated movement; append-only
  with preserved originals; counts are internal-only; no new experiment or
  source claim.

## One canonical list + redirect

- `RESEARCH-PRIORITIES.json` (`schema_version` 1, `owner` tern) is the sole list;
  `authority` explicitly says ordering is **scheduling judgment, not experiment
  authorization or validation of external reports**.
- `research-questions.json` is now `schema_version: 2`, `status: redirect`, with
  `canonical_path`/`history_path` and "carries no duplicate question state";
  old snapshot preserved in Git at `6424bb7b`. No conflicting second list.

## Ranks / IDs / paths

- Five items: Q-WORK-BENEFIT rank 1, Q-EVALUATOR-VALIDITY 2, Q-MEMORY-STATE 3,
  Q-DELIVERY 4, Q-SYNTHESIS-20260920 `answered` with `rank: null` (off the
  active ranking, not a low-priority task). IDs match the prior registry.
- All `source_paths` in the snapshot **and** in every history event resolve on
  disk (verified programmatically; **0 missing**).

## History — no fake moves, append-only

- `RESEARCH-PRIORITY-HISTORY.jsonl`: 5 events, `sequence` 1–5, unique
  `event_id`s; all four ranked items are `change: new` with `from_rank: null`
  and the explicit reason "no earlier ranked order is asserted"; the answered
  item is imported "not a new research result or claim that it was ranked
  previously." No invented prior ranks or backdating.
- `history_head` = `priority-000005` = last event. Item IDs in snapshot and
  history match exactly. Policy's append-only rule (never overwrite/reorder/
  delete; `corrects_event_id` for corrections) is not violated; nothing to
  correct here.

## Triage revisions — corrections preserve originals

- Four `<report-id>.20260925T034537Z.json` files each have `supersedes` naming
  the prior record, and both the original and revised files remain on disk
  (append-only correction, no overwrite).
- Each still binds the raw report bytes (`report_sha256` recomputed equal) and
  carries `priority_effect: unchanged` with reason, `baseline_history_head:
  priority-000005`, `change_event_ids: []` — no report is forced to create work,
  and none is promoted to a validated result.

## Counts not primary; no new claims

- Policy §"Sponsor refinement: priority, not counts" states the page shows rank,
  question, why, owner/next step, movement and history, and that **unread/triaged
  counts stay in internal loop/duty checking, not the primary page.**
- No new experiment: triage `direction_change_authorized`/`experiment_authorized`
  are false; any direction change still needs a tier1 decision. External report
  content stays labelled unverified.

## Limit (not a defect)

- All five baseline events share one UTC timestamp (initial baseline import), so
  the history contains no movement yet — expected for a first baseline, and the
  policy requires the initial load be labelled baseline rather than fabricated
  movement.

*Reviewed: `campaign4/RESEARCH-PRIORITIES.json`,
`campaign4/RESEARCH-PRIORITY-HISTORY.jsonl`, `campaign4/research-questions.json`,
`INTAKE-TRIAGE-POLICY.md` (priority section), and the four
`team/INTEL/triage/*.20260925T034537Z.json` revisions.*
