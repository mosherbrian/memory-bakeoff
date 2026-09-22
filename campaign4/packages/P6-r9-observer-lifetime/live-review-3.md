# P6-r9-observer-lifetime — live review 3 (independent)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-livereview-3`, start `2026-09-22T16:34Z`, deadline
  `2026-09-22T16:44:33Z` (`campaign4-p6r9-livereview3-deadline.timer`)
- **Grant:** `live-positive-release-3.json` (Tern `stagec-task`, signed
  `16:31:27Z`), binding review pinned at `f88170bb…`
- **Evidence:** `live-positive-3/` (`positive-handoff/` full runtime), 
  `live-execution-3/`, `live-positive-3-receipt.json`, `/tmp/p6r9-live-positive-3/`
- **Scope:** read-only review of actual identity, deliveries, handoff, claim,
  verdict, no-duplicate-send, timing and cleanup. No retry, no send, no
  mutation.

## Verdict

**PASS** — the first live positive worker→verifier handoff actually occurred.
Both signed seats were used by exact identity, exactly one dispatch per action
was delivered, the worker completion was published as the verifier's next
action, the verifier committed terminal-rest, timing reconciles to the signed
grant with a deliberately invalid negative control correctly failing, no
simulation/emulator was involved, and the runtime backstop's firing produced no
duplicate. Cleanup of the two prepared IDs was independently confirmed after the
automatic timer ran. This is ONE live witness, not whole-suite or campaign
acceptance.

## Confirmed

- **Gate/identity:** `gate.out` `{"gate":"PASS","registry_source":"live-agent-deck",
  "worker":"ba5a1ae8-1790093908","verifier":"203af130-1790093909"}`, rc0.
  I re-ran `case_entry.py gate` read-only against the same signed
  config/plan/signatures and reproduced `PASS` rc0. Delivered messages route to
  exactly those two signed seats (`deliveries.jsonl`, `outbox/send-000.json`,
  `outbox/send-001.json`, `manifest.json` routes). Both seats are the r9p4
  identities bound by `execution-binding-corrected.json` (`7cacfbcb…`).
- **Hashes:** `config_sha256` `3ca1e755…`, `signatures_sha256` `680b54aa…`,
  `plan_sha256` `9249a819…`, `binding_sha256` `7cacfbcb…` all recomputed equal
  to the files and to `live-positive-release-3.json`. Signatures bind
  `stagec_entry_sha256` `9a1bb23c…`, `r3_harness_sha256` `d7b4e517…`,
  `r3_host_adapter_sha256` `231f45f0…`, `candidate_harness_sha256` `cd84e8dd…`,
  `composition_manifest_sha256` `161afac5…`; I recomputed the on-disk
  entrypoint, harness, host_adapter, fixture_control, deposit, seat_emulator and
  fault_onset hashes — all match — rehashed the whole composition manifest
  **29/29 clean**, and confirmed candidate commit `f1d7c86`
  (`Preserve P6r9 repair-3 candidate and incomplete verification`). The release's
  `binding_review_sha256` `f88170bb…` equals the hash of
  `execution-binding-correction-review-4.md` (the corrected-binding PASS).
- **Exactly-once sends:** `receipt.sends = {"worker":1,"verifier":1}`; exactly
  two outbox deposits (`send-000` worker, `send-001` verifier) and four delivery
  lines (2 intent + 2 done). No manual send. Independent check: the runtime
  backstop `p6-stagec-h1.timer` fired once at `16:35:31Z` after both commits and
  produced **no** additional delivery or outbox row (deliveries held at 4,
  outbox at 2) and is now inactive — the fixture's duplicate-fire dedup held
  live.
- **Handoff:** worker claim `ex-7e4a97136be2` `outcome: completed`, published
  `next_action: p6c-h1v`; verifier claim `exv-7e4a97136be2` `outcome: completed`,
  `check: recompute-sha256`, `check_detail: all artifact hashes recomputed
  equal`. Receipt `committed_actions [p6c-h1v, p6c-h1w]`, `settled_actions` both,
  `outcome.worker.decision transition-committed`, verifier `terminal-rest`.
- **Artifact:** `art/out.bin` sha256 `46409ea69826a6733ced5dd67fc0a9080601cbaaacd7a02192732356d25c0c88`
  equals the hash in both claims (worker and verifier) — independently
  recomputed.
- **Timing:** `timecheck` `verdict accept`, `success 2`, `joined 2`,
  `failures 1`. The single failure is the candidate's built-in zero-signal
  negative-control row (`outcome no-end-failure`, all endpoints null) which
  correctly fails while the two real rows pass — no vacuous acceptance. Real
  rows: worker onset `16:33:30Z` det `0.0s` rec `0.0s`; verifier onset
  `16:34:05Z` det `0.0s` rec `0.0s`; uncertainty 1s; worker durations
  `[59.0s, 35.0s]` within the 180s/180s grants and `live_stop_utc 16:36:45Z`.
  Witness rows carry `ack:true`, matching `(action, execution, case)` and
  `onset_provenance fixture-producer-seat`; no duplicate witness rows.
- **Non-simulation:** `simulated false`, `induced false`, `overlay false`,
  `candidate_gate pass`; real host timers/wakes, real artifact bytes.
- **Cleanup:** the automatic `campaign4-p6r9-prep4-cleanup.timer` ran at
  `16:37:48Z`; both r9p4 IDs are now **ABSENT** from the live registry and the
  positive timer/service is retired (no p6r9/stagec units remain). Archive at
  `/tmp/p6r9-prep4-20260922T161741Z/automatic-cleanup-archive/`
  (`launcher-records.json`, `launch-manifest.json`) holds exactly the two
  prepared p6-fixture IDs, no main/historical IDs.

## Open / limits (do not inflate the verdict)

- **Exit code not separately archived.** `run.out` (summary), empty
  `run.err` and the bound receipt corroborate rc0, but no explicit exit-code
  artifact was filed; release condition 4 asked for exit archived. Cosmetic,
  not contradicting rc0.
- **Cleanup archive not yet filed to the package.** `live-preparation-4/`
  has no cleanup-receipt copy yet; the `/tmp` archive and verified registry
  removal exist. Cairn's remaining duty (prep condition 6 / live condition 5).
- **Orphan socket files remain** at
  `acp-sock/{ba5a1ae8…,203af130…}.sock` after registry removal (same inos as
  the binding). Registration cleanup succeeded; the socket files are leftover
  runtime artifacts, benign but not swept.
- **One host/load witness.** Timing acceptance is a single live point; the
  candidate's full observer-lifetime suite and the whole-repo suite remain
  deferred per the repair claims. This PASS does not certify them.

## Effect

Live attempt `P6r9-live-positive-3` is a genuine **PASS** for the bounded
positive-handoff case: one real worker completion handed off to one real
verifier completion, exactly-once, faithful identities and hashes, honest
timing with a correctly-failing negative control, and verified fixture cleanup.
Returned to Tern for next disposition; no retry, send, socket write or package
mutation occurred during this review.
