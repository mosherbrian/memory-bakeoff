# Portable core dependency boundary — Tern

Brian's evening charter amendment recognizes the reusable harness as a secondary
successful outcome and keeps research first. Minimal dependencies and reuse are
now explicit constraints; the in-flight P6-r6 composition grant is unchanged.
No compactor, provider/library adoption, speculative port or packaging project
is authorized by this ruling. Use accepted components before extending machinery.

For each future package changing portable core Python source, require:

    python3 campaign4/tools/check_core_imports.py <exact candidate core src>

Pin the checker, Python version, core-root inventory and candidate source hash
in verification. The root must include the full portable core, not a convenient
subset. The accepted P5-r2 src at80092f9 is the initial baseline; host adapter
source is separately identified and excluded deliberately, never mixed into core
and called an own-module exception. No changes to frozen input bytes are needed.

The checker parses all Python files and allows the running Python standard
library plus modules owned by that core root; it checks function-local imports,
literal dynamic imports and relative escapes. Computed dynamic imports require
review. It is a static dependency check, not a security proof: arbitrary aliasing,
exec/eval, shell-outs, external data and OS-specific behavior still require review.
Corvid must challenge the guard with negative dependency mutations when first
used as an acceptance gate. A checker PASS does not prove portability, actual
runtime package availability on every Python version, or host-adapter correctness.

Current baseline check passes. Six director smoke probes cover stdlib/local
success, external import, function-local external import, literal dynamic external
import, computed dynamic import, and escaping relative import. These are author
checks, not independent certification. No new machinery work package is opened
for this small guard; independent challenge belongs to the next core-changing
package's existing verification, and no current grant is interrupted.

An exception requires an explicit prospective director amendment naming the
need, dependency, alternative/reuse considered, portability/cost consequence
and test changes. Do not silently expand the whitelist or use a local wrapper
to hide a third-party import. Host integrations stay behind replaceable adapters.
The research-first boundary review and evidence-based shadow gate remain binding;
recognizing the harness as a deliverable does not authorize an unlimited build.
