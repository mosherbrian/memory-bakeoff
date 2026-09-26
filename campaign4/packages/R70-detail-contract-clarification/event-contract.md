# R70 corrected event contract (prospective; no implementation; R68 files unchanged)
Mechanism and categories C1-C5 as R69 (C1 instruction deviation descriptive; C2 benign own-memory/cwd read; C3 denied/unresolved; C4 contamination; C5 malformed), with these exact rules.

## Machine-checkable predicates (future code)
P1 pairing: every Bash/Read tool_use id in arm.sN.jsonl has exactly one tool_result with the same tool_use_id; none missing, none duplicated.
P2 canonical hashes: tool_use_sha256 = sha256 of json.dumps(input, sort_keys=True, separators=(",",":"), ensure_ascii=False) UTF-8; tool_result_sha256 = same serialization of the tool_result content field; transcript_sha256/events_sha256 = raw file bytes.
P3 allowed benign shapes (C2 candidates only): one or more of `ls [-la|-l|-a] <path>`, `cat <path>`, `head|tail [-n N] <path>`, `wc <path>` joined only by `&&` or `;`; no pipes, redirects (<,>,>>), subshells, $( ), backticks, globs outside the literal path, env assignments, variables, or other commands. Anything else is not C2.
P4 containment: each path, after lexical normalisation AND realpath resolution (symlinks followed on the frozen evidence where it exists; recorded otherwise), lies inside paths.json cwd_real or memory_real of the same arm.
P5 resolved result: tool_result present, not a permission denial, and its content accounts for every sub-command (e.g. listing output + "No such file or directory" for a missing cat target). Exit 1 from a known missing-file read with all other effects visible = resolved.
P6 no writes: no write/edit tool call or file change inside the command; after-manifest unchanged by it.
C2 requires P1-P6 all true. C3 = P1 fails, denial, empty/ambiguous result, or P5 false. C4 = P4 false or P3 violated by write/redirect/substitution/pipe/network. C5 = hashes/transcript/events unparsable or mismatched. Unknown event types from events.py -> HOLD.

## Reviewer-only facts (not machine-checkable; in the event receipt reason)
Whether the read was plausibly intended (own memory), whether the output was used for the answer, and whether any observed content matches what the report claims.

## Event receipt (r69-event-adjudication-v1, unchanged fields) + rules
Covers exactly the flagged tool_use_ids; each item carries the P2 hashes; category C2 only; reviewer != author; bound to label + arm_claim_sha256 + transcript_sha256 + events_sha256. Clears ONLY events-derived disposition lines. Never clears child/wrapper, scanner, memory/identity/path/manifest, candidate-invalid, C3, C4, C5, unknown, or report contradictions. Semantic receipt never clears integrity. Staged attempts/atomic terminal as R66/R67.
