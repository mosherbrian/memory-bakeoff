# Execute signed idle preparation only
Use preparation-release-1.json verbatim. Host start/deadline10m and timer before
work. Refuse name/workdir collision in live registry. Create listed workdirs.
Arm automatic cleanup BEFORE launch:
systemd-run --user --unit=campaign4-p8-prep1-cleanup --on-active=40m /usr/bin/python3 /home/bmosher/memory-bake-off/campaign4/packages/P8-go-unattended-qualification/cleanup-preparation-1.py
Capture command/rc, systemctl --user is-active campaign4-p8-prep1-cleanup.timer
and actual host deadline. Stop if timer not active. Idle timeout45m extra fallback.
Launch each JSON argv once with profile and unset environment as specified.
Capture raw start/end/argv/rc/stdout/stderr to role.raw_path immediately, even failure.
On partial/ambiguous failure preserve registry and return; no repeat or task.
On success capture registry, actual real socket metadata and streams if present;
no invented end/item/source timestamps. Three fresh seats remain idle. No task,
claim, agent-loop dispatch/run/callback or adoption authorized. Corvid5m binding
check of raw IDs/names/lanes/profile/workdirs/socket incarnation, source binary
hash and config compatibility then return. Do not fabricate a summary-schema
binding when raw facts suffice; Tern authors concrete live config/signature next.
Cleanup on abort remains authorized; archive before stop/remove owned IDs only.
No main seat or unrelated timer mutation. Runtime shared wrappers used as-is;
no source-time instrumentation needed. Capture effective model/config environment
at launch where available, never credentials. Return actual facts and readiness.
