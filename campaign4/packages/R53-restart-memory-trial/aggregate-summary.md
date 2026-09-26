# R53 aggregate summary (operator; verifier recomputes)

Participant calls: 18/18, all child exit 0 and wrapper 0. Saved memory: N 0/3, I 3/3, R 3/3. Primary joint (measured AND restored): N 3/3, I 3/3, R 3/3; R-I = 0 in blocks A, C, B.

| arm | saved | mem reads ok/fail | Bash/Read/Write | denials | measured | restored | gates | verifier |
|---|---|---|---|---|---|---|---|---|
| A-N | False | 1/0 | 10/3/1 | 0 | True | True | clean/clean | PASS |
| A-I | True | 0/0 | 11/0/1 | 0 | True | True | clean/clean | PASS |
| A-R | True | 1/0 | 10/1/1 | 0 | True | True | clean/clean | PASS |
| C-R | True | 1/0 | 7/1/1 | 0 | True | True | clean/clean | PASS |
| C-N | False | 0/1 | 7/1/1 | 0 | True | True | clean/clean | PASS |
| C-I | True | 0/0 | 7/0/1 | 0 | True | True | clean/clean | PASS |
| B-I | True | 0/0 | 8/0/1 | 0 | True | True | clean/clean | PASS |
| B-R | True | 1/0 | 8/4/1 | 0 | True | True | clean/clean | PASS |
| B-N | False | 0/1 | 5/1/1 | 0 | True | True | clean/clean | PASS |

Limits: one model (claude-sonnet-5), synthetic simulated services, ceiling effect (all arms succeeded), index injection inferred not observed, same-user evidence, heuristic scan plus manual audit. Memory-read counts here are operator heuristics (tool calls naming a /memory/ path); the verifier's transcript count is authoritative. No pooling with R43/R49/R52. Active operator minutes: unknown (not measured).
