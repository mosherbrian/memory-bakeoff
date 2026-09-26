# Reading sweep — recoverable history vs lifecycle projection

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 4.**
Signed opinion, not an audit. Commission (Tern): compare **one recoverable-history / compaction
method** with **one lifecycle-projection method**, emphasising (i) exactly what source can be
recovered and (ii) whether **old truth is still distinguished from current truth**.

Provenance key: `[read]` = primary source opened today 2026-09-26; `[ours]` = our measurement.

---

## Per source

**1. SKILL.state: Scalable Long-Horizon Agent Skills** — arXiv:2608.26263, full text. `[read]`
**Located at source at last** — Brian's named State example was an unverified lead in our notes
since cycle 1; this closes that gap, and two of his recorded expectations check out: the state
is a structured schema (5 fields reused across 100 CTF tasks), and the failure modes include
unknown schemas and delayed relevance. **Mechanism:** the model receives only (immutable skill
spec, structured state, latest observation); after each validated state transition the
intermediate reasoning trace is **discarded**, and the state is treated as a *sufficient
statistic*. **What is recoverable: nothing.** There is no recovery path — the discard is
terminal; recovery exists only inside the state schema. Their own Limitations concede the two
regimes this breaks: (2) an early observation whose relevance was not recognised was never
committed to state and cannot come back; (3) any task defined over the trajectory itself
(auditing, debugging provenance, explaining past actions) fails **by construction**.
**Old vs current truth:** obsolete facts are physically absent, so they cannot poison — their
drift experiment shows the payoff (0 recovery turns vs 5–8 hallucinated turns for history
baselines) — but "old truth" is **destroyed, not distinguished**. **Numbers:** InterCode CTF
pass@1 54.2% vs 43.2% ReAct, prompt 813 vs 1,909, cumulative tokens 387k vs 977k. **Note: the
"~16× shrink" figure circulating in our notes is not in the tables read**; measured here ≈2.5×
tokens, ≈1.3× on Sierra retail. Treat 16× as unverified. `[read]`
**Verdict: solid for bounded within-run execution; irrelevant-to-harmful for Brian's layer 1** —
it is the exact merge of prompt-exclusion and deletion that his corollary forbids. Confidence:
high (mechanism is stated outright, not inferred).

**2. pi-observational-memory (OM) V3 — the lifecycle projection** — primary docs at the pinned
archive `ce9fc98` (`docs/how-it-works.md`, `docs/concepts.md`, README). `[read]`
**Mechanism:** ledger-centred. Observations, reflections and **drops** are append-only ledger
entries; the memory the agent sees is a **projection folded from the ledger on the current
branch**; compaction payload is built deterministically from the fold. **What is recoverable:
everything the ledger holds, including dropped observations and their source evidence — but
recovery is id-addressed.** The `recall` tool "recovers source evidence for a 12-character
observation/reflection id" and is explicitly "not semantic search or a transcript browser." So
recoverability is real (Brian's corollary, implemented: *"Dropping does not delete history"*)
with a **discoverability ceiling**: if the id was never surfaced, the material is retained but
effectively unreachable. **Old vs current truth:** distinguished by **status, not time** —
observations are `active` or `dropped`; drops are tombstones written by a Dropper model call
that may judge an observation "superseded, redundant, or obsolete" but can only drop ids, never
rewrite or merge them. There is **no valid-time axis**: the projection shows what is active now
and never renders "this was true then." Supersession is a single model's judgement at drop
time — the same write-time-judgement risk we flagged in Zep (cycle 2) and the verifier-judge
risk in TrustMem (cycle 3). `[read]` `[ours:Gen27/28]` our runs add: strong context
production, **no query surface** — consistent with the docs' own "not semantic search."
**Verdict: solid — the best corollary-compliant shape we hold, with two named ceilings (id-
addressed recall; judgement-based drops).** Confidence: medium-high (docs + our two generations
of measurement agree).

---

## The comparison Tern asked for

| | SKILL.state | OM V3 |
|---|---|---|
| Prompt stays bounded | yes, strictly | yes (folded projection + compaction) |
| Source recoverable | **none** | ledger + source evidence via `recall` |
| Recovery reach | n/a | **only with a known id** |
| Old truth vs current | destroyed, not distinguished | status (active/dropped), **no valid time** |
| Who decides retirement | deterministic schema validation | **Dropper model judgement** |
| Trajectory tasks (audit, provenance) | impossible by construction | supported in principle, id-limited |

The two fail on opposite halves of Brian's corollary. SKILL.state keeps the prompt small and
pays with the past. OM keeps the past and pays in reach (ids) and trust (who judged the drop).
Neither carries **time** — no system in this pair can answer "was this true in March?", only
"is it active?" (OM) or nothing at all (SKILL.state).

## The one idea in this area that most deserves our attention

**Recoverability has two independent ceilings — deletion and discoverability — and our stack
currently fixes the first while ignoring the second.** OM proves exclusion ≠ deletion on our
own measurements; it also proves that retained-but-unaddressable is functionally deleted for an
agent that never learns the id. The cheap mechanism is the one Supersede (cycle 2) lacked and
Zep prints: the projection should carry **stable handles** (ids + provenance + status) for what
it omits, so omission is a pointer, not a disappearance. For Brian's composite: SKILL.state's
schema discipline is right for **within-run state only**, under a substrate that never discards
(pi-lcm class), with OM-style tombstones and **id-bearing omissions** as the bridge.

**What would change my mind:** an OM probe showing the agent reliably recalls ids it saw once in
the projection (raising the real discoverability ceiling above the doc's worst case); or a
SKILL.state variant with a write-through transcript log scoring no worse — at which point the
"deletion" objection becomes an implementation choice, not an architecture property.

— cairn, Reader. Sources `[read]`: arXiv HTML 2608.26263; local pinned archive
`bakeoff-archive/pi-observational-memory` (ce9fc98, sha256 `4ea7bba8…`), docs + README,
fetched/opened 2026-09-26.