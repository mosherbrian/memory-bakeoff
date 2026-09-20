# S3-9 verification receipt — 10/20 inactivity timers, row-ID matcher, sprint cadence + Signal

**Row:** QUEUE S3-9 · **Owner/verifier-of-record:** Alice (aletheia-dsh) · **Second seat (checks this receipt):** Verity
**Date:** 2026-09-15 · **Cost:** $0, local, read-only except the poller fixture harness · **No LLM in any decision path tested.**

Method: hermetic harness (stub `agent-deck` + stub `wake`, fixture QUEUE/HIST, env-overridden
`POLLER_DIR/HIST/QUEUE/INACT/WAKE`) driving the live `workers/fleet-poller.sh`; plus
static review and direct awk runs. `bash -n` clean.

## Per-item result

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | 10/20 inactivity timers fire deterministically | **PASS** (with one caveat) | 10min unclaimed → exactly one nudge, `fired=1`, no re-fire; 20min claimed-dark → owner **and** Ledger woken, `fired=1`; status-text edit restarts the clock; `done:`/`gated:` clear state; unresolvable eligible (`TBD`) logs + marks. |
| 2 | Sprint-style row IDs match (matcher regression) | **PASS** | The ID-AGNOSTIC pattern `/^\| *[A-Za-z0-9][A-Za-z0-9._-]* *\|/` matches both `\| 5 \|` and `\| S3-9 \|` (lines 3, 4 of a mixed fixture) and does NOT match `\|---\|`; §8's parser (`$(NF-1)`) extracts both rows. This closes the "43 of 51 rows matched / 7 S3-* blind" regression. |
| 3 | Sprint open/close rules proven by test (no LLM) | **FAIL — not implemented** | No sprint open/close mechanism exists in code: `fleet-poller.sh` has no sprint/close/stand-down/auto-start path; no new script or systemd unit implements it. Only the *plan* exists (`SPRINT-OPS-PROPOSAL.md` §26, Brian's 0–5). Nothing to test → cannot PASS. |
| 4 | Signal escalation path proven by test (no LLM) | **FAIL — not implemented** | No Signal escalation implementation or test found. `server.py`'s `signal` hits are unrelated readiness/turn-boundary prose; no `signal-cli`/channel send is wired into any decision path. Nothing to test → cannot PASS. |

**Overall: 2 PASS / 2 NOT IMPLEMENTED.** The 10/20 timers and the row-ID matcher are verified. The
sprint cadence and its Signal escalation are not implemented, so S3-9's items 3–4 cannot be
certified; recommend implementing them (or splitting S3-9 into the two verifiable items that ARE done).

## Caveats carried (do not affect the PASS verdicts, but the owner should see them)

1. **Posted-reason reset is over-broad** — the 10/20 timer's "one posted reason resets with
   justification" branch resets a claimed row's clock when the owner's name appears ANYWHERE in the
   last 60 BOARD lines AND any of {reason, because, blocked, waiting, justif, hold, pause} appears
   ANYWHERE in those lines. Observed live: it reset Corvid's 20min clock on unrelated BOARD text
   (tail-60: "corvid" 19×, reason-words 13×). Consequence: the 20min timer is effectively suppressed
   for active seats. Fix proposed to the builder: require the owner AND a reason word on the SAME
   line, and add a `POLLER_BOARD` override (BOARD is currently hardcoded, so this branch is not
   hermetically testable).
2. **Eligible-name resolution is a bidirectional substring match** on registry titles (first hit
   wins). Aliases: `alice→aletheia` handled; `GiLMore`/`TBD`/`rotating` resolve to "" and are logged
   (`no eligible seat resolves`). Fragile if one title is a substring of another — an explicit
   alias/base-match table would be safer. (Owner-dark = history mtime, unknown counts as dark — noted,
   acceptable.)
3. **`BOARD` hardcoded** (no `${POLLER_BOARD:-…}`), unlike DIR/HIST/QUEUE/INACT — limits hermetic
   coverage of the claimed-reset branch.

Live status: the running poller is the pre-§8 process; these behaviors are on-disk only until the
handoff restart. No live sends were made by this verification (stub wake only) and no vault files
were touched.
