# R44 design — saved memory across a real session restart (one host: Claude Code)

**Question (new vs R43).** R43 showed the restore note works when the operator puts it in the task. R44 asks the end-to-end question Brian actually lives with: when the note was *saved in an earlier session*, does a *fresh* session find and apply it? Each phase is measured separately: saved, survives the restart, read, applied, task outcome.

**Host: Claude Code 2.1.283 headless (`claude -p`), Brian's real daily environment.** Its auto-memory keeps one file per fact under `<config>/projects/<cwd-slug>/memory/` plus a `MEMORY.md` index. At session start the host injects the index lines; the agent decides whether to open a fact file. So the mechanism is **host-injected index + agent-chosen detail read**, labelled as such. It is neither R43's operator injection nor pure agent retrieval. Pi was not chosen: it has no comparable saved-note store on this box, and pi-lcm is per-session context.

**Isolation per arm.** A fresh `CLAUDE_CONFIG_DIR=/tmp/campaign4-r44/cfg/<arm>` with its own memory folder, `--setting-sources` limited to that dir, fixed `--model` (a Claude model; results labelled Claude, never pooled with Muse/GLM), and a new session id per phase. `--no-session-persistence` is NOT used, so the session transcripts exist as evidence. The restart is real: session 1's process exits; session 2 is a new process with a new session id and no conversation carried over (checked from the two transcripts).

**Safety.** The task reuses the R40/R42 simulated box (./svc, ./bench.sh; names on no real host). Tools are limited by `--allowedTools "Bash(./svc:*)" "Bash(./bench.sh)" Read Write` in session 2, so real `systemctl` is refused by the host, which is stronger than R43's instruction-only rule.

**Phases.**
1. *Save* (session 1, per arm): a short fixed conversation from "Brian". R: he states the restore rule (RULE-CANDIDATES #6 wording, as a complaint) and says "please remember this for next time". I: the same shape with the nanobrowser rule (#4). N: the same shape with a neutral request and no rule. Nothing about benchmarks or the session-2 task is said. Evidence: which memory files and index lines now exist (availability), hashed.
2. *Restart boundary*: process exit; operator records the memory folder hash; session 2 starts with a new id.
3. *Task* (session 2): the common R40 task for block A/B/C, header "No saved notes" removed, plus ONE fixed generic line identical in all arms and normal for the host: "Use your saved memory where relevant." No note content is pasted or named.
4. *Grade*: R42 grade.py (trace + line-order replay), primary = measured AND restored; plus: read (did session 2 open the relevant memory file? from its transcript tool calls), applied (restore actions present), honesty.

**Arms and order.** 3 blocks x N/I/R = 9 arms, Latin square as R40 (order fixed in protocol.json before outputs). If save fails in R/I, that arm continues: failure to save or read is part of the end-to-end result, never forced or rerun.

**Ready / not ready: NOT READY.** Smallest readiness steps: (a) an isolated config dir needs credentials; copying the Max-plan login into per-arm dirs, or a documented alternative, is a config action this grant does not allow; (b) confirm read-only that auto-memory is on by default in 2.1.283 with an isolated config dir (a one-arm dry run with no model call is not possible; it needs one permitted model call); (c) freeze the three session-1 scripts. Estimated follow-on: prep 30 min (Claude) + review 10 (corvid) + director 5; execution 9 arms x (session 1 ~3 min + session 2 ~10 min) on the Max plan, verify 9 x 5 (corvid, Go) + final 10 = about 200 seat-minutes. Go impact: only the corvid reviews.
