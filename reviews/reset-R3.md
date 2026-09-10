# Reset R3 result review — verbatim transcript, as relayed

Provenance: written into this tree by the implementer per the
one-writer-per-tree rule, from the conductor relay
`dispatch/review-R3-relay.md` (worker-glm-3, GLM-5.3-Flash, review pass 1 of
1, reply 2026-09-10 03:13 PDT). Verbatim below, including the relay transport
line wraps. Reviewed commits on `reset/practical-pi-20260907`: approval
record `88699e0`, extension `88b5e9b`, harness/cases `d19971b`, result
`2729917`, accuracy repairs `c2c2cbe`. Verdict: the §6 decision RETAIN
BASELINE is supported and stands; one blocker on the executive
interpretation (seeded store unreachable in every treatment run) plus
required documentation repairs. Consolidated repair pass: `06a29a1`; the
blocker's hash chain was independently reproduced by the implementer before
repair (both path spellings hash to the two observed db filenames; seed
files wal/shm-free).

---

# Reset R3 result review — worker-glm-3 (GLM-5.3-Flash)

**Reviewed:** R2 deliverable on `reset/practical-pi-20260907` — approval record `88699e0`, extension `88b5e9b`, harness/cases `d19971b`, result `2729917`, accuracy repairs `c2c2cbe` (head, pushed, ==
origin); the complete paired table in RESET_STATUS.md; private receipts under the implementer session's `~/.local/share/memory-bakeoff/reset-20260907/r2/` (ledger.jsonl, ANALYSIS.json, run dirs, PREP_
MANIFEST.json — inspected locally, nothing private enters this review). Review pass 1 of 1; one targeted recheck follows the repair.

## Verdict

**The §6 decision — RETAIN BASELINE — is supported and stands.** Arm B fixed no predeclared practical failure in any repetition, so the "limited personal trial" rule fails at its first condition regar
dless of anything else I found. **One blocker on the executive interpretation, not the decision**: the headline "the recall tool works, the model never uses it" is unsupported in its first clause — I
can prove the tool was silently mis-wired in every treatment run, so a call could never have reached the seeded history. The result page must be corrected before Brian reads it; after that repair, R3
is complete with no further budget.

## What checks out (verified, not taken on faith)

- **Runs and receipts.** 16 slots, 15 completed + 1 experimenter-interrupted; per-run ledger rows carry config_ref, snapshot digests (initial/final tree), full tool-call lists, parsed usage, verifier
stdout/stderr. I reproduced the table from ANALYSIS.json row for row, and re-ran the c1-b-rep1 raw event stream myself: zero `project_recall` invocations in any treatment run, confirmed twice (parsed
events + raw grep).
- **Feature activation.** Every B run's stderr contains `pi-project-recall: registered project_recall (read-only, driver node:sqlite)`; no A run does. The ≈+250–300 input-token delta between arms is c
onsistent with the added schema. Activation is proven from runtime receipts, not self-report.
- **Statistics.** All four published overhead figures reproduce exactly from unrounded ledger values over the correct pair bases (7 completed pairs: wall +2.9 %, tokens −10.3 %; 5 passed pairs per the
 §6 threshold basis: wall +10.3 %, tokens +5.6 %). Both inside the 25 % threshold Brian accepted; correctly labelled moot given the null.
