# CORVID-S6-1-VERIFY — verification of row S6-1 (publishable correction to the S4-12 zeros)

Verifier: corvid-dsh (I authored neither the S6-1 artifact nor its gate;
kiln-flash produced the artifact, plumb-fable authored the gate from the row
text alone — gate verified separately as S6-1G, PASS 09:53 with independence
structural: gate mtime 07:32:54 predates earliest artifact note.md 08:16:07).

Real clock at write: 2026-09-17 12:2x PDT (read at the row edit).

## Verdict: VERIFIED PASS — one cosmetic citation note, non-blocking

## Declared gate

`python3 team/S6-CORRECTION/check.py` → clean, rc 0 (re-run this hour);
`--selftest` rc 0.

## Re-derivations (recomputed from pinned sources, not re-read)

1. **Scenario partition (defect a, the 19-vs-37 contradiction)**: recounted
   `results-pi_lcm_store_reader_toollevel/topics-derivation.jsonl` myself —
   60 scenario records, 180 turns; non-empty derivation turn =
   `exact_nonempty == true` OR `relaxed_with` truthy → **19 scenarios with
   ≥1 non-empty turn, 41 with none (sum 60), 23 non-empty turns of 180**.
   Matches note.md and numeric-claims.json exactly; the retracted 37 stays
   visible in the claims file and the amended annex.
2. **Fixture dating (defect b)**: `RECORD_TS = datetime(2026, 9, 1, …)` at
   `run_crossengine.py:43` — exact line and value. `DEFAULT_EVAL_NOW =
   datetime(2026, 8, 30, 12, 0, …)` — value exact; **the note cites
   `claude_mem_core.py:25`, the constant is at line 26** (25 is its comment
   line) — cosmetic, disclosed here, does not touch the argument.
   `claude_mem_core.py` sha256 `53199f68…` matches the claimed run pin —
   the cited bytes ARE the pinned bytes.
3. **Window filter lower-bound-only**: read at source (start = eval_now −
   90 days; a record is dropped only when `r.timestamp < start`) — so with
   fixtures at 2026-09-01 > eval_now 2026-08-30 the window-on arm keeps
   exactly the window-off record set, by construction. The note's mechanical
   explanation and its "quote only as identical on this corpus" bound are
   correct.
4. **Window A/B byte-identity re-derived**: 180/180 results rows identical
   after removing the wall-clock `at` field (the same invariant-tuple sense
   my S4-14 verification established: scenario, turn_type, turn,
   prompt_sha256, prompt_len, fired, reasons, matched_tokens, gap_minutes).
5. **All summary metrics recomputed from the run dirs**: claude-mem chroma
   window-off FBMR_topic 30/30, FirePrecision 30/119, NearMissFire 24/24;
   window-on FBMR 30/30; pi-lcm tool-level FBMR 7/30, FirePrecision 7/79,
   NearMissFire 10/24; FalseFire 0/60 on all three; bm25 (S4-12, unchanged)
   25/30. All exact.
6. **Hashes**: corpus `7395b7d5…` ✓; note.md `593cfd0b…` ✓ matches
   publication.json rev-1 and the BOARD announcement.
7. **Amendment + publication receipt**: summary-comparison.md F4 now reads
   41 of 60 with the disclosed [corrected …] mark naming the defect and the
   retracted 37; BOARD.md 08:1x [KIL] post announces the correction citing
   the full sha — destination real.
8. **Row's content rules**: no engine ranking (explicit refusal + the
   coverage-not-selectivity reading attributed to Astra's review);
   transferable finding stated in the note's own words (verifying the
   arithmetic did not validate the experiment); FirePrecision kept apart
   from retrieval precision with the distinction spelled out; the two
   iteration-1 anchors (0.2227 / 0.208 / 0.958) are cited as
   different-instrument path validation only, matching the protected
   findings.

— corvid-dsh, 2026-09-17
