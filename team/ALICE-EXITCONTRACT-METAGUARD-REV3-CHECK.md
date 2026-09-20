# Second-seat / power check — checker exit-contract meta-guard rev 3

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 08:59 UTC · **Trigger:** standing second-check; Corvid's 08:58 rev-3
entry marks the second-seat re-check open for Alice (closes my 08:49 clean-root
marker-crier finding) · **Cost:** $0, read-only + `/tmp` scratch, one turn.

**Subject:** `repo-glm-dsh3/scripts/check_checker_exit_contracts.py`
(sha256 **`a09286ee…`**; was `fa579cc7…`), plus
`team/CORVID-EXITCONTRACT-CRASH-FIX.md` rev-3 section. No tree modified.

## Verdict

**PASS / AGREE.** Rev 3 closes my clean-root marker-crier finding: the clean
control now fails when a guard prints its own finding marker on the clean
fixture, and the self-test carries a `wolfer.py` case. All claims reproduce
independently; the five-case adversarial battery is caught in full, with no
false alarm on a correct checker. One residual (inherent, not a defect): the
meta-guard is the top of the contract stack and no higher check covers it.

## Verified claims (independent re-run)

| Claim | Check | Result |
|---|---|---|
| sha `a09286ee…` (was `fa579cc7…`) | re-hashed the real file | ✓ `a09286eeeedb…` |
| `--self-test` PASS, now five synthetic classes | re-ran it | ✓ PASS, rc 0, and the printed text names the clean-root marker-crier |
| 9/9 real contracts hold, exit 0 | re-ran the full driver | ✓ 9/9, rc 0 |
| clean control now forbids the marker | read `evaluate()` lines 178–185 | ✓ new `label == "clean"` branch; same `dirty_marker` regex, `_run` concatenates stdout+stderr so stderr is covered |
| correct checker does not false-alarm | drove the real `evaluate()` with my synthetic `correct.py` | ✓ `violations=[]` |
| marker-crier caught on the clean root | synthetic `wolfer.py` (prints marker every run, right exit codes) | ✓ `[clean control]: exit 0 but printed the finding marker` |
| stderr-only marker-crier caught (new probe) | synthetic `stderr_wolfer.py` (marker to stderr) | ✓ caught by the same clean branch |
| v1/v2 classes still caught | `prose.py`, `crashy.py`, `silent.py`, `always1.py`, `crashmarker.py` | ✓ all five flagged with the right message |
| live false-alarm risk 0 | ran each of the nine real guards on its own clean fixture and grepped its own marker | ✓ `marker_on_clean=False` for all nine, all clean rc 0 |

All adversarial scripts live in `/tmp/alice-mg3/` and were driven through the
guard's **real** `evaluate()` (imported from the real file), not a
re-implementation, so this is the guard's decision path.

## Self-loudness (meta-guard's own CLI contract)

Tested that the meta-guard is loud when the set is actually broken, on a
`/tmp` copy (real tree untouched): changed one guard's finding line
(`check_query_fork.py:101` `FORK {q}` → `forked-query {q}`), ran the copied
meta-guard → that guard **BROKEN** (`exit 1 without the finding marker`),
`8/9 hold`, **rc 1**. So the new clean-marker assertion did not soften the
failure path.

## Residual (inherent, not a defect)

The meta-guard is the 10th guard in the suite and sits *outside its own
contract*: no higher check asserts that the meta-guard itself exits nonzero
when it prints `BROKEN`, or that it never emits `BROKEN` on a clean set. I
verified both by hand above (broken copy → rc 1; real set → rc 0, 9/9), but
nothing guards that permanently. If the suite ever gains a runner above this
guard, an optional cheap smoke is: run the meta-guard on a known-good copy
(expect rc 0) and on a one-marker-mutated copy (expect rc 1). Filed as a
residual for the owner, not a blocker.

## Scope and limits

- The meta-guard ships only in `repo-glm-dsh3` (`repo`, `repo-glm-dsh2` have no
  copy), so this covers that tree's bytes only.
- I did not force a real guard to crash, re-run the guards' own suites, or
  touch any tree; the sibling guard hashes I re-checked are unchanged
  (`check_protected_findings.py` `bc9b52ca…`, `check_agents_known_failures_consistency.py`
  `f0f08542…`).
