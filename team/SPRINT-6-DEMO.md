# Sprint-6 demo — publish the correction, then make the test honest

Sprint goal (QUEUE.md, top): *get the correction out, and leave the instrument
able to fail a system that just returns everything.* Three rows, S6-1 to S6-3.
All three are done; every one passed an independent gate before it could be
called done, and every one has since been independently verified (below).
What is asked of you is at the end — three items, one of which needs nothing
from you. Finalized at sprint close, 2026-09-17 ~13:0x PDT (first draft 09:25,
before the verdicts landed).

## What changed for you

1. **The wrong number on the record is corrected and published.** The two
   memory systems reported at 0/30 last sprint were measured on retrieval
   settings their vendors do not ship. The correction is written, published to
   the board with its hash, and says explicitly that it ranks no engine.
2. **The test can now fail a system that just returns everything.** Last
   sprint's instrument held one record per store, so returning everything
   guaranteed a hit — a 30/30 measured coverage, not skill. The new instrument
   has cases where the correct answer is to retrieve *nothing*, and it
   separates a selective retriever from the firehose (returning everything) by
   a declared margin.
3. **The roadmap now governs the work instead of sitting beside it.** Every
   roadmap commitment has a line: what was promised, which artifact supports
   it, its status, and the next decision it needs. The charter you approved
   with caveats has its stale sections named, each with what replaces it.

## Results — each with its number, its check, its artifact

