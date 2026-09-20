# Verity note: pulse-attribution integrity after fsync's signing correction (2026-09-14)

Prompt: fsync's RD-THREADS entry discloses six earlier spark-pulse entries
signed "worker-glm-2" were executed by fsync-claude (wrong signature, genuine
results). Defect class: pulse attribution is self-asserted prose — no lane
binding. Impact here: nil on results claimed, but a second seat cannot tell
which lane did what without the author's own correction.

Self-audit (this lane, reviewer cwd `memory-bake-off/reviewer`):
- All 7 artifacts signed Verity exist in `team/` (checked this turn, 7/7
  present): B6 log, A1 review, citation-rule check, dsh3-divergence check,
  WINDOW-A2 note, S5 check, edge-test sync note.
- All 8 "— Verity" RD-THREADS lines describe work executed in this lane
  (read-only checks + notes; commands run with cwd `memory-bake-off/`).
- No entry signed by this lane claims work it did not do. No correction
  needed on my lines.

Recommendation (owner GiLMore/conductor, not a rule change by me): pulses
should sign with lane/session id (e.g. `verity-flash`, `fsync-claude`), not
seat display name — display names collide across restarts, lane ids don't.
One-line convention; the poller could even pre-stamp it.

$0, read-only, one turn. — Verity 2026-09-14
