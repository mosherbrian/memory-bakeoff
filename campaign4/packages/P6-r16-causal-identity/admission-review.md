# P6-r16-causal-identity — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r16-admission-1`, start `01:00Z`, deadline `01:10Z`
- **Brief:** `package.md` sha256
  `166125b26e499f7e902dc4814e72147918bf9d4e2992f76864881855f77ad729`; director
  release pinned.
- **Scope:** read-only admission + pinned concrete checks. No source edit.

## Verdict

**ACCEPTED (bounded).** The demonstrated gap is real and exactly as R15 recorded:
`case_entry._check_causal` selects the lexicographically first onset file
(verifier item) and pairs it with the worker detection, falsely raising
`E_CAUSAL`. The fix is confined to `case_entry.py`, and the authoritative mapping
is derivable from the signed manifest/turn bindings already in scope — no
filename, seat-label or prefix heuristic required. One bounded scope note is
pinned (item→action binding must come from verified bindings, not sidecar
self-assertion). Conditional kiln release follows this admission + pinned checks.

## Pin resolution

- R14 parent source `02ea693e48cc…`; acceptance commit `a7dadd7`; candidate outer
  manifest file sha256 `8584cbed8a97…` (= `candidate/manifest.json`).
- R15 evidence commit `872bb3c91533…`; `terminal-disposition.json`
  (`EXHAUSTED`, `INCOMPLETE_LIVE_WITNESS`, evidence `872bb3c9…`, verification
  `719c495c…` = `live-review-failed-1.md`); sibling evidence `live-failed-1/`.
- Governing rulings `4be99bf`, `84f094e`, `afa126f`, `650830c`, `5fefb0f`
  resolve; no altered bounds.

## Demonstrated gap (reproduced earlier, preserved)

R15: worker item `id492c9c28b64` onset `00:51:11`, verifier item
`i42e65da2879b` onset `00:52:37`. `sorted()` puts `i42…` first, so
`_check_causal` paired the verifier onset with worker detection `00:51:11` →
`E_CAUSAL`. Genuine authenticated rejection and 1+1 sends were already present;
only the timing gate was incomplete.

## Scope feasibility (authoritative mapping available)

In `run_case`, the signed manifest and observed bindings provide the required
identity: `manifest["worker_item"|"verifier_item"]` / receipt `items[wsid|vsid]`,
`det_by_action[action]`, and the turn bindings
(`turn-bind:<stream_key>:<item>` → action/execution/step). Onsets carry
`item/time/provenance/uncertainty`. Therefore each observed action's onset can be
joined to **its own** detection via the verified item→action binding.
**Bounded scope note:** validate the source item against its bound runtime item
and reject missing/ambiguous/conflicting mappings, nonfinite/negative uncertainty
as explicit owned INCOMPLETE/error — never fall back to filename order or seat
labels. If the allowed surface cannot carry the authoritative binding, return the
scope defect before coding.

## Pinned concrete checks

Positive / semantics:
1. Old wrong-pair diagnostic on immutable parent using **copies** of R15
   evidence (no historical edit) → reproduces `E_CAUSAL`; new code joins worker
   onset↔worker detection and verifier onset↔verifier detection, no cross-pair.
2. Reorder worker/verifier filenames both ways; an unrelated **earlier-sorting**
   unbound onset cannot change the result.
3. Distinguish control arm/apply time from worker/verifier completion onset; do
   not require verifier onset before worker detection. Keep causal inequalities
   and original finite uncertainty semantics (boundary passes/fails per ruling).
4. Genuine onset-after-own-detection and arm-after-source remain rejected;
   producer missing clock proof is never replaced with detection time.
5. At least one **unshared** independent identity mutation (not supplied by
   kiln). Exact production CLI composition with injected collaborators, not
   helper-only PASS. Replay of recorded R15 is DIAGNOSTIC new-code evaluation,
   never a retroactive live PASS.

Negative (must reject / classify):
6. Wrong execution/session/item/case mapping; swapped sidecar content; missing
   worker source; conflicting duplicate for the same bound identity → explicit
   owned error/INCOMPLETE, never arbitrary selection.
7. Missing optional action after a genuine rejection stays classified by the
   existing case requirements; no invented success.

Retained gate: composed 70 + P5 83 + P3 59 on the **actual new modules** with
recorded paths/hashes; no skip/deletion/weakening; counts grow only by explained
new tests; any inherited assertion conflict returns Tern. Preserve authenticated
rejection, no-COMPLETE, no-duplicate sends, T1–T4 and R13 safeguards; core and
every non-`case_entry.py` production byte compares to parent; descriptors/
manifests rehashed with correct `identical` flags and no self-reference.

## Bounds

ONE kiln ≤30 m then ONE corvid ≤30 m; admission 10 m separate. Ceilings
`1200worker/975verifier` → `1230/1005`. No automatic repair; honest timeout/FAIL/
INCOMPLETE returns Tern with bytes preserved. Known suite ~11 m — no 120 s
substitute. Live releases are separate; no live retry or fixture resurrection in
this allocation.

## Effect

Admission **ACCEPTED (bounded)** with the pinned concrete checks and the mapping
obligation. No implementation or release conferred. Returned to cairn/Tern.
