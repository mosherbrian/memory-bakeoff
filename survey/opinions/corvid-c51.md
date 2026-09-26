# Contrarian, cycle 51 — encode the correction where the tool already looks

**corvid · 2026-09-26 · cycle 51.** Signed opinion; ROLES.md “best rival idea.” Existing sources
only. Confidence **medium**.

**Challenge to cross-host delivery as the first remedy.** For an illustrative project-scoped
correction (“use pnpm here”), the cheapest path is **not** a memory service that syncs to Claude
Code, Pi and local agents. It is **project configuration/defaults**: commit the setting where each
host already resolves it (a project config/instruction file, a wrapper script, a lockfile-driven
default). Then bytes stored, host loads, model applies and useful outcome all hold **without
Brian operating synchronization** — because the correction lives where the tool looks, not in a
separate memory that every host must fetch. This *removes* the delivery problem instead of
solving it.

**When delivery/handoff is needed.** When the correction **can’t be encoded as a default**
(judgment, exception, cross-project) or a host ignores project defaults. Then prefer **selective
task handoff** — put the specific correction in the next relevant task’s packet — over making every
host load every correction. Carry c50: inferred preferences are already in the baseline; failed
induction doesn’t force training; no universal whole-history saving.

**Missing operation.** The gap is **triage/encoding**: detecting that a correction is
project-scoped and writing it into the native default — not delivery plumbing.

**Reversal.** If the correction is cross-project, judgment-laden, or the host doesn’t honour
project defaults, native encoding fails and cross-host delivery/handoff earns its place.

— corvid. No experiment.
