# Implementation language and delivery status — Tern decision

Recorded UTC: 2026-09-22T04:42:46.460746+00:00
Authority: ordinary implementation decision under Brian's charter, including
the evening amendment recognizing a reliable portable harness as a secondary
successful outcome, with research primary and reuse/minimal dependencies binding.

## Decision

Choose **A: keep Python**. The existing Python implementation is the intended
harness implementation to validate, deliver and maintain, not disposable work
awaiting an already-decided rewrite. No Go port is scheduled or implicitly owed.
A later port remains possible only under a separate evidence-backed decision.
This preserves C's option to port after behavior stabilizes without promising it.

This is a choice of implementation, NOT a declaration of operational readiness.
Accepted core artifacts retain their recorded acceptance scope; the host harness
is a candidate until the required live recovery, evidence-referenced shadow,
rollback and cutover gates pass. Simulated PASS does not authorize adoption.

## What the record actually said

ACCEPTED-ARCHITECTURE.md §6 line144 says:
“Use Go if that remains the agreed implementation choice.”
That conditional sentence does not establish an agreement to use Go, and this
record does not invent one retrospectively.

There WAS a Python prototype decision: P3-core-validator/package.md lines28–30
explicitly require Python3 standard library and describe a “replaceable prototype
core,” without committing a live adapter's language. The gap was the subsequent
prototype-to-deliverable decision, not the total absence of a language choice.
This ruling now supersedes that provisional status for future implementation
work and resolves the architecture's conditional language sentence in favor of
Python. Frozen architecture/contracts/hashes remain unchanged as historical inputs;
new packages pin this ruling alongside them. No prior acceptance is retroactively
expanded into a live-readiness claim.

## Why

We have accepted state, persistence, authority and clock work plus executable
regression evidence in Python. Current defects concern actual host integration,
identity, evidence and acceptance—not an observed inability of Python to serve
the task. Rewriting now would add a second implementation and fresh verification
work before the behavior is established, delaying the primary research goal.

Stdlib-only core dependencies and a replaceable host adapter already support
reuse. Python availability/version and OS-specific behavior are deployment
requirements to document and validate; stdlib-only is not universal portability.
A Go binary may be useful for a particular deployment, but we have no specified
target that currently requires it. Do not confuse a prospective packaging benefit
with evidence that the present implementation must be replaced.

Existing tests and traces are reusable behavioral specifications even across a
port; they are not discarded. Their passing results do not certify new code.
Any replacement must re-establish negative sensitivity, cross-implementation
conformance, persistence/restart compatibility and relevant live/shadow evidence.
Live evidence collected now remains evidence about these pinned Python bytes,
not automatic evidence for a future Go implementation.

## Consequences and revisit trigger

Continue the current P6-r7 allocation unchanged. No rewrite, port, extra dependency,
packaging project, scope expansion, or extra budget follows from this ruling.
Protect the core boundary through PORTABLE-CORE-RULING-20260922.md and its static
import guard; keep runtime/provider/agent-deck specifics in replaceable adapters.
At delivery, explicitly record tested Python/OS requirements and adapter limits;
do not claim broad portability without testing the claimed targets.

Revisit only for a concrete target or measurement showing interpreter deployment,
performance, distribution, or another material requirement cannot reasonably be
met by the current approach. Tern then records the target, alternative costs,
reuse plan and bounded migration/validation package; Brian retains scope/budget
changes. Behavioral maturity makes a port easier to assess, not automatically
necessary. Research-first and the smallest useful reliable harness remain the
criteria at subsequent package boundaries.
