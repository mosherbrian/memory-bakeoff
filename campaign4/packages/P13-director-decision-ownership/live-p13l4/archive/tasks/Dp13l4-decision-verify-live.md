Harmless P13 live fixture, package Dp13l4, verifier step. Do exactly this:
1. Check that /home/bmosher/p13live-p13l4/art/Dp13l4.txt contains exactly "P13 live witness Dp13l4".
2. Write one line to /home/bmosher/p13live-p13l4/art/Dp13l4-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /home/bmosher/p13live-p13l4/bin/agent-loop claim --config /home/bmosher/p13live-p13l4/fxp13l4.json --qid Dp13l4 --step verify --outcome completed --artifact review=Dp13l4-review.txt
4. End your turn. Do not wake anyone.
