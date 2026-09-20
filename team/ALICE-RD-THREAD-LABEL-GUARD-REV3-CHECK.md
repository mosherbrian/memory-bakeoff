# Second-seat check — RD thread label guard rev 3 (+ three coverage gaps)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 11:40 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of the new rev that folds my and Assay's findings. No tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_rd_thread_labels.py`
sha256 **`bb30e7a3…`** (rev 3; rev 2 `3ffd9fda…`, rev 1 `31331680…`), and
`team/CORVID-RD-THREAD-LABEL-GUARD.md`.

## Verdict

**PASS / AGREE on every rev-3 fix.** Rev 3 closes my two escape paths from rev 1
(unreadable → structured; out-of-range → `[MALFORMED]`) and Assay's two rev-2
gaps (impossible date-only; non-UTC escape), and the new line-anchoring removes
the prose-quote over-flag I noted. **Three new low coverage gaps:** a **future
date-only label escapes**, and **labels that are indented or in a list item are
invisible** to the `^\*\*` anchor.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `bb30e7a3…` | re-hashed | ✓ `bb30e7a3e180…` |
| `--self-test` PASS (all classes) | re-ran | ✓ PASS, rc 0 |
| real `RD-THREADS.md` default: 45 dated / 140 date-only / 36 unchecked / 0 flagged, rc 0 | re-ran | ✓ `46 / 145 / 39 / 0`, rc 0 (counts grew with entries) |
| `--strict` on the real log → rc 1 | re-ran | ✓ rc 1 (the historical non-UTC labels) |
| F1: impossible **date-only** label is `[MALFORMED]`, rc 1 | `**2026-13-01 — x**` | ✓ `[MALFORMED] 2026-13-01 —`, rc 1 |
| out-of-range time is `[MALFORMED]`, not a traceback | `**2026-09-13 24:00 UTC — x**` | ✓ `[MALFORMED] …24:00…`, rc 1, no traceback |
| F2: non-UTC time label surfaced, not invisible | `**2026-09-13 10:00 PDT — x**` | ✓ `[UNCHECKED-TIME]`, `unchecked_time_labels=1`; default rc 0, `--strict` rc 1 |
| line-anchoring removes prose over-flag | mid-line `text **2026-13-01 —** more` | ✓ not flagged |
| unreadable file is structured | `chmod 000` | ✓ (claimed; rev-2 verified by me and unchanged) |

## New gaps (all low; demonstrated, not theoretical)

**G1 — a future date-only label escapes.** `DATE_ONLY_RE` labels are validated
for *calendar* validity only (`_date_ok`), never compared to mtime:

```
**2099-01-01 — x**   ->  date_only=1, flagged_labels=0, rc 0
```

A date after the file's last write is impossible in exactly the same way a time
after it is. Fix: parse the date-only label and flag `date.date() > mtime.date()`
as `[AFTER-MTIME]` (or a distinct `[FUTURE-DATE]`).

**G2/G3 — indented and list-item labels are invisible.** All three regexes are
`^\*\*…`, so a label not at column 0 is silently uncounted:

```
  **2099-01-01 00:00 UTC — x**   ->  dated_labels=0, rc 0   (two leading spaces)
- **2099-01-01 00:00 UTC — x**   ->  dated_labels=0, rc 0   (list item)
```

Today's entries are column-0 so there is no live miss, but a seat that formats
an entry with a bullet or indent escapes the whole guard. Fix: anchor as
`^\s*(?:[-*]\s+)?\*\*` in all three regexes — still line-anchored (a mid-line
prose quote has non-space text before it, so it stays excluded).

## Scope and limits

- Synthetic probes under `/tmp`; the real log was read only. I did not edit the
  guard or its note.
- The detection-window limit (a bad label is only visible until the next append)
  still applies; this is a pulse-end check.
- `--strict` on the real log fails because of 39 historical non-UTC labels; that
  is a policy choice (advisory vs fail-closed), not a defect, but it means
  `--strict` is not usable until those are annotated.
- Scoreboard/board label fields remain out of scope.
