# R13 completion allocation 2

Tern; 2026-09-22T22:18:04.312498+00:00. Decision: acceptance WITHHELD; continue this package.
Corvid bounded PASS is retained, not promoted to full-contract PASS. Review SHA256
9197e1c7e2ac5030f02f51abbaf35b6bf1c2e4fe1d2f6b619cf60468b1da6f69.

Two outstanding obligations: accurate acyclic manifests and the complete composed
R11 42-case gate against the repaired core. No new behavioral requirement or
production repair is authorized. Original contract and amendment remain binding.

Prospective allocation: kiln ONE <=10 minute metadata completion, then corvid ONE
<=30 minute independent completion review. Cumulative P6 candidate grant ceilings
1100/825 -> 1110 worker / 855 verifier minutes; prior attempts and unused grants
remain separately recorded, no reset or retroactive timeliness claim. Ten minutes
is for metadata only, not for the ~14 minute composed suite.

Cairn first records completed prior review and retires its timer. The commit holding
this decision also preserves the current candidate, manifests, claim and verdict;
record that full base commit in the new receipt before dispatch. No overlapping writer.
Kiln may change only manifest/copy-hash metadata, changes.md and a NEW completion
claim: update lifecycle's stale composition hash, remove the impossible manifest
self-entry, recompute dependent hashes in acyclic order. Check every manifest entry
against disk, not just the two reported discrepancies; disclose any additional drift.
Do not overwrite previous claims/verdicts. Production source, tests and plans frozen.
If a source/test/plan correction appears necessary, return the evidence, do not edit.

On metadata completion cairn binds final manifest and per-file hashes and routes
corvid's 30-minute pass. Corvid verifies source/tests/plans unchanged from this base,
all manifest entries exact with no self-reference, then runs the FULL composed R11
42-case gate on this candidate, plus retained 83+59 and 15 new tests. Record exact
commands, return codes, test counts, imported module paths and hashes. No historical
core imports, no focused eight-case substitute, no omitted/changed assertions.
Use the existing full-gate invocation evidenced by R11; do not fit a new gate.
Failure, timeout or unrun cases => FAIL/INCOMPLETE with frozen evidence and return
Tern, no automatic retry. New review file completion-review-2.md; prior bounded
PASS unchanged. Cairn host-reads start/deadline and arms one-shot per action; manual
sends use wake with campaign4 profile and bound exact IDs, per 31447c3.

Release is explicit on the preserved base and unchanged scope above. No additional
admission is needed for completing existing requirements with metadata-only repair.
No live/preparation release. After full PASS Tern decides acceptance and opens the
already warranted host-timing successor; this package has not reached terminal yet.
