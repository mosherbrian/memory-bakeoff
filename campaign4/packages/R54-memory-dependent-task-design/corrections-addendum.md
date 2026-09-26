# Corrections to R53 memory-read counts (reanalysis; originals unchanged)
- My aggregate-table.json heuristic counted any tool call naming a /memory/ path. It showed A-N "1 ok read" (actually `ls -la <cwd> <memory dir>`, a listing of a non-existent/empty dir) and C-N/B-N "0/1". events.py (R53-event-reanalysis.json) gives: file_read_ok R 3, I 0, N 0; file_read_failed N 2 (C-N, B-N); A-N dir_listing 1 (not a read); total s2 tool uses 93. It matches director-event-counts.json on every expectation.
- The per-arm review's "N failed reads 3/3" is corrected to 2/3 plus one listing, as Tern recorded.
