# Dockerfile for PR #20 Expansion Tools

The main Dockerfile for PR #20 expansion infrastructure has been moved to the repository root as `Dockerfile.pr20`.

## Building the Docker Image

From the repository root:

```bash
docker build -f Dockerfile.pr20 -t pr20-expansion:latest .
```

## Running the Container

```bash
# Verify tools
docker run --rm pr20-expansion:latest python pr20_expansion_tools/verify_tools.py

# Dry run
docker run --rm pr20-expansion:latest \
  python pr20_expansion_tools/expansion_orchestrator.py --dry-run --target-loc 50000

# With output volume
docker run --rm -v $(pwd)/output:/workspace/output \
  pr20-expansion:latest \
  python pr20_expansion_tools/expansion_orchestrator.py \
  --target-loc 50000 --output-dir /workspace/output --dry-run
```

## Features

- **Deterministic**: `PYTHONHASHSEED=42` and UTC timezone
- **Minimal**: Based on python:3.11-slim
- **No external deps**: Only Python stdlib
- **Reproducible**: Same inputs = same outputs

See main documentation in repository root for full usage.
