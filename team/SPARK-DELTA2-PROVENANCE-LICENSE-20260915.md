# muse-drafter: watchlist-delta-2 provenance + license pass (spark pulse 2026-09-15)

Trigger 4 (new frontier candidates, `SPARK-WATCHLIST-DELTA-2-20260915.md`). All 8 items verified at ID level (arXiv API + abs pages); paper licenses read off abs-page license links; artifact links grepped from abs pages. **Candidate discovery only — no score import.**

| # | Candidate | ID verified | Paper license | Artifact surfaced |
|---|---|---|---|---|
| 1 | MemTX (transactional belief commit) | `2607.23929v2`, Li et al., 2026-07-27/28 | **CC BY 4.0** | none (abs page boilerplate only) |
| 2 | State-Aware Runtime (Cambridge Open Engage) | DOI `10.33774/coe-2026-vt9t2`, Xiwei Chen, v3 deliberation loop confirmed | n/a (COE working paper, not arXiv) | none (conceptual framework + agenda) |
| 3 | TraceCompiler (EPFL/Binome) | `2608.02680v1`, El Yadouni/Li, 2026-08-03 | **CC BY 4.0** | none on abs page |
| 4 | AgentProcessBench | `2603.14465v2`, Fan et al., 2026-03-15 | arXiv-nonexclusive | **`github.com/RUCBM/AgentProcessBench`** (abs page) |
| 5 | AgentTrails | `2607.18816v1`, Wu et al., 2026-07-21 | **CC BY 4.0** | none on abs page |
| 6 | HANDBOOK.md | `2607.25398v3`, Panavas et al., 2026-07-28 | **CC BY 4.0** | **`github.com/surge-ai/handbook`** (abs page) |
| 7 | AgentLongBench | `2601.20730v3`, Fang et al., 2026-01-28 | arXiv-nonexclusive | none on abs page |
| 8 | NetAgentBench | `2604.09678v1`, Twabi et al., 2026-04-03 | **CC BY 4.0** | none on abs page |

## Notes for carding (owner call)
- Version pins matter: AgentProcessBench v2, HANDBOOK v3, AgentLongBench v3 (API `published` = latest version date).
- Repo licenses (reconciled with parallel pulse `SPARK-WATCHLIST-DELTA-2-GROUNDING-20260915.md`, which ran first): `surge-ai/handbook` **Apache-2.0 (reuse-green)**; MemTX code **ARR (no license)**; TraceCompiler **no own artifact**.
- **`RUCBM/AgentProcessBench` repo license closed 2026-09-15: NO LICENSE file** (root listing: annotation_platform/data/eval/figs/utils/README only; About box shows no license; raw `main/LICENSE` 404s) → **all-rights-reserved until a license appears**. Read-only/design-reference posture like EvoMemBench. Data ships inside the repo (`data/AgentProcessBench/`, 1000 trajectories), so no separate dataset terms — same ARR cover.
- **Conflict flagged 2026-09-15:** parallel `SPARK-WATCHLIST-DELTA-2-GROUNDING-20260915.md` calls AgentProcessBench "data-MIT". Re-verified via GitHub API: root has no LICENSE; `data/` holds only `.DS_Store` + `AgentProcessBench/` + `AnswerOnly/` (no LICENSE); nested data dir holds only 4 JSONL files; README contains **zero** license/MIT/Apache/CC mentions (grep rc=1); GitHub license API returns **404**. The MIT claim is unsupported — treat as ARR. Card owner to adjudicate before any download.
- Strongest fits unchanged from the delta: MemTX (supersession-as-transaction, G1/G2) and HANDBOOK (stale-policy analogue with deterministic grader, stale-path concern).
- State-Aware Runtime v3 adds a deliberation loop (simulate → authorize one transition → observe → replan) — cite by DOI, never by name alone (generic phrase).

$0, API + abs-page reads, no Muse batching. — muse-drafter (Spark)
