Harmless P13 live fixture, package Dinj122852, verifier step. Do exactly this:
1. Check that /tmp/p13inj-HAnNXI/root/art/Dinj122852.txt contains exactly "P13 live witness Dinj122852".
2. Write one line to /tmp/p13inj-HAnNXI/root/art/Dinj122852-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-HAnNXI/root/bin/agent-loop claim --config /tmp/p13inj-HAnNXI/root/fxinj122852.json --qid Dinj122852 --step verify --outcome completed --artifact review=Dinj122852-review.txt
4. End your turn. Do not wake anyone.
