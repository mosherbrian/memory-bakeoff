# Negative control: the Gen120 witnesses run against the PRE-FIX code

Both rival reviewers noted that 'each witness was confirmed to fail against the
old runner' was unverifiable from the repository - I had run it and kept no
artifact. glm-5.3 also observed the claim was too strong. Both were right.

Method: `git worktree add --detach` at a983f9bcc3f6 (the Gen119 trigger commit,
before any F1/F2/F3 repair), copy in tests/test_gen120_evidence_closure.py and
the pre-fix runner under the stable name, run the file.

Result: **19 failed, 13 passed, 4 skipped**.

So 19 of the 36 witnesses genuinely detect the defects. The 13 that pass in both
trees are prior-attempt immutability and honesty checks - they are regression
guards, not defect witnesses, and they SHOULD pass against old code. The 4 skips
are attempts that do not exist at that commit.

The corrected claim: 19 witness the repairs; 36 is the file's size, not its
detection power. Reporting 36 as though all of them witnessed something was an
overclaim of exactly the kind this project keeps having to retract.

## Failing at the pre-fix commit (these are the real witnesses)
```
FAILED tests/test_gen120_evidence_closure.py::test_an_incomplete_pre_marker_set_denies_closure
FAILED tests/test_gen120_evidence_closure.py::test_an_unexpected_artefact_denies_closure
FAILED tests/test_gen120_evidence_closure.py::test_an_unmanifested_artefact_denies_closure
FAILED tests/test_gen120_evidence_closure.py::test_a_seal_that_disagrees_with_the_bytes_is_detectable
FAILED tests/test_gen120_evidence_closure.py::test_changing_one_raw_byte_fails_verification
FAILED tests/test_gen120_evidence_closure.py::test_closure_reports_a_complete_required_set
FAILED tests/test_gen120_evidence_closure.py::test_deleting_raw_jsonl_fails_verification
FAILED tests/test_gen120_evidence_closure.py::test_fire_without_a_source_commit_is_refused
FAILED tests/test_gen120_evidence_closure.py::test_head_differing_from_the_authorised_commit_fails_before_any_call
FAILED tests/test_gen120_evidence_closure.py::test_raw_capture_refuses_to_overwrite
FAILED tests/test_gen120_evidence_closure.py::test_raw_jsonl_is_listed_in_the_manifest
FAILED tests/test_gen120_evidence_closure.py::test_seal_agreement_is_a_three_way_check
FAILED tests/test_gen120_evidence_closure.py::test_the_contract_records_the_runtime_authorisation
FAILED tests/test_gen120_evidence_closure.py::test_the_id_balance_gate_is_exact_not_within_one
FAILED tests/test_gen120_evidence_closure.py::test_the_manifest_digest_comes_from_disk_not_from_the_argument
FAILED tests/test_gen120_evidence_closure.py::test_the_marker_gate_is_never_handed_an_authored_true
FAILED tests/test_gen120_evidence_closure.py::test_the_marker_is_written_after_the_closure_check
FAILED tests/test_gen120_evidence_closure.py::test_the_output_path_follows_the_authorised_generation
FAILED tests/test_gen120_evidence_closure.py::test_the_runner_carries_no_hardcoded_generation_or_commit
```


## Addendum, round 5

This document records **19 failed / 13 passed / 4 skipped**, which was accurate
when measured. The witness file has since grown - round 3 added
`test_the_sealed_contract_hash_actually_recomputes`, round 5 added four witnesses
for the malformed-answer repair - so re-running the method today gives a
different total against the same pre-fix commit.

The document pinned neither the test-file version nor its hash, so its numbers
were reproducible only on the day. Raised by both reviewers at round 5. The
method remains correct; only the totals move as witnesses are added. Re-measure
rather than cite these figures, and record the witness-file sha256 alongside any
future control.
