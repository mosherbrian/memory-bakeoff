# Source repository and provenance separation

Tern, 2026-09-22. Decision: YES to a separate harness repository with a conventional
src/, tests/, documentation and explicit core/host-adapter boundary. Brian's usability
finding is valid. Packages are provenance records, not a usable distribution tree.
No extraction, path change or new implementation allocation during active P6-r11.

At the already-planned portability/multi-project successor boundary, include source
extraction as the first bounded stage. Choose the exact then-accepted source; do not
freeze today's r9 as the eventual product while r11 correction is unresolved. Inventory
its complete import/subprocess/data dependency closure, including r5/r6 tools and
local core copies. A two-directory copy is not sufficient. Separate test emulators
from live adapter code and expose a small documented public entry point.

Import into a fresh small repository without corpus, upstream checkouts, transient
DBs, credentials or campaign transcript. Conventional files are edited in place from
then on. Keep original repositories/commits/packages unchanged, no filter/rebase or
history rewrite. An import manifest maps EVERY imported file to this repository's
full commit, original path and sha256; record original remote/identity and acceptance
scope. Existing per-file history is not invented: normal history begins at import,
with provenance links backward. Packaging relocation changes must be declared and
verified, not called byte-identical when imports/paths changed.

Distinguish two decisions going forward: package acceptance says which bytes passed
which checks; promotion says which immutable harness repository commit is the selected
codebase. Record both with full pins. Neither means deployed, portable, recovery-proven
or production-ready beyond its evidence. Initially no publishing/remote creation is
performed by this ruling; Tern can authorize concrete repository operations at that
boundary under the charter, without making Brian the scheduler.

Extraction acceptance: clean checkout outside the 13GB research tree can run the
required tests and documented entry points without absolute campaign paths; dependency
closure/import gate complete, stdlib-only core retained, and provenance manifest verified
independently. The original frozen inputs and verdicts remain reproducible unchanged.
No duplicated runtime copies left as competing canonical implementations in the new tree.
Do not carry every historical fixture or claim into the runtime distribution.

Pair with MULTI-PROJECT-RULING-20260922.md at the same planned portability boundary,
but use separately reviewable commits/stages: establish relocated behavioral equivalence
first, then validated policy injection and two-loop authority/resource isolation.
Moving files must not conceal authorization changes. New naturally tabular isolation
cases may be data-driven; no conversion of the entire old suite or new framework.
No Go rewrite, compactor or dependency adoption follows from extraction.

Immediate remedy is CODE-MAP.md linked from campaign README, with one maintenance
owner (Tern) and update trigger (source acceptance/promotion), not another ledger.
Research remains primary; this ruling protects a reusable deliverable while avoiding
interruption of the actual live-path defect. Open its bounded contract when that
boundary arrives; no simultaneous migration of in-flight package inputs now.
