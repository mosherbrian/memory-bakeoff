Harmless P12 live fixture, package {QID}. Do exactly this and nothing else:
1. Write the single line "P12 live witness {QID}" to the file {ARTIFACTS}/{QID}.txt.
2. Run this exact command:
   {BIN} claim --config {CONFIG} --qid {QID} --step worker --outcome completed --artifact out={QID}.txt
3. End your turn. Do not wake anyone.
