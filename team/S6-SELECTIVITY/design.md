# S6-2 design — a selectivity diagnostic the firehose cannot pass

Row S6-2 (Astra's Sprint-6 proposal, Brian approved 2026-09-16 evening).
Author: kiln-flash, 2026-09-17. Design frozen before any run; the manifest
pins this design's declarations and the results bind to the manifest by hash.

Cited before the corpus was built, per the standing re-measurement rule:
`team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md` — Brian's card on KnowledgeDrift v1
(MIT, frozen worlds, 2026-09-16). Its **Abstention** family is the control our
invocation instrument lacks: "correctly DECLINES on an unwritten subject, or a
written subject with no note." Its own headline (a lexical baseline above the
memory systems) independently reproduces the shape of our S4-14 result.

KnowledgeDrift choice: reuse-abstention

We reuse its abstention construction — unwritten subject, and written subject
with no note on the asked aspect — on our own store-per-case shape, because
running our engines against its frozen worlds would measure their corpus
rather than our invocation surface, and its 1,500-fact scale is built for
vault products, not for the small per-case stores our instrument uses. Per
the card's caveat we adopt the STRUCTURE and re-derive every score; none of
its numbers are imported, and its leaderboard is treated as a vendor-adjacent
claim, not evidence.

## Corpus (corpus.jsonl, frozen before the manifest)

10 cases, each `store` holds exactly 4 records (so a firehose always has
something to return), 1 query each, synthetic pattern-level content in the
fleet's voice — no raw transcript content, deterministic by construction
(the file is the freeze; its sha256 goes into the manifest).

- **5 retrieve cases** (`expect: "retrieve"`): exactly ONE record answers the
  query; the other 3 are plausible distractors drawn from three classes —
  same-entity different-fact, superseded/stale value of the same fact,
  different-entity same-fact-type. A store where every record helps is
  forbidden by design (that is the firehose's home turf).
- **5 abstain cases** (`expect: "abstain"`), reusing KnowledgeDrift's two
  abstention constructions:
  - *unwritten subject* (sel-006, sel-007, sel-010): the asked subject appears
    in no store record; the store holds plausible fleet records on other
    subjects. Correct behaviour: retrieve nothing.
  - *written subject, no note on the asked aspect* (sel-008, sel-009): the
    subject word appears in the store, but the asked fact was never recorded
    (postgres is documented; a postgres upgrade date is not; the search
    service is documented; its replica count is not). Correct behaviour:
    retrieve nothing. Declared honestly: a lexical engine may fire on the
    subject token here; if that cost keeps selective retrieval from
    separating from the firehose, the verdict below is STOP — that is the
    instrument reporting itself, not a failure to be engineered around.

## Arms, semantics declared before any run

| arm | semantics |
|---|---|
| `return-nothing` | `retrieved_ids = []` on every case. |
| `return-everything` | all 4 store record ids on every case. |
| `bm25` | in-tree `BM25Provider` (`src/memory_bakeoff/providers/bm25.py` @ canonical `be2bfa9`), per-case store ingest, `top_k=1`: returns the single top-scoring record iff its score > 0, else returns nothing. Deterministic; abstains by construction at zero overlap. |
| `oracle` | exactly the manifest's declared helpful ids — proves the scoring rewards the right answer before any engine is trusted. |

Engines (ONLY if the controls separate; never before the control rows):

| engine arm | semantics | adaptation labels every row carries |
|---|---|---|
| `pi_lcm_toollevel_sel` | `PiLcmToolLevelProvider` as pinned in S4-14 (verbatim relaxedVariants port; exact AND first, then ≤6 bounded variants; returns the full match set, `top_k=5`). | store: 4 records per case instead of 1; single-session relaxation gate port (S4-14 declared adaptation); record ts fixed 2026-09-01T00:00Z, uniform age, no time behaviour in scope |
| `claude_mem_chroma_lsa_no_recency_sel` | `ClaudeMemChromaLSANoRecencyProvider` as pinned in S4-14, `top_k=3` semantic neighbours. | store: 4 records per case instead of 1; top-3 semantic neighbours — the vendor policy has no abstention threshold, so non-empty output on abstain cases is an expected finding, not a harness fault; 90-day window disabled (S4-14 row-mandated primary); record ts fixed 2026-09-01T00:00Z, window behaviour out of scope per team/S6-CORRECTION/note.md |

## Scoring and the pre-declared decision rule

Set-F1 of `retrieved_ids` against the manifest's declared helpful set, per
case; an abstain case scores 1.0 only on an EMPTY retrieval, else 0.0.
Per-arm mean over the 10 cases. Separation gap = mean(bm25) −
mean(return-everything).

**separation_margin = 0.25** (of the metric's 0–1 range), declared before the
runs: on this corpus shape the firehose's mean is exactly 0.2 (five retrieve
cases at 2·1/(1+4) = 0.4, five abstain cases at 0.0), so a 0.25 margin
demands that selective retrieval do more than inch past the firehose's
ceiling. If gap ≤ 0.25, return-everything is not distinguished from selective
retrieval: **verdict STOP**, the finding is reported, and no engine runs —
an honestly demonstrated instrument limit is a completed result. If
gap > 0.25: verdict CONTINUE, engines run after every control row.

`truncation = null`: "everything" means the whole 4-record store — with
fixed store size this is fully reproducible.

## Determinism and temporal bounds

No wall-clock enters any decision: bm25 is pure math, pi-lcm lexical, the
chroma/LSA path is deterministic for a fixed ingest. All engine record
timestamps are the S4-12/S4-14 fixed stamp 2026-09-01T00:00Z (uniform age);
per the S6-1 correction, nothing here supports a claim about the 90-day
window — the no-recency arm is used precisely so the window is out of play.

## Chain of custody

corpus.jsonl (frozen) → manifest.json (declares helpful sets, margin,
truncation, `declared_at`; pins the corpus sha256) → results.jsonl (every row
carries the manifest sha256; controls first, engines only on continue) →
decision.json (verdict from the frozen rule) → review.json.
