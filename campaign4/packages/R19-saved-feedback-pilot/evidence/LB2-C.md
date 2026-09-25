[Unit]
Description=igw-console on strix-halo:8090
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/igw-console --host 0.0.0.0 --port 8090
Restart=on-failure

[Install]
WantedBy=default.target

Note: enable with `systemctl --user enable --now igw-console`, reach it at http://strix-halo:8090.
If DNS is unavailable, use http://<strix-halo-IP>:8090 instead.
