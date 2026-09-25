# R23 wording-2 review — corvid-eval

**Verdict: PASS.** The change is exactly one nudge string plus its test expectation; the
new text matches the released wording byte-for-byte; the focused test passes in the
private v2 source; no enforcement/schema/validation/blocking was added; installed v1
stays untouched.

Reviewer: corvid-eval. One look, local only; no matrix, live witness or install.

## Intake (hashes recomputed)
- `wording-2.diff` sha `c0598c1d…` = claim `diff_sha256`.
- Private `release-v2/agent-loop-bab903edd9f9/bin/agent-loop` = `eb9cc019…` (claim,
  BUILD.json); `BUILD.json` commit `bab903edd9f9…`.
- Installed `/home/bmosher/.local/bin/agent-loop` = `612e3c5c…` = R23 v1, **unchanged** —
  v2 is not installed, as required.

## Exact wording and scope (independently confirmed)
- Release `with` = `What happens next? If it is yours, do it now; if not, who has it, and do they know?`
  It appears verbatim in the diff `+` line, in the built `internal/loop/loop.go:426`, and
  in the test expectation `nudge_r23_test.go:28`; the old string `What happens next, who
  does it, and by when?` appears only on the `-` line. Byte-for-byte match with Tern's
  released replacement.
- `wording-2.diff` changes **only** the `Nudge` constant (question 2) and the one test
  `want` string. Questions (1) and (3), the `instructions()` placement (worker+verifier)
  and the director decision-notice placement, and the "prompt, not a check" comment are
  untouched. No artifact, schema, receipt, validation, parser, blocking or authority
  change.

## Reproduction
Extracted the private v2 source tarball to `/tmp/opencode/r23v2`, `GOPROXY=off`, go1.27.1:
`go test ./internal/loop/ -run TestNudgeReachesWorkerVerifierAndDirector -v` → **PASS**
(the test asserts the new string reaches kiln/worker, corvid/verifier and tern/director).

## Activation
Release states Tern activates at an idle boundary and restarts a stable 24 h observation
on v2, preserving R23v1 exposure (active since 20:15:37Z) without silently splicing
versions. No install in the author grant.

*Reviewed: wording-2-release.json, wording-2-claim.json, wording-2.diff, release-v2
(BUILD.json, bin, src tarball), installed binary; independent focused test.*
