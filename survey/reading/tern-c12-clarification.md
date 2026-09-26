# Clarification evidence does not select a storage architecture

**Tern · 26 September 2026 · primary reading, no experiment.**

[Capture v1, §2 and appendices D/E](https://arxiv.org/html/2609.02265v1) bounds decisions using only recency and channel provenance under specified distributions. Richer history changes the information available. Its clarification advantage depends on answer error and cost. The authors explicitly decline to treat their empirical cost comparison as verification of the theorem: utility and loss units differ, and the estimated distance does not certify the required bound.

Forty participants supplied histories against a fixed neutral assistant; competing systems were evaluated through replay. Stored participant annotations answered clarification requests, with a 7.1% realized replay query rate. This is not measured interruption time during live use of the competing systems. Synthetic answers and a query budget in the benchmark are another protocol, not a transferable one-question-per-twelve-turns recommendation.

**Inference, medium confidence:** files, integrated stores and learned controllers can all use more information than the restricted rule. The result motivates attention to ambiguity; it cannot choose A/B/C for Brian. Ask frequency, attention cost and correction benefit must remain separate.
