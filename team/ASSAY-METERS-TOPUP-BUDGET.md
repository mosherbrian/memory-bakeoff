# Assay — power check + fix: `meters.budget()` forgets spend across a top-up

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, no network, no LLM
**Thread:** Assay — instrument power checks.
**Trigger:** builder's RD-THREADS 12:07 finding (DeepSeek top-up reset the fleet
spend to ~$0).
**Subject:** `meters.py` (`/home/bmosher/conductor-chat/meters.py` and the
identical `conductor-chat-cairn` copy), sha256 `f2d5c8ea…`.
**Status:** fix validated, **not applied** — the budget rule is Brian's/GiLMore's.

## Defect (reproduced)

`budget()` computes `spent += max(0, baseline.deepseekLeft - ds.left)`. A
DeepSeek **top-up raises `ds.left` above the baseline**, so the term clamps to 0
and every dollar spent before the top-up is forgotten; the balance must fall back
under the old baseline before spend counts again.

Power check `meters_topup_power_check.py` drives the real
`budget(ds=..., orr=...)` (fresh temp `dsh-budget.json`, no network):

| read | true consumed | canonical spent | fixed spent |
|---|---:|---:|---:|
| init (ds 16.55) | $0.00 | $0.00 | $0.00 |
| spend $7.51 (ds 9.04) | $7.51 | $7.51 | $7.51 |
| **top-up +$20 (ds 29.04)** | **$7.51** | **$0.00** | **$7.51** |
| spend $9.03 more (ds 20.01) | $16.54 | **$0.00** | **$16.54** |

**Drain-to-refusal (the failure the `--check` probe exists to catch):**

| | total real spend when `--check` refuses |
|---|---:|
| canonical | **$45.10** |
| fixed | **$25.10** (one $0.10 step) |

So the campaign cap tolerates ~$45 of real spend, not $25 — the builder's
"about $45" is exact. The bug is DeepSeek-specific: the OpenRouter term tracks
cumulative `used`, which never decreases, so it cannot reset; only the
balance-based DeepSeek term is affected.

## Fix

`meters-topup.diff` sha256 `41f0f31d…`; guarded `meters.patched.py` sha256
`a515421c…`; `git apply --check` clean on **both** live copies.

Track `baseline.deepseekLast`. On each read:
- `left > last` → top-up: `baseline.deepseekLeft += (left - last)`, so `spent`
  stays continuous and a top-up never hands back consumed allowance;
- `left < last` → normal spend: move `last` down;
- persist whenever either changed (idle reads are unchanged → no write).

## Migration caveat (one-time, needs Brian's approval)

The current live state already lost the ~$7.51 (builder: reported $0.02 vs true
~$7.53). The fix **cannot recover it retroactively** — `dsh-budget.json` has no
record of the pre-top-up balance. To restore the true figure in one edit, set
`baseline.deepseekLeft = <current left> + 7.51` (equivalently `+=` the forgotten
amount) once, or accept the under-count. Either is a budget-rule call.

## Receipts

- `meters.patched.py` `a515421c…`, `meters-topup.diff` `41f0f31d…`,
  `meters_topup_power_check.py` `82ed78cd…` (v2, supersedes `d24c0843…`);
- sealed result `sealed-meters-topup-20260913/result.json` `68a36804…`
  (6/6 cases; supersedes `ddaa8460…`);
- live baselines `f2d5c8ea…` on both copies.

## Limits

Synthetic balances injected into the real function; no provider was called and
no live `dsh-budget.json` was read or written. The fix changes write frequency
(only while the balance moves) and adds one state field. Owner: builder (tool)
+ Brian/GiLMore (rule).

— **Assay** (`worker-glm-dsh2`).

---

## Rev 2 — edge cases (same fix, stronger power check)

The same `meters.patched.py` (`a515421c…`) and diff (`41f0f31d…`); the power
check gained three top-up shapes a naive fix could still get wrong:

| shape | canonical final spent | patched final spent | truth |
|---|---:|---:|---:|
| top-up **smaller than the old peak** (16.55→9.04→12.00) | $4.55 | **$7.51** | $7.51 |
| **two top-ups** with spend between (…→12.00→5.00→15.00) | $1.55 | **$14.51** | $14.51 |
| no top-up (pure spend) | $6.55 | $6.55 | identical |

The below-peak case matters: the balance never exceeds the original baseline, so
the old formula silently under-counts by the top-up amount — a top-up does not
have to be large to corrupt the figure.

## Carried limitation — concurrency

The fix persists `baseline.deepseekLast` whenever the balance moves (the old
code wrote only on first-ever init). `budget()` is called by both `server.py`
and `dsh-lane`, so two concurrent read-modify-write calls can lose an update to
`dsh-budget.json` (no lock). The exposure is small and a top-up is rare, but a
lost `deepseekLast` write could make a later top-up be measured from a stale
peak. A `fcntl.flock` around the read/persist would close it if the owner wants
that guarantee; it is not in this diff.

— **Assay** (`worker-glm-dsh2`).
