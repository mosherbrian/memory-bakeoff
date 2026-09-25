# R7-oracle-1 — independent validity + substance review

- **Reviewer:** corvid-dsh. Read-only; no gate repair, trial, install or author
  edit. R6 terminal/`verification-repair.md` (`67f6d45d…`) treated as input.
- **Worker claim:** `ex-R7-oracle-1-w1.json`; hashes verified equal —
  `feasibility.md` `00f6053d…`, `manifest.json` `e67c20d5…`.
- **Verdict: PASS — a concrete, evidenced FEASIBLE_PREREQUISITE finding, not
  trial readiness.** A later paired pilot still needs a separate release.

## Reproduced exactly (frozen gate, sandbox)

- Honest receipt at the legal location
  (`team/S13-STATEUPD-AUDIT/honest-receipt.md`):
  `check.py --root <sandbox> --receipt team/S13-STATEUPD-AUDIT/honest-receipt.md`
  → **rc 1, 70 findings, every one `CANDIDATE_SECTION`**; byte-identical to
  `evidence/honest-run.out`. **Zero** content findings (`MECHANISM_SOURCE`,
  `FLEET_EVIDENCE`, `UPDATE_MODEL`, `AVAILABILITY`, `LICENCE`, `BITEMPORAL_GRAPH`,
  `PRIOR_*`, `CARD_COVERAGE`, `DESIGN_ONLY` all absent).
- CLI contract: `--selftest` rc 0; `--bogus` rc 1; bare run rc 1 with the same
  70-finding set — matches `evidence/cli-contract.out`.
- **Meaningful content negative** (`no-bitemporal.md`, MemPalace bitemporal
  sentence removed): **exactly one new `BITEMPORAL_GRAPH`** plus the same 70,
  rc 1 — matches `evidence/negatives/no-bitemporal.out`. Content checking is
  live, not merely argument validation.

## Expected failure vs unrelated failures

All 70 residual findings are the documented faulty-discovery defect (filename
stems, headings, technology words: `Application`, `Caveats`, `JavaScript`,
`TEAM RECOMMENDATION`, date-coded stems, …). No unrelated failure remains at
the correct receipt location — the R6 `MECHANISM_SOURCE`/`FLEET_EVIDENCE`
findings are gone because the fixture was corrected, **not** by weakening the
gate (frozen `8c921fbb…`, unedited). The expected current failure (inventory)
is distinguished from the unproven future exit 0.

## Manifest / prerequisites

All **24** manifest entries re-hashed and match (gate copy, honest receipt,
three prior verdicts, three cards sets, run outputs, negatives). Recursively
over the evidence tree, **every distinct non-generated input byte is covered by
a listed hash** (the `negatives/root/**` inputs are byte-duplicates of listed
artifacts; only a generated `__pycache__/*.pyc` is unlisted). Originals
unchanged.

## No fabrication / no self-certification

The receipt is hand-declared to the gate's actual regexes, not produced by the
gate's own discovery; no corrected gate was built to bless its own oracle; no
measurements were invented. R6's errors (illegal receipt location; unrelated
content failures) are retained and answered rather than erased.

## Limits (recorded, not disqualifying)

- **Expected mechanism set is a defensible choice, not unique.** The fixture
  uses 8 hand-justified mechanisms (BASE four + Engram Alpha, mex, Munder
  Difflin, Procedural Graphs) and admits others (Zep, Letta, Supermemory,
  Heimdall) only with an explicit `System:`/`Product:` label. The review's fix
  permits "a heading that is a product name", and Heimdall's card title is a
  product name, so a repair implementing that broader reading could still
  reject this fixture. `feasibility.md` discloses this rule. Tern should treat
  the acceptance set as provisional pending the repair.
- Feasibility only; single seen task; **no memory-efficacy claim**; StreamB/real
  paired-trial prerequisite remains unmet until a repair implements and passes
  this criterion.

*Reviewed: `package.md`, `feasibility.md` (`00f6053d…`), `manifest.json`
(`e67c20d5…`), `evidence/{honest-run.out,cli-contract.out,negatives/*}`,
`evidence/sandbox/**`, R6 `terminal-disposition.json`/`verification-repair.md`,
frozen `team/S13-STATEUPD-AUDIT/check.py` (`8c921fbb…`), `EXTERNAL-*.md` cards.*
