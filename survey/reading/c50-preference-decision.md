# Synthesis c50 — preference evidence c46–49: what actually changes the arrangement

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 50.**
Own c46–c49 only; no new source. Carried qualifiers: same-model controls outrank headlines;
constructed preferences still define an intended task; static summary mistakes aren't
longitudinal rot; stage percentages aren't independent causes; a human comparator isn't a
ceiling; architecture-compatible ≠ deployed; no per-record audit, no teaching obligation, Brian
is not the librarian.

## Discriminates an action

**1. Written rules beat example-replay at fixed executor (c49: 78.5 → 91.2 unseen, same model).**
When examples reveal a useful distinction, retain an **editable inferred rule** instead of
replaying raw examples or requiring training. Brian's files already do this; nothing to install.

**2. Derived memory without the raw record loses the reasoning layer (c46: RAG over raw messages
beat Mem0's derived facts, smallest gains exactly on *revisit-reasons*; c48: single-turn
baselines ≈ No-Memory).** Action: the rule layer is an **index, not a replacement** — keep raw
sessions recoverable; point each rule at what supports it.

## Does NOT discriminate

**1. c47's 55.2%/16× headline.** Trained-policy + memory bundle, no fixed-executor isolation;
valid system evidence, attributes to no component — changes no arrangement decision.
**2. c49's 85% physical run and +6 human-summary comparator.** Different evaluation from the
91.2 textual number, stages not multiplicatively established, comparator not a ceiling — "invest
in the summarizer" is not yet an action, nor is any cost claim: correction burden is unmeasured
in all four sources.

## Changed advice (exact)

From "keep preferences as timestamped raw statements; resolve currency at read time" to:
**keep both — raw sessions recoverable, plus one editable inferred rule per recurring domain
where examples show a distinction, each rule carrying pointers to supporting evidence and a
revisable scope; explicit directions bind independently of any rule.** No staged teaching,
no summary-review duty on Brian; upkeep stays with the agent.

## Remaining unknown

**In-situ application accuracy.** All four endpoints are recognition (c46/c47), simulator-fed
(c48), or third-party rated (c49). Nobody measures whether the *right* rule fires on the right
query in a real assistant. If written rules misfire more often than read-time reasoning from raw
logs, the rule layer is net negative — this untested assumption would reverse the recommendation.

**Confidence: medium in the changed advice; high that the two discriminating controls are the
strongest in this set; high on correction-burden absence (searched in all four).**

— cairn. Built solely from reading/c46–c49.