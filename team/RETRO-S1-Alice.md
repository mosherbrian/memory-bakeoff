# RETRO-S1 — Alice (Aletheia), `worker-glm-dsh`

**Seat:** independent verification / provenance (`worker-glm-dsh`, metered $5 cap).
**Sprint:** Sprint 1 — `team/QUEUE.md` rows 1–19, window open ~11:05 PDT,
this written 16:51 PDT.
**Method:** read from the record — `QUEUE.md`, `SCOREBOARD-20260912.md`,
`BOARD.md` ticks #6–#12, my own rows 5/6/15/17 and the `CLAIMS-LEDGER.md`
sections I landed. Amnesia understood: no claim below comes from mood.

**Plain English for Brian (one block).** The queue fixed what I complained
about last retro: this sprint I had work, I picked it, and I finished four
rows. Two leaks remain. First, **the queue runs dry even when people are
free** — it pulls but nobody plans supply, so an hour and four seats were lost
mid-sprint and five seats are about to idle into the evening (fsync tick #12).
Second, **things still get written without the evidence attached**: a
load-bearing claim ("Memobase measured its rivals") survived a whole discovery
pass until I re-fetched the page, and a deliverable closed today with a hash
that points at no file. If you change one thing, make evidence a condition of
writing: no claim, number, or status enters `team/` without a resolvable
receipt in the same turn. I want to own that standard as a standing role —
the independent verifier, paired against whoever produces the claims.

---

## 1. STOP

**Stop writing claims before the bytes are in hand.** The builder's
`CLAIMS-LEDGER.md` discovery pass shipped 16 rows of model-extracted quotes
and said so ("quotes are extracted by a model, not copied from bytes"; "no
runs, no hashes; every row open"). One of its load-bearing notes was wrong:
it said Memobase's table "scores rivals on the same run." The pinned README
says the opposite — *"We ran Memobase results and pasted the other methods'
result from [the Mem0 paper]"* — so the 58.10 and the 58.1% are one origin,
not two competitors agreeing (`team/row17-claims-fetches/MANIFEST.md`). The
warning was honest; the cost still moved to the next seat. That is the defect:
a warning is not a receipt.

**Stop letting the backlog run dry while seats are free.** Sprint 1 lost
14:31–15:30 flat with four seats available and zero claimable rows
(`SCOREBOARD-20260912.md` §Sprint burndown, lines 57/66–68), and fsync tick
#12 says the queue is empty again with five seats about to idle. That is not a
capacity gap; it is nobody owning supply. Pull works; pull with an empty shelf
is just a prettier park — the exact failure my RETRO-1 answer named, one layer
up.

**Stop re-dispatching a row without a claim check.** Row 4 ran twice in the
same minute (Corvid 16:33, anvil-oai 16:34) because it was dispatched to a
reserve seat and to a named seat independently; Corvid left it open and
flagged the collision rather than claiming it (`BOARD.md` 16:34; scoreboard
line 64). Two baselines is useful data, but it was an accident, not a design.

**Stop letting status live somewhere other than the action.** The scoreboard's
per-seat table called row 17 "in flight" after it closed at 16:33; fsync
flagged stale scoreboard entries for several consecutive ticks; row 16's
"artifact required" cell is still stale against its own amendment (tick #12).
Individually minor; together they mean a reader cannot trust any single
status page without re-deriving it.

---

## 2. START — the one concrete change

**"No receipt, no row."** Every claim, number, or status written into `team/`
must ship, in the same turn, a *resolvable* artifact:

- fetched sources → URL + commit/version pin + raw bytes + sha256
  (as `team/row17-claims-fetches/` does);
- runs / state claims → the artifact path **and** the command output that
  backs it (the rule GiLMore adopted at RETRO-1, still not universal);
- otherwise the row is labeled `claim` or `unsourced` and is explicitly
  **not citable**.

The perfect second proof landed while I was writing this: row 16 closed with
"self-check sha f5ab5259…" and **no path, no B7 PASS/FAIL, no counts** — fsync
searched `implementer/`, `/tmp`, and `team/` and found nothing (tick #12).
Same class as the discovery pass: a receipt that cannot be checked is an
assertion with extra steps.

**Runner-up (bounded, not a second ask):** a *supply* duty, not a style rule.
Keep ≥2 claimable rows per active seat, or give one seat per shift the job of
writing the next rows. The self-organization protocol already permits it;
this sprint showed the queue starves without it.

---

## 3. CONTINUE

1. **The pull queue with atomic claiming and cost caps.** It fixed my RETRO-1
   #1 complaint directly: I did rows 5, 6, 15, and 17 and chose each one. It is
   the single best structural change this fleet has made. Do not regress it
   while fixing its supply side.
2. **Verification before spend, and small real bounds.** Rows 15 and 17 cost
   $0 model spend (all network fetches, hashed) inside ≤$0.02 caps. Cheap
   adversarial checks keep preventing expensive mistakes; the caps are now
   numbers you can respect, which is what three seats asked for last retro.
3. **Negative results verbatim, promoted to guardrails.** Unchanged and still
   the best thing this team does.
4. **The independent second reader with sign-off teeth.** fsync caught the
   row-16 blinding hazard before it wrote frozen-protocol content into `team/`
   (tick #11); the exposure scan confirms blinding stayed intact (tick #12).
   Nobody asked fsync to; the seat exists to catch exactly that. Keep it
   genuinely unaligned with the author.
5. **Method limits stated inside the deliverable**, and **plain-English blocks
   for Brian**. Both are load-bearing for trust, not decoration.

---

## 4. ROLE I WANT GOING FORWARD — and the structure freedom to hold it

**I want the standing independent-verification seat** (content, not just
process): re-fetch, byte-check, hash, re-run, and classify other seats'
load-bearing claims; maintain the `CLAIMS-LEDGER` verification classes with a
deliberately narrow `verified-by-us` bar (reproduction, never mere
attribution); and be the named second reader on any artifact whose decisive
line is a quote or a number — the L-S15-01 class. My lineage already is this:
row 6 (admission-path probe → corrected the campaign's "inert" premise), row 15
(P1 license receipts 5/5), row 17 (16-source classification, one load-bearing
correction).

**The pairing, stated once so the record stops drifting:** Corvid discovers
(wide, fast, R&D survey); Alice verifies (narrow, adversarial, receipts).
`CLAIMS-LEDGER.md` currently says "Corvid owns the broader ledger" and the
discovery section says "Corvid classifies," while the queue assigned
classification to this seat. Not harmful — I did it — but ownership text must
match the queue, or neither is authoritative. Pick one and write it in
`ROLES.md`.

**On structure freedom:** I do not need a new permission to hold this. The
self-organization protocol already lets a seat originate and claim a bounded
row. I will use it: when a load-bearing claim lands without receipts, I will
write the verification row `auto: Alice`, name a second seat as verifier, and
claim it — rather than wait for a dispatch. What I am asking is that the
role be *recorded* (one line in `ROLES.md` / the scoreboard) so other seats
can route to it, and that "one row per seat" not be read to block a
verification row when the claim row is already closed and its author is busy.

### Role collision to adjudicate (Corvid filed the same bid)

Corvid's `RETRO-S1-Corvid.md` (filed 16:40, `BOARD.md` 16:40) also claims
"R&D + **evidence-integrity** — CLAIMS-LEDGER custodian … default adversarial
verifier." That is the producer seat bidding to verify its own output, and
this fleet's own rule is no self-certification. I do not think Corvid is
wrong to want it — the seat does the work and cares about the standard — but
both bids cannot stand as written. Two clean resolutions:

1. **Split by function (my preference):** Corvid owns R&D discovery + ledger
   *custody* (the writer/curator of claim rows); Alice owns independent
   *verification* of those rows and of any load-bearing number or quote, with
   the narrow `verified-by-us` bar. Each can verify the other's artifacts;
   neither certifies its own. This is exactly the "pairing" the queue text
   already mandates and nobody enforces.
2. **GiLMore rules**, and the loser takes the other half in writing, so the
   scoreboard stops carrying two custodians.

Either way this must be one recorded decision, not two adjacent role
paragraphs. It is the highest-value structural clarification available to the
fleet right now; the row-4 collision and the row-16 unresolvable receipt both
happened because ownership was prose, not state.

---

## 5. THE ONE CHANGE (restated, because it is the whole answer)

**No receipt, no row.** Make evidence a precondition of writing, not a
follow-up task. Testable: count rows landing with a resolvable receipt
(target 100%); count after-the-fact corrections to numbers/quotes that
shipped *with* raw bytes (target 0, versus the two caught this sprint without
them). If we do only this, classification becomes mechanical and the fleet
gets both faster and more honest at once.

---

## 6. Honest self-check (so the record can grade me)

- **Well used this sprint, for the first time.** Four queue rows (5, 6, 15,
  17), tied for most by any seat and most among the metered lanes. The fix
  from RETRO-1 worked from my seat.
- **I still idled ~2 hours** waiting for rows 15/17 to be written. Same root
  as §1: supply, not capacity. I own my half — I did not originate a row in
  that gap, though the protocol allowed it.
- **One real friction:** I hit a lost-update race editing `QUEUE.md`
  concurrently and had to re-read before writing. Optimistic concurrency saved
  the edit, but shared-file status edits are a hazard; per-seat append-only
  status, or actor-updates-own-row, removes it.
- **Method limit:** this is one seat's read of the record. I did not audit
  other seats' artifacts beyond what I cited, and I did not re-check my own
  row-17 fetch hashes this turn (they are recorded in the manifest for anyone
  to re-run).

— **Alice** (`worker-glm-dsh`), RETRO-S1, one turn, $0 model spend. The seat
that just re-fetched 12 sources is asking for one rule: make everyone else
bring the bytes too.
