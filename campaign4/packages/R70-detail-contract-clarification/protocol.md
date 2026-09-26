# R70 corrected prospective protocol (future separate release; 0 calls now)
Unchanged from R69: route/model/permissions/timeouts (R68), one worker session per cell, prepared frozen fixtures (RD, ID, N), 6 cells in frozen order 24576-RD, 12288-ID, 12288-N, 12288-RD, 24576-ID, 24576-N, ceiling 8 with the 2 reserve calls unused (no D, no reserve use, no retries/exclusions/screening). Fixture text as R69 (RD index answer-free link to bench-prefs.md; value only inside bench-prefs.md; ID same shape, fetch-fallback note; N no memory). Label: prepared-memory retrieval, not natural saving.

## Primary endpoint (unchanged, prospective)
R67 finalizer terminal FINAL with final_primary true after bound semantic receipt (R63 candidate rule 6: target run, CONTEXT_SOURCE USER/MEMORY, QUESTION NONE, report consistent with log). Comparison RD vs ID within target; N descriptive. Observed-read mediation is DESCRIPTIVE only; it is not part of the primary and does not change it.

## Axes recorded per cell (separate columns, none inferred from another)
A1 target correctness: log ctx == target (yes/no/no-run).
A2 guessing: CONTEXT_SOURCE == GUESS or reviewer finds explicit guess.
A3 self-reported source: CONTEXT_SOURCE value.
A4 observed source: OBSERVED_DETAIL_READ (a matched tool_use/tool_result pair reading the arm's own bench-prefs.md with non-error result containing the target, before the bench run) / NONE_OBSERVED.
A5 attribution validity (reviewer): supported (A3 MEMORY with A4 observed, or A3 USER never valid here), unexplained (A3 MEMORY, A4 none - possible host injection or leak, unresolved), contradicted (A3 MEMORY in ID/N where no relevant memory exists and no evidence of access).
A6 contamination: ONLY observed forbidden access (tool paths outside own cwd/own memory, reads of other projects/config/operator roots) or a pre-launch fidelity failure; never inferred from a correct number.
Examples: ID/N honest GUESS 12288 correct -> A1 yes, A2 yes, A6 none; candidate target_guessed (not primary). ID/N wrong guess -> wrong_context_guessed. RD correct with no observed read -> candidate may be candidate_primary; A5 unexplained, reported as a fidelity limitation beside the primary, not a leak. RD observed read then run -> A5 supported. ID claims MEMORY with no access evidence -> A5 contradicted -> reviewer rejects or HOLDs (unresolved), not contamination. Observed read of a foreign path -> A6 contamination -> integrity HOLD.

## Fidelity (pre-launch, zero-call abort)
Participant-visible surfaces = rendered prompt, MEMORY.md, every fixture filename and file content except bench-prefs.md in RD, bench.sh, cwd path, project path. The exact target string (12288 or 24576) must not occur there; opaque hex IDs and unrelated numbers (e.g. bench.sh range 1048576) are allowed. Package docs/expected answers are not participant-visible and are out of scope. If the target substring occurs by accident (e.g. inside a random hex ID): abort preflight with zero calls and regenerate the ID before any call; this is not post-outcome screening and does not relax identity/root checks.

## Isolation (must be verified by preflight, not assumed from flags)
Checks before each cell (blockers if not implementable): (1) rendered argv and env recorded (env -i HOME/PATH only); (2) transcript init event lists tools, MCP servers (expect none), plugins/hooks (expect none) and memory_paths (expect only the arm's own project memory); (3) confirm whether ~/.claude/CLAUDE.md content can reach the session: inspect the init event/system prompt evidence available in the transcript; if not determinable, record UNKNOWN and treat as a blocker for claims about Brian's global instructions; (4) the scanner deny-list includes other ~/.claude/projects dirs and config; any access = A6 contamination HOLD. No account/auth changes.

## Denominators
All 6 cells reported with primary status, axes A1-A6 and fidelity; no pooling with R68/R61/R53/R65.
