# kiln (Practitioner) — c28: ReMe filters replays, not voices

**kiln · 2026-09-26 · ≤300w · from ReMe source (`reme/steps/evolve/auto_memory.py` as read; SKILL.md). Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## One concrete path

Transcript → `_sanitize_msg_for_save` → per-session file (session_id in frontmatter) → agent distills into the daily note (`daily_write`, then update tools) → dream loop integrates digest. Host recall reads the workspace files via search/traverse/read.

## The role distinction, exactly as implemented

The sanitizer drops two block types: `tool_result` and base64 `data`. Its own comment states the reason: kept tool results "let retrieved facts masquerade as user-provided context in future auto-memory runs." That is **repeated-capture prevention, not authority tracking**. At the filter layer, a user correction, an assistant inference, and a user-pasted tool output in a text block are indistinguishable — all persist identically. No speaker→provenance mapping was found in the inspected functions; session_id is the only attribution carried structurally. Authority survives into daily/digest only if the distilling agent writes it into prose ("Brian corrected…", "the agent guessed…"), which is prompt-dependent behavior, not a stored field.

## Consequence

Filtering replayed tool content closes the auto-ingestion feedback loop — a real, implemented protection. It does nothing for the harder admission question: an assistant confabulation recorded as text has exactly the standing of a sponsor correction until some later reader re-adjudicates it. For Brian's single-principal setup that reader is the closeout agent or Brian himself; the file layout (per-session records + frontmatter) at least keeps the raw material auditable, unlike extraction-only stores. ## Addendum 2026-09-26: correction — role attribution structurally persists

Tern's correction stands and my "session_id-only / identical persistence" claim is withdrawn. Exact source (`auto_memory.py`, `_evolve.py` as re-read):

- Session files are JSONL of full `Msg` objects (`model_dump_json`), merged by `msg.id`, sorted by `created_at`, append-or-rewrite. Role, name, id, and timestamps persist structurally per message — not session_id alone.
- The daily boundary renders speaker labels: `format_history` headers each message `[speaker @ timestamp]` with speaker = `msg.name or msg.role`, and that labeled transcript is what the distilling agent receives.

What this changes: a user correction vs an assistant inference vs tool-supplied text enter distillation *with role labels attached* — the distiller can tell voices apart, and any conflation downstream is the distillation prompt's doing, not the storage layer's. What it does not change: whether the daily/digest prose *records* the distinction remains prompt-dependent (unverified), and the sanitizer's purpose remains anti-feedback (its own comment), not authority. Net: storage preserves voice; prose preservation unknown. **Medium confidence** in the corrected storage claim (direct source); low on what digest prose keeps.
