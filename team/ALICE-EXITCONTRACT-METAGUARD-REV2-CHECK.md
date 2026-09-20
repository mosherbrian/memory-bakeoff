# Second-seat / power check — checker exit-contract meta-guard v2

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 08:47 UTC · **Trigger:** standing second-check (my 08:36 finding on
the v1 meta-guard; Corvid's 08:42 handoff marks the rev-2 re-check open for
Alice) · **Cost:** $0, read-only + `/tmp` scratch, one turn.

**Subject:** `repo-glm-dsh3/scripts/check_checker_exit_contracts.py`
(sha256 **`fa579cc7…`**), plus `team/CORVID-EXITCONTRACT-CRASH-FIX.md`. No
tree was modified.

## Verdict

**PASS / AGREE.** Rev 2 closes my v1 crash power-finding: a dirty-root crash
is now caught, and the marker check makes the "structured verdict" half of
Muse 4.1 real. All claims reproduce independently. **One new boundary finding
(low severity, latent — 0/9 live exposure):** the clean control asserts rc 0
and no traceback but does **not** assert the finding marker is *absent*, so a
guard that cries its marker on clean input slips through.

## Verified claims (independent re-run)

| Claim | Check | Result |
|---|---|---|
| sha `fa579cc7…` (was `9d6d27fe…`) | re-hashed the real file | ✓ `fa579cc7d95c…` |
| `--self-test` PASS, four synthetic classes | re-ran it | ✓ PASS, rc 0 |
| 9/9 real contracts hold, exit 0 | re-ran the full driver | ✓ 9/9, rc 0 |
| crash on dirty root is now caught | drove the guard's **own** `evaluate()` with my synthetic `crashy.py` | ✓ `exit 1 but output is a crash traceback, not a verdict` |
| prose-only/exit-0 still caught | synthetic `prose.py` | ✓ `exit 0, expected 1` |
| finding-less exit-1 still caught | synthetic `silent.py` | ✓ `exit 1 without the finding marker` |
| clean control has power | synthetic `always1.py` | ✓ `[clean control]: exit 1, expected 0` |
| marker check runs **after** the traceback check | synthetic `crashmarker.py` (prints marker, then crashes) | ✓ flagged as traceback, not as a clean detection |

The crashy/always1/silent/marker checks were driven through the guard's real
`evaluate()` (imported from the real file), not a re-implementation.

## Positive control — the marker coupling is real, not asserted

Corvid's claim is that editing a guard's summary wording now fails the
contract. Tested without touching any tree: copied `scripts/` to `/tmp`,
changed exactly one guard's finding line
(`check_query_fork.py:101` `FORK {q}` → `forked-query {q}`), and ran the
copied meta-guard:

```
  check_query_fork: BROKEN
      check_query_fork.py [dirty control]: exit 1 without the finding marker /FORK / :: ...
=== checker exit contracts: 8/9 hold   (rc 1)
```

The other eight stay OK. So the marker table does bind the guards' wording,
and the failure mode is a loud BROKEN, not a silent no-op.

## New boundary finding — clean control does not forbid the marker

`evaluate()` (lines 164–182) requires the marker on the **dirty** run but
never checks that the **clean** run omits it. A synthetic `wolfer.py` that
prints the marker on *every* run while still returning the right exit codes
passes both controls:

```
correct        violations=[]
prose          violations=['... exit 0, expected 1 ...']
crashy         violations=['... crash traceback, not a verdict ...']
silent         violations=['... without the finding marker ...']
always1        violations=[clean exit 1, dirty no marker]
wolfer         violations=[]          <-- marker emitted on the clean root
crashmarker    violations=['... crash traceback ...']
```

Why it matters: the marker exists to be the machine-readable verdict. If a
future guard prints its finding token unconditionally (or in a legend/header),
a consumer that greps the marker sees an alarm on clean input even though the
exit code is right — the S6 "machine-readable verdict" class one level up.
**Live exposure measured: 0/9.** I ran each real guard on its own clean
fixture and grepped its own marker — no guard emits its marker on clean
(`marker_on_clean=False` for all nine; all clean rc 0). The gap is latent, not
a live mis-grade.

**Recommendation (owner Corvid, low priority):** once, in `evaluate()`, add
`if label == "clean" and dirty_marker and re.search(dirty_marker, text):` →
violation "clean control emitted the finding marker"; or require each marker
pattern to be count-gated (`: [1-9]`, as most already are). Add a `wolfer.py`
case to the self-test so the control keeps this power.

## Scope and limits

- The meta-guard ships **only** in `repo-glm-dsh3` (`repo` and `repo-glm-dsh2`
  have no copy), so this check covers that tree's guard bytes only.
- All adversarial scripts and the mutated copy live under `/tmp/alice-mg2/`;
  the real tree was never written. The 9/9 result is the real driver re-run
  as-is on today's hashes.
- Minor, not filed as a finding: a guard that hangs on dirty input trips
  `subprocess.run(..., timeout=120)` and the uncaught `TimeoutExpired` aborts
  the whole meta-guard with a traceback — loud, but it leaves the remaining
  guards ungraded. Only relevant if a guard ever hangs.
- I did not force a real guard to crash or re-run the guards' own suites.
