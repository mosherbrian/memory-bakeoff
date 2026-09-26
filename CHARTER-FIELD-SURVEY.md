# Charter: agent-memory field survey and expert position

Status: APPROVED by Brian 2026-09-26 (answers below). In force from 2026-09-26. Campaign4 moves to Prove mode only (see Decisions).

## Purpose
Form and keep an expert position on agent memory that Brian can act on. The position must be broad (the whole field, not one claim), critical (it separates solid results from hype), and applied (it says what fits Brian's setup: Claude Code, Pi, local models on Strix Halo, and admin, rollout and model-testing work).

## Deliverables (living documents, updated every cycle)
1. **Field map.** A taxonomy of memory approaches (session notes and auto-memory, retrieval stores, compaction and summaries, knowledge graphs, learned procedures, and others), the main systems in each, key papers, benchmarks and their known flaws, and our own results. Every entry has a source and a confidence level.
2. **Position memo (one page, the main product).** Ranked bets: "for your use, do X because...". It also covers what is overrated and why, the open frontier, and what evidence would change each position.
3. **Question register.** Open questions, ranked by decision value times uncertainty, divided by the cost to answer. Each question is marked "answered by the literature", "answerable by a cheap probe", or "needs proof".
4. **Probe log.** Small experiments, each one linked to the register question it answers and to the memo line it changed.

## How work is done: three modes
- **Explore (default, most of the effort).** Read widely, compare claims, and write positions. The main instrument is synthesis, not checksums. Output: map and memo changes.
- **Probe (when the map shows that a question is decisive and unanswered).** Cheap and fast: hours, not days. Rigor matches the stakes. A probe may be run by hand and read by a person. Output: one probe-log line and a memo change.
- **Prove (rare).** Use the campaign4 machinery only when a claim will drive a deployment or rollout decision and a wrong answer costs real time or money. It needs Brian's approval.

## Rules
- Every claim carries a source and a confidence level. "Unknown" is a valid answer.
- Rigor is proportional to the decision the claim feeds.
- Every cycle must change the memo or the register, or say plainly "no change, because...".
- No repair chains. If a tool blocks a result, fix it once. After two fix packages in a row without a result, stop and tell Brian.
- A review asks: does this defect change the conclusion? If not, log it and move on.
- Reuse first. Before any probe, check published work and our own past results.

## Roles
A research panel, not an audit line (see survey/ROLES.md): Tern is the lead synthesist; corvid is the Contrarian; kiln is the Practitioner and field scout; cairn is the Reader and literature sweeper. Everyone writes signed opinions with confidence levels. The memo keeps a Dissents section. Brian approves the positions that drive real changes, and every Prove.

## Cadence and budget
- One cycle = one memo update. Target: two or three cycles each week.
- Budget: [Brian to set].
- The first cycle must deliver: a first field map built from existing material (the bake-off results, the research cards, the KnowledgeDrift ranking, R61/R68) plus the published literature, and a first position memo.

## Success
- Brian can read the memo in five minutes and act on it.
- A knowledgeable outsider would find the memo credible and well sourced.
- Each position can be traced to its evidence.

## Decisions (2026-09-26)
1. Scope: agent memory in general (all agent types, not only coding and ops). The position memo still says what applies to Brian's setup.
2. Audience: Brian first; the team at work second. Positions should be shareable with the team.
3. Lead: Tern, with more reasoning effort ("brain-expanding") and proportional rigor ("chill pill"): higher effort, a fresh context, this charter in place of the campaign4 package loop, web and literature reading allowed.
4. Horizon: first position memo by 2026-09-29; stable position by the Go reset on 2026-10-14. Brian wants ongoing, observable readouts all through.
5. Campaign4 (decided by Claude on Brian's delegation): Prove mode only. No new repair or qualification packages. R73 is declined. The R71/R72 machinery is parked, ready for a Prove request. R68 stays as the accepted result.

## Readouts (observable all through)
- `survey/READOUT.md`, rewritten by the lead at the end of every cycle, with these parts: what changed in the memo; top 3 open questions; what is next; confidence changes. Plain language, at most one screen.
- Claude publishes READOUT.md, the position memo and the field map as a private dashboard page for Brian, and refreshes it at each cycle end.
- The lead sends Claude one line at each cycle end (notify-claude).
- Stall rule: no READOUT change in 24 hours means the survey is stalled, and Claude reports it.
