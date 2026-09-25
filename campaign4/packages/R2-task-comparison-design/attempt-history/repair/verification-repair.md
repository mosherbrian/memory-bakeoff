# R2-design-repair-1 — independent recheck

- **Verifier:** corvid-dsh (not the author). **Initial verdict preserved** at
  `verification.md` (`a300faf4…`); baseline `review-baseline.md`.
- **Worker claim:** `ex-R2-design-repair-1-w1.json`; hashes verified equal —
  `design.md` `c4b52225…`, `feasibility.tsv` `f4063337…`,
  `corpus-pins.json` `1ca3a636…`.
- **Verdict: INCOMPLETE (outcome failed).** D1 and D3 are fixed and D4's
  substantive contradictions are resolved, but two explicit repair-decision
  requirements remain unmet (D2 hashes; D4 concrete top-k).

## D1 — corpus pinning — **fixed, verified on bytes**

`corpus-pins.json` pins the glob `feedback_*.md`: **21** files, **53,225**
bytes; I recomputed every sha256 against
`/var/home/bmosher/ai-notes/claude-memory` — **21/21 match, set equals the
glob, total exact**. The commit note is correct (`be6cc97` does not pin these
untracked bytes; content hashes are the pin). `design.md` line 14-17 corrected
"79 files" → "21 files, 53,225 bytes".

## D2 — inspect/adopt-or-exclude — **partial**

Paths, reasons and exposure disclosure are present and honest:
`invocation-corpus-v2/v3-standard` excluded (synthetic env-fact/convention
routing; string-presence action match is exactly the presumed-completion to
avoid; `results/` never opened — no prior outcome exposure);
`outcome-pilot-bundle-20260914` excluded (aggregates, no task-level outcomes);
prompt-habit proposal excluded (sponsor-gated). **Residual defect:** D2
required "exact path/**hash**/reason"; no hashes are given for any excluded
artifact. Locally available pins I verified:
`team/invocation-corpus-v{2,3}-standard/manifest.json` `18cfe106…`,
`team/outcome-pilot-bundle-20260914/events.jsonl` `7cd03aa5…`.

## D3 — endpoint/boundary scope — **fixed**

The endpoint is now explicitly a **narrow cued-recall** measure, "necessary but
not sufficient" and "never … proof that the aid improves Brian's work" — not
factual exact-match as useful work. Fresh sessions no longer imply continuity:
the observed transition is recorded (memory-directory sha256 at session end and
next start, plus per-arm artifacts; missing transition ⇒ boundary not observed).
Compaction honestly excluded.

## D4 — null/selection — **partial**

Fixed: null is "no detected difference at n=20", never proof of no benefit, and
retires **only the tested configuration**, never the class; calibration is a
**separate disjoint 6-item set** run once for harness validity only, with no
pool rebuild/retune on its results (control-success selection removed).
**Residual defect:** D4 required "Name concrete top-k/config **or mark missing
prerequisite**." `design.md` says only "top-k fixed before outcome access" — no
concrete value, and it is not recorded as a missing prerequisite. The treatment
configuration is therefore not reproducible as specified.

## Limits

D1/D3 fully resolved. D2 is substantively met (exclusion + no-presumption +
no-exposure) but lacks the required hashes. D4 resolved on the null/calibration
contradictions but not the concrete config. Both residuals are small and
correctable without a new experiment. No author artifacts edited; no run.

*Reviewed: `package.md`, `admission-review.md`, `repair-decision.json`,
`design.md` (`c4b52225…`), `feasibility.tsv` (`f4063337…`), `corpus-pins.json`
(`1ca3a636…`, all 21 hashes recomputed), `verification.md`,
`/var/home/bmosher/ai-notes/claude-memory` (21 `feedback_*.md`).*
