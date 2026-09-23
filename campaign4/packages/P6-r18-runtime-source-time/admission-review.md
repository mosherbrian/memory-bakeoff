# P6-r18-runtime-source-time — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-admission-1`, start `02:22Z`, deadline `02:37Z`
- **Brief:** `package.md` sha256
  `8e981e9e1834600e4efc7fcd5008205cd4b6d1c8573ab44b6b4c2dff44dbe5ec`; director
  release pinned.
- **Scope:** read-only admission + pinned checklist. No source edit, no live.

## Verdict

**ACCEPTED (bounded).** Premise confirmed against the actual installed runtime
snapshot: `acp-worker.emit` writes `{"t":kind,"item":…}` with **no timestamp**
and swallows write failures, and R17's real seats produced ends but no onset
sidecars. The proposed fix (instrument a **local** runtime copy + a stdlib helper
and consume the source receipt via `case_entry.py`/`harness.py`) fits the
authorized surface without touching the shared `~/.config/agent-deck`. Two
bounded design obligations are pinned: one exact source-record format with
truthful failure semantics, and no unsynchronized sidecar.

## Pin resolution / inputs

- R16 parent `c8e99cf…`; R16 acceptance `82b1418`; candidate
  `../P6-r16-causal-identity/candidate/`; outer manifest file sha256 `3862a0a2…`.
- R17 evidence commit `d0769c2e…`; sibling `live-review-failed-1.md` (onset dir
  empty → `E_NO_ONSET`); R17 terminal co-pinned.
- `inputs/manifest.json` hashes **verified byte-exact**: `acp-worker
  6871ceb1…`, `acp-go 72b50d8a…`, `acp-go-deepseek 0d009f0d…`. These are
  source snapshots, not credentials/permission.
- Governing `4be99bf`, `650830c`, `84f094e`, `883107e`, `f7b0cce`, `5fefb0f`
  resolve; quiet-rest duration blocker remains separate.

## Confirmed runtime schema (from pinned `inputs/acp-worker`)

- `emit(kind, **kw)` (`:492-499`): `open(stream,"a").write({"t":kind,"item":item,**kw})`
  inside `try/except Exception: pass` — best-effort, no timestamp, failures
  swallowed.
- `self.emit("end")` at `:1081/:1222/:1252` — the actual turn-end append carries
  no time/provenance.
- This is why R17 ends existed but no reliable source onset existed; the model-seat
  task text never requested a sidecar. Detection time must never be relabelled
  source time.

## Authorized surface / architecture

- Copy R16 locally; allowed production edits: `case_entry.py` and local
  `r3harness/harness.py` **only** to consume the new source receipt/join and
  exact fixture task instructions; new **local** `runtime/acp-worker` copy +
  small stdlib helper + fixture-only lane launch wrappers; tests/docs/manifests.
- **Frozen:** driver/ingress/store/lifecycle/validator/turn_handoff,
  `host_adapter`, existing transport/fault machinery; **shared
  `~/.config/agent-deck` and conductor-chat MUST NOT change**; no installs, model
  calls, real seat/service ops, credentials, or core clock/late-ingress rewrite.
  Any need outside returns a scope gap before coding.

## Pinned obligations (design decisions)

1. **One exact source-record format** specified in `interface.md`: either
   versioned fields in the same runtime `end` record or an **atomically paired**
   source record. Avoid an additional unsynchronized sidecar. Timestamp comes
   from the trusted runtime at the actual end append, bound to runtime
   session/item, with provenance and honest uncertainty/clock-discontinuity
   handling; unknown/discontinuity → INCOMPLETE (never backfilled/guessed).
2. **Failure semantics are truthful:** no swallowed evidence failure becomes a
   PASS; telemetry failure must not kill unrelated model work. An end proves the
   turn ended, not work success — stalled/cancelled/failed ends cannot certify
   completed work without an authenticated valid claim.
3. **Consumer binding:** bind the source record to the exact current
   session/item and action/execution via the existing authenticated
   runtime/claim/delivery mapping; unmatched/stale/duplicate/wrong-execution/
   conflicting source is not opportunistically matched; legacy records lacking
   reliable source stay explicitly unmeasurable. Already-verified explicit
   producer sidecars may remain only with declared source mode/provenance; no
   silent fallback or source chosen to obtain a pass. R16 own-action join and
   explicit identity hold.
4. **Task contracts** state exactly who records source time (runtime) and what
   worker/verifier emit (bound claim/artifact/check), with executable helper
   commands; no undocumented producer-sidecar task or synthetic stream emitter.
   `fixture-launch-plan.json` uses the local instrumented runtime with current
   model lanes preserved, exact source hashes, explicit opt-in
   destination/scope; no proposed fixture may accidentally execute the unchanged
   shared runtime. Disabled instrumentation stays backward compatible; fleet
   adoption requires fresh prep/review/signature, not this package.

## Blocking verification checklist (pinned)

- Reproduce R17 missing instrumentation on copied evidence + pinned runtime emit;
  establish the **real** emitted schema and local launch closure from the pinned
  runtime (not fakes).
- Tests exercise the actual candidate runtime **emit/write** in isolated tmp
  streams with injected clocks/no model calls; the consumer reads those **same
  emitted bytes** through production CLI composition. No parallel fake emitter,
  no model-authored timestamp.
- Prove normal success **and** genuine verifier rejection both produce usable,
  matched source records without model sidecar help.
- Negative matrix: missing receipt; empty/wrong item/session; previous execution;
  conflicting duplicate; malformed/partial source; UTC discontinuity; write
  failure; stall/cancel end without successful claim; delayed observer; restart.
  Each source matches only its own action; unknown timing never passes/backdates.
- At least one **unshared** independent source/identity mutation and an actual
  producer→consumer subprocess test of the shipped hook. Captured clock-boundary
  uncertainty explicit.
- Retain full composed **78** + P5 **83** + P3 **59** on the actual new modules
  (paths/hashes recorded); no skip/deletion/historical-source import; any
  assertion requiring legacy source is reconciled with corvid + Tern **before**
  change (no blanket weakening). Preserve R13/R14/R16 safeguards, no duplicates,
  real rejection, source-vs-detection vs recovery semantics and causal bounds.
  Accurate acyclic manifests/descriptors incl. runtime/helper/wrappers and an
  unchanged-core comparison; historical R15/R17 bytes unchanged.

## Bounds

ONE kiln ≤45 m; ONE corvid ≤40 m; admission 15 m separate. Ceilings
`1260worker/1035verifier` → `1305/1075`. Full suite ~11 m — no 120 s substitute;
honest INCOMPLETE on unrun/expired. No fixture grant in this package; candidate
PASS never certifies live timing or runtime adoption. Every prompt/receipt carries
an executable completion command (exact profile/session/action/absolute path);
failure returns Tern. The quiet-rest configurable-window correction is still owed
and not folded into this source-time change.

## Effect

Admission **ACCEPTED (bounded)** with the pinned obligations and checklist. No
implementation or release conferred. Returned to cairn/Tern.
