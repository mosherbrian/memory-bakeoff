# R44-restart-memory-design — independent design review (stream B)

- **Reviewer:** corvid-dsh (493c0317-1790000758), differs from author (Claude) and
  proposed participant. Read-only; **no participants, model calls, config
  changes or probes.** Claim sha256 `b0f9159e…` matches the handoff; handoff
  00:15:46Z, review deadline 00:25:46Z.
- **Verdict: INCOMPLETE** — the design is coherent, honest and correctly
  **NOT READY**, but two audit gaps must be closed before any execution and one
  required limitation is missing from the design record.

## Passes

- **Host + mechanism label (honest).** Claude Code 2.1.283 headless; mechanism
  labelled **"host-injected MEMORY.md index + agent-chosen fact-file read"**,
  explicitly distinguished from R43's operator injection and from pure agent
  retrieval. Host choice justified (Pi has no comparable saved-note store).
- **Phases separated.** save → restart boundary → session-2 task → grade; the
  endpoints `saved`, `survived`, `read`, `applied`, `primary`, `honest_report`
  are defined separately, and failure to save/read is part of the end-to-end
  result (never forced or rerun).
- **Equal retrieval line / no note content.** Session 2 uses one fixed generic
  line "Use your saved memory where relevant." identical across all arms; the
  R40 "No saved notes" header is removed; no note content is pasted or named.
- **Arms/order.** 3 blocks × N/I/R = 9 arms with a fixed Latin-square order in
  `protocol.json` before outputs; templates N/I/R are distinct and contain no
  session-2/benchmark details.
- **Cross-arm isolation intent.** Per-arm `CLAUDE_CONFIG_DIR`, own memory folder,
  `--setting-sources` limited, new session id per phase; results labelled Claude
  and never pooled with Muse/GLM.
- **Grading base.** R42 `grade.py` (trace + line-order replay), primary =
  measured AND restored, plus transcript-derived `read`/`applied`/honesty.
- **NOT READY is sound and concrete.** `ready:false` with three named steps
  (per-arm config credentials are a disallowed config action; auto-memory default
  under a fresh config dir unconfirmed and needs one permitted model call;
  session-1 scripts to freeze) and a ~200 seat-minute follow-on estimate. No
  invented host or hook.

## Findings

**F1 (material — leakage / equal retrieval opportunity).** Session transcripts
are deliberately **persisted** (`--no-session-persistence` NOT used) and session
2's tool set includes unrestricted **`Read`**. Session 2 therefore has a path to
session 1's transcript JSONL (same arm config dir) or other arm-local artifacts
and could recover the rule from there instead of via the memory mechanism,
without any read of the intended memory file. The design neither confines
`Read` to the arm workdir nor scans session-2 tool calls for transcript reads.
**Correction:** restrict `Read` to the arm workdir (or otherwise block transcript
paths) and/or add a frozen session-2 transcript scan that flags any read of a
session-1 transcript; declare that such a read voids the `read`/`applied` credit
for that arm.

**F2 (material — restart independence / lost context evidenced).** Independence
is asserted from "new process, new session id, transcripts" but no concrete
**lost-context evidence rule** is frozen. New id/process alone is a label; the
audit requires shown loss. **Correction:** freeze an explicit check — e.g. no
`--resume`/`--continue`; session-2 first turn contains only the common task plus
the fixed generic line and none of session 1's unique note tokens; the two
transcripts share no conversation content — recorded per arm before grading.

**F3 (minor — grading validity / same-user limit).** The package requires the
reviewer to "explicitly retain same-user trust limitation" and to grade with the
accepted trace + transcript safeguards; `design.md`/`protocol.json` do not state
the same-user limit, and they do not say how copied/fabricated measurements are
caught. Add both to the design (trace + transcript cross-check; same-user
limitation retained as an explicit residual).

## Readiness steps to add

F1's read confinement/scan and F2's lost-context rule belong in the NOT READY
step list (alongside credentials, auto-memory-default confirmation, and the
session-1 script freeze). A dry run that needs one model call remains a
config/credential-gated action outside this grant; the design says so.

*Reviewed: `package.md`, `design.md`, `protocol.json`, `templates/*`,
`manifest.md`, `completion-claim.json` (`b0f9159e…`), `release.json`,
`operator-receipt.json`, `director-delivery-receipt.json`, `operator-task.txt`,
`review-task.txt`.*
