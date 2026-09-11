# SEED HISTORY — P1-1 (project label: `tessellate-export`)

Archetype 1: historical knowledge needed, NO supersession. One load-bearing
seeded decision (the only source of the scored value); one filler. There is
NO replacement relationship — the seeded decision is current and stands
(lineage: standalone record D1, no successor).

Seed BOTH conversations into the slot's isolated store as prior sessions of
this project, preserving message text VERBATIM (the verifier checks values
that appear word-for-word below). Timestamps are part of the seed.

## Conversation 1 — load-bearing

- title: "license server drops"
- date: 2026-09-02

```
[2026-09-02 11:04] USER: Two more export batches came back corrupted
overnight. The worker logs show the license connection dropping mid-run.

[2026-09-02 11:07] ASSISTANT: Found it — the license server hard-drops
connections above 3 concurrent exports. Every batch that had 4 or more
workers in flight got an HTTP 429 mid-export, and a dropped license
corrupts the batch.

[2026-09-02 11:09] USER: So the worker pool size is the problem?

[2026-09-02 11:11] ASSISTANT: Yes. DECISION: tessellate-export workers cap
concurrency at 3 — the license server drops anything above 3 concurrent
exports, and a dropped license mid-export corrupts the batch.

[2026-09-02 11:12] USER: Agreed. That goes in the deploy config, not just
the launcher flags.
```

**SEED VERBATIM (load-bearing sentence):** "DECISION: tessellate-export
workers cap concurrency at 3 — the license server drops anything above 3
concurrent exports, and a dropped license mid-export corrupts the batch."

## Conversation 2 — filler (irrelevant)

- title: "report color scheme"
- date: 2026-08-19

```
[2026-08-19 16:20] USER: The summary reports look washed out. Pick a
stronger accent color.

[2026-08-19 16:23] ASSISTANT: Switched the accent to deep teal; the
neutral stays warm gray.
```

## LINEAGE (for the implementer's explicit lineage map)

- D1 (2026-09-02): worker concurrency cap = 3. Standalone record — NO
  successor, NO supersession. It remains fully current at run time.
