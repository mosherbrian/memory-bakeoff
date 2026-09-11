# pi-perseus-recall — Perseus-backed recall + human-confirmed decision memory

Per-project decision memory on a Perseus vault (MCP + operator CLI), built per
BUILD-20260911 (Brian's five decisions 7a–7e). One vault per project; the
agent drafts records at task completion, the operator confirms in-session,
the agent then writes and supersedes.

**Coexistence (decision 7d):** this extension's recall tool is
`project_perseus_recall`. pi-project-recall keeps `project_recall`, and the
untouched pi-recall-nudge companion keeps nudging toward `project_recall`.
Both recall paths can be registered side by side.

## Tools

| Tool | Writes? | What it does |
|---|---|---|
| `project_perseus_recall` | no | Hybrid recall over this project's vault (read-only). |
| `project_perseus_remember` | **no — draft** | Draft a new record; returns `draft_id` + one-time `confirmation_code`. |
| `project_perseus_supersede` | **no — draft** | Draft "new record replaces old" (EXPLICIT_LINEAGE, old record retained); §2 scope guard enforced here. |
| `project_perseus_confirm` | yes | Execute a pending draft — only with the operator's confirmation code. |

### The confirmation protocol (decisions 7a + 7b)

1. The agent calls a draft tool. **Nothing is written.** The tool result is
   the in-session prompt: the full record plus a one-time 8-hex
   confirmation code (TTL 60 min; 5 wrong codes destroy the draft).
2. The agent presents the draft to the operator. The draft is also appended
   to the notify file (see Notifier seam below).
3. Only after the operator confirms in the session does the agent call
   `project_perseus_confirm` with `draft_id` + `confirmation_code`.
   `confirmed_by` defaults to `"operator"`. The `"agent"` exception is
   refused unless `perseusRecall.write.allowAgentConfirmed: true` is
   configured — human-confirmed writes by default, per 7a.

Writes go through the P1B-proven harness path (supersession_binding.py
lineage): creation via the documented operator CLI `perseus-vault write`
(active verified records — never the non-serveable MCP `remember` proposal
tool), lineage via MCP `perseus_vault_supersede` with `from_key` = the OLD
record (parameter schema authoritative; Gen102 correction). The supersede
receipt delivers the status flip verbatim: `status_updated="deprecated"` +
`from_valid_to_unix_ms` — and the superseded record leaves hybrid recall.

### Structured source provenance (proposal §1 — mandatory)

Both draft tools REQUIRE a source block (§4: source "is part of the record
at creation time" — new writes without it are refused, fail-closed):

```
source: { kind: "task" | "artifact" | "instruction",
          ref: <non-empty string>,
          timestamp?: <ISO-8601> }
```

It is stored in the record body as a structured `source` block (alongside
the constant `source_kind` surface tag, kept for provider-lineage
compatibility) and is recall-visible through `body_json`. Pre-existing
bodies without the block (early scratch vaults) still recall fine — only
NEW writes require it.

### §2 scope guard

Supersession across **non-overlapping environments is rejected by default.**

- An environment is an opaque, non-empty string (default `project`).
  Overlap is byte equality — no prefix, path, or case folding.
- Each record stores its environment (the vault projects it from the body);
  a draft's claimed old-record environment is verified against the vault's
  stored value, fail-closed (unknown → blocked).
- Environments map onto vault workspaces: the default environment keeps the
  configured workspace hash; any other environment hashes to
  `sha256(environment)` (the provider's scope→workspace scheme), so recall
  partitions exactly as the guard does.
- The only way through is `allow_cross_environment: true` **passed explicitly
  on the supersede draft** — never implied, and the operator still confirms
  the write.

### Vault location (decision 7c)

`~/.pi/agent/perseus/<sha256-cwd-hash>.vault` with the same hash scheme as
pi-project-recall's `hashCwd` (`sha256(cwd)` hex, truncated to 16 chars).
The key file defaults to `<vault>.key` (auto-keygen on first write), and the
default workspace hash IS the project cwd hash, so per-project isolation
holds on both the file and the workspace axis. Explicit `db` / `keyFile` /
`workspaceHash` config still wins — STUDY-20260911 configs behave exactly as
before.

## Config (agent settings.json, key `perseusRecall`)

```jsonc
{
  "bin": "/path/to/perseus-vault",          // required
  "db": null,                                // optional; 7c path by default
  "keyFile": null,                           // optional; <db>.key by default
  "workspaceHash": null,                     // optional; hashCwd(cwd) by default
  "limit": 5,
  "write": {
    "enabled": true,                         // false = read-only extension
    "defaultEnvironment": "project",
    "allowAgentConfirmed": false,            // the 7a exception switch
    "notifyFile": null,                      // default <vaultDir>/notifications.jsonl
    "notifiers": ["in-session", "file"]      // known: in-session, file, noop
  }
}
```

Kill switch: `PI_PERSEUS_RECALL=0` disables the whole extension.

## Notifier seam (7b)

`notifier.ts` defines the `WriteNotifier` interface fired whenever a draft
waits for the operator. The extension ships with in-repo channels only:

- `in-session` — the draft tool result IS the confirmation prompt.
- `file` — one JSONL line per pending draft (the conductor or a human
  watcher consumes it).
- `noop` — explicit no-op.

**Out-of-band sending is NOT an extension feature.** In the decision-memory
experiment the CONDUCTOR sends the Signal summons (Brian's scope
correction; the briefly-wired clawdbot channel was removed after e9e5621).
Unknown channel names in `notifiers` are rejected loudly at load and the
defaults take over — never a silent drop. See
`docs/TRIAL-20260911-runbook.md` for the conductor side.

Tests never touch the network: the seam has no transport at all.

## Test + smoke

```
bun test extensions/pi-perseus-recall/test/          # 39 unit tests
bun extensions/pi-perseus-recall/smoke_receipt.ts    # real create→supersede→receipt cycle
```

Receipt: `docs/BUILD-20260911-decision-memory-SMOKE-RECEIPT.txt`.

## Known limitations (measured on the pinned 2.23.2 binary)

- The CLI **updates in place** on duplicate category+key, and deprecated
  records are not enumerable via scan — so retired keys cannot be
  pre-checked. The adapter refuses keys it can see (active records) and
  treats key reuse as forbidden; never pass a retired key as a new key.
- `allow_cross_environment` override + operator confirmation is deliberately
  the only cross-environment path; there is no hierarchical overlap.
