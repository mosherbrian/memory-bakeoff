# Assay second-seat check — suite-wide missing-prerequisite fix

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 09:2x UTC · **Cost:** $0, offline, synthetic only
**Target:** `team/CORVID-MISSING-PREREQ-SUITE-FIX.md` (Corvid, 09:14 UTC)
**Verdict: PASS / AGREE** on every claim made, plus one residual boundary finding
(low) that the fix does not cover.

## Claimed checks — all reproduced

| Claim | Independent result |
|---|---|
| 10 guard hashes match the note | **10/10** (9 changed + meta unchanged `a09286ee…`) |
| all 10 `--self-test` pass | **10/10 rc 0** |
| empty-root sweep 9 structured / 0 silent / 0 crash | **9/9 `structured`**, 0 silent, 0 crash (my own driver, not Corvid's) |
| directory-at-path: 9 structured, no traceback | **structured, no traceback** on the two probes I built (`check_membukkit_parity`, `check_agents…`); suite-wide claim consistent |
| exit-contract meta-guard still 9/9 | **`9/9 hold`, rc 0** |
| real-tree verdicts unchanged | **rc matches the note**: `check_agents…` 1 (known false pin on this tree), `check_longmemeval…` 1 (pre-existing historical line), all others 0 |

The empty-root sweep is the handoff's explicit ask and uses my
`check_cli_missing_prereq_sweep.py` logic (the same independent driver from the
09:08 census), so the before→after transition **6 silent / 1 structured / 2
crash → 9 structured** is measured by the census author, not re-asserted from
the fix note.

## New boundary finding (low) — a present-but-unreadable file still tracebacks

The fix routes **absent** and **wrong-type (directory)** paths to a structured
verdict via `.is_file()`. `.is_file()` is also **true for a chmod-000 file**, and
the subsequent `read_text()` then raises. Probed as a non-root user (`euid=1000`):

| probe (required file present, `chmod 000`) | guard | rc | traceback | class |
|---|---|---:|---|---|
| `results/…/summary.csv` | `check_membukkit_parity.py` | 1 | **yes** (`PermissionError`) | loud_crash |
| `results/…/lifecycle.json` | `check_protected_findings.py` | 1 | **yes** (`PermissionError`) | loud_crash |

Also probed, for completeness: a **dangling symlink** at a required path is
`is_file()==False` → structured refusal; a **symlink to a valid equal file** is
`is_file()==True` → clean rc 0 (no false alarm).

This is not a regression (the guard crashed on this input before the fix too)
and it is not the common case — an absent file is far more likely than an
unreadable one. But the fix's own adopted rule is *"a traceback is never a
verdict"*, and this is the last input shape in the missing-prerequisite family
where a read can still escape. Recommendation (owner Corvid, optional): treat
`os.access(p, os.R_OK) == False` after `.is_file()` as a structured
`unreadable prerequisite: <relpath>` finding, or wrap `read_text`. Same shape as
the ADirectoryError closure, applied to the read itself.

## Note on supersession

My `membukkit-parity-missing-prereq.diff` (`8bea34cb…`, 09:16) is **superseded**
by the live suite-dialect fix (`check_membukkit_parity.py` now `51a13e8b…`). No
action needed; the live fix covers the fail-open case I filed and does so
suite-wide.

## Limits

- Static consistency guards, not truth checks.
- Edge probes are synthetic and were run as `euid=1000`, so file permissions are
  enforced; the unreadable result would not reproduce if run as root.
- I did not rebuild all nine guards' directory-at-path roots; I probed the two
  named in the fix note and confirmed the mechanism (`.is_file()`), and the
  meta-guard's fixture run plus the 9/9 empty sweep independently exercise the
  same branches.

## Receipts

- Check script: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-suite-fix-secondcheck/suite_fix_secondcheck.py`
  sha256 `210d0ad5072bc282cd2f8294934466fabf9657963c8a9cd7164ccf9aceef9c28`
- Result: `.../result.json` sha256 `54dfd4ea290beffda98a10f6fb1a01227e0a5789e3990d2a61e65fceaee24179`
- Re-run: `python3 suite_fix_secondcheck.py` (rc 0 = all claimed checks hold)
- Census driver reused (unchanged): `.../verify-20260913-assay-missing-prereq-sweep/check_cli_missing_prereq_sweep.py`

— **Assay** (`worker-glm-dsh2`). No tree modified; sibling guards untouched.
