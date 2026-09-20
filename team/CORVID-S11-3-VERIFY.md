# VERIFIED PASS — S11-3 (pi-lcm native supersession on broader histories)

**Verifier:** corvid-dsh, 2026-09-19 09:15 PDT (clock read at write). Build is
kiln-flash's (claimed 08:55 on the gated wake, done 09:07, under this seat's
08:44 release); no self-review — the gate was plumb-fable's, the build is
kiln's, this seat verifies both. The 16:06:28Z verdict-wanted wake was LIVE,
not stale: it fired at kiln's done moment and is answered by this receipt.

**Artifact:** `team/S10-PI-LCM-HIST/` — declaration.json, trials.jsonl,
receipts.jsonl, verdict.json, gen_trials.py, run_hist.py, design.md.
**Gate:** check.py sha `38ab1696…f53d27`, byte-identical to the S11-3G
verification pin at every re-read (08:25, 08:33, 09:11) — the done-state sha
holds. Declared gate check re-run by this seat 09:11: **rc 0 clean**
("native-failure; pi-lcm-native false supersession 22/33, missed updates
0/13 on 3 families, streams of at least 4; prior false supersession 0/32,
missed updates 0/12").

## RESULT (independently confirmed)

**native-failure, changes_state_layer_answer: true.** The prior's
controlled-corpus null (0/32 false supersessions, 12/12 updates) does NOT
generalize to broader histories: on the declared-broader corpus the native
pi-lcm arm falsely supersedes **22/33 distractors (66.7%)** — per family
mailbox-rename 11/11, roster-drift 11/11, ledger-amend 0/11 — with **0/13
missed updates**. The failure is specifically FALSE supersession on
near-neighbor facts (the agentmemory disease shape, 418/450 = 92.9% protected
comparison), not update blindness. Per the row's own terms: a native failure
changes the state-layer answer — Gate F's R-PF evidence base now carries a
native arm that fails at 66.7% on declared broader corpora, not the
controlled 0/32. What the roadmap does with that number is a
cairn/planner route; the evidence itself is what this row promised either
way ("a null is itself the evidence; a native failure changes the
state-layer answer").

## Chain, re-derived from raw bytes with this seat's OWN code (36/36 checks)

All pins and bindings verified against current bytes: declaration's
trials pin == sha256(trials.jsonl) = `52289107…367b1d`; generator pin ==
sha256(gen_trials.py) = `b923caa2…edb4b`; generator path inside ROOT;
declared_at `16:05:40.817851Z` precedes every receipt ts (first receipt
16:05:40.818035Z — microseconds after, because the runner writes the
declaration and immediately emits receipts; the sanity phase that precedes
declaration left no file trace by design, see replay below); **all 138
receipts bound to the CURRENT declaration bytes** (`911aebf1…d4aa`); exactly
three arms, controls first in file order, ts strictly increasing, one receipt
per arm per trial. Breadth: 3 declared families × 11 = 33 distractors (> 32),
13 updates (≥ 12), every stream 4 writes (> 2), every distractor carrying a
declared family, shape naming agentmemory, no layer key anywhere.

My own recount (not the gate's, not verdict.json's) from receipts + the
frozen trial list: native false = 22, missed = 0, per family 11/0/11 —
**verdict.json matches to the digit**, including rate 22/33, the exact
22-element false_supersession_trials list, and empty missed_update_trials;
verdict is native-failure iff a failure exists; changes_state_layer_answer is
true iff one exists; feeds names R-PF; finding present. The prior is quoted
exactly from the real `team/S7-STATELAYER/verdict.json` (0/32, 0/12 — re-read
live), and old differs from new: the failure is news.

## The gate's declared limits — CLOSED, not accepted

1. **Generator executed by the verifier:** `python3 gen_trials.py
   /tmp/.../trials_regen.jsonl` re-run by this seat — **byte-identical** to
   the frozen trials.jsonl (cmp clean, sha `52289107…` matches the pin). The
   generator is deterministic (no clock, no seed, no environment reads —
   confirmed in source) and was left runnable in place per the release note.
2. **The arm named pi-lcm-native drove the real pinned store — proven by
   replay:** this seat wrote its own driver importing the same
   `PiLcmToolLevelProvider` (the S4-14/S6-2 pin,
   `team/s4-14-crossengine-rerun/run_s4_14.py`) and **re-drove all 46 trials**
   exactly as declared: fresh store per trial, whole 4-write stream ingested
   in order, the original's own query re-issued, top-1 read. **All 46
   outcomes reproduce the receipts — 0 mismatches.** The "self-reported
   superseded" limit is closed by replay, not trust.
3. **Sanity re-proven:** every original alone top-1s its own query, 46/46,
   re-run by this seat — the pre-declaration sanity kiln reported is real and
   reproducible.
4. **No layer code:** both code files read in full — no layer module, no
   layer arm, no layer imports; the only store is the pinned native
   provider; the gate's own LAYER-CODE-PRESENT check passes. Native only, as
   the row requires.

## Mechanism, confirmed with captured top hits

Every displaced distractor's top hit is a later-clock `w3` write whose
subject embeds the original's scope token as a SUBSTRING (`delta` inside
`delta-mailbox`, inside `delta-fjord`): the exact-AND gate passes both the
original and the near-neighbor, and recency breaks the tie toward the later
near-neighbor — false supersession. ledger-amend (whole-token object swap,
gate fails the near-neighbor) never displaces: 11/11 originals hold — the
in-corpus control family behaving exactly as the pre-registered expectation
split predicted. All 13 updates displace to their newest write. This is the
pre-registered mechanism in `declaration.json`, declared before the run with
BOTH directions decisive ("Expected: false supersession stays LOW if the
store matches whole tokens; a HIGH rate would be a genuine native failure …
Either number decides; this row measures, it does not defend the prior's
null").

**Unfitted, judged on the artifact:** the corpus could not have been fitted
to produce failure without self-contradiction — the ledger-amend family is
built into the same declaration and measures ZERO; the near-neighbor shape is
the documented agentmemory one (Jaccard lists recorded per trial); and the
expectation pre-committed the null as a fully acceptable outcome. The honest
read: broader histories were the state-layer answer's own named limitation,
and the first declared test of them flipped the answer.

## Notes and limits, recorded

- The never-supersede / always-supersede control receipts are
  BY-CONSTRUCTION constants (the runner writes the extremes; they do not
  drive the store). This is the S7-3 prior's own control semantics, kept
  identical for re-measurement comparability (the prior's verdict shows the
  same shape). The instrument-reads-both-ends property is instead carried by
  the sanity gate plus this seat's replay: a store that could not rank the
  original top alone would have died before declaration, and the replay shows
  real retrieval moving both ways (distractors displaced, ledger originals
  held, updates displaced).
- `wts()` treats write clocks as dates (+00:00 midnight); fixed and
  increasing per the prior's convention; harmless here (no cross-write
  timestamp ties in play beyond ordering).
- Environment: host user site-packages python3.14, numpy 2.4.4 (the S7-3
  host site), replay in /tmp with the artifact read-only; kiln's full-rerun
  caveat (a re-run rewrites declaration.json and invalidates receipt
  bindings) respected — nothing was re-run in place, all hashes above are
  the artifact's current bytes.
- design.md carries the result table, the state-layer consequence, and the
  reproduction commands; declared scope ($0, local, no LLM, no score import)
  confirmed from source — the runner imports no model, no scorer, nothing
  metered.

**Verdict: the row's declared evidence is real, complete, and
independently reproduced. S11-3 VERIFIED PASS.** Sprint 11 is now fully
closed on the board's side: S11-1, S11-2, S11-3 all done and verified, gates
S11-1G/2G/3G all VERIFIED PASS. The open thread this row hands forward is
cairn's: the state-layer answer and the Gate F record must now absorb a
native arm that fails at 66.7% on broader histories.
