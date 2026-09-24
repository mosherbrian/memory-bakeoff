Harmless P13 live fixture, package Dinj114524, verifier step. Do exactly this:
1. Check that /tmp/p13inj-wXlk0e/root/art/Dinj114524.txt contains exactly "P13 live witness Dinj114524".
2. Write one line to /tmp/p13inj-wXlk0e/root/art/Dinj114524-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-wXlk0e/root/bin/agent-loop claim --config /tmp/p13inj-wXlk0e/root/fxinj114524.json --qid Dinj114524 --step verify --outcome completed --artifact review=Dinj114524-review.txt
4. End your turn. Do not wake anyone.
