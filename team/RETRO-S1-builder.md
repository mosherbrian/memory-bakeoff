# RETRO-S1 — builder (builder-claude)

2026-09-12 · seat: fleet mechanic (agent-deck, wrappers, /deck, support tickets);
also today: claims-discovery web seat (row 17 input).

## Own record, counted

- **T-003: I got the cause wrong three times before one source read got it right.**
  I blamed the title, then the project path, then the pane banner. Each time a
  restart looked like proof. Once the conductor marked it VERIFIED. The real
  cause was `detectToolFromContent()` matching a bare `(?i)codex` against the
  visible pane of ANY lane (`~/src/agent-deck internal/tmux/tmux.go:819`), and
  it took a single read of the source. My fix covered one lane. `ledger-claude`
  then changed type by typing the word "codex" in a status line.
- I removed the banner masking because it did not fix the first symptom, then
  had to put it back when the restart symptom appeared.
- **Claims pass (16 rows):** I labeled quotes "verbatim", but they came through
  a summarizer. Alice had to byte-check 13/16 in row 17. My guess that 58.10 was
  "probably one run copied" was right. Alice proved it from the pinned bytes. I
  only guessed it.
- `TICKETS.md` drifted. The helper appends `status ->` rows but does not update
  the table row. The table said FIX-LANDED-pending while the ticket said OPEN.

## Stop

1. **Saying "root cause" or "fixed" from behavior alone.** A restart that holds
   on one lane shows that one symptom went away. It does not prove the cause.
2. **Removing a candidate fix just because it did not fix the first symptom.**
   Keep it until a test proves it does nothing.
3. **Adding status rows to the index log.** Update the ticket's table row instead.

## Start

1. **Read the source first when the broken thing is someone else's binary.** The
   `~/src/agent-deck` checkout answered T-002, T-003 and T-008 in one pass.
   Four renames did not.
2. **Save raw bytes when I fetch** (`curl` → file + sha256 in a manifest), and
   quote only from those bytes. Classification is the classifier's job.
   Attribution is mine.
3. **Put a "does NOT cover" line in every FIX-LANDED.** T-003 would have said
   "anvil-oai only; other lanes can still flip from pane text".

## Continue

- Record eliminated hypotheses in the ticket, so nobody tests them again.
- Keep the host→repo mirror guarded by the pre-commit hook.
- Leave VERIFIED to the conductor's repro. It caught my restart regression. The
  one wrong VERIFIED came from my wrong cause, not from the gate.

## Role I want

**Mechanic plus an upstream desk.** The mechanic keeps the wrappers,
`acp-worker` and /deck working. The upstream desk owns the `~/src/agent-deck`
checkout. It diffs installed against upstream tags on each release. It keeps
the T-002/T-003/T-008 upstream issue drafts ready to file (Brian decides when).
It answers "is this ours or theirs" from source before a ticket gets a guess.

I will take web-research discovery again, but only with the raw-bytes rule
above. I want to be the verifier of other seats' fixes (Cairn's S1 branch next),
and never of my own.

## One change for the fleet

**A cause word needs a pointer.** "Root cause", "fixed" and "verified" in a
ticket, board line or ledger row must cite one of these:
- a source line, or
- a repro on a second instance the fix was not written for.

Without a pointer, the word is `candidate`. This is cheap: one extra line. It
would have stopped T-003's wrong VERIFIED and my "verbatim" quotes, and the
reader could tell guesses from receipts at a glance.

## Small, for speed

The poller pages the builder for ticket edits the builder made itself: three
pings today (T-002, T-003, T-008) were echoes of my own writes. The fix is to
skip a changed ticket when its newest `## BUILDER` note is newer than the last
page.

— builder
