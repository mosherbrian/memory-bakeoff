Harmless P12 live fixture, package L6b-p12live2, verifier step. Do exactly this:
1. Check that /home/bmosher/p12live-p12live2/art/L6b-p12live2.txt contains exactly "P12 live witness L6b-p12live2".
2. Write one line to /home/bmosher/p12live-p12live2/art/L6b-p12live2-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /home/bmosher/p12live-p12live2/bin/agent-loop claim --config /home/bmosher/p12live-p12live2/fxp12live2.json --qid L6b-p12live2 --step verify --outcome completed --artifact review=L6b-p12live2-review.txt
4. End your turn. Do not wake anyone.
