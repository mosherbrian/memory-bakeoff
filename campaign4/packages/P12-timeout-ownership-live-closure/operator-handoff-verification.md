# OPERATOR-HANDOFF verification (independent, read-only)

Verifier: corvid. Package `P12-production-handoff-1`, verify step. Every value
below was read from this host; no file was modified. One line per check.

## 1. Manifest hash recomputation

PASS manifest sha256 = c478b0d0d3f700f1fb32f2ebe4d2b074ac57cc74ecd5adba07cf6972d0963fa8 (matches worker claim)
PASS binary_sha256 97a57db11aa8a4a87d89fd912804d42ce899bb35b3790742d790d424184a948f = /home/bmosher/.local/bin/agent-loop
PASS config_sha256 84e1c9cff48f157f038c787862709580aa777a99de8cb40b241a88e4c969cee6 = /home/bmosher/.config/agent-loop/campaign4.json
PASS handoff_sha256 b7c8160a9ff15f7a1aa3fbf82c5c34ff248ed8713290b3f7dc7cf6943bdf272f = OPERATOR-HANDOFF-20260923.md
PASS unit agent-loop@.service 7f70ee5790df63c156af60c32c71d2c87bb814cfb58ae910ac20b908a1768bbf
PASS unit agent-loop-liveness@.service 71c42358501c256fca8d9dfed74fe11d2250b65b772f90bce89dfe8adc5418c6
PASS unit agent-loop-liveness@.timer 502745ac8bc4431fe6d63177011451dcbfa678b87ea2ff9fe6023ced05fbd05b
PASS unit agent-loop-liveness-failed@.service 8ce594485762677aacb7ef923c6304c81c98da8c59370731a71e6de6cf11d03f

## 2. Status / pin commands

PASS `sha256sum /home/bmosher/.local/bin/agent-loop` = 97a57db1… (matches handoff pin)
PASS `sha256sum /home/bmosher/.config/agent-loop/campaign4.json` = 84e1c9cf… (matches handoff)
PASS binary strings carry `vcs.revision=8ad12b86fa82` (`mod agent-loop v0.0.0-20260923233318-8ad12b86fa82`)
PASS `agent-loop expose --json` known_limits = 5 bullets, matching the handoff verbatim
PASS `systemctl --user list-timers --all` shows `agent-loop-liveness@campaign4.timer` active on :00/:30 and the worker callback timer

## 3. Effect ownership (systemctl is-enabled / is-active)

PASS openwork.timer: disabled / inactive
PASS coax-dry.timer: disabled / inactive
PASS shadow-watch.timer: disabled / inactive
PASS agent-loop@campaign4.service: enabled / active
PASS agent-loop-liveness@campaign4.timer: enabled / active

## 4. Failure owner and known limits

PASS `systemctl --user show agent-loop-liveness@campaign4.service -p OnFailure` = agent-loop-liveness-failed@campaign4.service
PASS handler unit file exists (`systemctl --user cat agent-loop-liveness-failed@campaign4.service` resolves the unit)
PASS handoff known limits include live-acceptance (a) crashed-vs-restart-loop subtype, (b) 143 s contention, (c) local-commit-under-1 s assumption, (d) director checker-failure escalation up to 137 s, (e) timer/user-manager outage not covered

## Result

ALL PASS (17/17 checks). The handoff and its manifest match the live host
read-only; the required ownership states and the checker failure owner are
confirmed.
