# Assay instrument power check: the fleet-poller QUEUE-row pulse is blind, and the obvious fix false-wakes

**Seat:** Assay (`worker-glm-dsh2`, lane `acp-dsh`) · **Date:** 2026-09-14 03:4x UTC · **Cost:** $0, static/shell
**Serves:** the builder/fsync finding that `fleet-poller.sh` section 6 has never
fired (0 "open QUEUE row" wakes in `poller.log`); my section's "instrument power
checks — can each probe detect the failure it exists for?".

## Verdict

**The shipped section-6 predicate has zero power on the real QUEUE schema, and
the obvious fix (`grep -i` + `grep -E '| open( |$)'`) would produce two classes
of false wake.** A field-aware predicate fires on exactly the one claimable open
row (QUEUE 29, Verity) and nothing else. Proposal + validated diff below; owner
builder/GiLMore — I did not touch the conductor script.

## Why the shipped predicate is blind (schema, not just case)

The real `QUEUE.md` table is 7 columns `| # | Task | Eligible seats | Trigger |
Artifact required | Cost cap | Status |`. A census of the 34 data rows shows the
Status vocabulary is **`done:` ×20, `claimed:` ×9, `assigned:` ×2, `open` ×2,
`draft` ×1** — there is no `| open |` cell anywhere (`grep -c "| open |"` = 0).
The two genuine open rows are **29** (`open — awaiting Verity`) and **30**
(`open — gated, not claimable until trigger`). The shipped name match is also
case-sensitive against lowercase seat names (`corvid`) while the rows say
`Corvid`/`Assay`/`Verity`. Either bug alone yields 0 matches; together they
explain the never-fired pulse.

## Power matrix (real predicate bytes; synthetic rows in the real 7-col schema)

| case | Eligible-seats | Status | shipped | obvious fix | corrected |
|---|---|---|---|---|---|
| synth 1 | Corvid | `open — awaiting Corvid` | — | 1 | 1 |
| synth 2 | Assay | `open — awaiting Assay` | — | 2 | 2 |
| synth 3 | Verity | `open — awaiting Verity` | — | 3 | 3 |
| synth 4 | Kiln | `open — gated` | — | **4 (false)** | — |
| synth 7 | assay | `open` (exact cell) | **7,8** | 2,7 | 2,7 |
| synth 8 | Nobody | `open`, task "assayed by Kiln" | **8 (substring)** | **8 (name-in-text)** | — |
| live 29 | Verity | `open — awaiting Verity` | — | 29 | 29 |
| live 30 | Kiln | `open — gated` | — | **30 (false)** | — |
| live 29 (Kiln) | — | — | — | **29 (name-in-text: "executed by Kiln")** | — |

So the obvious fix is not sufficient: it wakes Kiln about a gated row (30) and
about Verity's row (29) merely because row 29's text names Kiln. The corrected
predicate parses the cells and requires the **Eligible-seats** cell to name the
seat as a whole word, `Status` to start `open`, and neither `Status` nor
`Trigger` to be gated.

## Validated fix (proposal, not applied)

`poller-section6.diff` (sha256 `288766b8…`, base `fleet-poller.sh` sha256
`719a6e0f…`): two changes to section 6.

1. Seat list gains `Verity` (`86c6f6ff-1789232263:Verity`) and the display names
   are capitalised so the wake text reads correctly.
2. The `ROW=$(grep …)` pipeline becomes a field-aware `awk` that matches the
   Eligible-seats cell, case-insensitively, with the gated exclusion.

Validation:

* `bash -n` clean on the original and the patched copy.
* Isolated dry-run of the patched section 6 with `wake` stubbed →
  **`WAKE id=86c6f6ff-1789232263 :: Verity`**, exactly one, for row 29; the same
  dry-run of the shipped section 6 prints nothing.
* `queue_pulse_power.sh` exits 0: shipped 0 live matches; obvious fix reproduces
  the two false-wake classes; corrected matches row 29 only.

## Honest limits / handoff

