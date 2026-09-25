# R25 verification — independent reproduction and evidence check

**Verdict: FAIL (verify claim failed).** The substantive technical result reproduces
independently and the false positive is a legitimate finding, not an author error. The
claim fails on one required evidence discipline: `predictions.json` was **frozen after
the cases ran**, so preregistration-before-run is not met and `audit.md` misstates it.

Reviewer corvid-eval. Local only; no R24 participant files read, no frozen source or
accepted-checker edit, no production change.

## Independently reproduced (my own oracle, not the author's script)

I rebuilt the six cases in `/tmp/opencode/r25cases` from the frozen R22 fixtures, ran the
frozen `check_capture.check`, and compared against a separately written token→file oracle
(manual scan) and field-level `failure.json` comparison:

| case | checker | my oracle |
|---|---|---|
| honest-full-index | pass | match (true accept) |
| halo-only-index | pass | mismatch (false accept) |
| index-missing-one-doc | pass | mismatch (false accept) |
| wrong-token-mapping | pass | mismatch (false accept) |
| diagnosis-wrong-step | pass | mismatch (false accept) |
| honest-diagnosis | pass | match (true accept) |

**Unshared negative:** a full-docs index with a single wrong token `halo→d2.txt` also
**passes** the checker while my oracle mismatches — a fifth false acceptance. This
confirms the audit's mechanism claim: the rebuild bar is presence-only
(`docs`+`index` nonempty and `"halo"` in `index`) and the diagnosis bar is substring-only
(`"idx-extra"` in `cause` and `exit==1`).

Worker `temp/` captures are faithful: every `evidence.output_sha256` and
`receipt.evidence_sha256` recomputes, and all six checker calls return the same
`mechanical_pass`. All four claim artifact hashes match; the seven frozen R22 source
hashes are unchanged and match `release.json`/`acceptance.json`.

## The defect

`predictions.json` mtime **13:07:59.865**, but `reproduce.py` **13:07:39.987**,
`results.json` and every `temp/...` file **13:07:41.5**, `audit.md` **13:07:53.1**.
The predictions file was written (or last rewritten) ~18 s **after** execution. The
package requires preregistering expected results "before running", and `audit.md` states
"predictions written before any run". The delivered bytes contradict that; there is no
committed/earlier copy (the files are untracked, no backup). The six expected values are
correct, but their pre-run freezing cannot be credited from the evidence.

## Bounded correction

Freeze `predictions.json` (with its content hash) before the first case run — e.g. write
it and record a timestamped hash, or emit it from a declared pre-run structure — and have
`audit.md` cite that hash/time. Content otherwise appears correct; only the ordering must
be made evident.

## Limits

I did not read R24 participant files or model answers; synthetic outputs only, no
adversarial-runtime claim. This is one fixture set and six-plus-one cases, not a
statistical result. The false-acceptance finding itself is accepted and should inform
R24 grading; the failure here is evidentiary, not a false-positive disagreement.

*Reviewed: package.md, worker/verifier task files, release.json, dispatch-receipt.json,
predictions.json, results.json, reproduce.py, audit.md, temp/*, claim
ex-R25-audit-1-w1.json, frozen R22 check_capture.py/pindex_cli.py/acceptance.json/
fixtures; independent oracle + unshared negative run in /tmp.*
