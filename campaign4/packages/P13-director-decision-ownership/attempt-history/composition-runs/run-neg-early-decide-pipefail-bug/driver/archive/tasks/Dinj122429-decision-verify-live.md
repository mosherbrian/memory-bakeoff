Harmless P13 live fixture, package Dinj122429, verifier step. Do exactly this:
1. Check that /tmp/p13inj-enEF7G/root/art/Dinj122429.txt contains exactly "P13 live witness Dinj122429".
2. Write one line to /tmp/p13inj-enEF7G/root/art/Dinj122429-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-enEF7G/root/bin/agent-loop claim --config /tmp/p13inj-enEF7G/root/fxinj122429.json --qid Dinj122429 --step verify --outcome completed --artifact review=Dinj122429-review.txt
4. End your turn. Do not wake anyone.
