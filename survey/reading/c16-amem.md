# Reading note — A-MEM: what one update actually touches — source, derived note, links

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 16.**
One source (Tern): **A-MEM, arXiv:2502.12110, methods.** Question: follow original content,
generated note/context and links **separately through one update** — does memory evolution
*replace source history* or *update derived representation*? Which retrieval/evolution controls
are evaluated; what remains unknown about **stale preferences/procedures**? ROLES frame: *"a
verdict per source: solid, oversold, or irrelevant for our goal"*; roadmap frame: layer-2
supersession must be *"conservative and evidence-backed rather than 'nearest neighbor means
replacement'"* — A-MEM's neighbour-triggered evolution is that exact mechanism, and my c3 read
already flagged it as history-rewriting with no provenance. This cycle tests that flag against
the primary text. Constraints honoured: no unsourced history-corruption analogy, no universal
retrieval-failure claim.

**Provisional frame (from c3 `[read]`, to verify or correct).** A-MEM builds atomic notes
(content + keywords + tags + LLM-generated contextual description); on ADD the LLM decides links
to existing notes by semantic + keyword overlap; EVOLVE prompts neighbouring notes to update
their tags/descriptions in light of the new note. My c3 claim: *"the original memory content is
kept, but neighbours' descriptions are rewritten with no provenance, no invalidation, no
tombstone."* Open questions for this read: (1) is note content itself ever mutated, or only the
derived fields? (2) which ablations exist — is evolution's contribution measured at all, and in
which direction can it err? (3) does any evaluation touch a contradicting later preference
(staleness), or only retrieval quality on LoCoMo-style QA?

*(facts + verdict appended after read)*

## Following one update through the three layers (A-MEM 2502.12110, §3.1–3.4, §4.4, App. B.3) `[read]`

**Note anatomy (§3.1):** each note = *(content x, timestamp t, LLM keywords, LLM tags, LLM
contextual description, link set)*. Content and timestamp come from the interaction verbatim.
The dense embedding — the retrieval address — is computed over **all textual components
including the generated ones**.

**What one ADD+EVOLVE actually mutates (§3.3 + App. B.3 JSON schema):** for each nearest
neighbour the LLM chooses *strengthen* (new link + tags) or *update_neighbor* (**new context +
tags**). The schema's output fields are `new_context_neighborhood`, `new_tags_neighborhood`,
`tags_to_update` — **there is no field for new content or new timestamp**. So: **evolution
updates the derived representation; source content and timestamp are never rewritten.** The
c3 flag stands, with one correction: I wrote that neighbours' *descriptions* are rewritten —
correct — but should have said explicitly that the content itself is untouched. The evolved
note object does *replace* the original in the set, unversioned: the interpretive layer is
overwritten with no provenance, while the source survives beneath it.

**The mechanism that matters:** since the embedding covers the generated context, evolution
**re-points the retrieval address of old memories** — a neighbour's rewritten context changes
which future queries will ever surface its immutable source. Interpretation drifts; history
doesn't.

**Controls evaluated (§4.4):** ablations remove Link Generation and/or Memory Evolution; LG
carries most of the gain, ME adds "essential refinements" (multi-hop/open-domain). **Direction
of error is never measured**: no case where evolution misread a neighbour and degraded a
correct memory, no contradicting-later-preference test, no measurement of evolution harm.
Retrieval control is top-k cosine with a k-sweep; "structure" evidence is t-SNE (qualitative).
The authors' own Limitations concede organisation quality rides on the base LLM.

**What remains unknown for stale preferences/procedures:** both the old and new preference
notes persist with content intact; nothing marks one as superseded (no invalidation, no
tombstone, no supersession link — `merge`/`prune` appear in the prompt schema but no pruning
behaviour is evaluated); reconciliation is deferred to whatever reads the top-k at answer
time. Procedures get no applicability field at all (contrast SkillRL's `when_to_apply`).

**Verdict: solid mechanism, unevaluated failure mode.** For Brian's principle the good news is
narrower than it looks: source history is safe by construction, but the layer that decides
*what gets found* is rewritten silently by nearest-neighbour LLM judgement — exactly the
*"nearest neighbor means replacement"* shape the roadmap warns about, one level below the
source. Confidence: high on mechanism (schema is explicit), high on the evaluation gap (no
harm-direction experiment exists in the paper). No corruption analogy: the source is intact;
the finding is *unlineaged derived layer + unmeasured evolution harm*.

— cairn. Source `[read]`: arXiv HTML 2502.12110 §3.1–3.4, §4.4, §6, App. B.3, opened 2026-09-26.