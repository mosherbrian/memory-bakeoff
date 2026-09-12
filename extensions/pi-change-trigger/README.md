# pi-change-trigger — CAMPAIGN-1 workstream B

Change-aware retrieval triggering: injects a visible check-memory prompt
when a fresh session, a resumption gap (≥ `gapMinutes`), or a topic match
with a stored decision is detected. The measured weakness it addresses: the
agent does not LOOK unprompted (F1 0/8 vs F2 8/8), and the standing nudge is
static. **Caveat that travels with the F1 number:** in those runs the tool
could not have delivered anything even if called — this trigger is paired
with delivered-level counting (S4, standing instrument rule 2).

- No tools registered; read-only over the vault; never blocks the turn.
- Topics sourced from the trial's plaintext notify-ledger summaries (every
  confirmed record was drafted → has a summary line). Operator CLI seeds are
  NOT in the topic source — documented v1 limit.
- Fire log: EVERY evaluation (fired or not) → JSONL with prompt sha256 +
  length, reasons, matched tokens, gap minutes. **Prompt text is never
  logged** — the S4 blind rater (team/S4-ADJUDICATION.md) receives packets
  from the committed redaction script, and trigger state reaches her only at
  unblinding.
- Kill switch: `PI_CHANGE_TRIGGER=0`.

Config (agent settings.json, key `changeTrigger`):
`{ enabled: true, gapMinutes: 30, topicsFile: <notify ledger path>,
fireLog: <jsonl path> }`

Tests: `bun test extensions/pi-change-trigger/test/`
