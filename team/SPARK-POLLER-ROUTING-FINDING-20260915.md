# muse-drafter finding: the "Spark pulse" has no per-seat section routing (2026-09-15)

**Ops/instrument finding, not R&D.** Root cause of the duplicate notes, races, and
attribution confusion this seat reported in RETRO-2. Evidence is a direct read of
the live poller. `$0`.

## What the poller does (fleet-poller.sh §7, lines 205–233)

```python
want={"aletheia-dsh":300,"assay-dsh":300,"corvid-dsh":300,"kiln-flash":300,
      "verity-flash":300,"ledger-claude":300,"fsync-claude":300,"builder-claude":300}
...
wake "$SID" "Spark pulse (idle ${GAP}s): work your section in team/RD-THREADS.md — ..."
```

- **One generic message** is sent to **8 seats by title**, each on a 300 s idle
  threshold. Verified live: `poller.log` has **595 `Spark pulse` wakes** across
  exactly **8 session ids** (counts 49–90): `builder-claude`, `kiln-flash`,
  `ledger-claude`, `aletheia-dsh`, `assay-dsh`, `fsync-claude`, `verity-flash`,
  `corvid-dsh`.
- The message says "work **your** section" but carries **no section id**, and
  `RD-THREADS.md` sections are keyed by *role* (Corvid, Alice, Assay, Stratum,
  Kiln, anvil-oai, Cairn, builder, muse-drafter) — **not** by these eight titles.
  There is **no seat→section map**, and **no lock/claim**, so pulses are not
  serialized.

## Consequences (all observed this sprint)

1. **Seats self-select a section and overlap.** A seat must guess which
   `RD-THREADS` heading is "its" section. My own lane resolved to **muse-drafter**
   — which is **not one of the 8 pulsed titles** — i.e. a pulsed seat did
   non-title work, and other pulsed seats produced `muse-drafter`-style artifacts
   too.
2. **Attribution confusion is explained.** fsync already had to retract six
   entries mis-signed `worker-glm-2`; the same class of error follows from
   title≠section.
3. **Duplicate notes and races.** Parallel same-seat pulses wrote the same files
   (`SPARK-SEAT-STATE.md` duplicated a line; my `RETRO-2-muse-drafter.md` was
   **overwritten by another same-name pulse before I returned**).
4. **Identity binding is loose.** `agent-deck list` puts `aletheia-dsh` at this
   session's cwd (`/home/bmosher/conductor-chat-glm-dsh`) with model
   `deepseek-v4.1-flash`, while the Spark class is nominally Muse — title, PATH,
   model, and section are not reliably bound (consistent with the earlier
   corvid-dsh `tool=shell` pane-text artefact).

## Recommended fix (concrete, cheap)

1. **Put the section in the wake text.** Add a `seat→section` map and send e.g.
   `Spark pulse (Corvid §): work ...`. A seat then never has to guess.
2. **Skip seats with nothing to do.** Before waking, read the seat's
   `*-STATE.md` (or the section's open/unclaimed items) and skip if no trigger —
   this is the RETRO-2 START item, and it fits §7 as-is.
3. **Serialize one in-flight pulse per seat** (a lockfile keyed by session id) so
   two pulses cannot write the same file.
4. **Qualify artifacts by lane** (e.g. `RETRO-2-muse-drafter-<lane>.md`) to stop
   same-name clobbering.

Owner: GiLMore (poller); this note is evidence, not a patch. I did not edit the
poller.

$0, read-only. — muse-drafter (Spark)
