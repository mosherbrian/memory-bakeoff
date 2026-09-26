# Contrarian, cycle 13 — Letta does upkeep, but it does not detect a silent prerequisite change

**corvid · 2026-09-26 · cycle 13.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and the best rival idea.”* Primary source: Letta `reflection.md`
subagent prompt and Letta Code memory/subagent docs (source-level; vendor documentation, installed
behavior unmeasured). `[read]` vs `[design]` labelled.

**The concrete mechanism.** Letta’s maintenance is a **background reflection/dream subagent** over
a **git-backed MemFS**, with **agent-owned skills** under `$MEMORY_DIR/skills` and a `/doctor`
audit. The reflection prompt is explicit about the workflow: collect “**Mistakes and corrections**,”
“**Contradictions** — anything that conflicts with what’s currently stored,” and “**Reusable
procedures**”; filter for lasting vs ephemeral and already-captured; make **surgical** edits
(“never rewrite wholesale”); update a skill’s **Common Pitfalls**; commit with author and summary.
Skills are created “ONLY when the conversation reveals a reusable, multi-step workflow… Skills are
not the default.” `[read]`

**What it does for the hard case.** A previously successful procedure’s prerequisite changes while
commands still exit zero. Detection: **there is none specific to the change.** The documented
trigger is conversational — a correction, a contradiction the agent notices, a “pattern in your
mistakes” — surfaced on a step-count or compaction-triggered reflection, or a `/doctor` audit of
placement/duplication/token use. Exit zero leaves no error and no correction, so nothing fires
unless the outcome mismatch itself appears in the conversation. Finding affected procedures is
then memory/skill search; revising is a surgical edit + commit; preserving the failed alternative
is **git history** (the prior version survives in the repo), optionally recorded as a pitfall.
`[read]`

**Where the rival beats agent-maintained files, and where it does not.** Beat: upkeep is executed
by the agent on an automatic trigger, commits are authored and versioned for free, and skills
travel across workspaces — no Brian copy/sync/author role. Does not beat: **detection of a silent
prerequisite change is unsolved in both**, because both depend on a signal that exit-zero withholds.
The integrated system automates *who* does the upkeep; it does not supply *what starts it*.

**My proposed design (not in the source).** `[design]` Store, with each skill, an
**applicability predicate**: a cheap artifact/prerequisite fingerprint (version string, config
hash, checker exit) plus its last verified outcome, and re-evaluate it on trigger or cheaply on a
schedule. A flip marks the skill superseded, keeps the prior version, and routes to re-derivation.
Git-backed MemFS is a natural substrate for “keep the failed alternative.” This is the c2/c3
check idea made concrete; Letta does not implement it.

**Verdict.** Prefer the integrated system **for executing agent-owned upkeep and provenance**,
not because it detects silent change. The strongest reason to prefer it to agent-maintained files
is that it removes Brian from the loop and versions every edit automatically — **medium
confidence** — while the detection gap remains an open design problem in both.

— corvid. `[read]` Letta docs fetched 2026-09-26; `[design]` applicability-predicate inference. No
experiment, no installed-version claim.
