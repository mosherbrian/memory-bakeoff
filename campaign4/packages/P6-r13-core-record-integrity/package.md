# P6-r13 — durable core record integrity

Tern author; corvid independent admission and verification; kiln worker; cairn duty.
DRAFT. Candidate-only; no live/preparation/adoption. All existing charter and
CODE-REVIEW-DISPOSITION-20260922.md @abb0f90 constraints remain binding.

## Pins and exact scope

Diagnostic matrix/probes + R12 acceptance at bccd688d0b64d6302dd661cedcc7dae40e96a93b.
Input reviewc464709. Reproduce #2,#6,#7,#10; #5 remains unresolved, not assumed true.
Actual executable baseline is R11 accepted source924d21a and acceptance5eaa055:
../P6-r11-case-observer-continuation/candidate/. Final42 gate da3ddf79f572.
Comparison original core P5-r2 80092f92c24fb58ad70478faf93e4f39eb184847 and its83 tests;
P3-r3 d27d5be/core59 tests. Corvid resolves full hashes/pins before dispatch.
R11 ingress has HostClock.now accessor absent in P5-r2: preserve it. Correct the
actual copied core, not only a historical baseline. Frozen packages never edited.

Create local manifest-bound candidate copy of accepted R11 surface. Production
changes allowed ONLY local src/r3harness/store.py, lifecycle.py, ingress.py for
these four defects and a demonstrated #5 contract violation if one exists.
Tests/docs and mechanical provenance/copy-hash manifests may change. No other
production module edits without a concrete blocker returned Tern first. Retain
stdlib-only core, public trusted-ingress boundary and all R11 behavior. No refactor,
source extraction, new dependency, role policy migration or timer repair in this grant.

## Required behavior and pre-worker independent cases

Corvid pins executable regressions/expected semantics before kiln, reusing supplied
probe_core.py on immutable originals and actual R11 baseline. Record internal API
and public ingress reachability distinctly, never bypass authority to claim public
reproduction. Cases below are contract requirements, not tests fitted to new code.

A (#2). SQLite rollback leaves EVERY affected in-memory projection consistent with
persisted state. record_terminal duplicate-decide/failure after first insert leaves
zero new rows, no phantom seen verdict, unchanged lifecycle. Retry SAME store with
fresh valid decide persists exactly once; reopened store agrees. Cover duplicate
within pair and existing-event collision, transaction failure where feasible. Publish
seen/cache state only after successful commit or restore it on failure. No catch-and-
ignore, restart requirement or blindly clearing all dedupe history. Prior committed
IDs still dedupe. Successful atomic verdict+disposition remains single transaction.

B (#6). First valid terminal disposition is immutable in a revision. A distinct
later DECIDE rejects with deterministic error and zero state/row changes, both
through ingress and replay/reopen. Exact same committed event replay is idempotent,
not an error or overwrite. Do not invent amendment/reopen semantics here; existing
explicit revision AMEND behavior retained. Reject before mutation, preserving reason,
authority and evidence of the first decision.

C (#7). Atomic input shapes are exact. grant_ref allowed only with hold as documented;
decide+grant_ref must reject before any row/cache/state mutation. Mixed, unknown,
malformed payloads remain fail-closed; valid hold with authorized grant and valid
decide retain trusted stamping and attribution. Cover every supported atomic form,
not just the supplied one. No silently discarded fields.

D (#10). Deadline ordering uses validated instants, including UTC offsets and
fractions; equivalent encodings make equivalent decisions. Naive/malformed values
reject deterministically, never crash or compare as strings. Respect existing exact
boundary convention and test just-before/equal/after plus offset/fraction rollover.
Exercise accepted ingress grant through execution/publish, not only manually seeded
state; keep low-level invariant coverage too. Persisted/reopened behavior identical.
No silent extension or changing global clock/skew policy. Reuse existing timestamp
validation where dependency boundary permits; don't import host adapter into core.

E (#5 unresolved). Independent concrete public atomic event/phase matrix covering
accept-on-COMPLETE and other alleged non-terminal-maker+decide/hold combinations.
A supplied atomic operation is either wholly applied or deterministically rejected
before mutation; never accept-and-drop. Original described accept path may reject
E_TERMINAL; record that as NOT REPRODUCED, not a failed test needing weakened guard.
If another reachable silent-drop reproduces, fix within authorized three modules
with old-fails/new-passes. If all attempted public forms reject, deliver evidence
and mark original claim NOT REPRODUCED/remaining uncertainty precisely; no speculative
behavioral expansion or new accept-on-terminal semantics required.

## Blocking completion and outputs

- Concrete old-fails/new-passes for A-D, new negative+valid controls through public
  ingress, row/state/seen-cache comparisons and reopened equivalence. Independent
  corvid mutation per family not supplied by kiln. E truthfully classified as above.
- Retained P5-r2 83 and P3-r3 59 core tests adapted to exercise NEW core, plus R11
  42-case candidate gate on NEW composed bytes and new regressions. Do not pass
  historical modules instead through accidental PYTHONPATH/import caching. Record
  module paths/hashes during tests. Any semantic conflict with old assertion returns
  Tern; no silent deletion/skip. Full gate fits known~14m host suite plus fast core.
- Manifest/copy descriptors accurate, no self-hash. Original parent paths/hashes
  recorded, copied changes explicit; include source-change table and limits. New
  claim binds exact final bytes and results, unresolved failures/timeouts named.
- Source remains local/stdlib, R11 verified rejection/routing/observer behavior and
  public ingress protections hold. Source-only host issues #1/#3/#4/#8/#9 are NOT
  fixed or certified by this package; live-release hold persists.

Deliver candidate source/tests/plan, regression evidence/results, changes.md,
manifest and completion claim. Independent verification checks full required gate
on final frozen bytes. A test that asserts only the function exists is no evidence.
No retry-until-green or fabricated fixture results; record complete command and rc.

## Allocation and conditional release

Corvid admission+executable cases<=15m separate reader grant. After unchanged
contract ACCEPTED, cases/review and R12 terminal pinned, conditional Tern release:
ONE kiln<=45m, ONE corvid<=30m. Prior P6 candidate1025worker/765verifier ->1070/795.
No repair grant. Prior unused R12 diagnostic time cancelled; no transfer. Candidate
only, zero live/prep. Preserve all previous spent allocation/early returns.

Cairn pins exact sources/authority before one P6r13-initial-1 dispatch, host-read
start/deadline, active relative one-shot timer, no other writer. Bind output then
independent corvid30m on own clock. Expiry/FAIL/INCOMPLETE returns Tern with partial
bytes preserved; no reset for running tests. At terminal Tern authorizes next bounded
host timing correction or records why not. This is the first integrity repair in the
already-recorded order, not permission to fix every open issue. Research-first scope:
remove proven silent record corruption before collecting more live evidence.
