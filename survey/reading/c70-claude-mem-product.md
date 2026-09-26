# Reading note c70 — claude-mem: is independent capture + task-time delivery actually supplied?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 70.**
Skeleton first; **one current primary product source, exact identity first**; no paper rereads,
no sweep, no probe, no install. Inherited profile on file: FTS/semantic-policy evidence from the
prior bake-off only — narrower than a capture/delivery evaluation. Questions: (1) is independent
capture plus task-time delivery **supplied**, (2) what **fixed context budget** and **failure
visibility** exist, (3) what **outcome** supports replacing the native-index path. Contrast with
existing ReMe/Hindsight cards only. Partial evidence is sufficient for a bounded recommendation.

*(facts + verdict appended below)*

## Identity (verified via GitHub API, 26 Sep 2026)

**thedotmack/claude-mem** ("Claude-Mem"), Apache-2.0, ~94.7K stars, pushed **today** — active;
author Alex Newman. Installer caveat stated by the repo itself: `npm install -g claude-mem` is
the **SDK/library only** and does **not** register hooks or the worker — plugin install is the
real product. Provenance noise kept attached: a third-party "CMEM" token officially embraced by
the creator. Cloud sync to cmem.ai is optional; local worker + SQLite + Chroma by default.

## Q1 — Is independent capture + task-time delivery supplied?

**Capture: supplied, mechanism-level.** Five lifecycle hooks (SessionStart, UserPromptSubmit,
PostToolUse, Stop, SessionEnd) record tool-use observations; semantic summaries; SQLite + Chroma
hybrid search; local Bun-managed worker with HTTP API and web viewer. Hooks fire mechanically —
**independent of the acting agent noticing**, the c69 trigger-independence property, genuinely
implemented. `[read]`

**Delivery: two paths, neither outcome-tested.** (a) SessionStart **injection** — "context from
previous sessions automatically appears", configurable ("what context gets injected") — the same
inject-an-index family as the native path Brian's stack fails in, with no stated fixed cap, only
"fine-grained control". (b) **On-demand MCP search** (search → timeline → get_observations,
~50–100 tokens/result index tier, ~500–1,000 full tier, claimed **~10× savings**, author figure,
no method) — but this path requires **the actor to decide to consult**, the exact second kind the
corpus flagged as paying worst. `[read]`

**Failure visibility:** pipeline visibility yes (worker logs, web viewer, citations by ID);
**delivery/application visibility undocumented** — nothing shows an injected item was loaded,
let alone followed.

## Q2 — What outcome supports replacing the native-index path?

**None.** No accuracy or retention benchmark in the primary; stars and activity are adoption, not
outcomes; the token-savings figure is unmethodologized. Same lesson as c64/c67: mechanism plus
adoption ≠ measured benefit.

## Contrast with existing cards (no re-reads)

**ReMe** adds read-time utility footers — claude-mem has citations but no per-record usage
signal. **Hindsight** integrates reflection over an experience bank — claude-mem summarizes
sessions but adjudicates nothing: nothing marks an observation invalid (the c68 gap survives
adoption intact).

## Verdict — bounded recommendation with unknowns

**A coherent, actively maintained capture/delivery product whose capture is real mechanism and
whose delivery is plausible but unmeasured; it does not address the reported bottleneck
(application), so it is a strong comparator, not an outcome-backed replacement of the native
index path.** Non-blocking unknowns: actual injection budget under load, delivery-failure
surfacing, summary staleness policy. Supports Tern's enforcement-first pilot ordering; adopting
claude-mem would add supply where the failure is authority.

**Confidence: high on identity and supplied mechanism (primary read today), high on absence of
outcome claims in the primary (searched it), medium that the injection path shares the native
truncation family (README-level inference, budget internals unexamined).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md (sponsor section), both roadmap inputs,
COVERAGE.md, systems/cc-safety-net.md context.