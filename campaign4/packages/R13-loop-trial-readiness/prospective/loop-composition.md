# R14 loop composition (prospective; supersedes only the D1/D2 parts of R12's preregistration)

Task, check, treatment, scoring, budgets and limits are unchanged from R12 preregistration.md (7b368e2; check 3F/2P broken -> 5P fixed). The future trial is named R14 (package dir packages/R14-loop-paired-trial) so it does not collide with this readiness package R13.

## At release (Tern), before any worker prompt
1. Create packages/R14-loop-paired-trial/ with manifest.py, collect.py and arm-manifest.json copied byte-exact from this package's prospective/ (hashes in completion-claim.json).
2. Build /var/home/bmosher/r14-arms/broken (read-only reference of the broken tree), T and C: each = `git -C ~/inference-gateway archive 7b368e2^ | tar -x -C <dir>`, then copy R12 curator/check-test_drain_on_disconnect.py to <dir>/tests/test_drain_on_disconnect.py, then `mkdir <dir>/notes` (not in broken). Verify `manifest.py compare arm-manifest.json <dir> --frozen igw,tests` exits 0 for all three.
3. Record secrets.randbits(1) (0 = T first). Fill templates: {ARM}, {ARM_DIR}=/var/home/bmosher/r14-arms/<ARM>; T phase 1 {SUMMARY_INSTRUCTION}=summary-instruction-T.txt and {SUMMARY_ARTIFACT}=summary-artifact-T.txt; C gets both empty. Phase 2: T {SUMMARY_BLOCK}=summary-block-T.txt with evidence/T-summary.txt verbatim (first 300 words if longer, recorded); C empty.

## Per phase, four times: R14-<A1>-p1, R14-<A1>-p2, R14-<A2>-p1, R14-<A2>-p2
1. Director: R10 provenance checks (installed acp-worker 083f6eb7, worker started after install, `new` in features, /ping exactly idle with no queue, no executing kiln loop package), then `{"text":"/new"}` on kiln's socket. The reply must be `new <unique ses_id>` with no REFUSED, plus one history boundary line.
2. `agent-loop dispatch --config /home/bmosher/.config/agent-loop/campaign4.json --qid R14-<ARM>-p<N> --worker kiln --verifier corvid --duration 10m --verify-window 10m --task @<filled worker file> --verify-task @<filled verifier file> --input packages/R14-loop-paired-trial/arm-manifest.json`, with a dispatch receipt carrying question_id Q-WORK-BENEFIT and stream_id A.
3. The installed loop (df5e6fc, internal/loop/loop.go instructions()) appends to both tasks: "agent-loop package <qid>, <step> step. When you are done, file your claim with this exact command (PATH is relative to /home/bmosher/memory-bake-off/campaign4 ...): /home/bmosher/.local/bin/agent-loop claim --config ... --qid <qid> --step <step> --outcome completed|failed --artifact NAME=PATH". The templates name the exact artifacts to put there. Every artifact is a file under artifacts_dir (the loop rehashes files; arms are outside it, so collect.py copies test output, a notes index and a manifest comparison, plus the igw diff in phase 2, into packages/R14-loop-paired-trial/evidence/<ARM>-p<N>/).
4. After the first worker reply: confirm the new id in `opencode session list` and in kiln's state file. Missing proof makes that arm INCOMPLETE.
5. Tern decides the phase package (question_answered after a PASS, or record failure) before the next /new.

## No teaching
Verifiers write only to packages/R14-loop-paired-trial/verify/, never into arms, and never message kiln. Evidence copies hold test output, hashes and diffs; notes content is indexed, not copied, and T's summary is read back only by the director for the T phase-2 slot. Curator files (R12 curator/, reference-fixed-app.py) are never copied into R14 or any arm.

## Secondary metric
First passing run in phase 2 = timestamp of the first kiln tool record in acp-history whose output contains "5 passed" for the check command. Otherwise "unavailable".
