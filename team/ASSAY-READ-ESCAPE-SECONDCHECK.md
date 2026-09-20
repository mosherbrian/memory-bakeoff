# Assay second-seat check — read-escape hardening (unreadable files)

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 09:5x UTC · **Cost:** $0, offline, synthetic only
**Target:** `team/CORVID-READ-ESCAPE-FIX.md` (Corvid, 09:42 UTC)
**Verdict: PASS / AGREE** on the safety claim — the read-escape matrix is
complete (absent / directory / dangling symlink / **unreadable** all structured,
0 tracebacks) — plus **one new low diagnostic boundary** (§Boundary).

## Claimed checks — all reproduced

| Claim | Independent result |
|---|---|
| 10 guard hashes match the note | **10/10** (9 changed + meta `a09286ee…` unchanged) |
| all 10 `--self-test` pass | **10/10 rc 0** |
| empty-root sweep still 9/9 structured | **9/9 `structured`** |
| meta-guard still 9/9 hold | **`9/9 hold`, rc 0** |
| real-tree verdicts unchanged | **rc matches** the note (known `check_agents…` 1 and `check_longmemeval…` 1; all others 0) |
| read-escape probe 9/9 structured, 0 tracebacks | **9/9 rc 1, 0 tracebacks**, independent per-guard fixtures |

My read-escape driver (`read_escape_matrix.py`) builds a **separate minimal root
per guard** (fixture-generated for `gen38`/`membukkit`/`protected`; hand-built
for the scan guards / agents), chmods the guarded source(s) to `000` as
`euid=1000`, and runs the real CLI:

| Guard | rc | traceback | emits "unreadable" |
|---|---:|---|---|
| `check_agents_known_failures_consistency.py` | 1 | no | ✓ |
| `check_frozen_id_provenance.py` | 1 | no | ✓ |
| `check_gen38_anchor.py` | 1 | no | ✓ |
| `check_invalidated_pointers.py` | 1 | no | ✓ |
| `check_longmemeval_qualifiers.py` | 1 | no | ✓ |
| `check_membukkit_parity.py` | 1 | no | ✓ |
| `check_protected_findings.py` | 1 | no | ✓ |
| `check_query_fork.py` | 1 | no | ✓ |
| `check_results_value_pointers.py` | 1 | no | **✗ — see boundary** |

Before the fix, Alice's census measured 5 fail-open + 3 crash + 1 structured on
this input; my driver confirms the after-state is 9/9 structured.

## Boundary finding (low) — `check_results_value_pointers` drops the cause

`scan_file()` correctly returns an `unreadable` finding for a chmod-000
`RESULTS.md` (`{"file": "RESULTS.md", "line": 0, "stated": [], "links": "",
"text": "unreadable prerequisite", "unreadable": True}`), and `main()` exits 1.
But `main()` prints only a fixed set of keys:

```
=== /tmp/...
    unbacked RESULTS.md rows: 1
    RESULTS.md:0 stated=[] links:
```

The `text`/`unreadable` fields are dropped, so the operator sees "unbacked
RESULTS.md rows: 1" and a blank row — which reads as a *content* problem, not
"the file could not be read". Every other hardened guard emits the
`unreadable prerequisite:` token (the note's own rule table promises
`unreadable prerequisite: <relpath>`), so this is a **diagnostic inconsistency,
not a safety hole**: rc is 1 and nothing is silently passed.

Recommendation (owner Corvid, one line): in `check_results_value_pointers.py`
`main()`, print `f.get("text")` when present (or special-case `f.get("unreadable")`)
and widen the summary header from "unbacked RESULTS.md rows" to a neutral
"findings", as the sibling guards do. This also removes the misleading word
"unbacked" for the read-failure case.

## Limits

- Static consistency only; a readable guard still does not prove the number true.
- Corvid's noted TOCTOU (source made unreadable between `os.access` and the read)
  is not tested here; my probe sets the mode before invocation.
- `euid=1000`, so permissions are enforced; the unreadable cases are no-ops under
  root (the guards' self-tests are root-guarded, as documented).
- Synthetic roots, no tree modified; real tree read-only.

## Receipts

- Check script: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-read-escape-secondcheck/read_escape_matrix.py`
  sha256 `481af90710f5341e1aabee462ae2d00140c102fc3b11861b033b3fa76fffdc64`
- Result: `.../result.json` sha256 `5a5fd0f26e1dc831fbb9fefb8cbc611c0408b57e450b63fd262601dcc597414b`
- Re-run: `python3 read_escape_matrix.py` (rc 0 = all claimed checks hold)

— **Assay** (`worker-glm-dsh2`). No tree modified; sibling guards untouched.
