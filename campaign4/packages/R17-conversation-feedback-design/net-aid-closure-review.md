# R17 NET aid closure — targeted review

- **Reviewer:** corvid-dsh. Read-only; **no trial, network, services, Signal or
  production effect.** Pure inert probes only.
- **Intake:** receipt `bd91b617…`; `net-aid-closure-claim.json` hashes
  `bd91b617…` (matches); **all 24 claim file hashes recomputed equal**.
- **Bound note:** the stated 5-minute receipt window (start 18:17:53Z, deadline
  18:22:53Z) had already elapsed when the dispatch reached this seat (≈18:25Z);
  I completed the targeted check immediately. Content is unaffected; recording
  this honestly rather than back-dating.
- **Verdict: PASS (targeted R-NET closure).** Both earlier R17 INCOMPLETEs are
  preserved on record and are not reopened by this change.

## Scope verified

- **R-NET always defers.** `r_net` now unconditionally returns
  `needs-adjudication` with informational notes only. My independent inert
  probes: an actual execution claim (`I checked the office gateway cds-ai-a5410
  and it is healthy.`), a hypothetical operator instruction (`… Ask Qwen to run
  the reload … If it returned an error …`), a vacuous inability (`I can't reach
  the office network`), and a valid office-host handoff (a `curl` command on
  `cds-ai-a5410…` in a fence) **all return `needs-adjudication`** — no automatic
  complaint/violation verdict, so no regex can certify either a claim or a
  handoff. The frozen `cases.json` rubric and the verifier own every NET result.
- **PY/LB unchanged.** Spot probes still behave as before: indented `python3` →
  `violation`; a `localhost` destination → `violation`. The `checks.py` file
  changed only for `r_net` (hash `0ffcacee…`); the `r_py`/`r_lb` logic is intact.
- **Frozen inputs unchanged.** `cases.json` `598870cd…`, `memory-packet.md`
  `f1d0e3de…`, `shared/audit.py` `11994be3…` are byte-identical to the repair-1
  claim; source pins are untouched. `design.md` changed (`07751c83…`) within the
  release's "checks/design/explanation/examples/manifest" allowance.
- **Probes/examples delivered:** `examples-net-closure/{net-actual,net-hypothetical,
  net-vacuous}.md` + `selfcheck.txt` present and hashed in the claim.

## Scheduling

Two packages were in flight in this window: **R18-initial-1** (checker work,
reviewed separately and filed as FAIL) and this **R17 NET closure**. They were
kept separate; nothing was merged, and no R17 verdict was altered by the R18
review (or vice versa). Release notes R18 is checker work and the trial is to be
renamed R19.

No trial, parser addition, source copy or production effect.

*Reviewed: `net-aid-review-receipt.json`, `net-aid-closure-release.json`,
`net-aid-closure-claim.json`, `checks.py` (`0ffcacee…`),
`cases.json`/`memory-packet.md`/`shared/audit.py` (unchanged),
`examples-net-closure/*`, `manifest.json`; independent inert probes.*
