# R58 readiness (offline; zero participant calls)
Runner copy operator/run-arm.sh (diff vs the pinned R56 runner: operator/run-arm.sh.diff). The R56 launcher, templates, fixture, scanner and settings are used unchanged from the R56 package, and the R57 grader is used unchanged.
- Memory snapshots with manifests: before-s1, after-s1, before-s2 (compared with after-s1 -> mem-compare), after-s2; ABSENT recorded when the store does not exist.
- Child exit and wrapper status are checked for both sessions. A failed session 1 holds the arm with no session 2. A failed session 2 is a HOLD in disposition.txt. Scan gate non-zero is a HOLD for manual disposition.
- The R57 grader is authoritative (grade-r57.json); manual=true is a HOLD for adjudication and never a silent primary.
- An immutable bundle per arm: freeze.sh copies the whole operator folder into evidence/<LABEL>/ via a temp dir and rename, writes arm-claim.json with every file hash, and refuses to overwrite.
Actual-runner stub regressions (tests/results.txt): ok (2 calls, 4 manifests, grade + bundle), session-1 failure (1 call, HOLD, no session 2, bundle), session-2 failure (HOLD exit=4), gate failure (HOLD for both gates), D one-call path (1 call), refuse-overwrite. Stub bundles are in evidence-stub/, not evidence/.
Unverified: live permission behaviour and model behaviour. One next step: Tern's decision on the frozen 14-call cohort on this runner (Max only; corvid 8 x 5 + final 10), or a 1-call D technical check first.
