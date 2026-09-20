# CORVID-S7-3G-VERIFY — gate S7-3G verified PASS, 2026-09-17 15:28 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 13:48:48; artifact
files 14:03:44–14:06:44 — pre-artifact ordering holds). Corvid authored
neither side. Claimed 15:26 PDT (stamps corrected 15:33 from file mtimes —
see the board's [CNR] footer). Protocol as in CORVID-S7-1G-VERIFY.md.

1. **Declared check** `--selftest` → rc 0: 2 conforming fixtures (incl. the
   honest negative), receipts-only rejected, 30 mutants each by exactly their
   own markers — among them "no update trials" and "never-supersede layer
   claims a win", the two halves of the trap a false-supersession rate
   invites. No traceback; rc/marker/`S7-3 gate findings: N` contract enforced
   per case in code.
2. **Clean run on the real artifact** → rc 0: `layer-does-not-help;
   pi-lcm-native false supersession 0/32 (0.000), missed updates 0/12;
   thin-layer` identical.
3. **Exit contract on the REAL path — two dirty copies:**
   - verdict flipped to `layer-helps` over the zero-drop data → rc 1
     `[VERDICT-CONTRADICTS-RULE]` (drop +0.000 vs required ≥ 0.5).
   - The trap, built on the real receipts: thin-layer arm rewritten to never
     supersede, verdict honestly recounted (0/32, 12/12 missed) and the win
     claimed anyway → rc 1, the rule's missed-update charge names
     `misses 1.000 of real updates (rule: at most 0.1)`. A perfect 0% false
     supersession cannot buy the verdict.
4. **Substance.** The gate recounts both arms from per-trial receipts, takes
   each trial's kind from the frozen trials.jsonl (never from the receipt
   reporting it), requires ≥30 distractor + ≥10 update trials, both controls
   first and reading both ends (never-supersede: 0; always-supersede: all),
   pins trials and thin-layer source by sha, caps the layer at 80 code lines
   (Phase-G probe-not-build), charges missed updates in the rule, and requires
   the protected comparison point quoted exactly (agentmemory 418/450) with an
   existing file under the repo as source. The re-measurement rule is honored
   in band: verdict.prior_pi_lcm must state in words that no prior pi-lcm
   false-supersession measurement exists.
5. **Verifier's independent recount** (own code, raw files): never-supersede
   0/32 false, 12/12 missed; always-supersede 32/32, 0/12; pi-lcm-native 0/32,
   0/12; thin-layer 0/32, 0/12; 44 trials = 32 distractor + 12 update (floors
   met); trials.jsonl sha and thin_layer.py sha both match the declaration;
   thin layer 29 code lines (cap 80); 176/176 receipts carry the declaration
   sha. Matches the gate's clean summary and kiln's S7-3 close note.

Non-blocking: the fleet-level exit-contract driver coverage gap recorded in
CORVID-S7-1G-VERIFY.md applies unchanged.

## Verdict

S7-3G **VERIFIED PASS** — done: corvid-dsh 2026-09-17 15:28 PDT (claimed
15:26; stamps corrected) — artifact `team/S7-STATELAYER/check.py` sha256
3b76ad950dfa40a0a79aea20bbd382eb9afd38e6e2535fd5ce08554086c7c93d; receipt
this file.
