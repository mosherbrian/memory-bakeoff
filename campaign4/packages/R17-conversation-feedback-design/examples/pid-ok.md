```
#!/bin/sh
PID=$(cat /tmp/rig.pid)
kill "$PID"
while kill -0 "$PID" 2>/dev/null; do sleep 1; done
nohup python rig.py > rig.log 2>&1 & echo $! > /tmp/rig.pid
```
