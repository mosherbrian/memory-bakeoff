# P2 sole repair — director reconciliation

Tern independently observed and hashed the repaired outputs at
**2026-09-21T15:57:15Z**, before the unchanged **15:58:36Z** repair deadline.
The worker completion wake was also received. The diff from preserved v1 is
exactly one replacement in walkthrough.md: `16:09:31Z` → `16:08:16Z`.
All other bytes in the four outputs are unchanged.

| Artifact | SHA256 |
|---|---|
| contract.md | fd573ad3d068f90afb3182fc145736c828eb34dde0798a5ebc1970076d13845e |
| transitions.md | 77b795749631b65d7b1907bb25c65c8f03dd5faad0d43c6a355ed65f93b40252 |
| ownership.md | c8126700897cfcb78cb25c7e481c5ecb32518858a5540e2d804874fdf84e4150 |
| walkthrough.md | c45c72a268054d83e4878e7e542cedd3dfa00f9773d431ada4047e2bf183238e |

Original v1 outputs and FAIL verdict are preserved in
`campaign4/p2-attempt-history/v1/`. The repair allocation has been consumed;
there is no second repair. This receipt is not independent verification or
final acceptance. P2 remains CHECKING until corvid's post-repair disposition.

Tern sets the post-repair verification deadline to **16:27:15Z**, 30 minutes
from this recorded observation of completion. Cairn owns routing to corvid and
retiring the timer on completion. No duplicate verifier attempt is authorized.
