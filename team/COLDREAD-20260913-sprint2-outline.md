# COLD-READ — SPRINT-2-OUTLINE.md (Brian-facing, awaiting his sign-off)

**Reader:** Stratum, per the cold-read queue rule ("any Brian-facing artifact
gets one read before it leaves"). The outline is GiLMore's file (2026-09-13
~09:5x); I changed nothing. **Scope:** the whole outline — it is short and it
is the single surface Brian is being asked to act on (rulings queue item 5).
**Method:** read against `team/BRIAN-FACING-STYLE.md` (4 rules) + staleness
against the team record as of 2026-09-13 ~21:5x PDT. One read, $0.

## Verdict: HOLD — do not send as-is. One stale ask, one missing ask; the rest is wording.

The outline does the style rules right: it is short, goals are Brian-story
sentences, the asks are enumerated, and the "NOT doing" section states the
stop switch. Nothing below touches its structure — the findings are that the
day outran it in three places.

## Findings (for GiLMore; owner fixes, reader never edits)

1. **Ask 2 was already answered — and the real decisions replaced it.**
   "The word on transcript-miner scale-up (pilot read)": Brian gave the word
   (approved with the closed-sessions rule), and the full corpus executed
   same-day (`TRANSCRIPT-MINING-FULL.md`, consolidated): 1,250 closed files →
   **4,098 unique operator turns**; **270 correction events** + 26
   repeated-instruction groups (240 events); **324 durable-fact candidates**
   (318 unique groups in the digest); 230 personal turns excluded, never
   persisted. The decisions Brian actually faces now are the note's "Next
   decision": (a) read/mark the 324-candidate digest — or delegate the
   curation criteria; (b) whether a model-assisted second pass runs. As
   written, the outline asks him a question that no longer exists and never
   surfaces the two that do.

2. **Goal 2's gate is satisfied; state it as an asset, not a pending gate.**
   "Full-corpus run gated on Brian's pilot read" — the gate is met. The
   correction corpus now exists with per-class precision bands that are
   decision-relevant to the invocation benchmark it feeds: negation and
   i_said ~100%, actually ~80%, env_fact_correction ~30–50%, wrong ~20–40%
   (local-eyeball samples, n≈5–8/class). A cold reader cannot tell from the
   outline whether goal 2 can start Monday; from the record, it can.

3. **A Brian decision exists outside the ask list.** The external-corpora
   recommendation records "Brian's two asks": the transcript-miner pilot word
   **and accepting the SWE-chat HF gate on the team account**
   (`EXTERNAL-CORPORA-RECOMMENDATION.md`; map row, 09-13). The pilot word is
   (stale-)listed; the SWE-chat gate decision is absent from "Asks of
   Brian." If the outline is the one Brian-facing ask surface before the
   window closes, it should carry both — or point at the recommendation for
   the one it omits.

4. **Housekeeping off-by-one, and the item finished tonight.** "Row 28 prune
   slice: Kiln + Verity co-sign" — the prune co-sign is **QUEUE row 29**
   (row 28 is the P2-entry second-driver verification). Verity's co-sign
   **landed 21:46 tonight, PASS** (`VERITY-KNOWN-FAILURES-PRUNE-COSIGN.md`):
   the prune is done and reviewer-visible. Mark it complete and fix the row
   number so Brian's checklist matches the queue.

5. **Goal 5 is partially executed — say so, or Brian will re-ask for done
   work.** Four candidate cards are filed since the outline was drafted
   (MemOps; StreamMemBench; STALE + Supersede; MemSecBench + GateMem) — all
   abstract-level, no score import. The outline's own name list still
   un-carded: StateMemBench, LongMemEval-V2, HaluMem, EvoMemBench/EvoArena.
   One status line ("4 of the named benchmarks carded; 4 remain") converts
   goal 5 from a promise into progress Brian can check.

6. **Ask 3 is right but one step short.** "R2 day-0 timing" is Brian's only
   R2 decision, correct. But the frozen-and-verified rev-2 deploy script
   still needs a **re-send to Brian's work machine before day 1** (Assay's
   register, row 9). Brian's cost is zero; the outline should name the send
   as a pending team step so "whenever convenient" doesn't silently become
   day 1.

## What the outline gets right (keep)

Story-format goals with the artifact each produces; the envelope/fairness
constraint stated once, plainly; "what we are NOT doing" as the stop switch;
housekeeping kept off Brian's critical path. With findings 1–3 fixed it is
serveable on a first read, which is the only read a busy human gives it.

— Stratum, cold-read pass. 2026-09-13 ~21:5x PT. No file touched but this
note; $0.
