# Scope blocker returned to Tern: P6 prepare_live.py non-dry-run manifest bug

File: campaign4/packages/P6-r6-live-preparation/src/prepare_live.py (NOT edited here).
Location: the `full[role] = {...}` assignment sits one indent level OUTSIDE its
`for role, name, lane, wdir, out in ...` binding loop (loop body ends with the
`stream = ...` line; the `full[role]` dict follows at loop-header indent).

Effect: after successful launches, only the LAST role (verifier) lands in
`full`; `build_manifest(..., full["worker"], ...)` raises `KeyError: 'worker'`.
Reproduced offline with real launches against the pinned tool (partial journal
shows both sides completed, then the KeyError). Live prep via non-dry-run
cannot produce its manifest until P6 fixes one indent.

This plan does NOT work around it by editing P6. The prep stage launches all
four seats explicitly and validates with prepare_live.py --dry-run (designed
injection path) over the real launch results, which passes fully offline.
Live prep via non-dry-run remains blocked on the P6 fix; Tern disposition required.
