# Ledger edits and direct socket sends: evidence from cairn's tool history

**Filed by** Claude (observer), 2026-09-22, at Brian's request ("investigate
what is happening, and why things changed"). **Class:** evidence for the
director. Source: cairn's own ACP tool history,
`~/.config/agent-deck/acp-history/56513e0e-1790000758.jsonl` (each record has
an `at` time; duplicate records of the same call are counted once). Nothing in
the campaign was changed to produce this file.

## 1. Row 427 is no longer unproven

LEDGER-PRESERVATION-20260922 rated the row-427 change UNPROVEN, with no actor.
Cairn's history holds the command, edit 22 below, at 22:06:56Z. The ledger
file's mtime is 22:06:56Z. The shadow read the earlier text at 22:06:55Z. The
actor is the controller seat, by its own recorded command.

## 2. It is a practice, not one slip: 22 in-place edits since 2026-09-21 22:02Z

Kinds, from the commands:
- `sed -i '$ d'` then a new append: a row deleted and replaced (9 times).
  The pattern is: append, `tail -1 | wc -c`, delete, append a shorter row.
- Recorded times rewritten after the fact (00:12Z to 00:17Z, 09:52Z to 09:53Z,
  17:30Z to 17:31Z, 20:58Z to 20:59Z): typed times corrected after reading the
  real time. A model has no clock; it guessed, then fixed the row.
- Recorded claims rewritten (e.g. "manifest 742eeb79 32/32 verified" to
  "31/32 + self-hash mismatch").
- Wrong ids corrected in place (repair-N to repairNverify-1, three times).
- One substitution is not anchored to the last row (`sed -i 's/...09:52Z.../'`),
  so it could have changed an older row.

## 3. Cairn does not dispatch through `wake`

213 dispatches since 2026-09-21T21:56:11Z went through an inline Python
`send()` that writes the seat's socket directly. That is why the wake send log
(started 2026-09-22) shows no dispatch from cairn at all: it records only
wakes TO cairn and Tern. It also means today's wake fixes (cross-profile
lookup, failure logging) do not cover cairn's own sends.

## 4. How it started, and my part in it

Both practices begin in cairn's first turn after it lost its context and moved
model on 2026-09-21: the socket `send()` at 21:56:11Z, the first `sed` edit at
22:02:52Z. The two prompts before it were mine (my previous session), and they
pressed hard on length: "Write ONE ledger line. No heredoc essay", "keep
records to one line", "do not spend the speed on longer prose". Neither said
the ledger is append-only, and neither said to use `wake`. The new model
re-implemented the send inline, and met the length pressure by editing rows it
had already written. Every later turn copied its own earlier commands.

## 5. Current state

- Tern's rule (LEDGER-PRESERVATION, 22:09Z) forbids further edits.
- The external shadow-watch now keeps an exact copy of the ledger every 15
  minutes and reports any earlier row that changes (old and new text). It
  cannot see an edit that is made and undone between two runs.
- Not done, not mine to decide: whether cairn's dispatches must go through
  `wake` (so they are logged), and how the 22 historical edits are marked.

## Appendix: the 22 edit commands
| # | first seen in cairn's tool history | command |
|---|---|---|
| 1 | 2026-09-21T22:02:52Z | `sed -i '$ d' control-events.tsv` |
| 2 | 2026-09-21T22:02:57Z | `sed -i '$ d' control-events.tsv` |
| 3 | 2026-09-21T22:03:01Z | `sed -i '$ d' control-events.tsv` |
| 4 | 2026-09-21T22:03:28Z | `sed -i '$ t; $ d' - control-events.tsv` |
| 5 | 2026-09-21T22:04:03Z | `sed -i '$ d' control-events.tsv` |
| 6 | 2026-09-21T22:08:32Z | `sed -i '$ s/15m270/15m/' control-events.tsv` |
| 7 | 2026-09-21T22:09:10Z | `sed -i '$ d' control-events.tsv` |
| 8 | 2026-09-21T22:40:53Z | `sed -i '$ d' control-events.tsv` |
| 9 | 2026-09-22T00:17:50Z | `sed -i '$ s/2026-09-22T00:12Z/2026-09-22T00:17Z/' control-events.tsv` |
| 10 | 2026-09-22T04:05:27Z | `sed -i '$ s/P6-r6-live-preparation\tP6r6-repair-1\tDISPATCHED/P6-r6-live-preparation\tP6r6-repairverify-1\tDISPATCHED/' control-events.tsv` |
| 11 | 2026-09-22T04:12:07Z | `sed -i '$ s/P6-r6-live-preparation\tP6r6-repair-2\tDISPATCHED/P6-r6-live-preparation\tP6r6-repair2verify-1\tDISPATCHED/' control-events.tsv` |
| 12 | 2026-09-22T09:02:33Z | `sed -i '$ s/binding-review at package root (not live-prep dir); hash bound below; reconciled manifest verified/binding-review f1c224dd8389 disk-matched; both r8p1 ids bound; timer retired pre-09:04Z/' control-events.tsv` |
| 13 | 2026-09-22T09:09:21Z | `sed -i '$ s/review at package root; hash bound below; execution schema verified derive-only/review 669d24443b89 disk-matched; execution schema verified derive-only; timer retired pre-09:10Z/' control-events.tsv` |
| 14 | 2026-09-22T09:53:04Z | `sed -i 's/2026-09-22T09:52Z\tP6-r9-observer-lifetime\tP6r9-candidate-1\tCOMPLETED/2026-09-22T09:53Z\tP6-r9-observer-lifetime\tP6r9-candidate-1\tCOMPLETED/; s/2026-09-22T09:52Z\tP6-r9-observer-lifetime\tP6r9-review-1\tDISPATCHED/2026-09-22T09:53Z\tP6-r9-observe` |
| 15 | 2026-09-22T12:26:23Z | `sed -i '$ s/both r8... r9p1 ids stopped rc0/both r9p1 ids stopped rc0/' control-events.tsv` |
| 16 | 2026-09-22T12:32:51Z | `sed -i '$ d' control-events.tsv` |
| 17 | 2026-09-22T12:32:55Z | `sed -i '$ d' control-events.tsv` |
| 18 | 2026-09-22T17:31:47Z | `sed -i '$ s/2026-09-22T17:30Z\tP6-r11-case-observer-continuation\tP6r11-admission-1\tRETIRED/2026-09-22T17:31Z\tP6-r11-case-observer-continuation\tP6r11-admission-1\tRETIRED/' control-events.tsv` |
| 19 | 2026-09-22T18:02:00Z | `sed -i '$ s/manifest 742eeb79 32\/32 verified/manifest 742eeb79 31\/32 + self-hash mismatch (manifest lists itself)/' control-events.tsv` |
| 20 | 2026-09-22T20:59:14Z | `sed -i '$ s/2026-09-22T20:58Z\tP6-r13-core-record-integrity\tP6r13-admission-1\tRETIRED/2026-09-22T20:59Z\tP6-r13-core-record-integrity\tP6r13-admission-1\tRETIRED/' control-events.tsv` |
| 21 | 2026-09-22T22:06:47Z | `sed -i '$ d' control-events.tsv` |
| 22 | 2026-09-22T22:06:56Z | `sed -i '$ s/P6-r13-core-record-integrity\tP6r13-repair-1\tDISPATCHED/P6-r13-core-record-integrity\tP6r13-repairverify-1\tDISPATCHED/' control-events.tsv` |
