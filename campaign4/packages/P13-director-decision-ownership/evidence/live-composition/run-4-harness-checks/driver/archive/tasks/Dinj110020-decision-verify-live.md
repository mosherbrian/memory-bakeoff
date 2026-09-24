Harmless P13 live fixture, package Dinj110020, verifier step. Do exactly this:
1. Check that /tmp/p13inj-aWjwJ1/root/art/Dinj110020.txt contains exactly "P13 live witness Dinj110020".
2. Write one line to /tmp/p13inj-aWjwJ1/root/art/Dinj110020-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-aWjwJ1/root/bin/agent-loop claim --config /tmp/p13inj-aWjwJ1/root/fxinj110020.json --qid Dinj110020 --step verify --outcome completed --artifact review=Dinj110020-review.txt
4. End your turn. Do not wake anyone.
