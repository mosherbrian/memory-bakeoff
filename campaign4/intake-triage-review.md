# Intake triage review — tier4 filing + tier3 proposed notification

- **Reviewer:** corvid-dsh (bounded reader, 6m). Read-only; no edits/install.
- **Verdict: PASS** (with notes). No adopted research claim; hashes and links
  resolve; notification config is a bounded wake with correct rc handling and
  no polling/controller revival.

## Triage records (`team/INTEL/triage/`, 2026-09-21…24)

All four validate against `INTAKE-TRIAGE-POLICY.md`:

- `schema_version` 1; `report_id`/`report_path`/`report_date` correct;
  `owner` tern; `tier` 4; `supersedes` null (no chain, so no conflict).
- **Hashes match actual bytes:** `05b59e3c…`, `9db997db…`, `8b5640d8…`,
  `623ff58c…` — recomputed from each raw `.md`.
- `fetched_at` matches each report's intake header exactly
  (e.g. 2026-09-21T14:15:24Z; 2026-09-24T14:15:02Z) — not invented.
- Dispositions are valid enum values: 21/23/24 `evidence_for_existing_question`,
  22 `parked` (matches the policy's "September22 reconnaissance is parked").
- `question_ids` all resolve to real IDs in `research-questions.json`
  (Q-WORK-BENEFIT, Q-MEMORY-STATE, Q-EVALUATOR-VALIDITY, Q-DELIVERY).
- **No adopted claims:** every record is `evidence_status: intake_report_only;
  external assertions not independently verified`, `direction_change_authorized:
  false`, `experiment_authorized: false`, with a tier1-release next action. No
  benchmark number is fleet-confirmed.

## `research-questions.json`

Schema valid; five stable IDs; `answered` (Q-SYNTHESIS-20260920) is distinct
from the overall benefit question (Q-WORK-BENEFIT stays `open`); all
`source_paths` resolve; `active_package_ids` empty (names no proposed work).
Scope note correctly defers historical coverage rather than zeroing earlier
reports' unread counts.

## Notification config (`intake-triage-notify.conf`)

Reviewed at **current bytes** `1394211b…` (supersedes the initial `e44216cf…`;
the director corrected systemd dollar escaping). `ExecStartPost` on the existing
oneshot `intel-intake.service` (timer unchanged, 07:15/12:15 Pacific). It invokes
the **existing** `agent-deck wake tern`; no new timer, poller, model loop, or
controller.

Escaping is now correct: `rc=$$?` and `"$$rc"` — systemd collapses `$$` to a
literal `$`, so `/bin/sh` receives `rc=$?` and `[ "$rc" -eq 3 ]`. Behavior:
`rc0` → `exit "$rc"` = 0 (success), `rc3` (queued) → `exit 0` (success), `rc1`
or any other → propagated as non-zero (failure → `OnFailure`). A queued wake
does not trip `OnFailure`; a real transport error does. Matches observed
rc0/rc3 semantics.

## Limits / notes (not blocking)

- The 2-hour SLA is **prospective**: these four dispositions were filed
  2026-09-25T03:40Z, well after the reports' 14:15Z fetches. That is consistent
  with a backfilled first batch before the notification is active; the page must
  not present the batch as meeting a 2h SLA.
- `active_package_ids` is empty everywhere; fine for a view-only tier4, but
  Tern should reconcile it against the production loop when a research package
  is next active.
- Raw reports are on disk and hash-bound; per Brian they still need commit+push
  (outside this review).
- `systemd-analyze --user verify` was attempted but hit socket-permission limits
  in the sandbox; privileged syntax validation is still to be run before
  install. Not a defect — a validation step outstanding, correctly deferred.

## Addendum — current bytes re-reviewed

Re-read after the escaping correction: file `1394211b…`. `$$` escaping and
rc0/rc3→success, rc1→failure are correct as above. No source assertions changed;
triage hashes and question refs are unchanged.

*Reviewed: `INTAKE-TRIAGE-POLICY.md`, `research-questions.json`,
`intake-triage-notify.conf`, four `team/INTEL/triage/*.json` +
`team/INTEL/AGENT_MEMORY_INTEL_2026-09-{21..24}.md`,
`~/.config/systemd/user/intel-intake.{service,timer}`, and live
`systemctl --user` state.*
