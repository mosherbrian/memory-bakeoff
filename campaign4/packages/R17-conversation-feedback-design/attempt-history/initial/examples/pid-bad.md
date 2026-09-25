```
#!/bin/sh
pkill -f rig.py
while pgrep -f rig.py > /dev/null; do sleep 1; done
nohup python rig.py > rig.log 2>&1 &
```