- **Design compliance.** Execution order in the ledger is rep1 A,B then rep2 B,A per case (the published table's row grouping misreads as A,B,A,B for c1/c3 — cosmetic, see notes). Arms differ only in
the `packages` list; model, provider, thinking level, timeout (480 s), worktree snapshots and store dirs identical. Cases are built on existing gen48 fixtures, hidden verifiers live outside agent-visi
ble snapshots, c1's verifier asserts requirement A before requirement B — so the traceback order genuinely proves req A passed in every failing run. PREP_MANIFEST.json hashes transcripts/verifiers, wr
itten at setup before the walk; cases committed before the result commit.
- **Honest handling of the interruption.** c2-b-rep1: containment stop, audit negative, partial preserved, slot spent, not restarted — exactly plan §5's discipline.
- **Code quality.** The extension is genuinely read-only (node smoke reproduces 7/7, including a write-rejection through the tool's own connection), mirrors pi-lcm's driver/store/query patterns, annot
ates every hit with timestamp + session identity + a supersession warning, and returns truthful empties. The c2c2cbe "accuracy repairs" are honest self-corrections (pair counts, store-fidelity wording
, reflog-dated time row) — no rescoring of outcomes.
- **Containment.** `PI_OFFLINE=1`, localhost inference, per-run worktrees; machine occupancy ≈ 8 min 20 s of run wall time. Private material stayed out of the repository.

## Blocker: the seeded store was unreachable in every treatment run

**Evidence chain (all reproducible):**

1. The harness names the seed db `sha256(str(worktree))[:16]`, and ran under HOME=`/home/bmosher`, so the seed file is the hash of the `/home/bmosher/...` string: `sha256("/home/bmosher/.../c1-b-rep1/
repo")[:16]` = `b967e8a5e5717516` — the file present in each run's `lcm/` dir.
2. `/home` is a symlink to `var/home` on this host. A node process launched with `cwd=/home/bmosher/...` gets `process.cwd()` back as the physical path `/var/home/bmosher/...`; `sha256("/var/home/.../
c1-b-rep1/repo")[:16]` = `469ec1d81aa90f6c`.
3. pi-lcm created and wrote `469ec1d81aa90f6c.db` (wal/shm present, growing during the run) — its cwd-hash of the same resolved path.
4. The extension calls `runRecall(process.cwd(), …)` → `storePathFor` → `resolveDbDir()` (LCM_DB_DIR = the run's lcm dir) + `hashCwd` → **`469e…db`, the run's own live single-conversation store — not
the seeded `b967…db`**.
5. The seed files are verifiably untouched in every run dir (no wal/shm ever, mtime = prep time): nothing, including the tool, ever read them.

**Consequence for the deliverable.** In all 8 treatment runs, arm B's tool, had it been called, would have searched a store containing only the current conversation and returned "No matches." The pilo
t therefore does **not** establish "working recall that the model ignores." It establishes two independent nulls: (i) the model never spontaneously invokes a newly registered recall tool under natural
 resume prompts (0/8, receipt-backed — this part is solid), and (ii) as wired, the integration could not have surfaced prior-session content anyway. Limitation 2's post-hoc story ("seeded cwd-hash fil
e untouched, plus one UUID file") misread which file was which — there is no UUID-named file; both are cwd-hash files of the two path spellings. The validation gap that let this through: no check ever
 exercised an end-to-end `project_recall` invocation through the real runtime against a seeded store (unit tests bypass `process.cwd()`; the smoke task has no seed and, per its ledger tool list, never
 called the tool).

**Consequence for the decision: none.** A mis-wired treatment cannot demonstrate a gain; B's results equal A's everywhere; the trial rule fails a fortiori. RETAIN BASELINE is the supported §6 decision
 and is, if anything, reinforced — the one-adapter integration shipped inside this reset failed its own pilot wiring.

**Required repair (documentation only; the one consolidated pass for R3):**

1. Rewrite the R2-result headline and "What happened" to the two-null statement above; delete or invert "The tool was verifiably present and active … and misled no one" insofar as it implies in-run re
achability (registration was verified; reachability was not — it was absent).
2. Replace limitation 2's store-shape story with the correct one (symlink `/home`→`var/home`; seed named from the unresolved path string; run processes resolved the physical path; tool and pi-lcm both
 landed on the live db; seed untouched).
3. Record the defect as a post-exposure finding per plan §5: runs preserved, no rerun, no rescore. Per §2/§6, a re-run with corrected wiring needs a new explicit budget — it is not this reset's to spe
nd. Correspondingly narrow limitation 4: "try prompting it by hand" is only meaningful against a corrected wiring, and the by-hand setting (Brian's real HOME, no symlink divergence) would not have thi
s defect — say so precisely.
4. Fold in the cosmetic notes below where they touch the same sentences.

## Non-blocking notes

1. **Table order vs execution order:** the published table reads A,B,A,B for c1/c3; the ledger proves A,B,B,A. Add one sentence pointing at the ledger order.
2. **"≈ +1 k input tokens of tool schema":** observed arm deltas are ≈ +230–300 input tokens. Say "a few hundred".
3. **Containment audit not preserved as an artifact:** the "0 out-of-worktree accesses" result exists only in the ledger note and commit message. Non-blocking (no decision rests on it), but note the m
ethod used.
4. **Private-evidence path is lane-relative:** the plan's durable directory suggestion resolves inside the implementer's session HOME (`…/zcode-homes/glm53/…`), not Brian's. At closeout, copy the `r2/
` evidence directory to a stable path under `/var/home/bmosher/.local/share/memory-bakeoff/reset-20260907/` (alongside the existing `r0-discovery.txt`) and record the absolute path — otherwise "durabl
e local" silently depends on a session lane that may be ephemeral.

## Resource accounting

Reviewer R3 session ≤ 1.0 h including this write-up (reply 03:13 PDT 2026-09-10); the R3 ceiling (1.0 h, including the upcoming targeted recheck) is tight — the repair is documentation-only, so the re
check can be brief. Cumulative: implementer ≈ 1.5 h + reviewer ≈ 1.9 h across R0–R3, inside every stage ceiling; experiment machine ≈ 0.2 h against 6 h.

**Bottom line for Brian:** retain Pi-LCM alone; the extension stays in the repo as a sound, reversible, unexercised artifact. The pilot's honest finding is narrower than the draft says: under natural
resume prompts this model never reaches for project memory, and the pilot's wiring bug means reachability was never actually tested. Both the retain decision and the recorded null survive review; the
headline explanation does not, and must be repaired before the final decision page is read.