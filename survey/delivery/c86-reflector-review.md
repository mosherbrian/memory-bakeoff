# Shipped reflector review — c86

Tern,26September2026. **Keep the one-file design; change the writer and undo path before the first unattended write.** No new service or Brian review ritual is needed. Source inspected at `/var/home/bmosher/.claude/reflector/reflector`, SHA256 `5272126283094d36e65a3f3bd35da4610b00f8402b03de0573604d4b5c328345`. Findings apply to that snapshot. Ten isolated CPU fixture observations reproduced in [results](c86-reflector-tests.json), using [reproduction code](check_reflector_c86.py). The tests invoke no model/network and mutate only temporary repositories. Production source, timer and memory were not changed.

## Fix first: ownership and recovery

1. **Unrelated edits enter the reflector commit and its undo.** Lines294–295 use `git add -A`. A pre-existing unrelated edit was captured, then `undo` reverted it. Stage only the exact changed paths; preserve unrelated work and explicitly handle already-dirty target files. This is the same practical failure found in pi-reflect, now reproduced here.
2. **Failed commits still publish changes and report success.** On a rejecting pre-commit hook, generated files/index edits remained, `applied` stayed positive, and `run` returned0 with `commit:null`. Validate/stage a complete change set before publishing; on failure preserve the previous active artifacts, report nonzero and persist a failure receipt. A Git hook alone does not make worktree writes transactional.
3. **Undo is incomplete on same-date reruns and failures.** `manifest-DATE.json` is overwritten; a second empty run erased the first run's skill list, so undo left that skill installed. A conflicting revert returned0 with an unmerged repository. Use unique run IDs and immutable manifests with exact changed paths, prior state and resulting commit/content hashes. Undo must stop/report conflicts rather than claiming success; avoid moving a skill with later edits without checking them. Git log scanning is limited to200 commits and no-op reruns are not idempotent for appended updates.

## Quote and scope contract

The basic absent-quote check rejects a fabricated quote. However, joining messages with newlines admits a quote spanning two different messages; this reproduced. Require a quote within one source message and retain its session/message identity. The advertised200-character maximum is not enforced. Quote presence is attribution evidence, not proof that the resulting lesson follows from it.

`collect` merges projects and returns only timestamp, user text and700 characters of preceding assistant text. A two-project fixture confirmed that cwd/session identity is lost. All generated feedback goes into one memory directory; procedures go into global skills. Preserve source/project scope and target it explicitly; an ambiguous local-to-global promotion should stay a candidate. Updates append text without retiring the conflicting old instruction. The prompt's instruction to avoid overgeneralization is useful but not a mechanical scope or supersession gate.

`basename(target_file)` blocks lexical traversal but follows symlinks: a temporary memory symlink updated a file outside the memory root. Resolve and check containment, and reject protected/unsupported targets. No model or real external file was used in this test.

## Publication, scheduling and measurement

A190-line fixture became191 lines and committed. The existing interactive Stop-hook threshold is not enforced by this Python writer; a later Stop hook may expose the overflow, but does not make publication bounded. Check the final index against the existing190-line/24KB contract before writes, with an explicit omission/failure report. No new cap policy is needed.

The supplied systemd timer says05:30 with `Persistent=true`; service runs `reflector run`. This review did not execute or inspect live timer state. Catch-up handles the previous day, not necessarily every missed day. Source failures/model timeout can exit before a stats receipt; Signal success is assigned after stats are written, so the ledger does not retain delivery success. Make failures/notification status explicit. The input cap is visibly reported but truncates the selected day's tail; index size is additional prompt content.

The dry-run JSON inspected has12 items and0 rejected quotes. Claude's reported improvement between prompt versions is useful operator feedback, not an independent semantic evaluation here. No real run was made. `corrections` and `repeats` are model-authored counts, **not** the automated fleet intervention/recurrence endpoint. Current input is Claude Code only, so the fleet pilot's Pi/ACP outcome remains uncovered. “Learned now active” establishes file publication, not receipt by an already-running host or later compliance.

**Delivery decision:** Claude can fix these paths in the existing file and rerun the supplied fixtures against the new revision. Keep the normal digest design and no-tools model call. Do not add a service; do not treat this review as authority to disable the timer or edit production. Local-GPU booking remains irrelevant to these CPU fixtures and normal authorized Cairn labeling; it still gates future GPU tests.
