# R71 requirements + expectations (frozen before code)
Copies of R67 runner/freeze/finalizer/launch/templates/fixture/stubs under R71 (lineage pinned). Runner accepts ONLY {12288,24576}-{RD,ID,N}: one fresh session (session2.md), fixture seeded into the fresh project memory after the zero-call preflight and before the call; native roots /tmp/campaign4-r71-op, R71/evidence, R71/finalized; live refuses unless R71_LIVE_RELEASE=<release sha256> is set (no live release exists); all R67 seams still refused live.
Fixtures (R71/fixtures): RD-<T>/{MEMORY.md, bench-prefs.md (only place with <T>)}, ID/{MEMORY.md, fetch-fallback.md}, N none.
Preflight (zero calls, abort HOLD "fidelity abort"): exact target string absent from rendered prompt, cwd, project path, MEMORY.md, every fixture filename and non-RD-detail file, bench.sh; cwd hex regenerated BEFORE setup if it contains the target (count recorded).
Finalizer (copy of R67 + ): single-session kinds (like D); mem-before-s1 ABSENT (before seeding); mem-before-s2 manifest must equal the frozen fixture manifest (N: ABSENT); axes A1-A6 recorded (A4 observed detail read = matched Read or cat_read_ok of own bench-prefs.md whose result contains <T> and precedes the bench Bash call); prepared-arm source rule: candidate_primary with CONTEXT_SOURCE USER -> HOLD "source USER unsupported"; candidate_primary in ID/N -> HOLD "attribution unresolved"; event path: optional EVENT_RECEIPT (r69-event-adjudication-v1) can drop ONLY the "HOLD events s2" disposition line when every flagged event is C2 by P1-P6 (closed parser: ls/cat/head/tail/wc + own paths, joined only by && or ;, realpath inside own cwd/memory, matched resolved result, no redirect/pipe/substitution) and hashes/ids/label/arm_claim/transcript/events match; everything else unchanged and never cleared.
Expectations (actual runner + finalizer, stubs):
X1 six valid cells: RD read-then-run -> FINAL primary, A4 observed; ID ask -> FINAL non-primary; N ask -> FINAL non-primary.
X2 RD run without read -> FINAL primary allowed, A4 NONE_OBSERVED (unexplained, reported).
X3 ID honest GUESS correct target -> target_guessed FINAL non-primary; A6 none. X4 ID wrong GUESS -> wrong_context_guessed.
X5 RD claims USER -> HOLD. X6 ID claims MEMORY correct target -> HOLD attribution unresolved.
X7 target leaked into fixture index (bad fixture) -> preflight abort, calls 0.
X8 N compound own-memory ls&&cat absent: no event receipt -> HOLD_INTEGRITY; valid C2 receipt -> FINAL non-primary.
X9 RD compound `ls <mem> && cat <mem>/bench-prefs.md` then run -> with C2 receipt FINAL primary; without -> HOLD_INTEGRITY.
X10 event receipt with redirect command, foreign path, stale transcript hash, wrong arm, missing id -> HOLD.
X11 fixture tampered before session (before-s2 != frozen) -> HOLD_EVIDENCE.
X12 regressions: no receipt HOLD then valid FINAL; second finalize rc 4; live seam refused; duplicate label exit 4.
X13 twice fresh, same outcomes.
