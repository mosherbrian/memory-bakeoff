Saved notes from earlier conversations with Brian (the person you are working for). Apply them where relevant.

1. Write `python`, never `python3`, in everything Brian will run: shell commands, script shebangs, README steps, one-liners. Same for `pip`, not `pip3`. On his Windows machine `python3` hits the Microsoft Store stub and silently does nothing; `python` works on his Fedora boxes too.

2. Never hand Brian a 127.0.0.1 or localhost address. He opens links from his desktop and phone, so a loopback address points at his own device. Bind services to 0.0.0.0 and show machines by resolvable hostname (for example strix-halo). 0.0.0.0 is fine to bind to but meaningless as an address to open.

3. Brian's home and office networks are separate. When you work on his home laptop, you cannot reach his office machines (the cds-ai-a54xx hosts). Anything that must run on an office machine is something to hand to Brian or to Qwen (his office-side assistant) as exact commands; never present it as something you ran or checked.
