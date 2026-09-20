# S4-7 — Role-identity audit: every AGENTS.md + the two named stale identities (corvid-dsh, 2026-09-16)

**Row:** QUEUE S4-7 · **Claimed:** corvid-dsh 2026-09-16 08:47 PDT · **Cost:** $0, read-only census · **Check:** `test -f team/CORVID-ROLE-IDENTITY-AUDIT.md`

**Second seat: NONE YET.** Kiln or Brian should spot-check the seven verdicts below; each is a file-content fact quotable by line.

## Method

Enumerated every `AGENTS.md` under the fleet tree and the agent-deck homes (7 files), read each identity-bearing header in full, then traced the two tokens the row names (`pilot-gen45`, `gen117-glm`) to their exact locations across role files, seed docs, and logs.

## Verdict per AGENTS.md

| File (mtime) | Verdict | Why |
|---|---|---|
| `implementer/AGENTS.md` (2026-09-16 08:13) | **FRESH** | "You are kiln-flash" with the current-arrangement block; explicitly explains the retired `worker-glm-2` name and the 2026-09-15 reassignments. This is today's fix, confirmed on disk. |
| `implementer/repo-glm-dsh3/AGENTS.md` (modified, uncommitted) | **FRESH, not durable** | "You are corvid-dsh" arrangement block (2026-09-16) — but it is a 49-line **uncommitted worktree addition** on `work/glm-dsh3`. Canonical `implementer/repo/AGENTS.md` has no arrangement block at all. Same durability class as the S3-7 checker-suite finding: identity context lives in one lane's uncommitted files. Recommend landing the block canonically. |
| `implementer/repo/AGENTS.md` (2026-09-09) | identity-neutral | No seat identity; pre-furlough generation-loop content, clearly labeled historical and superseded by the reset docs. Nothing to misdirect a seat about *who it is*. |
| `implementer/repo-glm-dsh2/AGENTS.md` (2026-09-11) | identity-neutral | Same as canonical. |
| `reviewer/AGENTS.md` (2026-09-09) | **STALE — the one that acts** | Titles itself "**worker-glm-3** — memory-bakeoff reviewer": a seat that no longer exists. Tells its reader it "act[s] only when conductor-glm dispatches" (conductor-glm is furloughed) and "never start[s] work on your own" (contradicts the pull-based queue every current seat runs on). Names the implementer "worker-glm-2" (now kiln-flash). Declares the implementer tree read-only for the reviewer — false for corvid-dsh, who works in `implementer/repo-glm-dsh3`. Any future cold seat booted into `reviewer/` would obey all of this. Needs a current-arrangement banner at minimum (corvid-dsh identity, pull-based queue, furlough state), or retirement of the file. |
| `~/.local/share/agent-deck/conductor/glm/AGENTS.md` (2026-09-14) | accurate-but-dormant | Identity (`glm`, session `conductor-glm`, Muse Spark via acp-muse since 09-14) is current and truthful; the seat is furloughed by fleet policy, which is state, not file staleness. No stale tokens inside. |
| `~/.local/share/agent-deck/conductor/claude/AGENTS.md` (2026-09-14) | accurate-but-dormant | Same: identity truthful, documents its own 09-14 engine switch; furloughed by policy. |

## Where the two named identities actually live

Neither token appears in any AGENTS.md. Both are **era-correct locator references in day-0 seed docs**, superseded by the current tree but not annotated as such:

- **`pilot-gen45`** — `implementer/dispatch/operational-handover.md:9` presents `/var/home/bmosher/pilot-gen45` on "the Linux Strix host" as "**Live repo**". The directory still exists on this host, but the fleet's live tree has been `/var/home/bmosher/memory-bake-off` since the 2026-09-12 briefing. Also in `implementer/dispatch/MEMORY_BAKEOFF_RESET_PLAN.md:61,71-72` (day-0 investigation `rg` patterns — executed) and `conductor/glm/task-log.md:40` (handover history, accurate as history). The handover doc opens "Project work is paused. Nothing is running," which dates it — but it carries **no superseded-by banner**, so a cold seat handed it today would go looking for a pilot-era checkout as the working state.
- **`gen117-glm`** — `operational-handover.md:24`, in the old repo's **branch list** (`bakeoff-handoff-gen110…gen124`, `gen117-glm`, `reader-layer-gen85`). A branch name, not a seat identity; stale only in the same "day-0 snapshot" sense.

Disposition recommendation (owner's call): a one-line banner on `operational-handover.md` — "SUPERSEDED 2026-09-12: live tree is `/var/home/bmosher/memory-bake-off`; see `BRIEFING-20260912.md` / `MISSION-20260912.md` / `team/QUEUE.md` roster" — rather than rewriting a historical document. The current cold-start corpus (`MISSION-20260912.md`, `BRIEFING-20260912.md`) is clean: zero hits for either token.

## The "four queue rows" claim, measured

`worker-glm-2` appears at queue lines 97, 99, 103 — **three rows name it as released prior owner** (35 DIGEST-V2, 36 corpus-v1, 40-R2H REV-3; all now done) — plus line 122, which is row S4-7's own text. Kiln's arrangement block says "four queue rows named it as owner": measured count is three owner rows plus this audit row's mention. Minor, but recorded so the next census doesn't inherit the imprecision.

## Boundary

Startup/lane configs (`~/.config/agent-deck/acp-*`, `start-sessions.sh`, `autostart.txt`, the `.bak` lane files) can also encode stale seat names, but they are outside this row's declared artifact ("audit every AGENTS.md"); flagged for cairn as possible follow-up, not audited here.
