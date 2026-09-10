# Review relay — RERUN-20260910 Stage C result review

Provenance: delivered as reply text by worker-glm-3 (GLM-5.3-Flash) on 2026-09-10 ~10:25 PDT,
bound to 2f562e2 on reset/practical-pi-20260907. Relayed verbatim below by conductor-glm;
transport line-wrapping may differ from the original pane. Record VERBATIM (with this
provenance header) at reviews/rerun-stageC.md per the standing review-recording rule.

---

# RERUN-20260910 Stage C result review — worker-glm-3 (GLM-5.3-Flash)

**Reviewed:** commit `2f562e2a727b4b05c9c43e7bf22c7c044c6ff60c` on `reset/practical-pi-20260907` (pushed; harness prep `682f90a` + `f96ef6d` + `2f562e2`, all on top of the closed reset's closeout), th
e predeclared plan `dispatch/RERUN-20260910.md`, and evidence under `/var/home/bmosher/.local/share/memory-bakeoff/rerun-20260910/{stageA-receipt,f1,f2}/`. Every load-bearing number below was recomput
ed by me from ledgers and raw event streams, not taken from the report.

## Verdict

**F1 NULL: supported. F2 "both sub-criteria MET, descriptive-only": fair, with two documentation corrections and one recommended artifact — none decision-changing.** No blockers. The decision package
to Brian can go out after the two wording fixes below.

## 1. F1 — the null is real this time

- **16/16 completed, zero failure codes** — all ledger rows `status=completed`, verifiers pass/fail (never error), no timeouts, no interruptions. Alternation in execution order is A,B then B,A per cas
e.
- **c1 fails requirement B in all four runs, both arms** — identical traceback in each: `frame(10) → steps:80, expected 40`; requirement A passes by assertion order, same as R2. c2/c3/c4 pass everywhe
re; c4's verifier (`VERIFIER OK` ×4) keeps the bound at 100.
- **0/8 `project_recall` invocations in arm B, with the seed verifiably reachable.** Receipts: every B run's ledger `tool_calls` (parsed from `tool_execution_start`) contains none. Reachability: I rec
omputed `sha256(process.cwd())[:16]` with node inside four run worktrees — `c1-b-rep1` → `3c692898516327b8`, `c2-b-rep2` → `98ec450b7cd7283e`, `c3-b-rep1` → `69f208fdc5e44a0a`, `c4-a-rep2` → `199e3a79
e3fca7d7` — each equals the single store filename in that run's `lcm/` dir, and sqlite read-only inspection confirms each store holds the seeded conversation(s) (c4 has both `seed-c4-older` and `seed-
c4-newer`) plus the run's live conversation. The R3 defect is fixed; the guard (`verify_store_reachable`, `run_pi_pilot_r2.py:203-213`) does exactly this check before any pi invocation and 16 completi
ons prove it never fired.
- **Prompt fidelity:** all 16 F1 rows' `prompt_sha256` equal sha256 of the frozen R2 prompt strings — verbatim reuse, cryptographically confirmed.
- **Overhead arithmetic both bases:** I reproduce 8-pair wall 28.35 → 28.73 s (+1.3 %) and 6-passed-pair wall 29.15 → 28.73 s (−1.4 %), tokens 27 250.5 → 29 804 (+9.4 %). One rounding nit: 8-pair toke
ns 30 449 / 27 250.5 = **+11.7 %**, not the claimed +11.8 %. All within the 25 % threshold either way.

Predeclared consequence correctly drawn: retain baseline; "no measurable gain when reachable and unprompted" is precisely what the receipts show. R2's finding (i) was not a wiring artifact.

## 2. F2 — counts, surfacing, and the open self-check

- **Invocation counts:** 18 `project_recall` `tool_execution_start` events total; per run c1 3/3, c2 2/1, c3 3/3, c4 1/2 — ledger == results doc (the conductor relay's "c3 3/4" is a relay typo). 8/8 r
uns invoked ≥ 1 (criterion ≥ 4/8 met with margin). All 8 rows are arm B, `nudge=true`, `phase=f2`; the c1 F2 `prompt_sha256` equals exactly frozen-prompt + predeclared nudge.
- **Surfacing, from transcripts (tool_execution_end results, not inference):**
  - c2 **both reps**: rep1 query `sailing` → 9 hits + 1 summary including six `seed-c2-prior` hits (the no-wrap/None decision, "12:00 sailing pending approval, not added", plus the seeded summary row)
; rep2 `sailing next_sailing` → seed hits with the None decision. Marker demo: `pending approval` appears 11× in rep1's raw stdout.
  - c4 **both reps**: rep1 → `seed-c4-newer` ("future change will make clamp return zero … only restored the 100 percent upper bound"); rep2 second call `clamp function` → `seed-c4-older` ("Cap the va
lve opening at 80 percent").
  - c3 control: all queries live-only, zero seed content — as designed. c1: never surfaced (below).
- **The open self-check resolves in favor of the direct hits.** The authoritative keys (`tool_execution_end.result.content[].text`, mirrored in `message_start`/`message_end` `role=toolResult`) verifia
bly contain seeded content with per-hit seed-conversation annotations, and seeded markers are present in raw stdout. Any seeded-marker grep that contradicted this must have used a full-length phrase (
tool snippets are 280-char truncated with `…`) or a single key among the several the content propagates through. Truth from events: surfacing happened where claimed.
- **c1-never-surfaced and the binding-constraint claim: supported — and I strengthened it.** The model's four actual c1 queries (e.g. `"steps per millimetre controller firmware gate positions"`) retur
n live-only hits, 0 from `seed-c1-prior`. I ran a query battery against the real c1 store through the extension's own AND-sanitization: `"steps per millimetre"` — the exact phrase in the task prompt —
 returns 2 seed hits; `"firmware"` 4; `"STEPS_PER_MM"` 2; `"telemetry steps"` 4; `"split"`, `"encoder ratio"`, `"control room displays"` seed-only hits; and a seeded summary ("Firmware swap planned: e
ncoder ratio doubles…Decision…") is LIKE-matchable. So retrieval itself works at short seed-vocabulary queries; the model's 5–7-token AND-queries were the failure. "Query formulation (or tool-side que
ry relaxation)" is the correct diagnosis. **Recommendation:** append this battery (queries + hit counts) to the evidence tree as an artifact so the claim, like everything else, is receipt-backed.

## 3. Corrections required in the decision package (documentation only)

1. **Overclaim, source: results doc line "in c4 both reps the recall results included the superseded 80 %-cap history."** False for rep1: its single call returned 2 live hits + 1 `seed-c4-newer` hit o
nly — no 80 %-cap content anywhere in that run (`grep -c "80 percent"` stdout = 0). True for rep2. The finding's substance survives reworded: *task-relevant use in both reps (rep1: recalled the seed's
 authoritative bound-100/deferred-negatives decision; rep2: additionally retrieved the superseded 80 %-cap and did not act on it); final bound 100 and verifier passing in both.*
2. **"+11.8 %" → "+11.7 %"** (median-token rounding, 8-pair basis).

Non-blocking observations to carry: c2 rep1 surfaced "12:00 sailing pending approval, not added" and the model added it anyway per instruction — a surfaced-constraint-not-acted-on instance that reinfo
rces keeping F2 strictly descriptive; Stage A retry 1's artifacts were overwritten after its evidence was quoted in the report (disclosed, checker fix committed `f96ef6d` — acceptable, but quote-then-
overwrite is worth avoiding in future stages).

## 4. Ceilings, accounting, integrity

Slots: F1 16/16 (≤16), F2 8/8 (≤8). Machine: Σ wall over 24 evaluation runs = 12.5 min + receipt 16.6 s ≈ 0.21 h of 6 h. Implementer ≈ 0.4 h of the 4 h shared ceiling; commit timestamps (09:41, 09:43,
 09:52 PDT) are consistent with the stated Stage A/B windows. F1/F2 `PREP_MANIFEST.json` written at phase start (16:52 Z / 17:00 Z); all eight case transcripts sha256-identical to the reviewed R2 seed
s. Private evidence lives at the durable real-home path; `PILOT_R2_PRIVATE` kept the closed reset's `r2/` tree untouched (still 926 files, ledger unmodified). Reviewer time this dispatch ≈ 1.0 h of th
e 2.0 h ceiling.

## Bottom line for Brian

With the seed reachable, the corrected rerun confirms: **unprompted, the model never reaches for cross-session memory (0/8); prompted, it always does (8/8), and the tool returns real prior-session con
tent — but in the one failure-critical case its own query style (long AND-queries) missed vocabulary that short queries would have retrieved easily.** Neither phase changed any verifier outcome; overh
ead is within threshold; no stale action occurred. F1's null and F2's descriptive "met" are both supported by receipts. Pi-LCM stays unchanged; the interesting open question for any future budget is q
uery formulation/relaxation, not wiring or willingness.
---

# Implementer repair-pass record (worker-glm-2, 2026-09-10 ≈10:35 PDT)

Appended after the verbatim relay above; not part of the review text.

- Correction 1 applied in `dispatch/RERUN-20260910.md` (Stage B result
  section, F2 paragraph): the "in c4 both reps … superseded 80 %-cap
  history" clause reworded per the review — task-relevant use in both reps
  (rep1 recalled the seed's authoritative bound-100/deferred-negatives
  decision; rep2 additionally retrieved the superseded 80 %-cap and did not
  act on it); final bound 100 and verifier passing in both reps. The
  results doc (`docs/RERUN-20260910-stageB-results.md` and its dispatch
  copy) never carried the overclaim; its c4 task-relevant-use bullet was
  extended to state rep1's use explicitly so both documents match the
  corrected wording.
- Correction 2 applied: `dispatch/RERUN-20260910.md` overhead line now
  reads +11.7 % (was +11.8 %). The results doc already stated +11.7 %.
- Non-blocking notes carried: (i) c2 rep1 surfaced "12:00 sailing pending
  approval, not added" and the model added it anyway per instruction — a
  surfaced-constraint-not-acted-on instance reinforcing F2's strictly
  descriptive framing; (ii) Stage A retry 1's quote-then-overwrite of
  evidence is acceptable-once-but-not-again; future stages preserve
  overwritten-run artifacts.
- Recommended artifact written:
  `~/.local/share/memory-bakeoff/rerun-20260910/f2/C1-QUERY-BATTERY.md`
  (the reviewer's c1 battery plus the model's actual transcript queries),
  receipt-backing the binding-constraint claim.
