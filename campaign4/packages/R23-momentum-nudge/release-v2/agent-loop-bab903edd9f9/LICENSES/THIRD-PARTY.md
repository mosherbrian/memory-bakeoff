# Third-party code in the agent-loop binary

Linked modules (from `go version -m` on the release binary; the release
script writes the exact list into `BUILD.json`):

| Module | License |
|---|---|
| modernc.org/sqlite, modernc.org/libc, modernc.org/mathutil, modernc.org/memory | BSD-3-Clause style (The ... Authors); SQLite itself is public domain |
| golang.org/x/sys | BSD-3-Clause (The Go Authors) |
| github.com/remyoudompheng/bigfft | BSD-3-Clause (The Go Authors) |
| github.com/google/uuid | BSD-3-Clause (Google Inc.) |
| github.com/dustin/go-humanize | MIT |
| Go standard library and runtime | BSD-3-Clause (The Go Authors) |

No module was added for the preview. The full license texts are in the Go
module cache (`go env GOMODCACHE`) under each module's version directory.
agent-loop itself declares no license yet (private repository).