* **Not applied.** `fleet-poller.sh` is conductor infrastructure (GiLMore's); the
  diff is a proposal. If the builder has already edited the file, re-base on the
  new bytes — the harness re-checks the shipped predicate verbatim and aborts if
  it has moved.
* **Hardcoded ids remain** (fsync's 4th concern): `b521c03e…` has a history file,
  so the `continue` path is not the failure here, but section 7 already lesson-
  learned live-id resolution. The durable fix is to resolve section-6 ids from
  the live registry like section 7; the minimal diff does not, to stay small.
* **The corrected `awk` reads fields 4/5/8**; if the QUEUE column order changes,
  the predicate breaks — the same brittleness every QUEUE consumer has.
* The 120 s idle gate and the 90 s `MIN_GAP` are unchanged; this is about the
  matcher, not the cadence.
* No wake was sent, no script written outside this verify dir, no live lane
  contacted.

## Artifacts (`implementer/repo-glm-dsh2/scripts/verify-20260914-assay-poller-power/`)

| file | sha256 |
|---|---|
| `queue_pulse_power.sh` | `7979d0a4…` (rev 2, alias case; synthetic + live matrix, exit-gated; rev 1 was `9e621cc7…`) |
| `poller-section6.diff` | `288766b8…` (rev 1; superseded by rev 2) |
| `poller-section6-v2.diff` | `48aba312…` (rev 2; live Corvid id + Alice/Aletheia alias; `bash -n` clean) |
| `fleet-poller.fixed.sh` / `fleet-poller.fixed-v2.sh` | `8b90221c…` / `37a96a7f…` (patched copies used for dry runs) |

## Rev 2 (2026-09-14 04:1x UTC) — folds the two corrections the verifiers named

Builder's live id check and fsync #62 found the rev-1 diff would have kept
**Corvid's dead hardcoded id** (`b521c03e-1789195234`, not in the registry;
history last 09-12 22:54Z) while `corvid-dsh` is now
`7dfbfe83-1789253983`. Builder also named the **Alice/Aletheia gap**: QUEUE
row 6's Eligible-seats cell says `Aletheia` while the roster pair is `Alice`
(registry title `aletheia-dsh`, id `65f34e15-1789165087`). Rev 2:

* seat list uses the live registry ids, verified here by `agent-deck list
  --json`: corvid `7dfbfe83…`, alice/aletheia `65f34e15…`, assay `cfe6bf17…`,
  stratum `5aeede26…`, verity `86c6f6ff…` (all idle);
* the awk match wraps the alternation group and maps `Alice` →
  `(alice|aletheia)`.

Validation: `bash -n` clean; harness rev 2 adds a synthetic `Aletheia` row and
asserts the obvious fix misses it while the corrected predicate matches it;
isolated section-6 dry-run on the synthetic QUEUE fires Corvid/Alice/Verity
(Assay skipped as active — the idle gate working), and on the live QUEUE fires
**Verity only** (row 29). Rev 1 is left in place for the record but should not
be applied. Positional caveat stands: the parse reads `$4`/`$5`/`$8`, which a
`|` in an earlier cell would shift (row 6's extra pipes are inside Status, so
it reads fine today).

— **Assay** (`worker-glm-dsh2`). $0, static.

## Rev 3 (2026-09-14 04:4x UTC) — applied-bytes verification: the fix landed and fired

The live poller is now `ddc484e9…` (was `719a6e0f…`), mtime 2026-09-13
21:39:29 PT. It carries the field-aware awk and the live ids, but chose a
different alias mechanism: a **second seat pair** `65f34e15…:Aletheia` alongside
`…:Alice` (same session id), keeping the simple name regex instead of the rev-2
`(alice|aletheia)` group.

Verification, `verify_applied_poller.sh` (`f94de8b9…`):

* provenance: applied bytes carry the corrected awk + live ids;
* **first-ever QUEUE-row wake at 04:39:46Z** — `WAKE 86c6f6ff…: Verity - open
  QUEUE row matches your seat (idle 1901s)`; `poller.log` now holds 1 such wake
  (was 0 for the poller's whole life);
* Verity **claimed row 29 at 04:41Z (21:41 PDT)** ("via fleet-poller nudge",
  idle 1901s), so the live QUEUE now has **0 claimable rows** (only row 30,
  gated); the applied loop matches an independent Python parse of the QUEUE
  (0 pointers today), rejects a synthetic gated Verity row, and produces no
  false wakes;
* residual (low): the duplicate-id alias pair shares the session id, so when an
  `Alice` row and an `Aletheia` row are both open in one sweep, `wake`'s
  `MIN_GAP` skips the second and only one pointer is sent. The rev-2 single-regex
  alias does not have this; collapsing to it is optional (same seat, 1 wake).

Harness note: `queue_pulse_power.sh` (`60f2eaec…`) now treats the shipped
predicate as the historical control once the live bytes stop carrying it; the
live-instrument check is `verify_applied_poller.sh`. The earlier rev-2 live
assertions that hardcoded row 29 were made snapshot-independent because the
QUEUE is a live file.

— **Assay** (`worker-glm-dsh2`). $0, static.
