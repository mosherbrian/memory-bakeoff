# Jev/Laya practical card: hook source + 46-case design review

**kiln · 2026-09-26 · sources: fast-jev-compaction source (compact.ts/state.ts/hooks, read-only clone — replaces second-hand intake), rank-check.py protocol (read, not run), probe design cases.jsonl + manifest.json, Tern's jev-laya card + probe draft, team intake docs. No calls, no install. Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs, principles, COVERAGE as context.**

## Hook source (primary, not intake account)

PostToolUse hook asking two `noul` questions per tool call (keep the call / keep its result verbatim), default threshold 0.5, pinned protection (first message + newest N never candidates), three actions (keep / drop_result / drop_call), token-budgeted batching. Verified in source. The intake's "full text archived, nothing destroyed" was **not** verified in this pass (no archive path found in grepped files — unconfirmed, not refuted). Jev (hosted TypeSafe API) vs Laya (local impl, Mac daemon) kept distinct; `noul`/confidence is distribution-derived, not P(correct).

## 46-case design review (S10 trials → binary supersession)

- **Request semantics:** NDJSON persistent socket per rank-check.py pattern (write/flush/readline); each case sends state {old_record, new_record, query} + questions.superseded {instructions, type:noul}. Instruction is explicit (same entity+property+updated value; similar wording insufficient). Matches the S10 scope-trap design (substring entities, version upgrades on both sides).
- **Baselines pre-stated:** majority-no 33/46; whole-token rule 46/46 (computed read-only). Ceiling acknowledged: classifier cannot beat the rule — value is the FP/FN profile on harmful retirement plus selective-risk at p≤0.1/≥0.9, not the score.
- **Label leakage:** content-side is fair (versions rise in both classes; entity traps cut both ways). **One envelope risk:** cases.jsonl lines *contain* `gold`, `rule_prediction`, `family` alongside `request` — the frozen plan must specify that only the `request` object is transmitted. Unspecified today.
- **Model identity:** served checkpoint/temperature unrecorded by design (manifest says so); capture from replies if present, else report unknown. Threshold frozen 0.5, no tuning, ≤46 calls, timeouts, zero writes.

## Verdict: READY CONDITIONAL — one blocker

Specify + verify the transmit envelope (request object only; gold/rule_prediction never sent) in the frozen plan, and this is ready: fair inputs, honest baselines, bounded cost, no writes. Without that line, the blocker is label leakage by envelope. Map store/scope/staleness/relevance/retrieval honestly: this probe tests *staleness screening on supplied pairs only* — nothing about capture, scope creation, retrieval, or calibration at scale.
