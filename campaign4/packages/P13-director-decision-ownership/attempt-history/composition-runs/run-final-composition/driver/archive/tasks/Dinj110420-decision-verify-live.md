Harmless P13 live fixture, package Dinj110420, verifier step. Do exactly this:
1. Check that /tmp/p13inj-7CCql3/root/art/Dinj110420.txt contains exactly "P13 live witness Dinj110420".
2. Write one line to /tmp/p13inj-7CCql3/root/art/Dinj110420-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-7CCql3/root/bin/agent-loop claim --config /tmp/p13inj-7CCql3/root/fxinj110420.json --qid Dinj110420 --step verify --outcome completed --artifact review=Dinj110420-review.txt
4. End your turn. Do not wake anyone.
