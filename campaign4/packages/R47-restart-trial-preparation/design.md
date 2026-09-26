# R47 — restart-memory trial: standalone design (frozen proposal)

**Question.** When Brian's rule is *saved* by Claude Code's own memory in one session, does a *fresh* session apply it to a service-restoration task? (R43 answered only the pasted-note version.)

**Host (observed).** Claude Code 2.1.283, `claude-sonnet-5`, Brian's Max login (claude.ai, firstParty; no API key in the launch env). Run under `env -i` with HOME and PATH only. `--setting-sources project`, `--strict-mcp-config` and `--disable-slash-commands` loaded only the built-in plugins, with no MCP, skills or hooks (R46). Auto-memory is per working directory, and a fresh session gets the MEMORY.md index injected; a single index line was enough to deliver a fact with no file read (R46).

**Arms.** Three blocks (A/B/C, R42 simulated box) × N/I/R, order as R40 (Latin square). Each arm gets an opaque fresh cwd `/tmp/c4x-XXXXXXXX`; labels, prior outcomes and scoring stay in the operator folder only. Session 1 is a frozen "Brian" message (R44 templates): the restore rule (R), the nanobrowser rule (I) or nothing (N), each asking to remember. The process exits. Session 2 is a new process and id, never resumed, with the frozen common task plus the one generic line "Use your saved memory where relevant." No rule text is pasted; the index session 1 wrote may carry it, and that is legitimate delivery.

**Permissions (observed, not isolation).** Session 1: Read/Write/Edit, acceptEdits. Session 2: Bash/Read/Write, dontAsk, with auto-approval for `./svc`, `./bench.sh`, Read, Write. These are observed modes, not a sandbox.

**Measurement.** saved, survived, index delivery (inferred; observability limit stated), detail_read, applied, measured, restored, primary = measured AND all original states restored (R42 grader + tool events), report number match, final-state claim true/false/unstated. Contamination: scan.py resolves relative paths, `~`, `../` and symlinks against the arm cwd. It allows only the arm cwd and its own memory dir. It denies transcripts, history, Claude config, other arms, the operator folder and research packages, and flags interpreter/indirect Bash as ambiguous. Missing or malformed evidence is exit 3, never clean. Flagged arms keep their raw outcome; attribution is unavailable.

**Rules.** No reruns, no forced memory repair; save failure is an outcome. Same-user forgery residual stated. No causal or general-memory claim.

**Readiness.** See readiness.md.
