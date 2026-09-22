# P6-r6-live-preparation — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r6-live-preparation/package.md`,
  sha256 `f2b7df485053ea9eeb379d3f20385f1f133d196434e749810592654b14805edf`,
  commit `e32c0dccacb28ba0dc9b9ab107ee9f8f2c569a38` (re-derived; working tree
  matches)
- **Dispatch/receipt:** `admission-dispatch.json` (`494276ba…`), recorded
  `2026-09-22T03:48:19Z`, deadline `2026-09-22T04:03:19Z`
- **Pinned checklist:** `preparation-timing-checklist.md` (written this pass)
- **Worker:** HELD

## Disposition

**ACCEPTED**, bound to the exact bytes above plus the pinned
`preparation-timing-checklist.md`. The contract correctly separates the
injected candidate PASS from actual live preparation, defines blocking
preparation/timing checks with an explicit separately-signed release, and keeps
all inherited pins and rulings binding. Actual idle preparation and Stage C
remain held; no worker execution occurs here.

## Pinned inputs resolve

- Parent P6-r5 `dad988277b5b7e633735d8eaae2d6134b84fa5a0` — resolves;
  `candidate-review-repair-2.md` (`f20527d2…`) matches my verdict and its
  injected PASS (189+59) is preserved as injected evidence, not live acceptance;
  its old plan (`06ba06df…`) does not launch or bind real runtimes and its source
  latency is honestly INCOMPLETE.
- Rulings recovery `4be99bf…`, identity `84f094e…`, turn `883107e…`, retirement
  `b2384d7…`, context `54b6087…`/session `92467e4…`, clock `650830c…`; accepted
  P5-r2 `80092f9…`; core `d27d5be…`; P2 `5bfbb071…` — all resolve.
- `SHADOW-REFERENCE-RULING-20260922.md` at `afa126f…` — resolves; it explicitly
  authorizes **no** shadow run, retirement, live effect or extra allocation, and
  the contract correctly says shadow is **not authorized here** and disclaims any
  incumbent-agreement oracle or adoption from injected tests.

## Feasibility (read-only checks performed)

- The two intended lanes exist: `/home/bmosher/.config/agent-deck/acp-go`
  (worker) and `.../acp-go-deepseek` (verifier).
- `agent-deck launch --help` confirms launch with an **optional** `-message`
  (i.e. a supported idle mode) and `-idle-timeout`, so "create/start two idle
  runtimes with no task dispatch" is feasible without touching shared wrappers.
- `AGENTDECK_PROFILE=campaign4 agent-deck list` shows exactly the four main
  seats (tern/corvid/kiln/cairn), so new `p6-fixture-*` names are free and the
  no-repurpose rule is checkable.
- All of the above was read-only; no seat was started, stopped or messaged.

## Contract validity

The deliverables are proper operational artifacts: a **separate** actual live
fixture plan (the candidate's plan stays simulated evidence and its fake files
are never relabelled live), executable preparation/cleanup tools, a
launch-manifest schema, an independent timing-witness tool/protocol, and a
bounded operator brief, all with exact commands/paths/resources/permissions and
no manual invented session IDs. Preparation must create/start only two new
`p6-fixture-*` sessions with isolated dirs and no task dispatch; record real
session IDs, profile, role, launch command, producer root, stream paths and
actual Unix socket identity/incarnation for both; reject fake-socket files,
wrong role/profile, stale incarnation and mismatched stream/root; never infer
identity from filename/title; transport and observer share the recorded
bindings; an idle runtime with no stream establishes its producer path from
inspected launch facts. The plan phases, cleanup ownership/archival, and the
pre-wake rejection conditions are explicit. Timing is independent of candidate
timestamps, with controlled onset/source, host-clock capture, provenance and
uncertainty; missing independent evidence stays INCOMPLETE; existing 30/180 s
detection and 60 s recovery (90/240) are measured appropriately and ordinary
model execution time is not detection latency. The contract also enumerates the
live cases (normal handoff, lost completion/failure recovery, queued/ambiguous
transport/restart, quiet rest) and requires feasibility within the held 15m run
rather than claiming all from one positive sample. The controlled preparation
release (≤10m cairn, preparation only, manifest + exact plan hashes returned;
corvid read-only check; then Tern signs the live plan+manifest) is correctly a
separate signed receipt, not automatic from admission or candidate PASS.

## Allocation

Worker ≤30m for operational tools/plan; independent candidate review ≤20m. Prior
cumulative P6 345/265 → **375 worker / 285 verifier** — arithmetic correct; all
r5 worker/candidate grants spent and historical clocks unchanged. The single live
witness 15 and cairn fixture 15 remain unspent/reassigned HELD; a separate cairn
preparation ceiling 10m is added and also HELD until the explicit preparation
release. Admission/checklist ≤15m; no work overlap; expiry stops/reconciles then
BLOCKED to Tern.

## Release conditions

Release kiln only after independent ACCEPTED unchanged contract + checklist
pinned, director admission recorded and the parent terminal pin; cairn uses
absolute paths, host start/deadline before wake, a relative timer and an explicit
action/attempt/execution receipt, binding output hashes before corvid. Candidate
PASS returns to Tern and never automatically starts preparation or Stage C.

## Non-blocking observations

- The contract's old-plan reference is a file hash (`06ba06df…`), not a commit;
  the parent commit pin `dad98827…` is the version authority.
- The `acp-go-deepseek` lane script is small (444 bytes); the verifier lane's
  actual launch/identity must be captured by the recorded bindings rather than
  inferred from its name, as the contract requires.

## Effect

Bound to contract bytes
`f2b7df485053ea9eeb379d3f20385f1f133d196434e749810592654b14805edf` at commit
`e32c0dccacb28ba0dc9b9ab107ee9f8f2c569a38` and to
`preparation-timing-checklist.md`. Worker HELD. No live seat/service, idle
preparation, Stage C, Signal, wrapper edit or clock change occurred. Disposition
returned to Tern.
