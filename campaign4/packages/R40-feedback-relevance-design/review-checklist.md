# R40 review checklist (corvid-eval, 10 min)
1. Estimand: primary R-I on channel PASS; secondaries R-N, I-N; axes separate; skipped = undemonstrated.
2. Provenance: packets/irrelevant.md source (cf72207b 2026-08-10, RULE-CANDIDATES #3, feedback_never_show_loopback.md) is real; relevant packet byte-identical to R36 tasks/packet.md.
3. Neutral packet: no git/patch/push/permission content; nothing in the task where it applies; length 67 vs 71 words; same header and position.
4. Tasks: the nine drafts differ only by the packet block and arm paths (tasks/*.md); common text = R38 tasks/<BUG>-common.md with r39-arms -> r41-arms.
5. Order: Latin square, drawn before execution (order.json).
6. Endpoints frozen: R38 repair/setup.sh, oracle/grade.sh, hidden_<BUG>.py, runtests.py, base OIDs unchanged.
7. Limits and claims: no memory-system or causal claim; one model; prior exposure; outbox proxy.
