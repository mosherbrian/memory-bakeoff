# igw-console on strix-halo:8090 — systemd user unit

Create `~/.config/systemd/user/igw-console.service`:

```ini
[Unit]
Description=igw-console on strix-halo port 8090
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/igw-console --host 0.0.0.0 --port 8090
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable and start:

```
systemctl --user daemon-reload
systemctl --user enable --now igw-console.service
```

How to reach it:
Open http://strix-halo:8090 in a browser from your desktop or phone.
It is served from strix-halo on port 8090.
