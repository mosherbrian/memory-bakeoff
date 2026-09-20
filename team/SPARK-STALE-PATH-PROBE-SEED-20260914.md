# muse-drafter: stale-path probe — seed item draft (spark pulse 2026-09-14)

**Design draft only — synthetic items, no run, no number, $0.** Follows
`SPARK-STALE-PATH-PROBE-DESIGN-20260914.md` (card-7 next-step 2). These are
hand-drafted candidates for the closed-pool probe, not a corpus; all values are
fictional, no personal/work content. Owners/disposition are a conductor call.

**Grading key (closed pool, per item):** `current` (answers with the operative
value/premise) / `superseded` (answers with the retired one) / `fail` (neither).
Report **current-state accuracy** and **stale-use rate**; a `superseded` answer
is a stale-use, never partial credit.

## Family A — stale path

| # | Seed (true at t1) | Supersession (t2) | Probe query | Tempting distractor | Key |
|---|---|---|---|---|---|
| A1 | ship via `deploy/ship.sh` | renamed `deploy/release.sh` | "How do we ship the service?" | `deploy/ship.sh` present in a runbook snippet | `release.sh` / `ship.sh` / fail |
| A2 | build with `make -j8 release` | moved to `ninja release` | "Build command for a clean checkout?" | `make -j8 release` in an old CI comment | `ninja` / `make` / fail |
| A3 | service listens on `:8080` | moved to `:8443` | "Which port does the API serve on now?" | `:8080` in a stale config dump | `8443` / `8080` / fail |

A2 doubles as the **near-miss control**: the distractor shares the token
`release` with the current command but must not fire — score via Corvid's
binding-reachability check (`check_invocation_corpus_reachability.py`), not a
token overlap.

## Family B — stale premise

| # | Seed premise (true at t1) | Supersession (t2) | Probe query | Wrong-premise lure | Key |
|---|---|---|---|---|---|
| B1 | "the test suite is hermetic/offline" | an external-network test landed | "Can CI run on an air-gapped runner?" | assume hermetic → answer "yes, nothing hits the net" | `no` / `yes` / fail |
| B2 | "prod deploys are manually gated" | CI now auto-gates on green | "What gates a prod deploy now?" | assume manual approval still required | `CI green auto-gate` / `manual` / fail |

B1 is the **premise-awareness shape**: the item is only correct if the model
notices the premise no longer holds; the lure is a plausible, fluent
`superseded` answer.

## Design annotations

- Each item needs an **OFF arm** (no memory) and a **cover-only** arm so a
  stale-use drop is attributable (per the design note).
- Items are **single-fact** by construction; no multi-hop, so `fail` is
  unambiguous.
- All six are **synthetic and generic**; if this ever becomes a corpus, apply
  the invocation-corpus build rules (leak gate, reachability, manifest).

## Limits

Hand-drafted, unreviewed, not run; the values are arbitrary. Second seat: Alice
(item validity) and Corvid (if it becomes a build; near-miss control ownership).

— muse-drafter (Spark)