**S6-1 — the correction (published).** What was reported: both systems at
0/30 on the frozen 30-moment corpus (FBMR_topic — "fires on all 30 moments
that matter"). Why it was wrong: each arm was scored on a retrieval surface
its vendor does not ship as the search path — the correcting knowledge was
already on file three days earlier and was not consulted. What the corrected
settings produce (S4-14 re-run, same corpus and harness, old against new):
claude-mem 0/30 → **30/30** on the vendor's actual chroma policy; pi-lcm
0/30 → **7/30** on the tool-level exact-then-relaxed path. No engine ranking,
per your approval. The two document defects found before publication (a
four-scenario count contradiction; future-dated fixtures) are fixed in the
re-run document first, and the note states the transferable finding:
*verifying the arithmetic did not validate the experiment.*
Artifact: `team/S6-CORRECTION/note.md` (sha256 `593cfd0b…`, rev-1), board
post [KIL 2026-09-17 08:1x]. Check: independent gate `check.py` written by
plumb-fable at 07:32, **before any artifact file existed** — clean, rc 0.
Independent verifier (corvid-dsh): **VERIFIED PASS**
(`team/CORVID-S6-1-VERIFY.md`) — one cosmetic citation note, non-blocking.

**S6-2 — the instrument that can fail the firehose.** Controls ran first, as
the row requires. Result: the controls **separate** selective retrieval from
the firehose — bm25 (a word-overlap retriever) 0.500 vs return-everything
0.200, gap 0.300 against a 0.250 margin declared before any run; the oracle
control (returns exactly the declared-helpful records) scored perfect on
every case, proving the scoring rewards the right answer. Because they
separated, the engines ran, with every adaptation labelled: pi-lcm tool-level
**0.600** (abstains perfectly — never retrieves on a should-retrieve-nothing
case — but rescues only 1 of 5 retrieve cases); claude-mem **0.250** — the
firehose level plus 0.05, which puts a number on "coverage, not skill"; bm25
**0.500**. Caveat in the same breath: bm25 fired on all five
should-retrieve-nothing cases because the in-tree tokenizer keeps function
words — declared in the review, not tuned away after the run. Engine numbers
are descriptive until independently verified.
Artifact: `team/S6-SELECTIVITY/` (design, corpus, manifest, results, decision,
review). Check: independent gate written 07:36, pre-artifact — clean, rc 0.
Design reviewed by Astra (the planning seat) against her own Sprint-6
specification, per `review.json`. Independent verifier (corvid-dsh):
**VERIFIED PASS** (`team/CORVID-S6-2-VERIFY.md`).

**S6-3 — the roadmap governs.** Eleven commitments mapped: five *supported*
by named artifacts, four *in-progress*, one *not evidenced here* (the Phase F
adopt/compose/build decision — recorded as absence-of-evidence, distinct from
*never-done*, which is the one commitment that has not happened anywhere and
is correctly held under the roadmap's own ban). Four charter sections are
superseded, each naming its replacement (the per-seat assignment map, the
seat-labor budget line, the origination mechanism, the blind-rater mechanic).
One experiment is **proposed, not built**: does retrieval selectivity convert
into material outcome on real work (fewer errors, less redundant
re-discovery, tokens/wall as the cost line) — selective pi-lcm surface vs
firehose claude-mem surface vs no-memory baseline, n=8 matched pairs per arm,
with an early-stop rule and an explicit "cannot distinguish" exit. It is a
proposal for your scope call, not a plan this sprint executed.
Artifact: `team/S6-ROADMAP/` (map, evidence, next-experiment, review). Check:
independent gate written 07:39, pre-artifact — clean, rc 0. Independent
verifier (corvid-dsh): **VERIFIED PASS** (`team/CORVID-S6-3-VERIFY.md`) with
one named minor defect: the map says "ten of the eleven named seats are
parked" where its own evidence lists eight — the structured data is correct,
the count clause is an arithmetic slip, and the disclosed correction line is
still owed by the author (kiln-flash).

## Scaffolding, not results

- **The gate rule.** New standing rule this sprint: the seat that writes an
  artifact does not write its gate. A new seat (plumb-fable) writes gates from
  the row text alone, before any artifact exists — a gate fitted to an
  existing document passes by construction. All three gates this sprint were
  written 07:32–07:39, before the first artifact file at 08:16.
- **D-1 (done):** the poller's log lines named the wrong seat for the ledger;
  the constant is fixed and the fallback is explicit.
- **D-4 (done, verified):** its machine check had passed while the work was
  undone — a check that cannot fail reads as a clean result. The check was
  amended to fail-first, the work redone, and the amended check re-confirmed
  from the reviewer seat at 12:26 (suite 116/0 plus the in-flight case it now
  requires; `team/CORVID-D-4-VERIFY.md`).
- **One incident, contained:** the reviewer seat sat dark ~30 minutes mid
  sprint (engine wedge, then a restart); no result was lost — the queue is the
  record and every verification is still queued.

## Verified — said plainly

Every result above is now **independently verified**: corvid-dsh (the
reviewer seat, which authored none of it) re-ran each declared check from its
own seat and re-derived the claims — S6-1, S6-2, S6-3 and all three gates are
VERIFIED PASS (`team/CORVID-S6-*-VERIFY.md`, verdicts 09:54–12:23). Two
caveats, in the same breath as the verdicts: S6-1 carries one cosmetic
citation note (non-blocking), and S6-3's map.md carries the count slip named
above, open until the correction line lands. The doer's own integrity notes
(in each `review.json`) remain notes, not certification — the doer dispatches
nothing but authors everything, so his word on his own work is the weakest
word in the room.

## What is asked of you — three items

1. **Sprint close — confirm or staff the remainder.** The machine reads the
   queue as complete: 73/73 build rows done-or-closed (standing fill-work
   excluded by design), spend $0.0299 of the $25.00 budget, and it has already
   asked you this question. Confirm the close, or name what stays open.
   *Cost: nothing.*
2. **The correction is published — no decision needed.** Your 2026-09-16
   approval ("publish the correction, not a ranking") is executed: board post
   with hash, canonical note, supersession of the 0/30 zeros stated. This item
   needs nothing from you; it is listed because the last demo's complaint was
   not knowing what was being asked.
3. **After 2026-09-20: the free window lapses and the fleet moves to the
   OpenCode Go budget (spend per row, not free turns).** The proposed S6-3
   experiment is the strongest candidate for first metered work, and it is
   scoped to be cheap to stop: n=8 matched pairs per arm, early-stop on
   regression, "cannot distinguish" as a completed result. Options:
   (a) **run it** under the Go budget after the 20th — cost is per-row spend
   on the doer seat, bounded by the stopping rule; (b) **defer** — the
   instrument stays frozen and quotable, the experiment stays proposed, no
   spend; (c) **re-scope** — tell us which question matters more and we
   re-derive the design. This is also the roadmap's Phase F decision
   (adopt / compose / build) in practice: the evidence map says what is
   supported; the choice of what to build next is yours.
