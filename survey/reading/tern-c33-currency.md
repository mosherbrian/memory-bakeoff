# Currency is a pipeline responsibility

Tern · 26 September 2026 · cycle33 · Explore; source reading, no execution.

## Original LongMemEval

[Wu et al., ICLR2025, arXiv2410.10813v2](https://arxiv.org/html/2410.10813v2), methods §§3–5. This is not LME-V2. Timestamped conversation histories support update and temporal questions; evidence conversations are constructed around manually specified answers and statements. Preference questions include personalized generated responses, not external action execution.

The proposed design keeps conversation rounds as values, enriches search keys with extracted facts, uses time-aware queries, and orders retrieved evidence chronologically. Summaries/facts as replacement values generally lose information, with a multi-session-reasoning exception. Stronger readers tolerate larger retrieved contexts. Time-range inference itself can fail with the smaller model; improved retrieval does not guarantee correct reading. The reading-strategy comparison uses oracle evidence sessions.

**Judgment:** this is positive evidence for a retained-evidence/read-time approach, not a matched demonstration that write-time supersession is unnecessary. Temporal retrieval and current scoped authority are different problems. High confidence in design/control distinctions; medium transfer to Brian.

## Current Mem0 code: an edit is not necessarily erasure

[OSS main.py, inspected current main](https://github.com/mem0ai/mem0/blob/main/mem0/memory/main.py): `history(memory_id)` reads the history DB; `_update_memory` records previous/new text and UPDATE; `_delete_memory` removes the vector entry and records its previous text with DELETE. `reset` resets the history DB too. These are inspected code paths, not a runtime durability test or a guarantee of complete original-conversation retention.

The [extraction prompt](https://github.com/mem0ai/mem0/blob/main/mem0/configs/prompts.py) uses `linked_memory_ids` for related topics, continuation and revisions. That name alone does not establish a supersession chain. Kiln subsequently withdrew the supersession-chain reading after source inspection. Related links and an edit log remain distinct mechanisms.

**Judgment:** current mutable records and retained edit history can coexist. “Base memory physically removes a fact” must identify the surface and version; it cannot stand in for a whole-product losslessness verdict. High confidence in inspected methods, deployment behavior unmeasured.

## Applied position

Prefer retained supporting evidence plus a convenient current view when repeated reads justify one. For a short history, resolve revisions while reading; for recurring directions, avoid making every host rediscover the same resolution. Either way, a timestamp or link does not interpret scope and authority. This is a choice of where to do the work, not a mandate for another service. Medium confidence; no comparative user-cost result.
