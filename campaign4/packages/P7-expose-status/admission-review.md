# P7-expose-status — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P7-admission-1`, start `03:41Z`, deadline `03:51Z`
- **Brief:** `package.md` sha256
  `e4adcd51f8e0e8bcff439761275e9d6e09106ce36fd3c790647f779884cae529`; director
  release pinned.
- **Scope:** read-only admission + pinned small adversarial checklist. No edits.

## Verdict

**ACCEPTED (bounded).** The deliverable is a read-only, derived status view +
machine-readable pending list with one documented render command, tests and a
source-map README. The basis, pins and existing shared artifacts resolve, and the
adversarial checklist is pinnable against real current evidence (open S13-1
decision, the retracted false-alarm row, R18 accepted vs R19 terminated). One
bounded readiness note: the inventory is pointers, not a second authority, and
rendering must be proven non-mutating and stable.

## Pin resolution

- Basis `campaign4/CONNECT-FINISH-LINE-20260923.md` present.
- R18 accepted source `7857c0ce86fd…`; R18 acceptance commit `b94ce3f`; R19
  `terminal-disposition.json` = **TERMINATED** ("Director engineering boundary:
  close Connect, move to Expose; not a technical failure", `live_executed:false`,
  admission preserved, successor P7).
- `ACCEPTED-ARCHITECTURE.md` (sections 5/7/8) and `CHARTER.md` present;
  `campaign4/pending-decisions.md` and `control-events.tsv` exist and are
  **not to be rewritten**. New P7 allocation is separate from historical P6
  ceilings `1360worker/1135verifier`.

## Pinned small adversarial checklist

Content / truthfulness:
1. **Injected unresolved judgment** (real open row `S13-1`, owner **tern**) must
   render with the exact question, owner, dependents, deadline (or explicit
   unknown) and next action — not a vague "blocked".
2. **Resolved/retracted** decision (the `07:38 RETRACTED — FALSE ALARM` row) links
   its source and **ceases** to be pending; it must not inflate the pending list.
3. **Missing/stale/contradictory evidence** renders as `UNKNOWN`/`CONFLICT` with
   owner and links — it must not look healthy, and the view never infers `PASS`
   or real-time liveness.
4. **Stale timestamps labelled**; accepted evidence distinguished from merely
   `PASS`/historical live witness (e.g. accepted R18 source vs R19 terminated,
   R9 historical positive).
5. **No invented sponsor decision**; authority not inferred from package-name
   order or model-typed timestamps; the edited TSV is a labelled activity log,
   not immutable truth.
6. **Allocations ≠ actual costs**; unavailable cost/timings explicitly `unknown`.
7. First real view includes the **Connect ruling**, the accepted R18 source and
   the P7 current state, with current code directory links; history retained.

Behaviour / safety:
8. **Render command** documented and single; output is derived and host-stamped
   with an explicit **as-of** time.
9. **Non-mutating:** rendering must not change any input; a repeat render is
   byte-stable except the as-of time; tests assert no writes to the shared
   `pending-decisions.md`/TSV or core state.
10. **Read-only inventory**: `inputs-index.json` is a declared pointer list, not a
    second mutable authority; no credentials read; no hosted server/new
    dependency/state mutation/live control.
11. **No automatic scheduling** claimed from the view (dependent enforcement is
    P8); no source extraction/core-adapter rewrite/deployment/multi-project.
12. **Stop at cap:** no reset or automatic successor; if a check is missing, state
    it rather than expand.

## Deliverables expected (for the gate)

`src/`, `tests/`, `status.md` (or self-contained HTML), `pending-decisions.json`,
`inputs-index.json`, `README.md`, manifest and completion claim; compact receipts
with full hashes in files and the exact completion wake command in every prompt/
receipt. On independent PASS the director may publish the derived view at the
campaign root.

## Bounds / sequence

Admission ≤10 m (this); conditional worker ≤45 m, verifier ≤20 m, plus ONE
eligible correction ≤15 m and its verifier ≤10 m (overall 100 m). Worker
conditional only on unchanged accepted contract + pinned checklist/review and no
overlapping writer; no P8/P9 execution authorized here. Cairn host-read
start/deadlines and one-shot timers; every dispatch/receipt carries the exact
executable wake.

## Effect

Admission **ACCEPTED (bounded)** with the pinned adversarial checklist and the
read-only/pointers-not-authority note. No implementation or release conferred.
Returned to Tern.
