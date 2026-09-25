# NET2-T: Reload office gateway router config (via handoff — cannot run from home laptop)

I am on your home laptop (strix-halo, Fedora) and cannot reach the office network from here. I did NOT reload anything myself. Below is the exact handoff for the office side.

## What needs doing
Reload `router.json` on the office gateway `cds-ai-a5410.cds.dmrc.lcl` (port 8300) and confirm it took effect.

## Hand to Qwen (office-side assistant) — exact commands to run ON an office machine

Run these on an office host that can reach `cds-ai-a5410.cds.dmrc.lcl` (e.g. an office workstation, NOT strix-halo):

```bash
# 1. Check current loaded config / revision (before)
curl -s http://cds-ai-a5410.cds.dmrc.lcl:8300/router/status | python -m json.tool

# 2. Trigger router config reload
curl -s -X POST http://cds-ai-a5410.cds.dmrc.lcl:8300/router/reload | python -m json.tool

# 3. Confirm it took effect (after) — revision/hash should change, routes should match new router.json
curl -s http://cds-ai-a5410.cds.dmrc.lcl:8300/router/status | python -m json.tool
```

If the gateway exposes a different reload endpoint, use whichever of these matches and report which was used:

```bash
curl -s -X POST http://cds-ai-a5410.cds.dmrc.lcl:8300/reload | python -m json.tool
curl -s http://cds-ai-a5410.cds.dmrc.lcl:8300/health | python -m json.tool
```

## What Qwen should send back
1. Output of the before/after status calls (revision or config hash + route list).
2. Confirmation the loaded revision matches the updated `router.json`.
3. If reload failed: the exact error body and HTTP code.

## Notes
- Nothing was run from strix-halo against the office gateway; home cannot reach `cds-ai-a54xx` hosts.
- Service bind reminder: if the gateway is restarted rather than reloaded, bind to `0.0.0.0` (not loopback) so it stays reachable on the office LAN.
