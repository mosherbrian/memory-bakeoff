# DECISIONS — decision log with receipts (newest first)

Format: date | decision | made by | receipt (commit/path). Append-only;
revisions get a new line referencing the old one.

- 2026-09-12 | Mission charter adopted; team self-organization approved; names/personas mandated | Brian | MISSION-20260912.md, BRIEFING-20260912.md
- 2026-09-12 | Kiln (worker-glm-2) claims build + execute with "make it survive contact" ownership; scaffolds team/ registry | Kiln | team/ROLES.md, team/CAMPAIGN-1.md, this file
- 2026-09-11 | Native capture probe: no derived lineage, output non-serveable, admission chain dead-ends (no admission evidence in capture bodies) | Kiln (planner-directed) | scripts/experiment_20260912_native_capture/FINDINGS.md, commit 84cc6b9
- 2026-09-12 | Worker-pi resume blocker fixed by clearing stale deck session binding (pi-acp session-map pointed at pre-trial conversation); fresh-start knob documented | Kiln | commit 706090b, docs/TRIAL-20260911-runbook.md
- 2026-09-11 | clawdbot-signal removed from the extension per Brian's scope correction (Signal is conductor-side); WriteNotifier seam kept | Kiln | commit 060d842
- 2026-09-11 | Experiment freeze: trial pre-registration committed before first evaluated cycle (10 cycles or 3 days; descriptive rules; stale-action target 0) | Kiln (per dispatch) | docs/EXPERIMENT-20260911-trial.md, commit 6df91c7
- 2026-09-11 | Trial finding #1: draft presentations now REQUIRE plain-language block before mechanics | Brian → Kiln | commit 4fbd904, docs/TRIAL-20260911-runbook.md
- 2026-09-11 | Decision-memory build complete: 7d rename, write surface, §2 guard, 7a/7b gate, 7c paths; smoke 16/16 | Kiln | commits 3f9498f..b6d7fe4
- 2026-09-11 | Trial mechanism frozen for the experiment: extension e9e5621 lineage (scope corrections applied through 060d842) | Kiln + reviewer | docs/TRIAL-20260911-runbook.md
- 2026-09-11 | STUDY-20260911-P1B verdicts stand: delivered-level gates 24/24; A-side fails P1-1; delivery is the measurement level | study record | repo/docs/STUDY-20260911-P1B-results.md
- 2026-09-12 | Audit chore (Aletheia via GiLMore): four dead links in the ROOT memory-bake-off/RESET_STATUS.md fixed to implementer/repo/-relative paths. The root file is untracked in Brian's HOME repo (identity "Brian Mosher") — editing in place was chore-sanctioned, but no commit was made there (one-writer-per-tree; committing as Brian would misattribute). This entry is the durable receipt; my own repo/RESET_STATUS.md copy needs no change (its bare paths resolve). | Kiln | /var/home/bmosher/memory-bake-off/RESET_STATUS.md (untracked), team/DECISIONS.md
