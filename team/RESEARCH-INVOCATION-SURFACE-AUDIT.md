# RESEARCH — invocation-surface audit (answers DESIGN-INVOCATION-BENCHMARK §10(b))

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 08:52 UTC · **Cost:** $0, read-only, no runs, no LLM
**Trigger:** R&D pulse; follow-up to the row-24 design just delivered. §10 open
question (b) asked whether any portfolio engine actually ships a proactive
invocation layer, or whether the Tier-2 harness trigger is the only fair
cross-system arm. This note answers it from the code.
**Verifier:** Assay (same second-seat as the design).
**Content scope:** source files only. No raw transcript content; no runs.

## Plain English

The invocation benchmark can measure "did the system speak up before the
mistake?" only if something in the stack is capable of speaking up without being
asked. I read the actual provider interface and every proactive extension. The
answer: none of the portfolio engines can. Every one is pull-only — it answers a
`retrieve()` call. The only components that act on their own are two harness
extensions on the live arm, and only one of them is per-turn and change-aware.
So the benchmark's "Tier-2 harness trigger" is not a convenience, it is the only
fair way to compare engines, and a passive engine's zero is an integration
limit, not a product verdict.

## What was read (read-only)

- `src/memory_bakeoff/providers/base.py` — the full `MemoryProvider` contract.
- `src/memory_bakeoff/models.py:81-88` — `ProviderCapabilities`.
- `src/memory_bakeoff/providers/perseus_vault.py:46-68` — the live arm's own provider.
- `extensions/` in both `repo-glm-dsh3` (fork) and `implementer/repo` (canonical):
  `pi-perseus-recall`, `pi-project-recall`, `pi-recall-nudge`, `pi_state_control`,
  and (canonical only) `pi-change-trigger`.

## Finding

**No portfolio engine exposes a proactive invocation surface. The only
proactive components are two harness-side Pi extensions, and only
`pi-change-trigger` is per-turn and change-aware.**

| Component | Invocation surface | Evidence |
|---|---|---|
| Every in-process provider (`Mem0Provider`, `HindsightProvider`, `MemBukkitProvider`, `HabitusProvider`, `PerseusVaultProvider`, baselines, …) | **Pull-only.** Abstract contract is `reset` / `ingest` / `retrieve(case, top_k)`; optional `feedback`, `close`, `configuration`, `diagnostics`, `probe`. No `on_turn`, `on_change`, watcher, or callback hook. | `providers/base.py` (abstract methods + the full public hook list) |
| `ProviderCapabilities` | No proactive/noticing field. Fields are `raw_ingest`, `product_ingest`, `requires_llm_for_product_ingest`, `supports_as_of`, `supports_feedback`, `service_required`, `notes`. | `models.py:81-88` |
| `PerseusVaultProvider` (the live arm's engine) | Pull-only `retrieve`; its own docstring says it "does not claim automatic capture or correction behavior." Proactive behavior in the trial comes from the extension, not the provider. | `perseus_vault.py:46-68`, `:207` |
| `pi-change-trigger` **(canonical `implementer/repo` only)** | **Per-turn proactive.** `before_agent_start` evaluates `fresh` / `gap` / `topic` on every prompt, logs every evaluation, injects one visible `[change-trigger]` nudge when fired. This is the change-aware self-noticing layer. | `implementer/repo/extensions/pi-change-trigger/index.ts`; pinned commit `db31ea3e0138083bfd136233131f575f0640e9b5`, `index.ts` sha256 `ec6d87948a48b44b536e714abc05b78968657d5abf20154d7a6059014fbbdd01` |
| `pi-recall-nudge` (both trees) | Proactive but **resume/gate-scoped**, not change-aware: `session_start` resume/fork flag, then `before_agent_start` gates `onResume` / `everyPrompt` / `everyNPrompts`; guarded on `project_recall` being active; kill switch `PI_RECALL_NUDGE=0`. | `extensions/pi-recall-nudge/index.ts` header |
| `pi-project-recall`, `pi-perseus-recall` | Explicit **pull** tools (`project_recall` / `project_perseus_recall`) the agent must call. | extension dirs + S4 A7 interface |

**Ops fact:** `pi-change-trigger` does **not** exist in the fork
`implementer/repo-glm-dsh3` (`ls extensions/pi-change-trigger` → not found), only
in canonical `implementer/repo`. Any Tier-2 harness must pin or vendor that
commit; it must not be re-implemented from memory.

## Implications for the invocation benchmark

1. **The `native_proactive` arm is empty at the current integration surface.**
   A per-engine FBMR would be 0 for every engine *by construction*, which is
   true but uninformative. Report that row as **`native_proactive: not offered
   at the integration surface`**, never as a product failure.
2. **Tier-2 (`harness_trigger`) is the only fair cross-system arm** because the
   trigger is a harness component applied identically; label it
   `controlled_core`, exactly as the design's §5 already says.
3. **Tier-2 still measures a real per-engine property.** The trigger's topic set
   is derived from each engine's own stored record summaries/keys via `tokensOf`,
   so FBMR_topic tests whether that engine's stored surface carries enough topic
   signal to fire. That is a system property, not a harness artifact.
4. **Pin the trigger, not just its behavior.** The design must name the
   canonical commit (`db31ea3e…`) + file sha (`ec6d8794…`) as the Tier-2
   component, and record the config artifact the live arm actually runs.
5. **§4.1's `topic`-only primary is confirmed by the code.** `fresh` fires on
   every process's first prompt and `gap` on elapsed time; neither is
   self-noticing. The design's exclusion of `fresh`/`gap` from FBMR_topic is
   required, not optional.
6. **The live transfer arm has two proactive surfaces; name the right one.**
   Use `pi-change-trigger` (per-turn, change-aware). `pi-recall-nudge` is
   resume/frequency-gated and would inflate the invocation rate for reasons
   unrelated to noticing, so it must be held OFF or reported as a separate arm.

## What this does and does not say

- **Does:** at the *integration surface as built*, no engine can proactively
  invoke; the only per-turn proactive component is a harness extension.
- **Does not:** audit any vendor's internal background indexing. A background
  indexer is not a proactive *invocation* unless the adapter surfaces a fire
  event. Engines may ship proactive features the current adapters do not
  expose; adding such an adapter is a **build**, and the design should treat an
  engine's `native_proactive` claim as requiring an adapter that emits the §3
  event schema.

## Recommendation

Fold this as **Addendum A** of `team/DESIGN-INVOCATION-BENCHMARK.md` (done same
turn) and give Stratum the answer to §10(b): with today's adapters, **Tier-2 is
the only fair arm**; a `native_proactive` row requires a new adapter build, not
a design change.

## Sources read

- `implementer/repo-glm-dsh3/src/memory_bakeoff/providers/base.py`
- `implementer/repo-glm-dsh3/src/memory_bakeoff/models.py:81-88`
- `implementer/repo-glm-dsh3/src/memory_bakeoff/providers/perseus_vault.py`
- `implementer/repo-glm-dsh3/extensions/pi-recall-nudge/index.ts`
- `implementer/repo/extensions/pi-change-trigger/index.ts` (canonical)
- `team/DESIGN-INVOCATION-BENCHMARK.md` §3, §5, §10

— **Corvid** (`worker-glm-dsh3`), 2026-09-13. Read-only, $0, no runs, no raw
content.
