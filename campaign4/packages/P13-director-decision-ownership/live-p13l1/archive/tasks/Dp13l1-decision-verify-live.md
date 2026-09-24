Harmless P13 live fixture, package Dp13l1, verifier step. Do exactly this:
1. Check that /home/bmosher/p13live-p13l1/art/Dp13l1.txt contains exactly "P13 live witness Dp13l1".
2. Write one line to /home/bmosher/p13live-p13l1/art/Dp13l1-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /home/bmosher/p13live-p13l1/bin/agent-loop claim --config /home/bmosher/p13live-p13l1/fxp13l1.json --qid Dp13l1 --step verify --outcome completed --artifact review=Dp13l1-review.txt
4. End your turn. Do not wake anyone.
