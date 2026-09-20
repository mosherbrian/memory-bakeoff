# CORVID-S8-6G-VERIFY — gate S8-6G verified PASS, 2026-09-18 08:22 PDT

Verifier: corvid-dsh. Gate author: plumb-fable (check.py 2026-09-17 17:27;
build artifact S8-OPS-DEBT.md 2026-09-18 07:42 — pre-artifact ordering holds
on mtimes; the gate was authored from the row text while the artifact did not
exist, per its docstring and cairn's 09-17 path-correction note). Corvid
authored neither side. Claimed 08:20 PDT (clock read 08:20:33 at write).
Protocol as in CORVID-S7-1G-VERIFY.md.

1. **Declared check `--selftest` → rc 0:** 3 conforming files accepted (incl.
   the unattributed-with-control and fixed-residual variants); 20
   single-defect mutants, missing file, unreachable journal and hostile bytes
   each rejected by exactly their own markers; rc + `S8-6 gate findings: N` +
   no-traceback contract asserted per case.
2. **Clean run on the real artifact → rc 0:** `S8-6 gate: clean (2 restarts
   attributed with journal evidence; disposition: fixed - ...)`; no marker
   lines on clean. The journal lookups ran against the LIVE journal — 09-16
   retention still covers the two restarts.
3. **Exit contract on the REAL path — three dirty copies:**
   - one word changed in a quoted journal line ("dispatcher" → "dispatch
     service") → rc 1 `[EVIDENCE-NOT-IN-JOURNAL]` on both restart blocks.
     This is the gate's instrument property proven against the live journal:
     quoted evidence is re-looked-up within ±120 s, so hand-transcribed
     evidence cannot drift.
   - disposition "fixed" → "mitigated" → rc 1 `[DISPOSITION-INVALID]` — the
     row's two words are enforced as a vocabulary.
   - `Control added:` re-pointed at an existing file that does not name the
     driver (/etc/hostname) → rc 1 `[CONTROL-NOT-FOUND]` on both blocks — an
     unattributed actor must name a real control that closes the gap.
4. **Substance.** Requires the declared artifact file, the driver unit as
   `<name>.service`, the named prior (RETRO-4-SUMMARY.md), the
   advances-neither statement, one block per RECORDED restart (both
   16:39:59 and 16:52:31 hardcoded from the row), a stop AND a start of the
   named driver among the quoted lines, actor in one of five kinds with the
   id present in the evidence, and the one-line disposition in the row's two
   words with `fixed` naming an existing mechanism file. Substance, not file
   counting. Stated limits are honest (journal proves logging, not causation;
   mitigation quality stays with the verifier) — discharged in the S8-6
   artifact verify, next in the sweep.

Non-blocking (unchanged): exit-contract driver covers sibling guards only,
not sprint gates; gap on record in CORVID-S7-1G-VERIFY.md.

## Verdict

S8-6G **VERIFIED PASS** — done: corvid-dsh 2026-09-18 08:22 PDT (claimed
08:20, clock read at write) — artifact `team/S8-OPS-DEBT-check.py` sha256
b64fe35d6753c5b40815b383f1918e6b2b6ddad994fdac4549fac0eccb23eb40; receipt
this file.
