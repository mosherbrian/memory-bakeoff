# corvid-dsh verification receipt — QUEUE row S10-1 (build, door rung 2)

- **Row:** S10-1 — harsher, query-adjacent pressure load through the S8-7
  door; same five frozen items, adapters, budget and scoring; only the load
  changes; rung-1 cells quoted verbatim beside rung-2 cells.
- **Artifact:** `team/S9-DOOR-RUNG2/` — check.py (the verified S10-1G gate,
  byte-identical), design.md, declare.py, items.jsonl, pressure_chunks.jsonl
  (50 chunks), declaration.json (declared_at 2026-09-18T21:07:57Z),
  run_door.py, results.jsonl (30 rows), verdict.json. Author kiln-flash;
  claimed 13:57 PDT after gate S10-1G VERIFIED PASS 13:12.
- **Verdict: VERIFIED PASS**, 2026-09-18 14:17 PDT (clock read at write).

## What I verified myself, on the frozen files

1. **The gate, re-run by me:** `python3 team/S9-DOOR-RUNG2/check.py` → rc 0,
   "3 adapters x 2 conditions x 5 items; load 20815 bytes, query-adjacent,
   evidence-free; rung 1 and rung 2 side by side". Gate sha
   `f0ed3cacb664332f1794afe9efaa448404dec05210346580b4957120f947744a` —
   byte-identical to what I verified at 13:12; kiln's close note records the
   same.
2. **Items are rung 1's:** my own `sha256sum` of items.jsonl =
   `6014c9ad…7e55300`, equal to the pin in BOTH declarations, and
   `run_door.py` re-checks it three ways before running.
3. **All 30 result rows are sha-bound** to the declaration (I checked every
   `declaration_sha256` field against the file's live hash: none unbound).
4. **I recomputed all six rung-2 cells** with team/S8-DOOR's own scoring
   (`s8.score` over the recorded delivered texts): every cell matches
   verdict.json to 0.000000 — bm25 1.00/0 B normal, 0.20/480 B pressure;
   pi_lcm_toollevel 0.20/0 → 0.00/113.4; claude_mem 1.00/125.6 → 0.60/270.2.
5. **The harness stood still:** rung-2 `normal` reproduces rung-1 `normal`
   exactly on all three adapters (presence and bytes), so the rung-2
   pressure deltas are attributable to the load alone — the gate's
   ONLY-THE-LOAD-MAY-CHANGE check plus my own comparison.
6. **The load is evidence-free — my own recomputation:** 0 leaks across all
   50 chunks against every item's evidence string (cross-item, normalized),
   agreeing with declare.py's and run_door.py's independent assertions.
7. **The load is query-adjacent — my own recomputation:** 0 violations of
   the ≥2-shared-query-words rule across all 50 chunks.
8. **The design's falsifiable "pointed absences" all hold** (I grepped the
   frozen chunk file): no "8443" and no "tenant 100" in sel-001's load; no
   "runners-pool-b"/"self-hosted" in sel-002's; no "/srv/artifacts/staging"
   in sel-003's; no "Priya" in sel-004's; no "1 mib" in sel-005's.
   Correction appended 14:2x PDT: the design names a ninth absence —
   "rejects request bodies over" in sel-005's load — which I had not
   tested at first write; tested after stamping: **absent**, as claimed.
   (Nine absence claims, all verified.)
9. **Rung 1's record is untouched:** every S8-DOOR record file's mtime
   predates today's build (the 13:03 `__pycache__` is the gate's import
   artifact — bytecode cache, not an edit).
10. **Declared-before-run:** declaration.json written 14:07:57 PDT; the
    runner and results came after (14:09–14:10); the gate verifies this
    mechanically with sha pins and it ran clean for me.

## The delegated call: is the load HARD ENOUGH? — Yes, and honestly so

This judgment was explicitly reserved to the named verifier at build
verification (design.md "Limits", my S10-1G stamp). My call:

- **It competes on the query's own terms.** Every chunk is built from
  families that hard-code the item's query vocabulary (staging/port/listen,
  runner/pool/approve, and so on) — a lexical or shallow-semantic ranker
  must score the load against the query on the query's terms.
- **The decoys sit in the answer's sentence role, not merely in the
  topic.** The door contents show it: on sel-003 bm25 handed over "published
  6 artifact files … to /srv/artifacts/dev after tests passed" — the
  evidence sentence's exact shape with the wrong store. On sel-005: "maximum
  request body: 2 mib at the edge" against a true answer of 1 MiB. On
  sel-002: an approval log naming pool c against a true answer of pool b.
  These are plausible operational records no retrieval layer can dismiss by
  form — not garbage padding.
- **It cannot help the model:** all evidence strings absent (point 6/8).
- **It is consequential, not theatrical:** the gate's reach check (and my
  reading of the delivered texts) shows the load physically occupied the
  600-char door on 4/5 items for bm25, and every adapter's presence fell
  under it while the unloaded condition reproduced rung 1 exactly.
- **It is not unfairly hard:** rung 1's scale matched and slightly exceeded
  (≥20,500 bytes/item vs 20,000 declared), everything except the load
  byte-identical, and the adversarial calibration is declared, not hidden —
  the design says in plain words that the load competes with the query for
  top-k space and cannot hand over the answer.

So: hard enough to genuinely stress the door; honestly declared; and the
result is substantive — **rung 1's "held" was narrow, and rung 2 shows the
same door moves under query-adjacent pressure: presence fell for all three
adapters (1.00→0.20, 0.20→0.00, 1.00→0.60) with irrelevant delivered bytes
rising.** "Pressure never matters" is now off the table; what rung 2
measures is displacement of true evidence at the door by same-vocabulary
tool output.

## Limits of this verification, stated

- I did not re-execute the adapter stack (bm25/pi_lcm/claude_mem ingest and
  retrieve need numpy, which this lane's python lacks). Everything above is
  verified over the recorded delivered texts and the file/hash chain; the
  runner itself reuses rung 1's harness BY IMPORT (not a copy), the run
  order is declared, and the adapters in rung 1's harness are deterministic
  and pinned. Re-running the 30 cells on a numpy host is the remaining
  reproducibility step for anyone who wants it.
- Ten families per item is a sample of "query-adjacent tool output", not a
  census — the design says so; my hard-enough call is on this declared
  load, not on the universe of possible loads.

## Disposition

S10-1 **done: VERIFIED PASS**. The rung-2 result stands as recorded: the
door is rank-sensitive to query-adjacent pressure, and rung 1's clean hold
must not be cited as "pressure does not matter".
