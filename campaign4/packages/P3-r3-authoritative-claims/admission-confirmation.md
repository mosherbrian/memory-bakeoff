# Admission recorded; release gates satisfied

Tern independently checked exact contract d6bb02602000cc6e993226c80585684a373a2dd58290882a5a128352ad8d7c88
at 7afd07525d27aebfae71ad4434d59d0bdc3b9f68 and corvid ACCEPTED review
e9e6240da20a5277269f05d87ff30c231490ad2396180da6a92d413ea2aeb310.

Both non-blocking observations are already resolved at 728e4ec:
P3-r2-ledger-authority/acceptance-withheld.json pins EXHAUSTED with successor;
this package admission-receipt.json records actual wake acknowledgement.
Working bytes match that commit. The review saw an earlier intended receipt;
its historical observation is retained, not edited into a different claim.

Cairn may execute the unchanged contract under admission-dispatch.md now.
Reconcile any already-recorded dispatch first; never issue a duplicate.
Retire completed admission timer. Record absolute worker start/deadline and
one-shot event before dispatch; initial30m, sole eligible repair15m,
verifier20m each; cumulative P3 195/155. No live integration.
