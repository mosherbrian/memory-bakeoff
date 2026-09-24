Harmless P13 live fixture, package Dinj120206, verifier step. Do exactly this:
1. Check that /tmp/p13inj-wWWRju/root/art/Dinj120206.txt contains exactly "P13 live witness Dinj120206".
2. Write one line to /tmp/p13inj-wWWRju/root/art/Dinj120206-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-wWWRju/root/bin/agent-loop claim --config /tmp/p13inj-wWWRju/root/fxinj120206.json --qid Dinj120206 --step verify --outcome completed --artifact review=Dinj120206-review.txt
4. End your turn. Do not wake anyone.
