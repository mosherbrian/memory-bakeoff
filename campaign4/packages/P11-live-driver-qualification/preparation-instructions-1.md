Execute preparation-release-1.json ONLY, four fresh idle seats. Before launch:
read host UTC, record start+15m deadline, collision-check names/workdirs against
campaign4 registry. Arm cleanup with systemd-run --user
--unit=campaign4-p11-prep1-cleanup --on-active=110m --timer-property=AccuracySec=1s
/usr/bin/python3 /home/bmosher/memory-bake-off/campaign4/packages/P11-live-driver-qualification/cleanup-preparation-1.py
Verify timer active and record actual cleanup deadline. Timer failure -> no launch.
Capture registry before, binary hash and exact argv. Launch each role once with
specified profile, environment exclusions and no message; raw stdout/stderr/rc/
host start/end at raw_path. On partial ambiguity reconcile, never repeat launch.
Capture post registry, real socket type/inode/mtime and actual runtime mapping.
No tasks, claims, Go run/dispatch or systemd fault permitted. Corvid existing10m
checks exact IDs/names/lanes/profile/workdirs/socket incarnation and candidate hash.
Return facts and binding verdict to Tern for materialized live signature. Retain
owned idle seats only until cleanup; no auto extension. No main-seat operations.
