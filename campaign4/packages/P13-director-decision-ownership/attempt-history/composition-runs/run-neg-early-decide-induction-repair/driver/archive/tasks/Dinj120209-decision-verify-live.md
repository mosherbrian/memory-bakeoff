Harmless P13 live fixture, package Dinj120209, verifier step. Do exactly this:
1. Check that /tmp/p13inj-PX65s3/root/art/Dinj120209.txt contains exactly "P13 live witness Dinj120209".
2. Write one line to /tmp/p13inj-PX65s3/root/art/Dinj120209-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-PX65s3/root/bin/agent-loop claim --config /tmp/p13inj-PX65s3/root/fxinj120209.json --qid Dinj120209 --step verify --outcome completed --artifact review=Dinj120209-review.txt
4. End your turn. Do not wake anyone.
