# Muse ideation batch 6 — declared maintenance lists in an evidence-integrity suite

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Authorization:** fleet-poller R&D pulse 2026-09-13 (standing Muse cadence,
`team/RD-THREADS.md` Corvid thread; original approval Brian via GiLMore
2026-09-12, `scripts/experiment_20260912_muse_ideation/PROTOCOL.md`).
**Trigger:** the suite now leans on four hand-maintained declared lists — the
lifecycle index's `skip:`/`log:` entries, the meta-guard's covered set, the
cross-copy shared-file list, and the superseded-id index — and this pulse alone
required two manual `skip:` additions (Assay's rev-4 note and the gate card),
one of which would otherwise have flagged the suite's own operational doc.
**Cost:** one batched call; meter `openrouter` `$0.00 → $0.01 today` read on the
wire (spent $7.0587 → unchanged; the `spent` line lags whole-cent updates). No
block signals. Latency 20.9 s, 2,216 chars.
**Receipts:** `implementer/repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/receipts/batch6-*`
(summary `181b116e…`, history `4a590dae…`, stream `527ae3ce…`, state `5612f2f0…`,
pty `1997ae8d…`); prompt `PROMPT6.txt` sha
`8c17bb50e847565f681af4ec5dc8eb64064dcee39275658d12f61202cd9f6731`, recorded
before sending.

**Plain English (for Brian):** the guard suite increasingly depends on lists
that a person has to keep up to date. I asked an outside ideation model how
those lists fail at scale. It named five: an exemption list that grows until the
check has nothing left to check; entries that point at files that were renamed
or deleted; the incentive to exempt a new violation rather than fix it; a
required-controls list that drifts from the actual checkers; and shared-file /
superseded-id lists that miss a new copy or a new supersession. Four are worth a
bounded probe; one is already what the meta-guard does. Nothing here is a finding
until a probe produces a receipt.

## Prompt (verbatim, preregistered)

See `PROMPT6.txt` (sha above). Public methodology only; no project-specific
detail. It describes the general shape of the problem — declared allowlists,
required-control sets, canonical shared-file lists, superseded-identifier lists
— and asks for failure modes plus minimal self-checks, deliberately including a
vacuously-passing check, a list that drifts from its artifact, and a perverse
incentive to grow the list.

## Muse output (verbatim)

1. **Vacuous exemption — the check that excuses itself:** the mechanism-documentation allowlist grows until it covers every file the check would otherwise flag, so the check scans zero non-exempt files and reports "pass." Self-check: assert `non-exempt scanned count > 0` and report `exempt fraction`; fail if the denominator is zero or the fraction exceeds a cap.

2. **Ghost exemption — drift from the artifact it names:** an allowlisted path is renamed, deleted, or repurposed so the entry points at nothing — or at a file that is no longer mechanism documentation — while its replacement copy evades the check. Self-check: every entry must resolve to an existing file bearing a live marker (e.g. required header) or the suite fails with an orphan list.

3. **Exemption-as-fix — incentive to grow the list:** adding one line to the allowlist is cheaper than fixing the underlying defect, so maintainers appease the check by exempting each new violation and the list grows monotonically. Self-check: each entry requires an expiry date plus owning issue, the suite fails on expired entries, and fails if the list grows for N consecutive runs without a fix-linked removal.

4. **Paper controls — required-control set drifts from checkers:** the declared "controls every checker must have" goes stale when a new checker ships without implementing a listed control, or a control is retired but stays required, producing silent gaps or false failures. Self-check: cross-join the list against the checker registry — fail on any required control implemented by zero checkers and any checker advertising an unlisted control.

5. **Forked canonical / stale supersession — shared-file and old-ID lists drift:** the canonical-shared-file list misses a new copy location so diverged copies go uncompared, and the superseded-identifier list misses alias spellings or new supersessions so old forms are cited as current and never caught. Self-check: auto-discover copies by name/hash rather than trusting the list and fail on any unlisted copy or hash divergence; plant one canary citation of each listed old form per run and fail if the check does not flag it, plus generate candidates from history to flag unlisted old forms.

## Disposition (one per item; `ACCEPT` names a bounded probe)

1. **ACCEPT.** Probe: a declared-list guard must fail when it scanned **zero
   non-exempt inputs** and must report the exempt fraction (new coverage class
   **U6**, "vacuous pass on an empty denominator"). Bounded: add the assertion to
   `check_identifier_lifecycle.py` and one self-test case (index + only-skipped
   files → rc 1), then re-run the live census.
2. **ACCEPT.** Probe: extend the lifecycle index lint to flag a `skip:`/`log:`
   entry that matches **no scanned file** (this already bit us — `skip:
   IDENTIFIER-LIFECYCLE.txt` was inert until removed). New coverage class
   **U7**, "inert declared-list entry". Bounded: one function + a self-test case.
3. **ACCEPT (merged with 2).** Probe: each `skip:`/`log:` entry must carry its
   reason/source in the index (already partly true) and an inert entry fails;
   report the entry count so growth is visible. The expiry/owning-issue half is
   process, not a static check — recorded, not implemented.
4. **DUPLICATE.** The required-controls set is exactly the meta-guard's
   `_COVERED_NAMES` completeness check shipped 2026-09-13 (`6cd289e7…`), which
   already compares live `check_*.py` against the covered set **both ways**. The
   one un-covered sub-case — a control whose fixture no longer exercises the
   guard — is not statically checkable from the list alone; it is the meta-guard's
   own dirty-fixture marker contract.
5. **ACCEPT (split).** (a) auto-discover shared copies rather than trusting
   `REPO-CANONICAL.txt`'s `shared:` list — new coverage class **U8**, "undeclared
   shared copy" (the same completeness gap guard 15 rev 2 closed for the map).
   (b) index completeness: derive superseded ids from the ledger's `SUPERSEDED`
   markers and fail if one is absent from the index — new coverage class **U9**,
   "index misses a recorded supersession" (`L-HS-02` completes the current
   index, so a probe would be green today and guard the next move). **Alice's
   second seat binds the parse:** the ledger's `supersed` surface is 6 lines but
   only 1 is an id move (L793); the other 5 are a class label (L794/L860), a
   prose back-reference (L821), a table header (L853) and a process note (L945),
   so a word-based probe would raise 5 false "missing supersessions" — parse
   only the `**SUPERSEDED — see … : <ids>` id-mapping marker. (c) the per-run
   canary citation is **DUPLICATE** — the lifecycle guard's `--self-test` already
   plants `L-HS-02` canaries (the superseded id) through the real scan path.
   **Alice's caveat, folded:** that canaries the *detection logic*, not a per-run
   canary on the **live corpus** as Muse literally proposed; the live 0-uncued
   census plus the self-test is the substitute, so "DUPLICATE" holds for logic
   but is not doing quite the same work as the proposal.

**Net:** 4 ACCEPT (2 and 3 share one probe; 5 splits into U8/U9) / 1 DUPLICATE.
None is a finding; each ACCEPT needs a run before it counts.

## Handoff

- **Corvid:** U6 + U7 are one bounded probe on the lifecycle guard/index
  (assert non-empty non-exempt scan; flag inert entries). U8 is a cross-copy
  discovery probe. U9 is a ledger→index completeness probe.

- **Coverage map:** add U6–U9 as candidate classes (not guards) so the next
  slice is chosen from the list; the map's own `check_map_hashes.py` already
  demonstrates the discovery pattern for U8.
- **Assay/Alice:** second-seat this note (is any ACCEPT already covered? is the
  DUPLICATE correct?) before any probe is built. **Alice ran it**
  (`team/ALICE-MUSE6-SECONDCHECK.md`): all four ACCEPTs genuinely uncovered, the
  item-4 DUPLICATE correct, one wording caveat folded above; she names U6's
  precedent (`check_map_hashes.py` already fails on an empty map) and binds U9's
  parse. Probes remain Corvid's.

## Postscript (2026-09-13) — all four ACCEPTs built

All four ACCEPTs are **no longer hypotheses**:
`check_identifier_lifecycle.py` **rev 5** (`1ca1c87c…`) prints `vacuous scan`
(zero non-exempt files; never `--advisory`-suppressed) and `inert declared-list
entry: <name>`, both exiting 1, with a real-CLI self-test for the pair; **rev 6**
(`45922e91…`) adds the optional `--ledger` cross-check for **U9** (a ledger
`SUPERSEDED` table row absent from the index fails). **U8** lands in the
cross-copy guard **rev 5** (`f8bd89a9…`): the tree set comes from the
declaration's `tree:` lines and every `implementer/repo*` checkout is discovered
(`undeclared tree:` / `declared tree missing:`), and **any** declaration with no
`tree:` lines — shared-only or comment-only — is a `no declared tree set`
instrument failure (Alice's two second-seat findings; Assay's v1+v2 patches) so
the discovery layer cannot go vacuous. Live censuses: lifecycle 31 citations / 0
uncued; cross-copy 2 known drifts / 0 tree gaps. Coverage map
**rev 12–16** close U6/U7/U9/U8; only **U3** (record-text identity, needs artifact
changes) remains. See `team/CORVID-IDENTIFIER-LIFECYCLE-GUARD.md` Revs 7–8 and
`team/CORVID-U5-CANONICAL-DRIFT-GUARD.md` Revs 3–5.

— **Corvid** (`worker-glm-dsh3`). Muse proposes, Corvid disposes; nothing here is
evidence. $0.01, one batched call.
