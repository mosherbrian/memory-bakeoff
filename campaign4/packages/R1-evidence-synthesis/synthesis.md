# R1 evidence synthesis — September 20 frozen record

Commit `485d783d`; all paths below are `git show COMMIT:PATH` bytes; hashes
verified against sources.json (124/124). Started from the answer page, then
re-derived against the primary verdicts; where later evidence (S13 transfer,
corvid reproductions) supersedes the 13:11 answer page, the later record wins.
No fresh corpus, experiment, or significance claim. Words: target <=1500.

## Method note

Retrospective synthesis of existing results, not a blinded experiment; prior
exposure to summaries is disclosed per the contract. Existing corvid verdicts
are provenance for re-derivation, not authority: every number below was checked
against its recorded artifact (denominators kept). Arithmetic was checked by
reading recorded outputs only; no reproduction was executed.

## Observed results (not interpretations)

**Real-work benefit: not established.** Nothing through September 20 measures
task outcomes with memory on vs off, continuity through actual compaction, or
reduced errors/repeated discovery. S11 rows concern query rejection (S11-ABSTAIN3)
and false replacement (S11-LAYER-HIST): retrieval/delivery proxies, not task
improvement. (Answer page row 1; both S11 verdicts.)

**BM25 relevance rejection, constructed sets.** The S11 corpus-coverage rule
(abstain iff distinct-content-token supported fraction < threshold, min_df 1)
meets its pre-registered two-sided bar at thresholds {0.25, 0.5} on BOTH the
declaration set (0.5: 5/5 irrelevant rejected, 0/5 useful lost) and the sealed
holdout (0.5: 3/5 rejected, 0/5 lost). No threshold was selected; the full grid
is reported. Priors failed the same bar: S7 stopword prefilter 0/5 rejected +
1 useful lost (`artifact-refuted`); S10 margin rule 2/5 + 1 lost
(`mechanism-fails`; grid 0.5→0/0, 1.0→2/1, 1.5→5/2). Corvid independently
recomputed the full grid from the declared formulas (33 checks pass) and
confirmed bar_met_at = {0.25, 0.5}. Honest limit: holdout partially-supported
distractors cap rejection at 3/5; 0.75 loses useful retrievals first.
(S11-ABSTAIN3/verdict.json; CORVID-S12-2-VERIFY.md.)

**Transfer to KnowledgeDrift: fails.** Unchanged rule on 120 frozen probes
(40 Abstention / 40 Retrieval / 40 Rationale, two sha-pinned worlds): at 0.5,
0/40 correct abstentions with 10/80 useful lost — strictly worse than not
applying it. Best case 0.75: 6/40 abstentions at 20/80 lost (25%); 1.0: 24/40
at 51/80 (64%). No threshold meets the pre-registered bar (materially above
0/40 with ≤8/80 lost). Mechanism, confirmed by corvid's per-item fractions:
the benchmark builds unanswerable questions by recombining vocabulary the
corpus already contains, so per-term coverage stays high; only queries with
corpus-absent ordinary words are rejected. Corvid's independent reproduction
agrees on 4/5 thresholds; the one divergence (0.5 useful lost: 13 vs 10) is
the pooled-vs-positional corpus-semantics issue the author lists open — and
both values fail. `results.json` and
`results-attempt1-repeated-tokens.json` are byte-identical (sha
59b0a3b2… both); do not double-count them. (S13 verdict.json;
CORVID-S13-1-REPRODUCE.md.)

**Composing BM25 with pi-lcm: no benefit.** Permission-based construction:
bm25 arm mean set-F1 0.5 (5 retrieve/0 abstain), pi-lcm arm 0.6 (1/5), compose
exactly pi-lcm's profile — gate opens on 1/5 retrieve cases and discards
bm25's other coverage. Verdict `not-complementary`; Decision Gate F option B
loses this justification. A union-style construction would be a new declared
configuration. (S7-COMPOSE/verdict.json.)

**False replacement: native fails, tested layer worsens.** On broader frozen
histories native pi-lcm falsely supersedes 22/33 distractors (0/13 missed
updates); the key-equality thin layer supersedes 33/33 (0/13 missed) —
reduction −0.5 against a pre-registered bar requiring +0.5. The earlier
controlled 0/32 null for both arms does not generalize. Verdict
`close_trivial_layer_class`; corvid re-ran generator (byte-identical corpus),
harness (268 identical receipts), and an independent recount matching every
cell including the six-cell sensitivity grid. Scope: "false replacement" =
newer write wins the original query's top result, NOT demonstrated deletion;
this tests the bake-off MEMORY contestant, and `compaction_measured: false` —
nothing here measures Brian's stack compaction. (S10-PI-LCM-HIST and
S11-LAYER-HIST verdict.json; CORVID-S12-1-VERIFY.md.)

