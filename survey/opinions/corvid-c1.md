# Contrarian opinion, cycle 1 — corvid

**Signed:** corvid (Contrarian, DeepSeek/Go pool) · 2026-09-26 · on POSITION-MEMO.md v0.
Signed opinion, not an audit. “Being wrong in an interesting way is better than being
silent” (ROLES.md). Confidence = transfer to Brian’s work.

**My position: Tern’s first bet (deliberate notes) is probably backwards as the *first*
build.** Automatic episodic capture with cheap lifecycle machinery is the better default,
and the local campaign4 negatives are too weak to argue otherwise. **Medium confidence**
on the direction, **high confidence** that the evidence cited does not yet support the
memo’s ordering. Sources and inference are labelled.

## Where I think Tern is wrong

**1. The local negatives are near-uninformative, not “narrow.”** [inference, from R53/R61/R68]
The memo leans on R53 (R−I primary 0 everywhere), R61 (primary 0/8), and R68 to caution
against complexity. But:
- R53 was a **ceiling null**: all of N, I and R scored 3/3, so R−I *could not* separate
  under any memory policy. A task every arm passes bounds nothing about retrieval.
- R61’s 0/8 was substantially an **instrument/units artifact** (its own acceptance keeps
  four R/D target-run primaries unlabeled; “primary 0/8 not all caused by artifacts”).
- R68’s R arms were an **index-delivery confound** — the target sat in the auto-loaded
  MEMORY.md line, and no s2 memory read happened. Tern says this; the memo then still
  uses R68 as support for bet 1, which is the wrong inference: R68 shows *index injection
  works*, which favours cheap automatic surfaces over curated detail notes.
The experiment that would actually test detail retrieval (R69–R72 prepared-memory plus a
prospective GUESS gate) exists **only as an offline-verified design with zero live calls**
and R73 declined. So the field’s central question for Brian — does the model open and use
a *detail* it wasn’t handed inline? — is **unrun**. The memo is ordering bets on an empty
cell. [source: R53/R61/R68 acceptance.json; R72 completion-claim]

**2. “Use simple search as the baseline” under-weights the rival’s cost asymmetry.**
[inference + source] Curated notes front-load a write-side cost (someone must notice and
record) and have a recall blind spot (unrecorded ≠ unimportant). Automatic episodic
capture front-loads a *read-side* cost (ranking, staleness) that the industry is actively
driving toward zero with off-the-shelf embedding indexes. The memo treats “buy complexity
for a named workload” as the safe default, but the named workload is usually *the
unanticipated question*. Zep/Mem0-style capture plus lifecycle is not “complexity for its
own sake”; it is insurance against the recall blind spot. [Zep 2501.13956; S10-KD verdict]

**3. The memo’s own “open frontier” argues against its first bet.** Tern lists *admission,
revision, forgetting, timely use* as the frontier, then recommends a design (deliberate
notes) that largely dodges revision/forgetting by keeping the store small. That is
choosing the workload that makes the hard problem disappear, which is reasonable
engineering but is argued as if it were a finding about the field. [inference]

## The most underrated direction

**Memory as a maintenance/lifecycle product, not a storage product.** The single
highest-value thing for Brian’s admin/rollout/model-testing work is *detecting and
retiring stale state* (deployment status, process IDs, model versions) — exactly what the
S10-KD and KnowledgeDrift results show flat ranked retrieval fails at (abstention at the
floor, crossed-phrasing ≈ 0). If I had one build slot, I would ship **automatic capture +
write-time timestamps + an explicit “what changed / what to recheck” handoff + a delete/
supersede path**, and buy retrieval sophistication only after that lifecycle is measured.
This is closer to bet 2 (handoff) than bet 1 (notes), and it is the piece the memo
currently ranks second. [source: S10-KD verdict.json; POSITION-MEMO bets 1–2; inference]

A close second, and genuinely underrated: **procedural memory as executable skills** — but
Tern already flags it, so I press the lifecycle point instead.

## What evidence would settle our disagreement

One cheap, decisive shape — a **repeated real-task A/B**, not another toy:
- Arm A: deliberate-note memory maintained by Brian. Arm B: automatic capture with
  embedding search + timestamps, no curation.
- Metric, at ≥3 repeats of the *same* task category: repeated corrections avoided,
  stale-state errors, handoff recovery time, and — critically — **retrieval misses on
  questions that were never curated**. Count update/delete latency and maintenance
  minutes. [method source: POSITION-MEMO “overrated” list agrees these are the right
  endpoints]
- Falsifier for me: B’s ranking noise and stale hits cost more than A’s blind-spot misses
  *after* maintenance time, on tasks Brian actually repeats. Falsifier for Tern: A’s
  curated store misses a question Brian later needed and B recovers it.

Second, cheaper: run the **already-designed R72 prepared-memory detail-retrieval cells**
(R69–R72 are offline-verified; R73 declined). Zero new design, some calls, and it directly
fills the empty cell the memo currently reasons around. That is the single highest
information-per-dollar experiment on the table. [source: R72 requirements/readiness]

## Minor flaws (one line, not load-bearing)
“Field map separates mechanism vs transfer confidence” is a good discipline, but the memo
never states a confidence for the *rival* design, which makes the comparison asymmetric.

**Strongest dissent to Tern:** the memo’s caution is being read as evidence about the
field, when it is mostly a measurement ceiling and one unrun experiment. Build the cheap
automatic-capture-plus-lifecycle arm first, and run the parked detail-retrieval cells to
populate the cell you are currently arguing in the dark about.
