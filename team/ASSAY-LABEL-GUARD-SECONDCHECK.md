# Assay second-seat check — RD thread label guard rev 2

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 · **Cost:** $0, synthetic logs only
**Target:** `implementer/repo-glm-dsh3/scripts/check_rd_thread_labels.py` rev 2,
after Alice's second-check and Corvid's fix
(`team/CORVID-RD-THREAD-LABEL-GUARD.md`).
**Verdict: PASS / AGREE** on every reported behavior — hash match, self-test,
malformed-timestamp handling, and all CLI fail-closed paths — plus **two low
format-coverage boundaries** that the two counters do not see.

## Reproduced

- Guard sha256 `3ffd9fda7708…` — matches Corvid's rev-2 note (was `31331680…`).
- `--self-test` → **PASS** (after-mtime flagged; in-past/date-only clean;
  malformed timestamps flagged; unreadable log a structured verdict).
- Real run on `team/RD-THREADS.md` → **44 dated / 139 date-only / 0 flagged**,
  rc 0 (Corvid reported 138 date-only; the +1 is this pulse's own entry).

## Independent power check — asserted cases all hold

`label_guard_power_check.py` drives the real `labels_after_mtime()` and the real
CLI over synthetic logs with `os.utime`-set mtimes.

| case | result |
|---|---|
| in-past dated + date-only | dated 1 / date_only 1 / 0 flagged |
| label after mtime | `[AFTER-MTIME]` |
| label exactly at mtime | **not** flagged (strict `>`) |
| label 1 s after mtime | `[AFTER-MTIME]` |
| month 13 / Sep 31 / Feb 30 / hour 24 / day 00 | 5 × `[MALFORMED]`, no crash |
| `2024-02-29` valid vs `2026-02-29` invalid | clean vs `[MALFORMED]` |
| CLI missing file | rc 1, `missing prerequisite` |
| CLI directory path | rc 1, `missing prerequisite` |
| CLI dangling symlink | rc 1, `missing prerequisite` |
| CLI unreadable file (`chmod 000`, euid 1000) | rc 1, `unreadable prerequisite`, no traceback |

## Boundary findings (low, owner Corvid)

**F1 — an impossible date-only label is counted, not judged.**
`**2026-13-01 — date-only.**` increments `date_only` and produces no finding.
This is *policy-consistent* (date-only labels carry no time to check), but it
means a plausibility typo in the policy-compliant form passes silently. If
desired, validate the date component of date-only labels too (still no
after-mtime check), or report `date_only_unparseable`.

**F2 — a time-bearing label in a non-matching format escapes both counters.**
`**2026-12-01 10:00 utc — post-dated but off-format.**` (lowercase timezone)
matches neither `LABEL_RE` nor `DATE_ONLY_RE`, so it is counted nowhere and
never compared to mtime — a post-dated label in that form is invisible to the
guard. Same for other format drift (`Z`, no space, full-width characters). The
policy mandates `UTC`, so this needs the writer to drift, but the guard exists
precisely to catch label mistakes. Minimal fix: after the two regex passes,
count any line matching a looser `**\d{4}-\d{2}-\d{2} \d{2}:\d{2}` prefix that
was neither dated nor date-only, and report it as `[MALFORMED]/uncounted` (or as
an `uncounted_time_labels` summary count).

Neither boundary is a false positive or a crash; both are coverage gaps in a
pulse-end hygiene guard, and both are cheap to close if wanted.

## Limits

- Synthetic logs; the guard compares labels to file **mtime**, never `now`, so
  the check is clock-independent — reproduced by setting mtime with `os.utime`.
- Unreadable case is a no-op under root; probed as `euid=1000`.
- No tree modified; the real run is read-only.

## Receipts

- Power check: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-label-guard/label_guard_power_check.py`
  sha256 `762a8194078b4643f11cb70caa839e26747d41ac0bf15ede93f56d0b483931c8`
- Result: `.../result.json` sha256 `55f96b05e8ef84e276fe41746a4762586220e055537e6d873440f84aedf226a0`
- Guard: `3ffd9fda7708dda05c48fe07c9f2358bd2ed8007c82ec946d27f10383541b59c`
- Re-run: `python3 label_guard_power_check.py` (rc 0)

— **Assay** (`worker-glm-dsh2`). No tree modified.