**Abstention weakness is not BM25-specific.** Five implementations score 0/40
abstentions on the frozen KD sample (control BM25 Retrieval 0.53 / Rationale
0.12; dense_lsa 0.28/0.07; tfidf_cosine 0.50/0.10; hybrid_rrf 0.50/0.07;
claude-mem controlled core 0.28/0.07). Finding: flat ranked retrieval has no
decline concept. Caveat travels with every number: the benchmark author fields
its own system in its ranking. (S10-KD-CROSS/verdict.json; S7-KD-WORLDS lane.)

**Competing text can starve delivery.** At a declared 600-char door, rung-2
query-adjacent load cuts evidence presence 100%→20% (BM25), 20%→0% (pi-lcm),
100%→60% (claude-mem adapter); rung-1 pressure caused no loss. This is evidence
delivery, not task harm or daily-work frequency. (S8-DOOR and S9-DOOR-RUNG2
verdict.json.)

**Gate episodes, traced to frozen rules.** Both S13 gates were VERIFIED FAIL
in both rounds, for opposite reasons. S13-1G demands an expression-tree rule
(`{"op","args"}` round 1; `{"score","reject"}` + `threshold_grid` + `id` +
`abstained`/`useful_retrieval` round 2); the frozen S11 declaration carries a
declarative config (`decision:"supported_fraction_lt_threshold"` +
`content_stopwords` + `min_document_frequency`, grid under `thresholds`,
items under `item_id`, baselines under `passed`) — an impossible
expression-tree selector no faithful build can satisfy. S13-2G demands one
substantive mechanism section per inventory name parsed from the real cards:
12 names (4 non-mechanisms: two heading prefixes, a recommendation heading, a
filename) round 1, exploding to 73 names ("Caveats", "JavaScript", …) round 2
— satisfiable only by fabricated sections. Both selftests stay green because
their synthetic fixtures mirror the demanded shapes, not the real frozen
inputs: the same fixture-vs-real-input class as S12-1G rounds 2–3. (For
contrast, S12-1G failed then passed round 4 once bound; S13's attempt-2
results mismatch was caught by Tern with the pinned runner re-executing
byte-identically.) These are measurement-process failures caught by the
process, not memory-efficacy evidence for or against. (CORVID-S13-1G-VERIFY.md;
CORVID-S13-2G-VERIFY.md.)

**Open judgment, not evidence.** Pooled-vs-positional corpus semantics (author
10 vs corvid 13 useful-lost at 0.5) is genuinely unresolved — registration
order was never demonstrated (all three entered git together) — but both
values fail the bar, so it moves no conclusion today. It is a pending
interpretive question, recorded as such.

## Interpretation (separated from results)

Nothing supports a memory aid improving Brian's real work; nothing refutes
that one could. What the record actually bounds: (a) one relevance rule that
survives its bar locally but not externally, for a vocabulary-shaped reason;
(b) one protection class closed on one failure shape, with compaction
unmeasured; (c) delivery fragility under adversarial load, unlinked to task
harm; (d) a flat-retrieval abstention gap across five implementations.
Retrieval ≠ delivery ≠ task improvement; replacement (top-result contest)
≠ deletion (data loss). Threshold grids are data, never menus.

## Recommendation: one discriminating step

Run a **preregistered memory-on/off comparison on matched local tasks
measuring task outcomes and delivered evidence** (the answer page's proposal,
kept): same tasks, memory present vs absent, pre-registered outcome measure
(task success + evidence delivered, not retrieval scores), full reporting of
both arms. **Falsification/stop:** if the arms do not differ, or differ only
on proxy scores without task-outcome movement, stop — do not tune, transfer,
or compose further. **Feasibility limit:** needs agenda audit + scoped
preregistration first (authorization per selection notes); no compaction
coverage is claimed — compaction enters only if a later step instruments a
real compaction boundary.
**Why alternatives rank lower:** the external transfer is already done and
failed (S13); a positional rerun changes no outcome (10 vs 13, both fail);
a new protection needs a mechanism audit first (the key-equality class just
closed); more local threshold tuning selects after outcomes. This step is
the only one that can move the real-work question either way.
It is a proposal, not authority to run it.
