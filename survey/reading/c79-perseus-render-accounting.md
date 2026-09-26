# Reading note c79 — Perseus render accounting: is there a no-silent-omission contract?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 79.**
Skeleton first; **requirement 2**, bounded source read only (no wheel import/run, no model calls,
no runtime tests, no whole-file audit). Source root:
`/tmp/claude-1000/-var-home-bmosher/09b5ba50-67c7-4535-b27c-5baa3e1c4fa8/scratchpad/perseus-pkgs/`
(hashes/identities in `receipts/c78-perseus-source-20260926.json`; Context Engine 1.0.26 = one
large `perseus.py`, targeted reads only). Questions: when an include **fails**, is **excluded by
tier/condition**, or **changes after source publication** — what evidence do `render`/`--explain`
give? Does the shipped **execution manifest** account for **intended versus actually emitted**
material, or only executed directives? Keep the resolved `prompt-size` strict gate separate (not
re-checked). Deliver: does an existing **no-silent-omission contract** exist for one narrow path
(possibly strict render), and precisely which paths remain outside it. Stop at named unknowns.

*(trace + verdict appended below)*

## What the source shows (perseus.py 1.0.26, targeted greps/ranges only)

**Include failure → in-band visible warning.** `@include: file not found: <path>` renders as a ⚠
block **inside the output** (same pattern for `@read` missing file/key, missing tool executable,
plugin validator errors). A missing source cannot vanish silently from a render.

**Tier exclusion → Context Manifest appended to the render.** Skipped directives are recorded
(name, tier, summary, line) and emitted as a "📋 Context Manifest — Tier limit" block with
re-run hints (`--tier 2/3`), whenever tier limits caused skips.

**Source change → drift warning.** "⚠ Integrity drift: `<path>` was modified/deleted during
render" — the changed-after-publication class is surfaced **when the change happens during
render**; a change between renders is simply a different render.

**`--explain` execution manifest:** JSON with per-directive entries, the skipped list, cache
stats, version, and a stable `render_id` (feedback loop hooks). So the manifest accounts for
**executed + tier-skipped** material — intended-vs-emitted for the tier class, not merely
executed directives.

**Config-declared size boundaries:** `max_include_bytes` 512 KB cap, depth 5; a per-include
size **warning** exists but is **default-off** (`max_include_warn_bytes: None`).

## The contract, and precisely what stays outside

**Yes — a no-silent-omission contract exists on the narrow compile path (render/--explain):**
missing includes, tier skips, and during-render drift all produce visible evidence, in-band or in
the manifest. It is a **visibility contract, not enforcement**: nothing blocks emission on
omission; the only hard gate remains `prompt-size --strict` (the already-resolved separation,
not re-checked).

**Outside it:** (1) **post-render delivery** — the manifest certifies the render, not what the
host later sends or truncates (Brian's boundary stays upstream-of-manifest); (2) **windowed
content** — whether `last=N`/`since=` truncation is surfaced: **named unknown, not verified**;
(3) oversized-include warning default-off; (4) `@budget` inside an `@include` not enforced
(documented, prompt-size warns); (5) false `@if` branches are author intent, not logged as
omissions — correct by design but worth naming.

**Cell delta proposal:** Perseus render-accounting **requirement 2: partial → yes-narrow**
("compile-path omission visibility: missing/tier/drift surfaced; enforcement separate; host
delivery outside"). Not a load bound for any host row.

**Confidence: high on the four evidence channels (direct source lines), high on
visibility-not-enforcement (manifest emits, no raise), medium on the outside-list completeness
(two named unknowns: window-truncation surfacing, manifest persistence defaults).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c78.md, systems/perseus-context-engine.md,
systems/perseus-ledger.md.