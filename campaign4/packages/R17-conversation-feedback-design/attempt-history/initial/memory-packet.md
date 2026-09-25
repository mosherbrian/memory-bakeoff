Saved notes from earlier conversations with Brian (the person you are working for). Apply them where relevant.

1. Write `python`, never `python3`, in everything Brian will run: shell commands, script shebangs, README snippets, one-liners. Same for `pip`, not `pip3`. On his Windows machine `python3` hits the Microsoft Store stub and silently does nothing; `python` works on his Fedora boxes too.

2. Never hand Brian a 127.0.0.1 or localhost address. He opens links from his desktop and phone, so a loopback address points at his own device. Bind services to 0.0.0.0, and display and record machines by resolvable hostname (for example strix-halo). 0.0.0.0 is fine to bind to but meaningless as an address to open.

3. When stopping or waiting on a process, act on a PID you captured or verified: save `$!` at launch (a pidfile), or list with `ps -eo pid,args | grep ...`, read the PID, then `kill <pid>`. Do not pipe a command-line pattern match straight into kill (`pkill -f`, `pgrep -f ... | xargs kill`), and do not wait with `while pgrep -f ...`: the pattern can also match the shell running the command. Note that `$!` after `setsid` is the wrapper, not the job.
