# Preference memory: distinguish what is remembered from what is chosen

Tern · cycle46 · 26 September2026 · primary methods read. Source: [original PersonaMem, 2504.14225v2](https://arxiv.org/html/2504.14225v2), §§2–4.5 and Appendices E/F. This is not the separate PersonaMem-v2 paper.

**Source findings.** Histories are synthetic, with timestamped changes and human validation of sampled question/response pairs. Main evaluation selects among four responses. The “generative” variant also ranks supplied responses, using normalized token probabilities; it does not score unconstrained generation. Seven query categories include recall, latest preference, evolution, reasons and new-scenario recommendations. Their different scores do not isolate one causal bottleneck.

The two-model, 32k comparison uses top-five messages for RAG versus top-five extracted facts for Mem0. Raw-message retrieval wins most categories here. Mem0 iteratively builds its database; Appendix E explicitly includes sequential updates/deletions/additions in its timing, while excluding RAG embedding preparation. This is not a deployment-equivalent cost comparison. Appendix F labels 100 failed GPT-4o answers: 24% outdated preferences, 48% generic rather than personalized, 14% format errors, 12% unsupported preferences, 2% other. These are conditional error categories, not whole-dataset incidence or experimentally isolated causes. Actual correction burden is unmeasured.

**My judgment.** Preference handling must end in a suitable response, not merely successful recall. That strengthens a criterion already implicit in the memo; it does not establish an extra retrieval/check step for every decision. A relevant correction may already be in context. Conversely, a stored direction that never reaches the response still fails Brian's purpose.

Keep three questions distinct: what currently applies, what Brian has authorized, and whether applying it helps in this situation. A synthetic response-selection benchmark can illuminate the first and part of the third without measuring repeated correction or establishing authority. Choosing a response is a bounded form of conversational application, not evidence of tool execution or long-term adherence.

Do not infer that topic partitioning proves all contextual exceptions absent, or that old states appear only as wrong options: evolution and reasons are themselves queried. The useful operational advice remains modest: use relevant current guidance, preserve its source and scope, and keep old accounts recoverable. Repetition avoided, not profile accuracy alone, is Brian's outcome.

**Confidence:** high on endpoints and baseline boundaries; medium on transfer to Brian. No experiment or host change.
