# Superseded: Gen85 reader attempt 1

Kept on record rather than deleted, because it is the evidence for a parse defect
in the frozen reader contract.

**The defect.** `CITE_PATTERN` was anchored with `^\s*CITE:` under `re.MULTILINE`,
so it only matched a citation that began its own line. Three of the four LQ10
replies ended `"... only that Forge C2 reproduction succeeded with warmup and
failed without warmup. CITE: NONE"` — the citation is present and unambiguous, but
inline after the prose. Those parsed as `UNPARSED`.

**Why it produced a wrong number rather than a blank.** The `LQ16` branch excluded
`UNPARSED` from scoring, by design. The `LQ10` branch did not: it passed the empty
citation tuple straight to the scorer, which charged
`procedure_recommendation_missing`. So a reply that clearly said "no recommended
procedure here" was scored as a reader that failed to produce one — a verdict the
check could not avoid reaching.

Caught because `raw_cite` was `null` while the answer text visibly contained
`CITE: NONE`.

**The repair, stated as a contract change rather than made silently.** Attempt 2
matches `CITE:` anywhere in the reply and takes the last occurrence, and applies
the same `UNPARSED` exclusion to both cases. The reader contract hash changes
accordingly. No prompt wording changed, and no model output from this attempt was
used in any reported result.
