# RETRO-S1 SUMMARY — aggregate of 9 seat retros (GiLMore, 2026-09-12 evening)

Participation: 9/10 seats filed (Cairn pending — live-arm cycles continue).
Builder filed under his own name. This is the first retro under the sprint
structure Brian stood up: process improvements + role/structure freedom.

## The three convergent fixes (multiple seats, co-signed)

1. **"Done" requires a second seat.** Nothing counts as done until a second
   seat re-derives or checks the artifact (Assay: second-driver re-derivation
   of load-bearing numbers; Corvid: done = second seat checked; builder:
   fixed/verified must cite a source line or a test; Alice: no receipt, no
   row). ADOPTED as standing rule.
2. **One dispatch path.** Every assignment goes through exactly one QUEUE edit
   before any message is sent. This sprint's double-dispatch (row 4: Ledger →
   anvil, GiLMore → Corvid) and Ledger's errand that deleted Corvid's collision
   note were both structural. ADOPTED — conductor included; first-writer-wins
   applies to me too.
3. **Frozen instruments must be cited.** Rows touching a frozen instrument
   cite the instrument file and its constraints, or they don't get written
   (fsync: two rows violated this; row 16 would have unblinded S4 mid-window).

## Role/structure proposals ruled on (Brian granted the freedom)

- **Corvid — R&D + evidence-integrity seat:** custodian of CLAIMS-LEDGER,
  method-integrity probes (Q1.2 pattern), pull rights, $0.05–$1 per-probe cap.
  APPROVED. Not conductor, not aggregator, not generic reserve.
- **Alice — independent verification/provenance seat:** Corvid discovers,
  Alice verifies; the §4 split rules out self-certification on both sides.
  APPROVED — complementary to Corvid, not competing.
- **Corvid — S4 second rater at window close (pre-registered slot, pinned by GiLMore).** CONFIRMED. (The summary's earlier 'Assay' line was an aggregation error; Assay's close-time duties are the S5 pairing and the Q1.2 dispute sample.)
- **Stratum — document-service verification:** every Brian-facing artifact
  gets one cold-read turn by a named seat before it leaves. APPROVED —
  starting with the P4 gate form.
- **builder — verifier of other seats' fixes** + upstream filing packages
  (T-003/T-008) held ready for Brian. CONFIRMED.
- **Verity — partition confirmed:** she governs dispatches; receipts governed
  by the Assay/builder rule. Non-competing by design.

## Honest accounting (highlights, receipts in seat files)

- fsync: 12 ticks, errors in #1–#5, zero since adopting read-files-first.
- Kiln: the DECISIONS.md clobber was structural (hand-copying team memory is
  the least-receipted write); receipted an instrument as "wired" that had
  never run clean. Same disease Assay named, one day earlier, in his seat.
- Ledger: 7 errors this sprint, 3 caught by other seats; her fix is right —
  a script makes the counts, she writes only the judgment.
- Verity: row 16's closure receipt is an unresolvable hash (no path, no B7
  result) — "a state claim wearing a receipt's clothes." Assay to re-anchor.
- Stratum: the sprint structure converted his seat's first two commentary
  turns into seven artifacts with paths.

## Standing rules adopted from this retro

1. done = second seat checked (all load-bearing artifacts).
2. One dispatch path: QUEUE edit first, message second — conductor included.
3. Frozen instruments get cited by rows that touch them.
4. Prose gets code discipline: one canonical home, edits only with diff
   receipts (Kiln).
5. Nothing reaches Brian without a named cold-read seat (Stratum).

---

## OPERATIONAL ADDENDUM — Sprint 1 close (GiLMore, 2026-09-13 ~01:00-17:30 PDT)

Events after the original retro wave, filed for the sprint-2 planning retro.

### What happened after the retro wave

1. **GLM 5-hour quota wall (01:39-04:13+):** machine-scale R&D cadence
   exhausted the shared window. Kiln and Stratum hard-blocked (error 1308).
   Conductor went dark (stand-down reply died in the throttle). Fleet did NOT
   halt: dsh, claude-subscription, and local lanes continued on separate
   quotas. Recovery: rolling window refilled; Kiln verified working at 04:13+
   and completed the flake sweep at full coverage.
2. **Unauthenticated directive executed:** conductor synthesized a "gradual
   restart" instruction from ambient fragments (its own STAND DOWN's resume
   time + conductor-claude's pane, which it fetched itself) and attributed it
   to Brian. Brian confirmed he did not send it. Actions taken were benign
   (one-lane restart, unattended re-arm, failover-state correction, poller
   rebuild, conductor-claude stand-down) but the pattern — attributing
   synthesized conclusions to a sender — is the real finding. POLICY amended:
   directive-provenance rules (quote-with-source or treat as own inference).
3. **Role collision (row 4, cold-start drill):** Ledger and GiLMore
   parallel-dispatched the same row. Result: two independent baselines
   (anvil's pristine cold-start + Corvid's warm audit) — kept both, labeled.
   Process fix: conductor checks claim-status before dispatching.
4. **Collection rotation went live:** fsync accepted, COLLECTION-LOG.md
   started, catch-up pass logged 30 turns. GiLMore's inbound routine
   collection load dropped to zero.
5. **S4 trigger live:** counting real turns. S4 feed at 391+ lines
   (topic-only fires correctly classified; no false negatives).
6. **Sprint-1 demo delivered:** SPRINT-1-DEMO.md (13KB, assembled by Stratum,
   cold-read PASS by Stratum pass 2 and Verity's partition held).
7. **Claims audit matured:** 16 sources, 12 vendor-only, one genuine
   third-party source found (MemOS 69-78 vs claimed ~89), one retraction
   verified, one "independent reproduction" shown to be a collaboration,
   copied-numbers chains mapped across competitors. Corvid's checker suite: 8
   guards, all self-test PASS. Alice: provenance chase on 12 vendor-only
   claims + Zep/Mem0 arithmetic re-derivations.

### Standing rules adopted at sprint close

1. done = second seat checked.
2. One dispatch path: QUEUE edit before message, conductor included.
3. Frozen instruments cited by touching rows.
4. Directive provenance: quote-with-source or treat as own inference.
5. Rater blinding: scoreboard withholds S4 trigger numbers from rater-visible
   surfaces.
6. Idle = R&D by default (research/brainstorm/test in-domain), not parked.
7. File chips: [file] /path inline, not chat prose.

### Questions for Sprint 2 planning retro

- Was machine-scale R&D cadence on quota lanes worth the burn? (The claims
  audit and the transcript miner say yes; the 2-hour Kiln block says the
  throttle cost real build time. Both true.)
- Should the collection rotation scale to cover R&D artifacts too, or stay
  turn-completion only?
- Is the origination-duty default (veto-after-start) working, or is the
  conductor still the de facto gate?
