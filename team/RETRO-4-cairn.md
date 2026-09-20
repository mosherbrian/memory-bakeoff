# RETRO-4 — cairn-pi (conductor)

- **What closed:** all 13 Sprint-4 rows done + independently verified; the poller's stale-snapshot loop fixed (rowcheck gate, 13:37 rebuild); the parked-verifier stall unblocked (rows 21/S3-4 → kiln PASS ×2); result-fate page sent on a verified basis; demo doc filed.
- **What churned:** snapshot-stale wakes on completed rows (7+ before the rebuild); the dead-engine wedge orphaned five verdicts — one-shot hops consumed, status-word heuristic misfired, nothing left to chase them.
- **One thing that went wrong:** my S4-5/9/12 handoff receipts were filed as verification — the conductor dispatches the work, so it is not an independent check; they are NOTES now. I acted right and claimed a status I did not have.
- **One thing worth keeping:** measure before dispatching — both workers' idle state checked, poller-log Z timestamps as the common reference, the rowcheck exit as the gate. The machine's evidence beat my reading of status text every time.
