# R13 preregistration: new-task paired trial carried by agent-loop (stream A, Q-WORK-BENEFIT)

Prepared by Claude as curator in R12. Nothing here has run. Execution needs Tern's separate allocation and release.

## Task (curated; kiln never sees this section)
- Repo: ~/inference-gateway. Fix commit 7b368e2 "router: fix drain_on_disconnect - three bugs the unit tests could not see". Broken tree = 7b368e2^.
- Check (existing, frozen): tests/test_drain_on_disconnect.py at 7b368e2 (5 tests), run as `python -m pytest -q -p no:cacheprovider tests/test_drain_on_disconnect.py` with the host's system Python (pytest 9.0.3, httpx, pydantic, fastapi present; no installs).
- Contrast, reproduced 2026-09-25 on isolated copies: broken tree + check -> 3 failed, 2 passed, rc 1 (test_drain_reads_to_completion_then_closes, test_drain_is_bounded_by_its_deadline, test_drain_closes_even_when_upstream_errors); fixed tree + check -> 5 passed, rc 0. Evidence: curator/contrast-*.txt.
- Reference fix: igw/router/app.py at 7b368e2 (curator/reference-fixed-app.py). Held by the curator; never copied into an arm or a prompt.
- Second candidate considered: a71e762 (admin forget preview; 1 failing test broken, passing fixed). Not chosen: a one-assertion change is too small to separate the arms.
- Rejected: every conductor-chat fleet-poller fix. Kiln read the full cbc9d52^ poller in R9, which already contains those fixes, and R8 listed or opened 74b8b4b, cdaa2f8, 74e7f46, 85a36ff, d9eeaab and acc04ee.

## Exposure evidence
kiln seat history (acp-history a79067ca, 16k lines) and the archived kiln-flash history (fcb1e5e6, 35k lines): 0 mentions of "inference-gateway"; 16 of "igw", all timer names in systemctl listings. Call this task newly selected / task-unexposed in the trial sessions. It is not proven absent from model training. ~/inference-gateway and the curator files stay on the same host; the prompts forbid reading them, and a contamination scan (below) checks it. That is a scan, not a sandbox.

## Arms and treatment (same as R9)
- Arms T and C, each a fresh snapshot /var/home/bmosher/r13-arms/<arm>/ = `git archive 7b368e2^` with tests/test_drain_on_disconnect.py replaced by the check version, no .git, plus an empty notes/. Same model (kiln, opencode-go/muse-spark-1.3-contributor), same wrapper, same prompts except the treatment slots, same budgets.
- Phase 1, 10 min: inspection only (tasks/phase1-worker.txt). T only: {SUMMARY_INSTRUCTION} = tasks/summary-instruction-T.txt, so kiln writes its own <=300-word summary to /var/home/bmosher/r13-arms/T-summary.txt (outside every arm dir) inside T's phase-1 turn. No extra prompt. C gets an empty slot.
- Phase 2, 10 min: repair (tasks/phase2-worker.txt). T: {SUMMARY_BLOCK} = tasks/summary-block-T.txt with the summary verbatim (truncated to the first 300 words if longer; recorded). C: empty. Both keep all files and notes.
- Order: before the first worker prompt the director records secrets.randbits(1) in the package: 0 = T first.

## Loop composition (no new machinery)
Four loop packages, in order, each with question_id Q-WORK-BENEFIT and stream_id A in its dispatch receipt: R13-<first>-p1, R13-<first>-p2, R13-<second>-p1, R13-<second>-p2. Each: `agent-loop dispatch --qid ... --worker kiln --verifier corvid --duration 10m --verify-window 5m --task @<filled worker task> --verify-task @<filled verifier task>`. The loop owns dispatch, the worker deadline, the claim, the verify step and the recorded decision. Tern decides each phase package (question_answered or successor_opened) before releasing the next one.
Director step before each release (the only non-loop action): the R10 provenance checks (installed acp-worker 083f6eb7, worker process started after install, `new` in the features list, /ping exactly idle with no queue, no executing kiln loop package), then `{"text":"/new"}` on kiln's socket. The reply must be `new <unique ses_id>` with no REFUSED, plus one history boundary line. After the phase's first reply, confirm the id in `opencode session list` and in the state file. Missing proof makes that arm INCOMPLETE.

## Verification without teaching
Verifiers write only to the package's verify/ directory, never into an arm, and never message kiln. Phase-1 verifier: code and test hashes unchanged, notes listed by name and size only, T summary word count. Phase-2 verifier: test files unchanged, the check's rc and output, the diff against the broken snapshot. Tern's decisions are not shown to kiln. Next-phase prompts are the fixed templates.

## Outcomes (fixed now)
- Primary, per arm: phase-2 SUCCESS = the unchanged check exits 0 with 5 passed and nothing under tests/ changed.
- Secondary: time from the phase-2 prompt to the first worker test run whose output shows 5 passed, taken from acp-history tool-record timestamps. If no such record exists, report "unavailable". Phase duration is never used as a stand-in.
- Also recorded: pre/post outputs, diffs, notes written, summary delivered and words, timer or deadline cuts, and extra prompts.
- Contamination scan of each phase's records: any read of ~/inference-gateway, `git log/show` there, campaign4 packages, curator/ or reference-fixed-app.py flags the arm (reported, not hidden).
- Timeouts, partial fixes and edited tests are reported as such. No retuning after outcomes.

## Limits
n=1 per arm; one ordered pair; same model; unexposed-in-session, not proven unseen. The result can show loop-carried feasibility plus one paired observation, not general efficacy. Completing this through the loop is what the stream B start condition asks for; that is Tern's call.
