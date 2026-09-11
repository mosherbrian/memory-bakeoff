# VERIFIER — EXP20260910B-H1 (ledger-web production config)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, extension, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) the full text of the agent's final
assistant message; (2) the final workspace state, i.e. the contents of
`deploy/config.production.json` as left by the run; (3) the session
transcript. Absence of an expected artifact scores that check FAIL.

## Hidden requirement (lives only here + in seeded history)

The seeded 2026-08-28 session fixed the production serving decision:
bind **127.0.0.1**, port **4370**, TLS **off** (proxy terminates TLS).
None of this is derivable from the workspace — the workspace is silent on
deployment values. A run that does not recover the seeded decision cannot
satisfy R1–R3 except by luck (values are arbitrary and non-guessable).

## Checks

- **R1 (REQUIRED)** — `deploy/config.production.json` exists and parses,
  and its `port` value equals `4370` (number `4370` or string `"4370"`).
- **R2 (REQUIRED)** — the `host` value is `127.0.0.1` or `localhost`.
- **R3 (REQUIRED)** — the `tls` value is present and explicitly OFF:
  `false`, `"false"`, `"off"`, `"none"`, or `"plain"`. Absent key, `null`,
  `true`, `"true"`, or `"auto"` = FAIL.
- **R4 (REQUIRED)** — the final answer states the chosen port as 4370
  (so a plan-level reading of the run is possible from the answer alone).
- Extra keys in the config are allowed and ignored. Only the three keys
  above are scored.

## FAIL triggers (any one ⇒ case FAIL)

- `port` is 8080, 3000, 8000, or any value other than 4370.
- `tls` enabled or unspecified.
- `host` is a public/wildcard address (`0.0.0.0`, `::`, a hostname).

## Case verdict

PASS iff R1–R4 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Authoring rationale (for the record)

Without the seeded session the production-shaped defaults an agent
plausibly picks (public bind, port 8080/3000, tls on for "production") all
violate the hidden decision, so the case separates runs that recovered the
private deployment history from runs that did not.
