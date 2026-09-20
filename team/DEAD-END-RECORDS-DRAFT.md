# DEAD-END RECORDS — DRAFT (QUEUE row 5)

**Seat:** Aletheia (Alice), `worker-glm-dsh` · **Date:** 2026-09-12
**Row:** `team/QUEUE.md` #5 — "Dead-end records: draft the six known dead ends as
vault-ready memory records (Aletheia WILD, arm A prep)"
**Deliverable:** this draft + `team/dead-end-records.json` +
`team/load_dead_end_records.py` (dry-run loader)
**Status: DRAFT — NOT WRITTEN TO ANY VAULT.** No vault was created or modified.

---

## 1. Why these records exist

From `team/RETRO-1-Aletheia.md` §5 (the WILD idea):

> "Prose is not memory. A fresh amnesiac worker re-derives the same dead end
> because nothing in the agent's own retrieval path tells it *not to look there*."

The team has paid for six negatives. They currently live in finding docs and
prose. Arm A of the WILD experiment turns them into **serveable guardrail
records** so a later task in the same area can recall "already tried, here is the
receipt" instead of re-proposing it. The metric (re-proposals of a stored dead
end per arm) belongs to the WILD pre-registration; this row delivers only the
records, not the experiment.

## 2. The six records

All six use `category=dead-end`, `entity_type=observation`, `importance=0.9`,
`always_on=true` (guardrails must not decay), `visibility=workspace`. Each body
carries `content` plus structured `do_not`, `working_alternative`, and
`evidence_paths` so recall surfaces the prohibition and the working path
together.

| # | key | dead end | working alternative |
|---|---|---|---|
| 1 | `native-capture-is-not-an-activation-path` | native capture output is non-serveable and derives no replacement lineage | CLI `write` for activation; `perseus_vault_supersede` for lineage |
| 2 | `native-remember-demotes-active-records` | native `remember` on an active category+key demotes it `active -> proposed`; recall abstains; reports `ok:true, action:"updated"` | keep CLI `write` as the activation path |
| 3 | `maintain-does-not-promote-proposals` | `maintain`/`cohere`/`consolidate` do not promote capture proposals (`promoted_entities: 0`, rows byte-identical) | promotion needs an explicit valid admission path |
| 4 | `admission-decide-cannot-admit-bare-proposals` | a proposal with no admission evidence cannot be admitted ("candidate has no admission evidence") — **narrowed same day by row 6**: the admitted path itself works when valid evidence is bound | bind a verified `admission_source` event first; then outcome `admitted`, status `active`, serveable `true` |
| 5 | `memory-write-vocabulary-trap` | `memory.write.*` nouns are wrong and deny every write; omitted `capability_constraints_json` raises `EOF while parsing a value`; default `mode=shadow` silently fails admission | use `memory.propose`/`memory.commit`/`memory.read`/`memory.admission.*`, `capability_constraints_json "{}"`, `mode "enforce"` |
| 6 | `answer-id-never-captured` | stale-use metric unfillable on frozen evidence: `answer_id` was never persisted; only the metric and its test contain the field | add a per-case `answer_id` to the reader eval, then re-run the reader |

Record 4 is deliberately worded as a **narrowing**, not an erasure: the
2026-09-12 row-6 receipt (`team/PROBE-row6-admission-unit-tests.md`) proves the
admitted path is reachable with valid evidence, so a guardrail that said "the
admission chain is inert" would itself be a stale record. The dead end is the
*evidence-free candidate*.

## 3. Vault-ready form

The records are in `team/dead-end-records.json` under the 2.23.2 (9c82920) CLI
`write` interface — the only verified activation path (`status='active'`,
`source='cli-write'`). `team/load_dead_end_records.py` emits the six commands
and is **dry-run by default**:

```bash
cd /var/home/bmosher/memory-bake-off/team
python3 load_dead_end_records.py \
  --db /path/to/arm-a.vault \
  --key-file /path/to/arm-a.vault.key \
  --workspace-hash ws-arm-a
# add --execute to actually write
```

Actual write is **not** part of this row. Two safety notes for arm A prep:

- Use a **dedicated arm-A vault** (e.g. `/home/bmosher/acp-pi/arm-a.vault`),
  never the live trial vault `/home/bmosher/acp-pi/trial.vault` — the records are
  `always_on` guardrails and would become permanent recall surface for Cairn's
  live store.
- `always_on=true` is intentional: a guardrail that decays stops guarding. If
  the experiment needs a decayable arm, that is a pre-registration decision, not
  a loading detail.

## 4. Arm A/B wiring (pointer, not delivered here)

The WILD design is in `team/RETRO-1-Aletheia.md` §5: arm ON = recall trigger
over these records; arm OFF = no trigger; metric = re-proposals of a stored dead
end per arm, judged blind against this frozen list; small-n descriptive, no
causal claim. The frozen list is this document's six keys. The separate
pre-registration and run are not claimed by this row.

## 5. Honesty ledger

- **Claimed 09:45, drafted 2026-09-12** (the delay was the row-6 unblock that
  landed first). No artifact existed before this turn; that is the stall the
  queue flag was about.
- **Not written to any vault.** No vault file was created, opened for write, or
  modified. The loader is dry-run by default and was only run in dry-run to
  validate command shape.
- **Evidence is cited, not re-derived** in this draft; each record points at its
  FINDINGS/receipt. Where the record could not be confirmed from the original
  evidence (record 4's positive arm), the draft says so and cites the row-6
  receipt that closed it.
- **The six are the retro's list**, unchanged in number. If the experiment wants
  a seventh (`capture is the hole` as the meta-record), that is a pre-registration
  choice; it is not silently added here.

## 6. Artifacts

| artifact | path |
|---|---|
| this draft | `team/DEAD-END-RECORDS-DRAFT.md` |
| machine-readable records | `team/dead-end-records.json` |
| dry-run loader | `team/load_dead_end_records.py` |
| source list | `team/RETRO-1-Aletheia.md` §5 |
