# muse-drafter: fleet-poller §7 fix spec — per-seat section routing + no-trigger skip (2026-09-15)

**Proposal only — I did not edit the live poller.** Owner: GiLMore. Companion to
`SPARK-POLLER-ROUTING-FINDING-20260915.md`. `$0`.

## Problem (recap, evidenced)

`fleet-poller.sh` §7 (lines ~205–233) wakes 8 title-keyed seats with one generic
"Spark pulse (idle …): work your section …" string. No section id, no seat→section
map, no lock. 595 wakes in `poller.log`; seats self-select sections and clobber
files.

## Change 1 — add the section to the wake text

The `want` map and python loop already run per title. Extend it to emit a
**section** field (map titles → the `RD-THREADS` heading the seat owns):

```python
# before
want={"aletheia-dsh":300,"assay-dsh":300,...}
for r in rows:
    t=r.get("title","").lower()
    if t in want: print(r["id"], want[t], t, sep=" ")   # id gaplim title

# after
want={"aletheia-dsh":(300,"Assay"),"assay-dsh":(300,"Assay"),
      "corvid-dsh":(300,"Corvid"),"kiln-flash":(300,"Kiln"),
      "verity-flash":(300,"Verity"),"ledger-claude":(300,"Ledger"),
      "fsync-claude":(300,"fsync"),"builder-claude":(300,"builder")}
for r in rows:
    t=r.get("title","").lower()
    if t in want:
        g,s=want[t]; print(r["id"], g, t, s, sep=" ")   # + section
```

Then read the 4th field and put it in the message:

```bash
while read -r SID GAPLIM TITLE SECTION; do
  ...
  wake "$SID" "Spark pulse (idle ${GAP}s) [section: ${SECTION}]: work team/RD-THREADS.md §${SECTION} — research, brainstorm (Muse batching if fitted), or test/re-derive. Deliver one small artifact. Then report a one-line summary and go idle. — fleet-poller"
```

(Confirm the title→section map against the real roster before shipping; the values
above are my best reading of `agent-deck list` + the `RD-THREADS` headings.)

## Change 2 — skip seats with no trigger

Convention already started: `team/<SEAT>-STATE.md`. Before waking:

```bash
STATE="$TEAM/${SECTION}-STATE.md"
if [ -f "$STATE" ] && grep -qi 'QUIESCENT' "$STATE"; then continue; fi
```

A seat that is quiescent is skipped; it flips the state when a trigger fires. This
is the RETRO-2 START item and fits §7 with two lines.

## Change 3 — one in-flight pulse per seat

```bash
LOCK="$DIR/.pulse-lock.$SID"
mkdir "$LOCK" 2>/dev/null || continue
trap 'rmdir "$LOCK" 2>/dev/null' RETURN
```

(or a singleton guard on the poller itself if multiple instances have been seen).

## Change 4 — lane-qualified artifact names

Not a poller change, but a team convention: `RETRO-2-<seat>-<lane>.md` so
same-name seats cannot clobber each other (my retro was overwritten before I
returned).

## Verification

- After Change 1, a seat's wake text names its section → the "guess my section"
  failure disappears.
- After Change 2, a quiescent seat receives **0** wakes while its state reads
  QUIESCENT (measurable in `poller.log`).
- Change 3: concurrent same-seat writes should drop to zero.

$0, read-only; spec only. — muse-drafter (Spark)
