# kiln (Practitioner) — c70: one rulebook, one preference, named pilot

**kiln · 2026-09-26 · see systems/cc-safety-net.md (+ addendum from primary custom-rule docs). Quoting ROLES: practical fit. Roadmap inputs, principles, COVERAGE as context.**

## Named pilot: project-scoped python-not-python3 rulebook

One rulebook, one rule: block bare `python3` invocations in the project scope with reason directing `python` (sponsor example, direction corrected). Positive cases: `python3 -m pytest`, `python3 script.py` → blocked with reason. Negative cases: `python script.py` allowed; `python3` outside project scope unaffected; unparseable invocations fail open (documented gap, counted not hidden). Pilot checks (proposed, unexecuted): `rule verify` clean, `status`/`doctor` ready (not degraded), explain-trace on one positive, audit log shows denials not outputs, legacy-file check confirms no inert shadow rules. Invalid-config behavior is part of the test: break a copy? No — verify only; degradation visibility via status is asserted from docs, not demonstrated here.

## Why this pilot, fit judgment

Narrowest enforceable preference with fixture-tested schema, additive-only (cannot weaken built-ins), per-project scope via git, existing Claude + Pi adapters (Pi parity unverified — pilot runs Claude first, Pi second only if the first holds). No approval-per-rule (fixtures pre-approve the semantics); no tests-run prerequisite to *recommend*. Residual: uncovered interpreters/flags, fail-open misses, obedience beyond the gate unmeasured. **Medium confidence** in fit; benefit unmeasured.
