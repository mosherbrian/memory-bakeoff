# Review relay — query-relax targeted verification

Provenance: delivered as reply text by worker-glm-3 (GLM-5.3-Flash) on 2026-09-10 ~11:16 PDT,
bound to d11ab3c (16b5505..d11ab3c) on reset/practical-pi-20260907. Relayed verbatim below by
conductor-glm; transport line-wrapping may differ from the original pane. Record VERBATIM
(with this provenance header) at reviews/query-relax-review.md.

---

# Query-rel targeted verification — worker-glm-3 (GLM-5.3-Flash)

**Scope:** `16b5505..d11ab3c` (single commit, single file: `extensions/pi-project-recall/index.ts`, +68/−3), validation tree `~/.local/share/memory-bakeoff/rerun-20260910/query-rel/`. **4/4 PASS, no b
lockers.**

**(1) Read-path-only, read-only preserved, revertible — PASS.** The diff touches only the query logic in `index.ts` (new `relaxedVariants` + `MAX_RELAXATION_ATTEMPTS = 6`, `storeSessionBounds`, and th
e relaxation block in `runRecall`); the connection is still `openReadOnly` (`readOnly: true` / `readonly: true`), every attempted query is the same SELECT shape — strictly less restrictive, never a wr
ite. No harness, case, ledger, or docs files in the commit. Single-commit revert restores the prior behavior exactly.

**(2) Trigger widening (empty → no-prior-session-hits): correct AND safe.** *Correct:* with an empty-results-only trigger, the recorded c1 failure mode — the exact query matching the run's own prompt
echo — would never fire, because those queries returned live hits; the widened trigger is the minimal change that addresses the observed failure. *Safe:* it fires only when the store has >1 conversati
on AND the result is empty or live-only; tries at most 6 variants; accepts a variant only if it reaches prior-session content, otherwise the original result stands **unmarked** (empirically shown by q
uery 4 and all seven battery queries); accepted results are prominently marked `RELAXATION-SOURCED` with the failure reason and the relaxed query. Single-session stores — the normal new-project case —
 never relax, so the original result stands unchanged whenever no prior session exists. One cosmetic nit: the tool `description` still says "on an empty result the query is auto-relaxed" and doesn't m
ention the live-only trigger; the runtime header compensates, but the description should be updated whenever this lands anywhere durable.

**(3) Validation reproduced — PASS, numbers exact.** I ran `validate.ts` (the extension's real `runRecall` against the store copy `33cfb10aad6df144.db`) and the unit suite:
- Model queries: q1 → relaxed to `"steps per millimetre controller firmware"`, seed=1; `"microsteps stepper motor calibration"` → `"calibration"`, seed=1; `"gate position conversion factor"` → `"gate
position conversion"`, seed=1; `"gate position calibration"` → `"gate position"`, seed=2; `"stepper motor microsteps configuration"` → **seed=0, relaxed=false** — the code tried every variant and none
 reached prior content, which is itself the receipt for the zero-token-overlap claim (all four tokens absent from the seed). Counting the repeated q1 in both reps: **5 of 6 invocations now seed-surfac
ing**, matching VALIDATION.md's table row-for-row including the relaxed variants.
- Short battery: all seven queries `relaxed=false` — **relaxation never fired**; results identical by construction (these queries reach seed on the exact query, so relaxation could not trigger) and by
 observation. One cosmetic inconsistency: VALIDATION.md says "results identical to recorded" but prints 3/5/2/4/2/2/2 where `C1-QUERY-BATTERY.md` recorded 2/4/2/4/1/1/2 — the difference is purely coun
t basis (the battery artifact counted message hits; `validate.ts` counts scope=all hits, i.e. messages **plus** the seeded summary's LIKE hits, which explains exactly the +1s). Substance correct; the
wording could name the basis.
- Tests: **12 pass, 0 fail** — reproduced at `d11ab3c`.

**(4) F1/F2 untouched, addendum correctly labeled — PASS.** The commit changes no outcomes and no result documents; the addendum in `dispatch/RERUN-20260910.md` (lines 221+) explicitly labels the work
 "mechanism test ONLY — descriptive; does NOT change any F1/F2 outcome, adds no evaluation slots, runs no pi invocation and rescores nothing." One cosmetic note: the addendum lives in the untracked di
spatch file; the git-tracked `docs/` results copy doesn't carry it — fold it into `docs/` at the next docs commit so the git record stays self-contained (same ownership convention as the dispatch file
 itself, so not a blocker).

**Bottom line:** the relaxation mechanism is bounded, marked, read-only, revertible, and does what the recorded c1 evidence said was needed — 5/6 of the model's actual failed queries now reach the see
ded decision content, the sixth is provably unreachable by any term-drop, and nothing about F1/F2's outcomes or claims moves. Reviewer time ≈ 7 min. **PASS — released.**