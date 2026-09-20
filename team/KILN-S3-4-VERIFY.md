# Kiln — verification of row S3-4 (exposed-span rater seating + round-2 verdicts)

**Verdict: PASS** — the row's deliverables exist, the counts are exact, the
id sets reconcile to the frozen bundle, and the exposure disclosure is
present as the PO narrowing required — with the evidentiary class stated
explicitly (see the caveat). Verified 2026-09-16 12:55 PDT, $0, reads only.
Verifier re-point: cairn (Verity parked per the 2026-09-15 furlough roster);
I authored neither the row (GiLMore) nor its artifacts (Corvid prepared the
package; conductor-claude judged it) — independence holds.

## What was verified

**1. The round-2 verdict file's counts are exact.**
`team/BLIND-VERDICTS-round2-conductor-claude.md`: Task A (standard-tier
reachability labels) = **60 rows, 60 AGREE, 0 DISAGREE** (the one "DISAGREE"
string in the file is the column header's "basis (only if DISAGREE)"). Task B
(correction-event classifications) = **286 rows, 286 CONSISTENT, 0
INCONSISTENT** (likewise, the one "INCONSISTENT" string is the header). The
done cell's "60/60 AGREE + 286/286 CONSISTENT" reproduces exactly.

**2. Task B judged exactly the frozen bundle's events.** The 286 `RC2-`
item ids in the verdict file are **set-equal** to the 286 unique
`event_id` prefixes of `team/outcome-bundle-scale-20260915/events.jsonl`
(sorted-set comparison, programmatic). The blind round-2 classification check
and the Cairn-verified outcome bundle are the same 286 events.

**3. Seating with disclosure exists, in the distributed form the PO chose.**
The PO narrowed S3-4 (BOARD 2026-09-15: "no unexposed rater exists — seat
best-available with the exposed span documented, do not block"). The
disclosure chain on disk:
- `CORVID-BLIND-QUORUM-REGISTER.md` — the published exposure roster
  (`saw-output` flags with per-rater basis: Corvid, Assay, Verity), the
  census conclusion "**Count of eligible blind raters on the metered lane:
  0**", and the governing rule that any rating produced under exposure "is an
  exposed rating and must be reported as such."
- Row 37 (`VERITY-S4-B6-ENCOUNTER-LOG.md`): Verity's own exposure log and
  recusal.
- The seated rater is named in its artifacts: `BLIND-PACKAGE.md` /
  `BLIND-PACKAGE-20260915.md` ("For: conductor-claude") and both verdict
  files. `team/RATER-HANDOFF.md` carries the seal rules the rater operated
  under.
- Package controls: round-2 package sealed and leak-scanned before seating
  (Corvid 2026-09-15: `probe_blind_package_scan.py` → 0 findings) plus
  `BLIND-PACKAGE-FIDELITY.md` (item-fidelity control: only verdict fields
  removed from sources, nothing altered).

**4. Provenance chain of the verdicts.** Round 1 (2026-09-14,
`BLIND-VERDICTS-conductor-claude.md`: 36/36 AGREE Task A; 8/10 Task B with 2
real INCONSISTENT findings — the `env_fact_kind` miner defect, since fixed in
the bundle that round 2 judged) was received and posted by cairn from the
conductor lane. Round 2 followed the same lane after the package was sealed.
The two rounds are consistent with each other: round 1 found the real defect,
the bundle was corrected, round 2 re-judged the corrected set clean.

## Caveat (stated, not blocking)

**These are disclosed-rater verdicts, not blind ones — by design.** The
seated rater is a fleet seat whose prior context included team material, the
quorum register had already ruled the metered-lane blind quorum failed, and
the PO's narrowing accepted an exposed rater so evaluation would not block.
Per the register's own rule, the 60/60 and 286/286 results must be cited as
**disclosed-rater agreement**, never as independent blind confirmation. The
all-agree pattern is also the expected shape for criteria the team itself
wrote (the rater judges consistency with the team's definitions, not the
truth of the definitions). Neither point reduces the row to FAIL — the row's
own scope, post-narrowing, is exactly this — but any future citation of
"60/60 AGREE" outside the fleet must carry the disclosed-rater qualifier.

Minor note: conductor-claude has no B6-style encounter log of its own; its
exposure is structural (fleet-conductor role, team-file context re-seed) and
is documented via the PO call and the quorum register rather than a
first-party log. Recording that here so the next quorum census includes it.

— **kiln-flash**, 2026-09-16 12:55 PDT. PASS on S3-4, with the
disclosed-rater classification carried on the record.
