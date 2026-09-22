# P6-r11 — routing-repair verification (error-before-timing + bound manifest)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r11-routing-repair-verify-1` (existing ≤25 m grant)
- **Repair:** `routing-error-propagation-repair.md` @ `ffa3104`; prior INCOMPLETE
  `candidate-review-routing-negatives.md` (`57208e38…`) preserved.
- **Candidate (immutable through this pass):** `case_entry.py`
  `701a383e0f28…` (base `2326e6b8…`), `turn_handoff.py` `2b6aa7ef…` (frozen),
  `harness.py` `d7b4e517…` (frozen), manifest `2e2fa4f5…`.
- **Evidence:** `candidate-review-routing-repair-evidence/` (forged producer,
  runner, negative logs, full-gate log). No candidate edit, no live effect.

## Verdict

**PASS (bounded).** The entrypoint now surfaces the harness authority/routing
error **before** timing/acceptance gates: the two previously-masked negatives
return their original codes (`E_FORGED_ROUTE`, `E_CLAIM_MISMATCH`), never
`E_NO_LATENCY`, never `verified-rejection`/`COMPLETE`/`terminal-rest`, with the
worker handoff preserved and exactly 1+1 sends. Legitimate results pass through
unchanged, the propagation is structured (not specimen-specific), the manifest is
correctly bound, and the full gate is independently green (42/42). Residuals
below are minor and bounded.

## Check 1 — error-before-timing (PASS)

`_raise_for_harness_error` (`case_entry.py:558-569`) raises the harness's own
`error`/`detail` when the result is a dict **without** a `decision` key and with
an `error`; results carrying `decision` pass through. It is invoked at `:1149`
(run-fixture) before the case/timing gates and inside `_rerun_cli`/`_reattach_cli`
(`:1117-1137`). Code inspection confirms a structured predicate, not a hardcoded
label or text match of one specimen.

Independent CLI reproduction with the private forged verifier producer (original
signature-bound worker `seat_emulator.py`; only the verifier claim is malformed):

| negative | rc | surfaced error | verified-rejection | worker commit | sends |
|---|---|---|---|---|---|
| forged route (`route:"attacker"`) | 3 | `E_FORGED_ROUTE: worker field route rejected; routing/authority belong to launcher` | **none** | `handoff-done:p6c-h3w` present | `msg-counter 2` |
| wrong execution (`exv-WRONGEXECUTION`) | 3 | `E_CLAIM_MISMATCH: execution does not match launch manifest` | **none** | present | `msg-counter 2` |

Both: no `verified-rejection:*` key, no verifier turn, no `terminal-rest`/
`COMPLETE`, no duplicate dispatch, no `E_NO_LATENCY`.

**Not specimen-specific:** independent direct probe raised `E_BIND_CARRY` for an
unrelated harness failure and passed through `verified-rejection` /
`transition-committed` decision results untouched.

## Check 2 — passthrough retained (PASS)

- FV-W and FV-WV: rc0 `accept-open`, `verified-rejection` with `expected
  46409ea6…` / `observed 9809428b…`, sends 1+1.
- QR-W: rc0 `timecheck accept`, `duplicate-end-ignored`/`terminal-rest`, 1+1.
- Focused tests: `test_r11_routing_repair.py` + `test_r11_rejection_newpass.py`
  → **8 passed**.

## Check 3 — bound manifest (PASS)

`candidate/composition-manifest.json`: 34 entries; **no self-entry**; every
listed path exists with matching recomputed sha256; `bound_from
completion-claims/ex-p6r11-routing-repair-1.json`; `baseline 05eba448`;
`changed` = `case_entry.py`, `tests/test_r11_routing_repair.py`, `changes.md`.
`turn_handoff.py`/`harness.py` unchanged from the frozen lineage; R3_REVISION
unchanged (`81d6fe17…`). No metadata shortcut or self-hash.

## Check 4 — full gate (PASS)

`PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider`
→ **42 passed in 839.51 s** (38 retained + 4 new routing tests), independently
run on the final entrypoint; no skips, no cache provider.

## Bounded residuals

- `E_NO_LATENCY` remains the honest outcome for a legitimate (decision-bearing)
  harness result that lacks timing rows — preserved by construction, but not
  independently triggered here (hard to force without a harness failure).
- Expiry/outer-stop/replay checks were verified in the prior closeout
  (`687a811f…`) and not re-run in this pass; full gate covers the retained suite.
- Lost-completion and queued/ambiguous controls remain out of scope.

## Effect

One bounded verdict: **PASS** — routing errors propagate before timing, both
supplied negatives are un-masked, legitimate rejection/success and the manifest
are intact, and the full gate is independently green. Returned to Tern.
