# CORVID-S13-1-REPRODUCE — independent reproduction of S13-1

Verifier: corvid-dsh. I did not author the row, the pre-registration, the runner
or the author's results. My own numbers were written to
`team/S13-KD-COVERAGE-TRANSFER/corvid-reproduction.json` **before** I opened
`results.json` or `verdict.json`. Reproduced 2026-09-20 21:5x–22:0x PDT.

## Verdict

**Reproduction succeeds. The row's conclusion is independently confirmed: the
S11 corpus-coverage rule does not transfer to the KnowledgeDrift sample — at
every declared threshold either it declines ~nothing or it buys abstentions by
rejecting far more than the 8/80 useful-loss bar. One number diverges from the
author's (threshold 0.5: my 13/80 useful probes declined vs the author's 10/80),
and the cause is the corpus-semantics issue the author already lists as open.
The divergence does not change the outcome.**

## Which of the three checks I performed

**All three.**

1. **Re-execution of `run_transfer.py`.** I re-ran the file
   (`sha256 b3031d0dae433915de8533696f908d1986652f8e96d910475ce297b63976d402`)
   from the frozen inputs and it rewrote `results.json` **byte-identically**
   (`sha256 59b0a3b2657a57b35979a66ab3dd65a748b063e3bf7fd24625144d589c1bd5fb`),
   and `results-attempt1-repeated-tokens.json` is likewise byte-identical.
2. **Independent derivation with my own implementation.** I wrote my own
   coverage computation from the pre-registration and the frozen S11 rule
   (`content_stopwords`, `min_document_frequency=1`, distinct content tokens,
   strict `<`, empty content → 0), tokenised `[a-z0-9]+` on lowercased text
   (the S11 rule's own tokenizer, `S11-ABSTAIN3/run_abstain3.py:26`), and built
   the corpus per probe.
3. **Validity review** — whether the two numbers measure the intended thing
   (below).

## Counts: mine vs the author's

| threshold | my abstentions (of 40) | author abstentions | my useful declined (of 80) | author useful lost |
|---|---|---|---|---|
| 0.0 | 0 | 0 | 0 | 0 |
| 0.25 | 0 | 0 | 1 | 1 |
| 0.5 | 0 | 0 | **13** | **10** |
| 0.75 | 6 | 6 | 20 | 20 |
| 1.0 | 24 | 24 | 51 | 51 |

Full per-family/per-seed numbers and per-item coverage are in
`corvid-reproduction.json`. No items were unresolved; no item had zero content
terms.

## Divergence and its cause

The **only** divergence is useful probes declined at **threshold 0.5: 13 (mine)
vs 10 (the author's)**. (My positional breakdown there: Retrieval 7+6 = 13,
Rationale 0; the author's: Retrieval 10, Rationale 0.) Every other cell matches
exactly.

Cause, demonstrated: **corpus semantics**. The author's runner pools **every**
inscribe record in the whole stream into one df table
(`run_transfer.py`: `for op in w["ops"]: if op["op"]=="inscribe": … df[t]+=1`),
so later inscriptions can support earlier queries. I built the corpus at each
probe's **own position** in the stream (records inscribed before that probe's
recall op), which is what the pre-registration's *"each sampled probe answered
at its own position in the ops stream"* describes, and what the author's own
`open_fidelity_issues[0]` calls the strongest remaining objection.

Effect: 29 of the 120 probes have a higher coverage under pooling than
positionally; at threshold 0.5 exactly three cross the line —
`s1-R403` (0.533→0.467), `s2-R1204` (0.526→0.474), `s2-R1603` (0.500→0.438) —
all Retrieval probes that the positional (preregistered) reading declines and
the pooled reading keeps. There is no divergence at any other threshold because
no other probe's coverage crosses a grid point between the two corpora.

**Neither value rescues the row.** At 0.5 the author's own reading has 0
abstentions, so 10 vs 13 useful lost both fail the bar; the outcome is unchanged.

## Validity review — is it measuring the intended thing?

- **The second number is "answerable probes the rule would reject", not "useful
  retrievals destroyed."** The runner never executes BM25 and never joins
  against a baseline's successful retrieval; it counts probes of family
  Retrieval|Rationale whose coverage falls below the threshold. Tern's
  correction in `verdict.json` is right, and my reproduction has the same
  character. The count is conservative and honest under that name; the
  pre-registration's stronger wording ("discards an answer it should have
  given") is not established by this runner.
- **The rule cannot see the way this benchmark makes questions unanswerable.**
  The author's mechanism note is correct and I confirm its shape from my
  per-item fractions: KnowledgeDrift's Abstention probes recombine vocabulary
  the corpus contains, so per-term coverage stays high and the rule declines
  nothing; only queries containing words absent from the corpus are rejected.
  Demand-side (does any record answer this?) is not what a coverage rule tests.
- **Corpus semantics is the live fidelity gap**, and it is the exact source of
  my one divergence; the author flags it as unresolved. My positional reading is
  the preregistered one; aligning the runner to it would change only the 0.5
  cell, to a value that still fails.
- **Bounds are uninformative at the extremes** (0.0 declines nothing; 1.0
  declines everything), but the whole grid is reported and no threshold was
  selected, as required.

## Binding: does `run_transfer.py b3031d0d` produce `results.json 59b0a3b2`?

**Yes — confirmed by re-execution, byte for byte.** The author has been wrong
about this once before (the ad-hoc attempt-2 script, caught by Tern); as it
stands now the binding holds:

- `run_transfer.py` sha256 `b3031d0dae433915de8533696f908d1986652f8e96d910475ce297b63976d402` — matches the file and the pin in `verdict.json`.
- re-running it writes `results.json` sha256 `59b0a3b2657a57b35979a66ab3dd65a748b063e3bf7fd24625144d589c1bd5fb`; `cmp` against the saved original: identical.
- `results-attempt1-repeated-tokens.json` is byte-identical to `results.json`, consistent with the recorded "identical at all five thresholds" repair history.
- `results.json.prereg_sha256` = `7e0484db…` matches `sha256(PREREGISTRATION.md)`.

## Summary for the board

The reproduction is **not blocked and not divergent in outcome**. It agrees with
the author on 4 of 5 thresholds and on the answer (transfer fails), and the
single differing cell (0.5: 13 vs 10 useful probes declined) is fully explained
by pooled-vs-positional corpus semantics — the author's own open issue — and
does not move the conclusion. Independent numbers:
`team/S13-KD-COVERAGE-TRANSFER/corvid-reproduction.json`. — corvid-dsh
