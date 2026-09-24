Harmless P13 live fixture, package Dp13l2, verifier step. Do exactly this:
1. Check that /home/bmosher/p13live-p13l2/art/Dp13l2.txt contains exactly "P13 live witness Dp13l2".
2. Write one line to /home/bmosher/p13live-p13l2/art/Dp13l2-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /home/bmosher/p13live-p13l2/bin/agent-loop claim --config /home/bmosher/p13live-p13l2/fxp13l2.json --qid Dp13l2 --step verify --outcome completed --artifact review=Dp13l2-review.txt
4. End your turn. Do not wake anyone.
