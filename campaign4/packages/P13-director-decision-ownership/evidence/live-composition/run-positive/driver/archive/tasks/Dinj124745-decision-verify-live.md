Harmless P13 live fixture, package Dinj124745, verifier step. Do exactly this:
1. Check that /tmp/p13inj-NWlJh7/root/art/Dinj124745.txt contains exactly "P13 live witness Dinj124745".
2. Write one line to /tmp/p13inj-NWlJh7/root/art/Dinj124745-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-NWlJh7/root/bin/agent-loop claim --config /tmp/p13inj-NWlJh7/root/fxinj124745.json --qid Dinj124745 --step verify --outcome completed --artifact review=Dinj124745-review.txt
4. End your turn. Do not wake anyone.
