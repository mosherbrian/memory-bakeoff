Harmless P13 live fixture, package Dinj123323, verifier step. Do exactly this:
1. Check that /tmp/p13inj-iLD9uS/root/art/Dinj123323.txt contains exactly "P13 live witness Dinj123323".
2. Write one line to /tmp/p13inj-iLD9uS/root/art/Dinj123323-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-iLD9uS/root/bin/agent-loop claim --config /tmp/p13inj-iLD9uS/root/fxinj123323.json --qid Dinj123323 --step verify --outcome completed --artifact review=Dinj123323-review.txt
4. End your turn. Do not wake anyone.
