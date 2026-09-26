# Reading sweep — applicability & supersession of learned procedures and preferences

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 2.**
Signed opinion, not an audit. Question: when a stored procedure or preference is retrieved,
what makes it **applicable now**? Three things get merged in practice:
**(a) the stored claim** ("we learned X"), **(b) the validated outcome** (X passed check C under
environment E at time T), **(c) present applicability** (is E still E?). Cycle 1 proposed
re-check-at-use; this cycle tests that against three actual update mechanisms, read in full,
not as abstracts.

Provenance key: `[read]` = full text read at source today (arxiv.org HTML, 2026-09-26);
`[card]` = our cards, not re-read; `[ours]` = our measurement.

---

## Per source

**1. Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents** —
arXiv:2606.27472v1, full text. `[read]`
**Actual update mechanism:** the agent LLM rewrites a bounded notes field (500–7,150 chars)
after each session; raw sessions are **never re-fed**. There is no supersession operation, no
valid time, no provenance, no history — replacement happens only if the rewrite happens to
overwrite the stale value. **Failure modes (full text, new to us):** errors are dominated by the
relevant fact being *compressed away or not overwritten* — answers like "no information about
Rachel" — i.e. **loss, not staleness**, is the dominant error. Their fix is not a lifecycle
design but an RL-trained currency policy (GRPO, Qwen2.5-3B, single run, 9.0→16.7%).
**Limitations they concede:** single run/seed; the "scale" axis adds distractor sessions, not
more updates to the tracked fact; the constant-ratio null is n=25; the matcher is lenient.
**Transfer caveat they don't state:** their setup *deliberately deletes history* (no re-feed), so
their numbers bound the worst case — Brian's corollary regime (exclude from prompt, keep
recoverable) is exactly what they did not test. "More memory recovers nothing" is a claim about
notes-rewriting, not about retrieval from lossless history.
**Verdict: solid measurement, narrow scope; oversold as a fix.** Confidence: high on the
mechanism reading, high that the caveat matters to us. Facts only — procedures never appear.

**2. Zep / Graphiti: bi-temporal edge invalidation — the strongest competing lifecycle we can
locate** — arXiv:2501.13956v1, method sections. `[read]`
Tracks **four timestamps per fact edge**: transactional (`created_at`, `expired_at` — when the
system learned/retired it) and temporal (`valid_at`, `invalid_at` — when the fact held true).
Supersession: a new edge is compared by an LLM against semantically related existing edges
**constrained to the same entity pair**; temporally overlapping contradictions invalidate the old
edge (`invalid_at` ← new edge's `valid_at`), never delete; the system "consistently prioritizes
new information." Retrieved context prints valid ranges and leaves currency to the reader.
This is the only located mechanism that supersedes **while preserving history** — Brian's
corollary, implemented. **Limitations for our question:** invalidation is still a write-time LLM
judgement — the roadmap's "nearest neighbor means replacement" risk sits inside the mechanism
itself; "prioritizes new information" is a recency heuristic, not evidence-backed; and the model
is *facts-between-entities* — procedures and scoped preferences don't fit the edge shape.
`[ours]` Our Gen19/20 ingestion gates never exercised this machinery.
**Verdict: solid as a lifecycle mechanism for facts; unproven for procedures.** Confidence:
medium-high on what it does, low on transfer to procedure scope.

**3. Voyager skill library — the procedure lifecycle that actually exists** —
arXiv:2305.16291, method + limitations. `[read]`
Procedures are executable code, admitted **only after execution + GPT-4 self-verification
pass**, indexed by the embedding of a generated description, retrieved top-5 by embedding of
(task plan + environment feedback). Lifecycle is **append-only**: no invalidation, no versioning,
no retirement, no environment identity stored with the pass. Applicability is never re-checked
from the store — but because the skill is code, **the environment re-checks it at every use**:
a stale skill fails loudly with an execution error. They concede self-verification sometimes
passes wrong successes.
**Verdict: solid as mechanism, irrelevant as benchmark evidence for Brian** (Minecraft), but it
contains the asymmetry that matters. Confidence: medium.

---

## The one idea in this area that most deserves our attention

**No located lifecycle design represents "applicable now" as a first-class object — and for
executable procedures the check is free, while for remembered claims it is never built.**

Read across the three: Supersede keeps only (a) the claim, and loses it. Zep models (b) as a
validity *interval of a fact*, decided by an LLM at write time. Voyager stores (b) as an
execution-verified artifact but no applicability metadata — and gets use-time re-checking for
free, because running the code *is* the applicability probe. The design consequence for Brian's
stack is narrower than "build a skill library":

- **Executable steps:** store (artifact + verifier that passed + environment identity at pass).
  Applicability = run or re-verify; failure is loud and cheap. Voyager's asymmetry says: prefer
  encoding procedures where a check exists, because the check is the lifecycle.
- **Prose procedures and preferences** (no free check): the Zep shape transfers — append, mark
  superseded with explicit invalidation, never delete — but the write-time LLM judgement must
  stay *inspectable*, since that is where "nearest neighbor means replacement" lives.
- Either way, retrieval should hand the reader the **validity data separately from the claim**
  (Zep's printed ranges are the only located UI for this), so the executive, not the store,
  decides applicability — Brian's five-part split, enforced at the schema level.

**What would change my mind:** a located system that stores procedure applicability conditions
and evaluates them at read time (I looked and did not find one among these three or cycle 1's
set); or evidence that write-time invalidation judgement (Zep's weak point) fails more often
than use-time re-check costs.

## Gaps kept as unknown

- "STALE", StateMem, MemStrata, Attestor: still unlocated identities `[card]`.
- Zep's invalidation precision was never measured in its paper, only end-task scores; our own
  runs never reached the mechanism `[ours]`.
- Supersede's multi-seed training significance: authors' own open item.
- Nothing here is our reproduction; all external figures quoted from full texts read 2026-09-26.

— cairn, Reader. Sources `[read]`: arXiv HTML 2606.27472v1, 2501.13956v1, 2305.16291, fetched
2026-09-26.