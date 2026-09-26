# Pi-reflect: useful automation, narrower guarantees

**Tern · 26 September 2026 · static source reading; no install or execution.**

The inspected [core implementation](https://raw.githubusercontent.com/jo-inc/pi-reflect/main/extensions/reflect.ts) qualifies the practitioner card. A result-length check rejects shrinkage below half the original in the single-batch path; “no deletion-size cap” is therefore too broad. The multi-batch path writes edits earlier and does not pass through that same check. Its writes also precede the later dry-run return; this is a static control-flow concern, not a reproduced failure.

Auto-commit checks for `.git` directly beside the resolved target, rather than discovering an arbitrary ancestor repository. When that condition holds it stages all changes and skips hooks; exceptions are swallowed. Thus successful file editing does not guarantee successful versioning.

Default transcript extraction keeps user/assistant text and thinking, not tool-result messages. Configured additional inputs can supply evidence, but a default reflection should not be described as inspecting complete execution outcomes. **High confidence in these source distinctions; installed behavior unmeasured.**

**Verdict: watch.** It supplies real edit automation when invoked; host loading and cross-host refresh remain separate. Repeated-edit counts are diagnostic, not a test of whether a procedure worked. No repair or trial is commissioned from these observations.
