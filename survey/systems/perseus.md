# System deep-dive — Perseus (decision memory): has the valid-time/admission problem changed?

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 2.**
Commission: compact Perseus deep-dive using our Gen29/Gen30 version-specific findings and the
current primary source paths. Question: **has the valid-time/admission problem changed, or is
that unknown?** Reading-only; no campaign work, no product run.

Provenance key: `[read]` = primary source opened today; `[ours:GenNN]` = our scored result;
`[live]` = observation from this lane's running integration today.

## Identity and what is reachable today

- Scored identity: official `perseus-vault` **v2.23.2**, commit `9c82920`, published hash
  `e9b0912c…` re-verified byte-for-byte in Gen29. `[ours:Gen29]`
- **The only reachable primary source is still that same v2.23.2.** I re-checked the vendor
  status page today: *"Source access is temporarily unavailable… GitHub-hosted source and
  release links are on hold while repository access is restored."* `[read]` The local source
  tarball (`~/bakeoff-archive/perseus-vault/source/perseus-9c82920.tar.gz`) is the only copy
  this host can open; its CHANGELOG stops at 2.23.2 (2026-08-26). `[read]`

## The defect, re-confirmed at source (v2.23.2)

Gen30's root cause reads out of the source directly: `models::Entity` (`src/models.rs:6`) —
the struct that carries an entity through the codebase — **has no `valid_from_unix_ms` /
`valid_to_unix_ms` fields**, while the schema and several parameter structs do (e.g.
`CorrectParams.valid_from_unix_ms`, commented "Application-time period (#363)"; `remember`
accepts it). `[read]` So the Gen30 mechanism follows structurally: any path that reads an
entity, mutates it and writes it back — which is exactly what `admission_decide(approve)` does
— re-persists through `Entity` and loses the application-time columns. Gen30 measured it:
`remember` honours `valid_from = T−200d`; approval rewrites it to the approval instant;
**serveable XOR retroactive**, no documented path yields both. `[ours:Gen30]`

## Has it changed? — **Unknown, with the defect standing in the only obtainable artifact**

Two facts, kept separate:
1. In v2.23.2 — the only source and release reachable today — the defect is **structural and
   still present** (source-confirmed above). `[read]`
2. Whether a newer release fixes it is **unknown**: the vendor calls the source hold temporary,
   but no newer artifact, changelog, or release note is obtainable, so this is not a "no change"
   finding. Any claim beyond v2.23.2 would be speculation. `[read]`

## New this cycle: the live pi integration is a *different* supersession design `[live]`

This lane runs a pi-facing Perseus surface (`project_perseus_remember/supersede/confirm`,
`source_kind pi-perseus-recall-decision-memory-v1`). Its lifecycle choices differ from the
vault paths Gen29/30 scored, and matter to our question:

- **Supersession is declared, not inferred.** `supersede` requires an explicit `from_key` +
  `reason`; the old record is retained (explicit lineage), cross-environment override is
  rejected unless passed explicitly, and keys are never reused. There is **no nearest-neighbour
  LLM judgement** — the failure the roadmap warns about ("nearest neighbor means replacement")
  is designed out by giving up inferred supersession entirely. This is the third distinct point
  on the spectrum: Supersede = rewrite-whatever-the-notes-say, Zep = write-time LLM judgement,
  pi-Perseus = declared lineage only.
- **History is preserved on correction** — Brian's corollary holds on this surface.
- **No valid-time parameter is exposed at all.** `remember` takes `source.timestamp` — a
  provenance stamp for the source event — not an application-time axis. The retroactive-valid-
  time capability remains unreachable from the agent write surface, same shape as Gen29's
  finding, now on the newer integration.
- **The admission/confirm step fails in a new way: starvation, not reset.** The draft→confirm
  gate is operator-confirmed by design; `[ours]` this lane recorded 59/88 lifetime drafts
  **expired unconfirmed**, including 5 consecutive expirations on 2026-09-19, after which the
  T0 agent-confirm tier was enabled. Gen30's admission step destroyed valid time; the pi
  admission step can starve records out of service entirely. Same lesson, different axis:
  **every admission gate is where the memory system actually fails** — the write path is never
  the problem.

## Successes preserved (unchanged, Gen29) `[ours:Gen29]`

Across three identical repetitions: `unmapped_provenance` **0** (exact native-ID provenance on
every hit), `scope_collapse` **0** (workspace isolation held), `future_leakage` **0**
(checkpoint discipline absolute), `false_supersession` **0**, both transaction-time
historical-belief cases **passed**, reads do not disturb the store. Scope and provenance are
this product's demonstrated strengths and nothing this cycle contradicts them.

## Verdict

**Watch, with a narrow deploy-now carve-out.** The decision-memory surface as run on this lane
(declared-lineage supersede, scoped, provenance-stamped, append-never-delete) is safe and
useful today for scoped decisions — we are living on it. The **bitemporal ambition remains a
schema promise the write paths do not keep**, in the only version we can verify, and the
admission gate is the demonstrated failure point in both forms measured (time reset in
v2.23.2 MCP; confirm starvation on the pi lane). Do not re-admit Perseus to scored testing
until a post-2.23.2 artifact is obtainable — per the roadmap, only a product change reopens it.
**Confidence: high** on the source-confirmed v2.23.2 structural finding and on the preserved
successes; **explicitly unknown** on upstream change; **medium** that the pi-lane starvation
pattern generalises (n=1 lane).

— cairn. Sources opened 2026-09-26: vendor status page (perseus.observer/source), local source
tarball 9c82920 (`src/models.rs`, `src/tools.rs`, `CHANGELOG.md`); Gen29/Gen30 input cards;
live tool schema of this session.