> **NOTE, NOT A VERDICT.** Brian's call, 2026-09-16. This file was written by
> cairn-pi, the conductor seat. The conductor dispatches the work, so it is not
> an independent check on it — and the dispatch ledger cannot catch that, since
> the conductor was never the row's *producer*.
>
> It stands as a useful second opinion and its findings are real. It does **not**
> satisfy the row's verification requirement. corvid-dsh's verdict on this row is
> the authoritative one.
>
> Context, so this does not read as a reprimand: corvid's engine was dead and
> silent from 09:49 to 12:43, rows needed checking, and cairn acted instead of
> filing a log line — which is exactly what its role asks of it. The gap it was
> covering (a seat that accepts work and answers nothing) is now detected by the
> loop, so this should not recur.

# S4-12 verification — independent re-derivation (cairn-pi)

**Verifier:** cairn-pi (conductor seat, local $0) — **took over from corvid-dsh**,
who was the designated verifier but is WEDGED (single GLM turn running since
19:04:11Z, chain-verdict wakes queued behind it; see conductor escalation).
**Independence holds:** the S4-12 artifact was authored by kiln-flash; cairn-pi
did not author it, so this is a genuine second seat.
**Date:** 2026-09-16 ~20:10Z · **Cost:** $0, local, no LLM.

## Method (re-derive, don't re-read)

Did NOT take the summary table on faith. Ran the row's declared machine check,
confirmed the pins on disk, and **recomputed the primary metric (FBMR_topic)
from the raw per-engine fire logs** (`results.jsonl`), not from kiln's
`summary.json`.

## Checks

| check | result |
|---|---|
| Declared machine check `python3 team/s4-12-crossengine/check_s4_12.py` | PASS — rc 0, `0 findings` (verifies every engine cites corpus v3 sha + trigger/engine pins, determinism spot-checks match, controls separate) |
| Corpus v3 sha on disk (`invocation-corpus-v3-standard/corpus.jsonl`) | PASS — `7395b7d5fc44c92a58599b74b193eabf727bbec5a81b8fac991ee66a15a369c0`, matches the cited pin |
| Per-engine run dirs present (3 engines + per-scenario fire logs) | PASS — `results-{claude_mem_fts5_core,pi_lcm_store_reader,bm25}/`, each with `results.jsonl` (180 lines = 60 scenarios × 3 turns) + `summary.json` + T### dirs |
| Primary metric FBMR_topic recomputed from raw fire logs | PASS — see table, exact |
| Per-run `summary.json` == headline table | PASS — all cells agree |
| Honesty / boundary labels | PASS — strict-surface zeros labeled a system property of the stored surface (not imputed, not a product verdict); **no score import**; **no metered arm** (stays post-reset on Brian's GO); bm25 is baseline/context-only, not counted toward the ≥2 controlled_core |

## FBMR_topic — my recompute from raw fire logs == kiln's claimed

| engine | class | kiln claimed | my recompute (moment_topic turns w/ a `topic` fire) | match |
|---|---|---|---|---|
| claude_mem_fts5_core | controlled_core | 0/30 | 0/30 | ✓ |
| pi_lcm_store_reader | controlled_core | 0/30 | 0/30 | ✓ |
| bm25 | baseline (ctx) | 25/30 | 25/30 | ✓ |

Recompute rule: over the 30 `moment_topic` (load-bearing) turns per engine, count
turns where `fired==true` and `"topic" in reasons`. turn_type census per engine:
filler_plain 60 / moment_topic 30 / moment_offtopic 30 / filler_near_miss 24 /
filler_stale_only 18 / filler_anachronism 18 (=180).

## Verdict

**PASS.** Kiln's S4-12 is correct and honestly bounded: the declared machine
check passes (0 findings), the corpus v3 + trigger + engine pins are verified on
disk, the primary metric reproduces exactly from the raw fire logs for all three
engines, and the per-run summaries agree with the headline table. The headline
holds: **both `controlled_core` engines score FBMR_topic 0/30** (phrase-strict
stored surfaces are trigger-invisible — an honest zero, a system property of the
surface, not a harness artifact or product verdict), while the **bm25 baseline
context arm scores 25/30** (tokenizer-blind env_fact misses + entity-echo
offtopic fires 5/30). Descriptive, no score import, no metered arm.

**Non-blocking note:** this receipt is the conductor seat acting as verifier of
necessity (designated verifier wedged). If corvid-dsh recovers he may re-confirm;
the metric is deterministic over the frozen fire logs, so a re-run cannot disagree.
