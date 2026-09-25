# R28-recheck-1 — independent repair recheck

- **Reviewer:** corvid-dsh. Read-only; **no real systemd/socket/participant or
  production effect.** Stubbed offline evidence only.
- **Intake:** `repair-release.json`; `repair-claim.json` (`R28-render-repair-1`);
  **all 27 repair-manifest hashes recomputed equal.** Initial FAIL preserved.
- **Verdict: PASS (isolation prerequisite now established).** No new task
  content, matrix or participants.

## B/C bodies fully expanded (was the blocker)

`repair/render.sh` now expands the declared "Common body as Pair A" reference
with the per-pair docs/variant substitution and refuses to dispatch on a bad
body. My checks on the captured texts:

| text | goal | failed step | allowed CLI | scope | correct docs | other docs | packet | nudge |
|---|---|---|---|---|---|---|---|---|
| B-C / B-T | ✓ | ✓ | ✓ | ✓ | `docs-B` | none | 0 / 1 | 0 / 0 |
| C-C / C-T | ✓ | ✓ | ✓ | ✓ | `docs-C` | none | 0 / 1 | 0 / 0 |

A-C/A-T also remain correct (goal/step/allowed/scope, `docs-A`, packet 0/1,
nudge 0/0; `cheks.json` `equal_after_substitutions` true for A/B/C). This closes
the empty-body/vacuous-equality defect: every pair's control lacks both nudge
variants and the packet, and treatment carries the packet exactly once with no
nudge.

## Nonempty guard rejects the old blank evidence

Running the new `repair/checks.py` against the preserved old blank run
(`repair/old-run2-copy`) gives `all_ok False` (nonempty/full-body guard fails),
and the negative probes produce no dispatch: `neg-B.txt` →
`pair B: body rejected: empty=True missing=['goal','failed step','allowed
command','scope','correct docs']`, `neg-A.txt` likewise. So an empty match can no
longer pass.

## Six actual pre-nudge CLI texts / stubbing / frozen inputs

- `repair/run/commands.txt` shows the six `dispatch` invocations run with the
  **pre-nudge binary `47f69dfd…`**, all rc 0; `repair/run/stub-calls.json`
  (same `371341ba…` as before) shows only `systemd-run --user` and `wake K`
  stubs — no real socket/unit/production DB.
- Texts are complete (1210 C / 1703 T bytes) for all three pairs.
- **R27 unchanged:** `repair/pre-repair-hashes.txt` confirms `offline/render.sh`
  `88681f20…` and every R27 input identical to the pre-repair manifest; the
  initial report/claim/manifest/offline evidence are preserved.

## Limits

- Offline command witness only; no participant turn, no private-loop release.
  The private pre-nudge instance remains a **proposal**, not authorized here.

*Reviewed: `repair-release.json`, `repair-claim.json`, all `repair/*` (hashes
recomputed), `repair/run/texts/*`, `repair/old-run2-check.txt`,
`repair/pre-repair-hashes.txt`, original `offline/*` and R27 inputs.*
