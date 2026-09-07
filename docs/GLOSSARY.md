# Glossary — the reader-interference vocabulary

Written 2026-09-06 because Brian, who owns this project, said the terminology had
been opaque to him for twenty-four hours. If a term in a handoff is not in here,
that is a defect in the handoff.

Examples are real, taken from the Gen122 run.

---

## The thing under test

**Reader** — the local model being questioned: `qwen3.6-35b-vulkan-nothink`,
temperature 0, seed 0, stateless, one shot per call. Called "the reader" because
its only job is to *read* records handed to it and answer. It is **not** a memory
system; it sits downstream of one. The bake-off tests memory systems; this
experiment tests what a model does with what a memory system hands it.

**Record** — one fact, with an id and a revision number:

```
rev1  REC-09EA507DF9   The Nocturne foundry casts on floor darnwick.
rev2  REC-29D9BFB7F1   The Nocturne foundry casts on floor pemberly.
```

Same subject, two versions. `rev2` supersedes `rev1`.

**Core** — one self-contained world: a subject, its records, its question. Twelve
of them, deliberately unrelated (foundries, terminals, granaries), so a result in
one is not a quirk of one word choice. **The core is the unit of evidence.** Twelve
cores, not sixty observations - cells within a core are not independent samples
and may never be pooled as if they were.

**Cell** — one question, in one core, under one condition. 12 cores x 5 conditions
= 60 cells.

---

## The five conditions

Each core is asked five ways. Two are the experiment; three are controls.

| condition | what the reader is shown | correct answer |
|---|---|---|
| `CLEAN_CURRENT` | only the current record | the current value |
| `CLEAN_HISTORICAL_AS_OF` | asked about an older revision | the old value |
| `CONFLICT_CURRENT_FIRST` | both records, current first | the current value |
| `CONFLICT_STALE_FIRST` | both records, **stale first** | still the current value |
| `INSUFFICIENT_CURRENT` | asked about a revision that does not exist | **refuse to answer** |

The two `CONFLICT` rows are the actual question: does showing the outdated record
first change the answer. The other three are controls - if the reader cannot get
`CLEAN_CURRENT` right, its conflict answers mean nothing.

**As-of revision** — the point in time the question asks about. "What is it as of
revision 2." This is what makes `CLEAN_HISTORICAL_AS_OF` and `INSUFFICIENT`
possible.

**Interpretable** — a core counts only if it passes all three controls AND every
one of its cells produced a graded row. In Gen122 all twelve failed their
controls, so zero cores were interpretable, so there was no result.

---

## Scoring

**Disposition** — the reader's own verdict on the situation: resolved,
insufficient, contradictory. Separate from the value it gives.

**Success predicate** — four things must all hold for a cell to count:
coherent disposition, correct record id, **exact** value, and a citation that
supports the selection. Gen122 failed only the third, in 48 of 48 cells.

**Answer class** — the nine-class terminal ontology: `CURRENT_ONLY`,
`STALE_ONLY`, `UNSUPPORTED_VALUE`, `CORRECT_INSUFFICIENT` and so on. Every answer
lands in exactly one.

**Canonicalisation** — the only normalisation permitted before comparing values:
casefold, and collapse internal whitespace. Nothing else. Deliberately narrow, so
that "close enough" cannot creep in.

---

## Evidence machinery

**Freeze** — a sealed snapshot of the whole experiment: prompts, schedule,
grader, protocol module, runner, tests. Hashed, so nothing can be quietly changed
after results are seen.

**Attempt** — one numbered sealed directory, `results/gen<N>/attempt<M>`.
Append-only: an attempt is never edited, only superseded. Gen118 has eighteen
attempts because each apparatus repair invalidates the previous seal.

**Contract / contract_sha256** — the hash binding a freeze together. It
recomputes from the sealed payload plus the source pins, so a changed file is
detectable.

**Manifest** — the per-attempt list of artifacts and their hashes. A file not in
the manifest is not verified by anything, which was the F1 defect of Gen120.

**Marker** — the run's own label for itself. `RUN_EVIDENCE` means citable.
`NON_EVIDENCE` means it happened and proves nothing. Derived from observed gates,
never authored, and never backfilled.

**Journal** (`reader_journal.jsonl`) — exact response bytes, base64, one
append-only record per call, fsynced before anything decodes them. This is the
raw evidence. `reader_records.jsonl` is the *parsed* view and is not raw.

---

## Terms that mislead

**"Burned" / "exposed" / "the schedule is spent"** — used throughout this project,
and **easy to misread**. It does NOT mean the model remembers anything. The reader
is stateless at temperature 0 and seed 0; re-asking an identical prompt returns
an identical answer, as Gen122 confirms.

What is spent is **experimental blindness, ours not the model's**. Once we have
seen how the reader answers a given case, any protocol rule *validated on that
same case* is fitted to an outcome we already knew. That is the Gen114 error, and
it is why Gen118 refused an acceptance class "suggested by the observed failures".

Practically:

- re-running unchanged: harmless, deterministic, and pointless
- iterating on the prompt to **diagnose**: fine, cheap, encouraged
- claiming a **confirmatory result**: needs cases whose outcomes did not inform
  the rule being tested

Claude wrote "the schedule is spent" in the Gen122 handoff, implying a fixture
rebuild was required. Brian challenged it and was right; the phrase was inherited
from the project's own "burned" language without examination.

**Independent unit** — the core, not the cell. Sixty cells are not sixty
observations. Any claim of the form "48 of 60" is describing cells and is not a
sample size.
