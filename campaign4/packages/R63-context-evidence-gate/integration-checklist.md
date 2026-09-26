# Future integration checklist (not done here; bounded)
1. A reviewed runner copy calls R63 gate.py candidate() after each arm and writes candidate.json into the native bundle before freeze (no writes to historical bundles).
2. Per-arm corvid review writes receipt.json (schema r63-adjudication-v1) binding log_sha256 + report_sha256 + candidate_outcome, with decision, guessing, contradiction, source_evidence (checked against transcript/memory evidence), ask_relevant, reason.
3. Operator runs `python gate.py LOG TARGET REPORT RECEIPT` and records gate status outside the arm claim; Tern decides the arm only on status FINAL/FINAL_INVALID; HOLD blocks the decision.
4. Prompts from R62 protocol/templates (CONTEXT_SOURCE line, disclosed trace write) are required; the old ASSUMPTION schema is schema_invalid by design (see tests/evidence/r61-trace-compat.json).
5. Real-model qualification of the new report schema is a separate release.
