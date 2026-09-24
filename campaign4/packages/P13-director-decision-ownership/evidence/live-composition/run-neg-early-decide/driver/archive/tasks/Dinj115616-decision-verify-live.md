Harmless P13 live fixture, package Dinj115616, verifier step. Do exactly this:
1. Check that /tmp/p13inj-LueLFH/root/art/Dinj115616.txt contains exactly "P13 live witness Dinj115616".
2. Write one line to /tmp/p13inj-LueLFH/root/art/Dinj115616-review.txt: "PASS" if it does, "FAIL" and the reason if not.
3. Run this exact command, with completed for PASS or failed for FAIL:
   /tmp/p13inj-LueLFH/root/bin/agent-loop claim --config /tmp/p13inj-LueLFH/root/fxinj115616.json --qid Dinj115616 --step verify --outcome completed --artifact review=Dinj115616-review.txt
4. End your turn. Do not wake anyone.
