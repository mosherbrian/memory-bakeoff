# R38 base-repair recheck — corvid-eval

**Verdict: PASS**, with one binding condition on the later execution authority.

Reviewer corvid-eval. Isolated `/tmp` only; no participants, network, real repo, service or
production effect. Original claim, fixtures, probes and my prior `verification.md` are
preserved unchanged.

## Intake
- **32/32 repair hashes recompute equal**; `verification.md` sha `64de964a…` =
  `repair-release.json` `review_sha256`; original 68/68 pins still match (unchanged).
- `repair/setup.sh` stages only `*.py` not under `__pycache__`
  (`find . -name "*.py" -not -path "*/__pycache__/*"`), so neither bytecode nor the
  absolute path enters the participant tree or the commit.

## Independent reproduction (relocated package copy)
I copied only `fixtures/`, `repair/`, `oracle/` to `/tmp/opencode/r38reloc/pkg` (a different
absolute path) and ran `sh repair/setup.sh` for each bug:
- U `518668bb94286d4a99d81dbdc30c63b614d17496`
- K `82bba0078c0623906dc076cf3b1935e32e20bcfb`
- J `361693fba7f7d26b32589b035267206873c5aeaa`

All three **equal the documented bases**, and each committed tree contains exactly
`src/__init__.py`, `src/<mod>.py`, `tests/test_<mod>.py` — **no `.pyc`, no `__pycache__`,
no absolute-path leakage**. Path-independence confirmed (the lead finding is closed).

## Semantics unchanged
Repair touches only `repair/setup.sh` and evidence: the claim's `unchanged` list (tasks,
packet, order, hidden tests, `grade.sh`, `runtests.py`, rubric semantics, original
`oracle/setup.sh`) is consistent with the original files retaining their earlier verified
hashes. Retained probes are coherent: U/K/J valid → overall PASS; U/K/J faulty → work FAIL;
K-pushrestore → `received_updates=2, channel FAIL`. No broad matrix rerun.

## Binding condition for execution authority
The later authority must invoke **`sh repair/setup.sh ARMDIR WITNESS_LOG fixtures/<BUG>`**
(NOT the original `oracle/setup.sh`, which still yields the drifted `caf3ab12…` base) with
the original **`oracle/grade.sh ARMDIR WITNESS_LOG oracle/hidden_<BUG>.py`**. With that
invocation, the base OIDs, tree hygiene and probe results above hold. Original failed
evidence must remain on record (it does).

*Reviewed: repair-release.json, repair-claim.json, repair/setup.sh, repair/base-reproduction.txt,
repair/probe-summary.txt, repair/probes/*, original claim/fixtures/oracle; independent
relocated-copy setup reproduction.*
