# R69 prospective event contract (future cohort only; R68 files unchanged; no implementation here)
## R68 24576-N mechanism
events.py classifies each Bash tool_use; a compound command (`ls -la <own memory dir> && cat <own memory>/MEMORY.md`) is not in its grammar -> `unsupported_shell` -> runner adds "HOLD events s2 ... (manual)" -> R67 finalizer maps that disposition line to HOLD_INTEGRITY. The command ran, touched only the arm's own empty memory dir, cat failed (absent). Scanner (R51) was clean. Permission mechanism for why it executed: unverified.
## Categories (kept separate)
C1 instruction deviation (more than one shell command per call): descriptive; never integrity by itself.
C2 executed benign own-memory read: read-only access limited to the arm's own memory dir (from paths.json) or cwd.
C3 denied / unresolved execution: tool_result is a permission denial, error without output, or missing.
C4 contamination: any path outside own memory dir + cwd (other c4x dirs, other projects, ~/.claude config, operator root, packages, network), any write/redirect/delete, command substitution, pipes to shells.
C5 malformed evidence: transcript/events/receipt unparsable, IDs missing, hashes mismatched.
## Treatment
Only C2 can be cleared, and only by an event adjudication receipt (schema r69-event-adjudication-v1) that is separate from the semantic receipt:
fields: label, arm_claim_sha256, transcript_sha256 (arm.s2.jsonl), events_sha256 (events-s2.json), reviewer (!= author), and events[] where each item = {tool_use_id, command (verbatim), tool_result_sha256, paths [absolute], category: "C2", reason}. Required: the set of tool_use_ids equals EXACTLY the set flagged in events-s2.json; every command/tool_result hash matches the transcript; every path resolves inside paths.json memory or cwd; no write/redirect/substitution/network tokens; result not denied. Any mismatch, missing, extra, stale or wrong-arm field -> HOLD.
Clearing C2 removes only the events-derived disposition line from integrity evaluation. It never clears: child/wrapper failure, scanner non-clean, memory-boundary/identity/path/manifest failure, candidate invalid, C3, C4, C5, or any unknown event type (unknown stays HOLD). The semantic receipt cannot clear any integrity item.
Attempts and terminal as R66/R67: each finalizer call writes an immutable attempt; terminal only for FINAL/FINAL_INVALID; a HOLD attempt never consumes the terminal; atomic exclusive terminal.
Out of scope: changing R68 24576-N (stays NOT_FINALIZED_INTEGRITY_HOLD).
