Harmless P12 live fixture, package L1-p12live1, verifier step. Do exactly this:
1. Check that /home/bmosher/p12live-p12live1/art/L1-p12live1.txt contains exactly "P12 live witness L1-p12live1".
2. Write one line to /home/bmosher/p12live-p12live1/art/L1-p12live1-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /home/bmosher/p12live-p12live1/bin/agent-loop claim --config /home/bmosher/p12live-p12live1/fxp12live1.json --qid L1-p12live1 --step verify --outcome completed --artifact review=L1-p12live1-review.txt
4. End your turn. Do not wake anyone.
