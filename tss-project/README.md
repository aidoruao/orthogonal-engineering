# TSS v10

Production-grade AI accountability infrastructure. Standard library only,
fully offline, 18 files.

Read the [Monument](tss_monument/TSS_v10_MONUMENT.txt) first — it is the
single source of truth for what this system is, does, and does not do.

Quick start:

```bash
python3 tss_web/tss_server.py       # web UI at http://localhost:8000
python3 tss_cicd/tss_cicd.py        # hermetic build gate
python3 tss_tests/tss_tests.py      # unit tests
```
