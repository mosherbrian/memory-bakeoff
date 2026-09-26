# Contrarian, cycle 18 — the rival is agent-directed reading of the raw record

**corvid · 2026-09-26 · cycle 18.** Signed opinion, not an audit. ROLES.md: *“the strongest case
AGAINST the current position memo, and for the best rival idea.”* Sources: Gen45 pilot, Ground
Truth First (2607.21962), GateMem (2606.18829), R68, ReasoningBank (2509.25140). `[read]`

**Rival: retained source + agent-directed lookup** (ReadAgent-style pagination / full-context
replay) instead of skill-bank and integrated retrieval. No extraction layer, no embeddings, no
observations: the executive reads the record, decides what to fetch, and cites it verbatim. ReadAgent
is the concrete method (Lee et al., 2402.09727 — panel’s source, not independently re-read here).

**When retention + executive reading spares a second interpretation layer.** When the task corpus
is small and query volume is low: every fact stays verbatim, provenance *is* the source, and there
is no extractor/observer/opinion layer that can be wrong. Gen45 is the local warning against the
opposite move — arm B’s bounded composed view **lost 7/12 to 12/12** against stock replay, its
control tools were largely unused (6 patches, 0 transitions), and bounding per-request context
**did not bound total work** (337 requests, 3 timeouts). Ground Truth First: full rendered history
**ties or beats** the best memory system at the short horizon and shows no judge-independent
advantage at nine weeks, at ~2× read cost. So replay is the incumbent a memory layer must displace,
not a strawman. For preferences, reading the raw record also avoids the observation/opinion layer’s
own drift — relevant given the near-duplicate/dedup fold risk noted in c16.

**Price reasoning, not storage.** Replay pays input tokens per request (≈quadratic; Ground Truth
First’s 2× read cost). Agent-directed pagination instead pays **query-time reasoning and lookup
decisions** — and can fail by *selection*: stopping early, missing the page, or ignoring the lookup
tool (Gen45; ReasoningBank’s own note that MemGPT “will often stop paging … before exhausting” the
store). Neither cost is storage. And **index delivery is not capture superiority**: R68’s index
delivery produced 2/2 correct runs with no s2 read, so an auto-injected index can look like success
while the retrieval question is untested.

**Where this beats c17’s integrated preference layer for Brian.** For compact, repeatable
model-test/rollout evidence (logs, configs, short transcripts), raw-record reading is simpler,
verbatim, and has no service upkeep; it also keeps procedure/applicability checks where they belong
(artifacts), which no integrated read solved. Checkers are not exclusive to native files, but the
raw record is the cheapest place to put one.

**Smallest conditions that reverse me.** When retained history grows enough that per-query reading
exceeds budget (many sessions × many queries), when cross-session entity aggregation is required,
or when lookups are frequent and the agent demonstrably stops early — then an index/service earns
its place. **Medium confidence**; the reversal is measurable, not hypothetical.

— corvid. `[read]` Gen45, 2607.21962, 2606.18829, R68, 2509.25140 fetched/read previously; ReadAgent
per panel source. No experiment.
