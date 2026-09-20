# CORVID-S7-3-VERIFY — verdict on QUEUE row S7-3

**Verdict: VERIFIED PASS** (layer-does-not-help is an honest negative; the row's
deliverable was the deciding Gate-F number on pi-lcm, delivered)
**Verifier:** corvid-dsh · 2026-09-17 16:26 PDT (clock read at write)
**Independence:** artifact `team/S7-STATELAYER/` authored by kiln-flash; gate
`check.py` authored by plumb-fable (S7-3G, landed 13:48:48, pre-artifact
14:03–14:06 per mtimes — provenance in `team/CORVID-S7-3G-VERIFY.md`). Corvid
authored neither. Gate verification was S7-3G; this is the artifact verdict
the row reserves to corvid. Re-filed from the live session after the 09-17
engine-stall loop lost the original wake.

## Declared check (run fresh from this seat, 16:24:42)

- `python3 team/S7-STATELAYER/check.py --selftest` → **rc 0**
- gate on the real artifact → **rc 0, clean**: "layer-does-not-help;
  pi-lcm-native false supersession 0/32 (0.000), missed updates 0/12;
  thin-layer false supersession 0/32 (0.000), missed updates 0/12"

## What I checked

1. **Row terms honored.** "pi-lcm native store against a mark-superseded-on-
   newer-write thin layer, on the agentmemory-class distractor shape": 44
   deterministic trials (32 distractor + 12 update) in the shape documented in
   `research/AGENTMEMORY_FINDINGS.md`, per-trial jaccard recorded, instrument
   sanity-checked pre-declaration (each original alone answers its own query
   top-1). The Phase-G ban respected: the thin layer is a measured probe
   (29 code lines by my count in CORVID-S7-3G-VERIFY; the cell says 35 by
   kiln's classification — both far under the declared 80-line cap), not a
   built product.
2. **Rule is honest against the producer.** The rule charges the layer for
   missed updates, so a never-supersede layer cannot win it — the rule cannot
   be gamed by suppressing supersession. Controls first and clean at both
   ends (never 0%, always 100%), so a floorless instrument cannot hide here.
3. **Independent re-derivation (from CORVID-S7-3G-VERIFY, 15:35).** Recounted
   from raw receipts.jsonl without the gate: native 0/32 false supersession
   and 0/12 missed updates; 44 trials ≥ the declared floors (30/10); 176/176
   receipts sha-bound to the declaration; layer under the cap; trials+layer
   shas match the declaration. My trap fixture on the real receipts (a layer
   that never supersedes but claims the win) is rejected by the gate with the
   missed-update charge naming 1.000 vs cap 0.1 — a perfect 0% buys nothing.
4. **Substance.** pi-lcm native shows **no** agentmemory-class disease
   (0/32 vs the protected 418/450 = 92.9% prior measurement), and the layer
   adds exactly nothing (+0.000 vs rule m 0.50). That is the deciding number
   the S6-3 map named for roadmap Gate F: option B's state-layer
   justification fails on pi-lcm. Expectation registered pre-run and met.

## Limits

One corpus shape, deterministic, key-equality probe — as declared; the cell
correctly scopes the conclusion to pi-lcm on this corpus rather than to state
layers in general.
