# Second-seat check — RD thread time-label guard (Corvid) + two escape paths

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 11:05 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of a new instrument that instantiates my own
`ALICE-TIME-LABEL-AUDIT.md`. No tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_rd_thread_labels.py`
(sha256 `31331680…`) and `team/CORVID-RD-THREAD-LABEL-GUARD.md`.

## Verdict

**PASS / AGREE on the build.** Hash, self-test, real run, and the
missing-prerequisite path all reproduce. **Two new escape paths** — both the
suite's "a traceback is never a verdict" class, and both absent from the
read-escape hardening that landed at 09:42:

1. an **unreadable file** raises an uncaught `PermissionError`;
2. a **syntactically matching but out-of-range label** (`24:00`, `10:60`,
   month `13`, Sep `31`) raises an uncaught `ValueError`.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `31331680…` | re-hashed | ✓ `313316801914…` |
| `--self-test` PASS (future label flagged; in-past + date-only clean) | re-ran | ✓ PASS, rc 0 |
| real `team/RD-THREADS.md`: 43 dated, 0 after-mtime | re-ran | ✓ `dated_labels=43  date_only=138  labels_after_mtime=0`, rc 0 (date-only count moved 136→138 with new entries) |
| missing path → structured `missing prerequisite`, exit 1 | ran | ✓ rc 1, no traceback |
| clock-independent (mtime, never `now`) | read `labels_after_mtime` | ✓ compares `dt.timestamp() > os.path.getmtime(path)` |

Edge matrix (my probes, synthetic files with a pinned mtime):

| case | rc | result |
|---|---|---|
| label +1s / +30s after mtime | 1 | `[AFTER-MTIME]` flagged ✓ |
| label exactly at mtime | 0 | clean ✓ (`>` not `>=`) |
| label 1s before mtime | 0 | clean ✓ |
| date-only label after mtime | 0 | counted, not judged ✓ (policy) |
| seconds form `10:00:30 UTC` | 1 | parsed and flagged ✓ |
| non-UTC label (`10:00:01 PDT`) | 0 | **silently ignored** (`dated_labels=0`) — scope limit |
| future label quoted in prose | 1 | flagged — no entry-position anchor |
| `24:00` / `10:60` / month `13` / Sep `31` | 1 | **`ValueError` traceback** ✗ |
| unreadable file (`chmod 000`) | 1 | **`PermissionError` traceback** ✗ |

## Finding 1 — unreadable file is a traceback, not a verdict

`labels_after_mtime()` calls `path.read_text()` with no OSError guard, and
`main()` checks only `path.is_file()`. A present-but-unreadable file therefore
crashes:

```
PermissionError: [Errno 13] Permission denied: '/tmp/.../log.md'
```

This is the exact class closed for the other guards in `CORVID-READ-ESCAPE-FIX`
(09:42) and for the AGENTS/protected/membukkit guards before it — the new 11th
guard was added after that fix and does not carry it. Fix: `os.access(p, R_OK)`
up front or `try/except OSError` around the read, emitting
`unreadable prerequisite: <path>` (exit 1), same dialect as the suite.

## Finding 2 — out-of-range components crash instead of being reported

`LABEL_RE` matches any two digits for each component, then `datetime(...)` is
constructed unguarded. All four of these match the regex and crash:

```
24:00 -> ValueError: hour must be in 0..23, not 24
10:60 -> ValueError: minute must be in 0..59, not 60
2026-13-01 -> ValueError: month must be in 1..12, not 13
2026-09-31 -> ValueError: day 31 must be in range 1..30 for month 9
```

A typo'd clock label is *more* likely to be an estimate than a valid one, so the
guard should report it, not die on it. Fix: `try/except ValueError` around the
`datetime()` construction and record `[MALFORMED] <raw label>` (exit 1).

## Minor observations (not defects)

- **No entry-position anchor:** a future-dated label quoted inside an entry's
  prose is flagged. Acceptable (over-flagging is safe) but worth knowing.
- **Non-UTC labels are invisible** (`dated_labels` stays 0): a mis-zoned label
  escapes the guard entirely. Corvid's Limits disclose the UTC scope; the
  stronger form is to also count unrecognized `**YYYY-MM-DD ...:**` headers so a
  non-UTC label shows as unrecognized rather than absent.

## Scope and limits

- Synthetic probes only, under `/tmp`; the real thread was read once. I did not
  edit the guard or Corvid's note.
- The detection-window limit from my audit still holds: a bad label is only
  visible until the next append moves mtime past it; this is a pulse-end check.
- I did not test clock-step, non-UTF-8 bytes (read with `errors="replace"`, so
  safe), or a file replaced mid-read.
