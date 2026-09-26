# kiln (Practitioner) — roadmap reconciliation addendum

**kiln · 2026-09-26 · follow-up to kiln-c1 · docs/reading only, no installs, tests, or probes. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack."**

## Responsibilities vs services

The five responsibilities (lossless history; explicit state/lifecycle; semantic/causal retrieval; bounded working memory; one context composer) are jobs to be done, not products to buy. No single named service below covers all five — that is the point of the architecture matrix the roadmap still lacks. Each shortlist row names one layer, the mechanism question it would answer, and a builder's verdict. All confidence is low–medium: this is historical-intake reuse (Phase 2 roadmap + Gen124 reconciliation + Gen125 field refresh/intake by reference), not hands-on experience.

## Reading shortlist (mechanism-based)

| # | Candidate | Layer | Distinct unanswered mechanism | Verdict | Evidence / unknowns |
|---|-----------|-------|-------------------------------|---------|---------------------|
| 1 | pi-lcm | 1 · lossless history | Does a branch-aware, replayable canonical event DAG actually survive as the substrate everything else derives from? | **watch** (candidate, not winner) | Roadmap's best substrate match; but Gen45 live pilot tested a composed view, not the full five-layer stack (7/12 vs 12/12, control largely unused — read PI_STATE_CONTROL_GEN45 before generalising). Unknown: replay/branch cost on Brian's Pi in practice. |
| 2 | pi-observational-memory (OM-like projection) | 4 · bounded working memory | Can continuous compression/synthesis keep "what to think about now" without becoming a competing source of truth? | **watch** | Strongest observed working-memory match per roadmap; failure mode is projection-as-truth plus duplicate compaction ownership. Unknown: behaviour on Brian's admin/rollout tasks vs the measured sessions. |
| 3 | Membukkit | 3 · structured retrieval/routing | Does bucket/routing structure give scope/config/current-state separation, or just topical clusters with stale state inside? | **watch** | Explicitly the roadmap's high-priority open question; our controlled result (routing ≈ dense scan on stress) does not answer it. Unknown: scan fraction unmeasured; no Phase-2 admission run. |
| 4 | StateMem / MemStrata (or reference repro) | 2 · explicit state/lifecycle | Conservative evidence-backed supersession with valid-time vs transaction-time kept apart — does any runnable code actually do it? | **watch** (repro if no product path) | StateMemBench search came back NOT FOUND per reconciliation; MemStrata needs a reproducible local path. Unknown: whether either is more than a paper. Do not buy; reproduce-or-skip. |
| 5 | Claude-Mem (real coding-memory system) | 4/5 · working memory + composer adj. | Does a production coding-memory's compression/compaction beat files-plus-handoff on recurring model-test/rollout work? | **watch** | Real system on coding-memory leaderboards; our earlier controlled read (90-day window artefact) is a configuration caution, not a verdict. Unknown: install/maintenance weight on Brian's box; needs Phase-D admission before any claim. |

## What I would not do (builder's view)

- Not install any of the five this cycle: Phase-D admission machinery exists and is idle — use it before any product touches Brian's stack.
- Not treat pi-lcm/OM as assumed winners: they are architecture candidates with one negative pilot between them, not a validated composite.
- Not confuse benchmark absence with nonexistence: unlocated names (StateMemBench repo, MemStrata runnable) are unresolved identities, per commission.

## Fit for Brian's stack

Claude Code scoped notes + files-plus-lexical on Pi/local remain the deployed baseline (kiln-c1). Everything above is watch-listed behind a named mechanism question and a Phase-D gate. **Medium confidence** in the baseline; **low** in any product pick — same split as Tern's memo, from the same reason: no Phase E/F evidence yet.
