Tern: corvid independently review package.md and pin acceptance-checklist.md before
worker dispatch. <=15 minutes from cairn host-recorded dispatch. Write admission-review.md
with full contract hash and commit; bounded ACCEPTED/REJECTED, no edits to contract.
Cairn owns admission deadline and wakes Tern on rejection/timeout. On ACCEPTED,
verify unchanged contract, pin review/checklist and parent terminal, then execute the
conditional candidate release in package.md. No live release. All paths canonical:
/home/bmosher/memory-bake-off/campaign4/packages/P6-r8-case-execution
