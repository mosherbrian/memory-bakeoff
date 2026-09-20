# CORVID-S4-8-VERIFY.md — corvid-dsh verification of QUEUE row S4-8

**Verdict: PASS** — 2026-09-16 14:45 PDT. kiln-flash authored; corvid-dsh
verifies (independence holds). Machine row: per the adjudication 5b note,
verification = self-test + live rows, both re-run this pass.

## Declared check

`python3 $HOME/.config/agent-deck/rowcheck --self-test` → **10/10 logic
controls hold, rc 0**: clean holds; missing artifact, failing check,
prose-only artifact, duplicate id, absent row, non-executable check,
either-or informational alternative, unquoted path, check-less row all
detected.

## No LLM, no second dialect

- Source scan: no `openai`/`anthropic`/`requests`/`llm` imports or calls —
  pure deterministic Python, as the row requires ("No LLM in it").
- Exit contract: named findings printed, rc 1 iff findings, rc 0 clean — the
  `scripts/check_*.py` shape, not a new one. The self-test's finding classes
  match the S4-11 guards' contract (verified separately).

## Live rows

`rowcheck <row>` re-run across all eleven sprint-4 rows this pass: rc 0 on
S4-1/2/3/4/5/9/10/11/12/13 and — after the fix below — S4-8 itself. Zero
findings on every done row; the gate demonstrably parses real queue rows,
resolves real declared checks, and reports real statuses.

## Infra gap found and fixed during verification

The done note says rowcheck was "symlinked into each zcode seat's $HOME so
the declared check resolves fleet-wide." **This seat's symlink was missing**
(`$HOME/.config/agent-deck/` absent under
`~/.local/share/agent-deck/zcode-homes/zc-repo-glm-dsh3/`), so the declared
check exited 2 here — the only rc≠0 in the sweep. Fixed during verification
by creating the missing symlink to `/home/bmosher/.config/agent-deck`;
`rowcheck S4-8` now rc 0 from this seat. Non-verification note for cairn:
audit the other seats' symlinks rather than trusting "each".

Row S4-8 moves done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 14:45 PDT.
