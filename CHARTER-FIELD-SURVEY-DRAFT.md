# DRAFT charter: agent-memory field survey and expert position

Status: DRAFT for Brian (2026-09-26). Not in force. Campaign4 continues until Brian approves a switch.

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
- **Lead synthesist:** a model that is strong at broad reading and judgment. It owns the map, the memo and the register.
- **Critic:** it challenges the positions, finds weak evidence, and grades each flaw by whether it changes the conclusion.
- **Prober:** it runs the probes.
- **Brian:** approves the memo positions that drive real changes, and approves every Prove.

## Cadence and budget
- One cycle = one memo update. Target: two or three cycles each week.
- Budget: [Brian to set].
- The first cycle must deliver: a first field map built from existing material (the bake-off results, the research cards, the KnowledgeDrift ranking, R61/R68) plus the published literature, and a first position memo.

## Success
- Brian can read the memo in five minutes and act on it.
- A knowledgeable outsider would find the memo credible and well sourced.
- Each position can be traced to its evidence.

## Open choices for Brian
1. **Scope:** agent memory in general, or memory for coding and ops agents only?
2. **Audience:** only you, or also the team rollout at work?
3. **Lead model and where it runs:** ChatGPT in the web chat (it is good at this, but has quota limits and needs a handoff path), Tern with this charter, or Claude Opus or Fable as a fleet seat.
4. **Budget and horizon:** for example, first memo in 3 days, with a stable position by the Go reset on Oct 14.
5. **Campaign4:** pause it, finish the current package and then pause, or keep it only as the Prove mode.
