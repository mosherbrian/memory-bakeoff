Harmless P11 live fixture, package {QID}, verifier step. Do exactly this:
1. Check that {ARTIFACTS}/{QID}.txt contains exactly "P11 live witness {QID}".
2. Write one line to {ARTIFACTS}/{QID}-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   {BIN} claim --config {CONFIG} --qid {QID} --step verify --outcome completed --artifact review={QID}-review.txt
4. End your turn. Do not wake anyone.
