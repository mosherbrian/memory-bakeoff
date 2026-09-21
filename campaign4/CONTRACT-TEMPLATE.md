# Work-package contract — PROVISIONAL

**This is a transcription of Tern's architecture §3, not a design.** P2 replaces
it with the frozen version. It exists only so P1 and P2 have something to be
written against.

```text
Task or question — and the decision it informs
Inputs and expected output
Completion check, or named judgment reader
Worker, verifier and duty owner
Time/spend limits
Permitted data, tools and writes
```

The controller generates IDs, timestamps and hashes. Standard environment
settings and limits inherit from named, versioned defaults.

| Work type | Additional contract |
|---|---|
| Experiment | metrics, controls, thresholds, exclusions, comparison method |
| Implementation | required behaviour, regression evidence, permitted changes |
| Judgment | named reader, bounded effort, required disposition |
| Higher-risk action | explicit permissions and recovery requirements |

Admission produces **either** an accepted contract **or one bounded explanation
of what is missing.** Not a negotiation.
