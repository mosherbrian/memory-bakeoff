# P9-go-supervised-preview — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P9-admission-1`, start `06:03Z`, deadline `06:13Z`
- **Brief:** `package.md` sha256
  `63053fe3447fe05dcdc882fe60db5c3a4e6224c7390a55994010c33916d362a3`; director
  admission delivery pinned.
- **Scope:** read-only admission + pinned checklist. No implementation.

## Verdict

**ACCEPTED (bounded).** Pins resolve and are co-pinned; the fixed-roadmap scope
(read-only Go status/Expose view + packaging/docs from commit `71318c4e`) is
buildable **without touching frozen control modules**, and the six predeclared
checks are concretely pinnable. P8 is honestly `NOT_READY_UNATTENDED`; P9 must not
render qualification green and must label known liveness blockers. Conditional
Claude release follows this unchanged ACCEPTED admission + pinned checklist.

## Pin resolution

- `agent-loop` source `71318c4e7a0ed142acd61d4553f31e5bad0fb474` resolves in the
  private worktree `/var/home/bmosher/projects/agent-loop-p8r1`; base
  `4a00d675…` is its ancestor. `campaign4/CONNECT-FINISH-LINE-20260923.md`
  `95b44c3`, `OVERNIGHT-EXPOSE-LIVENESS-RULING-20260923.md` `9f0466e`,
  `GO-RELEASE-TARGET-20260923.md` present.
- Co-pinned hashes recomputed equal: P8 `terminal-disposition.json` `02a7317a…`,
  `qualification-final.md` `f6009bbc…`, amended `repair-1-review.md` `d0c077ee…`;
  P7 `package.md` `e4adcd51…`, `admission-review.md` `ce08567f…`;
  `GO-RELEASE-TARGET` `11d844f8…`.
- P8 terminal = **EXHAUSTED / `NOT_READY_UNATTENDED`** (future-heartbeat false REST,
  missing incarnation binding, live residuals; no adoption), successor P9.

## Scope feasibility (no hidden repair)

- Allowed work is read-only presentation (a Go `status`/pending view), an explicit
  source-linked inventory of campaign decisions/qualification, overhead counts
  from real loop events, docs/README/config-template and a private release
  archive. `internal/core`, `internal/host`, `internal/py`, dispatch/routing/
  claims, timer callbacks, supervision, startup/stop/control-state/store are
  frozen — **no control change may be bundled**. If a required read-only datum
  needs a control edit, the author returns the precise limit to Tern (this is the
  correct bounded failure, not an expansion).
- Known P8 blockers (future-time heartbeat + no incarnation binding) are
  **declared known**, not re-fixed here; service templates carrying them must be
  shipped as clearly **unqualified examples**, never recommended unattended.

## Pinned checklist (maps the 6 predeclared checks)

1. **Real Go status view / pending list** from a private ledger/inventory: inject
   an unresolved blocked judgment → owner/question/dependents/next action/source;
   resolve it → pending removed and source retained; no reference to
   conversational memory; P8 `NOT_READY` never renders qualification green.
2. **Missing/stale/conflicting/empty inputs** → `UNKNOWN`/`CONFLICT`, never
   healthy rest; **P8 NOT READY cannot render green**; repeated render stable
   except as-of; source links resolve from the shipped layout; read-only proven by
   before/after hashes + row counts, including on malformed input.
3. **Overhead counts** from a predeclared ledger sequence with duplicate
   observations and known events: compare each count/duration to the sequence
   (no name-suffix heuristic, no duplicate-row double-count, no grant-as-duration);
   absent history → unknown; corvid adds independent event + missing-data
   mutations.
4. **Source diff proves frozen control modules/behaviour**; retained Go
   core/host/loop regressions + **125 conformance** run on the final binary;
   read-only changes do **not** inherit a P8 unattended PASS; any shared control
   change = scope fail.
5. **Archive extract** into a fresh private dir; documented build / install-to-
   private-dir, help/status/pending/check and stop/restore exercised with isolated
   files and injected transport/system commands (no real seats/services); no
   dependency/path fixed to this host; restore rehearsal cannot touch main.
6. **Claims/manifest match actual bytes** (no cache/credential/debris); README
   identifies source tree + limitations and labels **SUPERVISED PREVIEW / NOT
   QUALIFIED FOR UNATTENDED USE**; final evidence separates reproduced checks from
   author-reported results.

Also required: config template placeholders (check refuses incomplete/wrong seat
bindings; no live campaign IDs as reusable defaults); stop documented as NOT
cancellation of armed deadlines; project-scoped timer inventory/cleanup; no
automatic continuation for old principal-less packages; trusted-host CLI boundary;
no GitHub release/main merge/global install/fleet cutover; no automatic service
install/enable.

## Bounds / sequence

Admission 10 m (this) → Claude initial 60 m → corvid verify 20 m → ONE eligible
packaging/read-only correction 20 m + recheck 10 m = 120 m, separate P9 ceiling;
P8 history unchanged, unused P8 grants cancelled; no automatic extension/P9-r2.
Only admission is released now; no author work/live/publication authorized by it.
Every receipt carries host-UTC start/deadline, one-shot duty timer and the exact
executable wake; timeout → BLOCKED then Tern.

## Effect

Admission **ACCEPTED (bounded)** with the pinned checklist and the frozen-control
limit. No implementation/live/publication conferred. Returned to Tern for the
Claude release.
