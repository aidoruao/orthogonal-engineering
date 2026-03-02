# Orthogonal Engineering Compendium

> **READ BEFORE GENERATING OR MODIFYING CODE.**
> This document is the canonical strategic knowledge base for this repository.
> Every environmental assumption, tactical fix, and verification procedure is
> recorded here.  AI agents and human contributors alike **must** consult this
> compendium before making changes, especially to CI workflows, weight
> generation, hashing, or cross-platform code.

---

## 1. Introduction / Rationale

### 1.1 Why Windows CI Crashed (PR #27)

PR #26 introduced deterministic weight generation and Merkle root verification.
The CI workflow only targeted `ubuntu-latest`, so Windows-specific failures were
not caught during review.  After #26 merged the following issues were discovered
on the Windows runner:

| Root cause | Symptom |
|---|---|
| CRLF line endings in checked-out Python scripts | `SyntaxError` / hash mismatch |
| Default `cp1252` stdout encoding on Windows | `UnicodeEncodeError` on any UTF-8 output |
| Hard-coded forward-slash paths | `FileNotFoundError` on Windows |
| Unpinned `safetensors` version | `AttributeError` for int64 tensors |

PR #27 fixed these blockers so that CI passed on all three runners.

### 1.2 Why Cross-Platform Determinism Is Critical (PR #28)

The orthogonal engineering methodology requires that every generated artifact
(weights, datasets, Merkle roots) is **byte-for-byte reproducible** regardless
of:

* Operating system (Linux, macOS, Windows)
* Python micro-version (3.11.x vs 3.12.x)
* CI runner hardware (x86-64, arm64)
* Local vs. cloud execution environment

Without this guarantee, audit trails are meaningless — the same code commit
could produce different Merkle roots on different machines, making
reproducibility impossible to verify.

---

## 2. Tactical Fixes / Lessons Learned

### 2.1 Line-Ending Normalisation

**Problem:** Git on Windows checks out text files with CRLF endings by default,
making SHA-256 hashes differ from the LF-only Linux baseline.

**Fix:** Add a `.gitattributes` file with:

```gitattributes
* text=auto eol=lf
*.py  text eol=lf
*.yml text eol=lf
*.json text eol=lf
*.md  text eol=lf
```

This forces all text files to use LF in the working tree on every OS.

### 2.2 Path Handling

**Problem:** Code used hard-coded forward-slash strings (`"seed/pr_25_seed.yaml"`)
that fail on Windows when joined with `os.path.join`.

**Fix:** Always use `pathlib.Path` for path construction.  `pathlib` normalises
separators on every platform transparently.

```python
# BAD
path = "ontology/pr26_ontological_issues.json"

# GOOD
from pathlib import Path
path = Path("ontology") / "pr26_ontological_issues.json"
```

### 2.3 Encoding Flags

**Problem:** On Windows, Python's stdout/stderr default to the system locale
encoding (`cp1252`), not UTF-8.  Any code writing Unicode characters to stdout
will crash or produce garbled output.

**Fix:** Set `PYTHONIOENCODING=utf-8` in every CI job:

```yaml
env:
  PYTHONIOENCODING: utf-8
```

This must appear at the workflow level (not just per-step) so it is inherited
by all subprocesses.

### 2.4 CI Matrix

**Problem:** The original `gate.yml` only tested `ubuntu-latest` with Python
3.11.  Platform-specific bugs went undetected.

**Fix:** The `pr28-determinism.yml` workflow uses a full matrix:

```yaml
matrix:
  os: [ ubuntu-latest, macos-latest, windows-latest ]
  python-version: [ "3.11", "3.12" ]
```

---

## 3. Environmental Assumptions

The following assumptions are explicitly tested by `tests/test_falsification.py`.
If any assumption fails, CI exits with a non-zero code and reports the exact
file, line, OS, and Python version.

| ID | Assumption | Test |
|---|---|---|
| F_PLATFORM_001 | `hashlib.sha256` of a fixed byte string returns the same hex digest on every platform | `test_f001_seed_bytes_sha256_deterministic` |
| F_PLATFORM_002 | `struct.unpack_from('<q', …)` and two's-complement int64 masking produce known numeric vectors | `test_f002_int64_arithmetic_vectors` |
| F_PLATFORM_003 | `pathlib.Path` resolves relative paths and normalises separators correctly on all OSes | `test_f003_pathlib_path_independence` |
| F_PLATFORM_004 | stdout and stderr use UTF-8 encoding (requires `PYTHONIOENCODING=utf-8`) | `test_f004_stdout_utf8_encoding` |
| F_PLATFORM_005 | `struct.pack('<q', value)` encodes int64 in little-endian regardless of host endianness | `test_f005_struct_pack_little_endian` |

### 3.1 Python Versions

Supported and tested: **Python 3.11** and **Python 3.12**.

Known difference: Python 3.12 changed the default hash seed for built-in types
(`PYTHONHASHSEED`).  All code that needs reproducible ordering must use
**explicit sort keys** or **canonical serialisation** — never rely on `dict`
ordering or `hash()` of arbitrary objects.

### 3.2 Integer Arithmetic

All weight generation uses **emulated signed 64-bit two's-complement
arithmetic**:

```python
def _int64(value: int) -> int:
    value = value & 0xFFFFFFFFFFFFFFFF
    if value >= 0x8000000000000000:
        value -= 0x10000000000000000
    return value
```

Python's `int` is arbitrary precision, so no native overflow occurs.  The mask
ensures platform-independent behaviour that matches C `int64_t` semantics.

### 3.3 UTF-8 Output

All file I/O must specify `encoding="utf-8"` explicitly:

```python
# BAD (uses platform default on Windows)
with open(path, "w") as f:
    f.write(data)

# GOOD
with open(path, "w", encoding="utf-8") as f:
    f.write(data)
```

### 3.4 CI Runners

| Runner | OS | Architecture |
|---|---|---|
| `ubuntu-latest` | Ubuntu 22.04+ | x86-64 |
| `macos-latest` | macOS 14+ (Sonoma) | arm64 (Apple Silicon) |
| `windows-latest` | Windows Server 2022 | x86-64 |

**No local device assumptions:** all determinism verification must pass inside
CI runners.  Do not rely on developer-local tools or environment variables not
set in the CI YAML.

### 3.5 Filesystem Path Independence

* Use `pathlib.Path` everywhere.
* Use `/` operator for path joining, not string concatenation.
* Do not hard-code absolute paths.
* Compute paths relative to `Path(__file__).parent` anchors.

---

## 4. Guidelines for Future Contributors / AI

1. **Read this compendium first.**  Understanding the environmental constraints
   above prevents re-introducing fixed bugs.

2. **Consult `ontology/pr26_ontological_issues.json` before making changes.**
   Each issue has an ID, root cause, status, and resolution notes.  If you are
   fixing something that maps to an existing issue, update the JSON.

3. **Run the determinism and falsification tests locally before pushing.**

   ```bash
   python tests/test_cross_platform_determinism.py
   python tests/test_falsification.py
   ```

4. **Cross-check Merkle roots before merging.**  The `compare-merkle-roots`
   CI job enforces this automatically, but it is good practice to verify
   locally on multiple Python versions.

5. **Do not add platform-specific code paths.**  All code must be
   OS-agnostic.  Use `pathlib`, explicit encodings, and emulated arithmetic.

6. **Pin new dependencies** in `requirements.txt` with exact versions
   (`==`) for reproducibility.  Justify any version change in the PR
   description.

7. **Document environmental assumptions** in this compendium and in the
   ontology JSON whenever new ones are introduced.

---

## 5. Audit / Verification Procedures

### 5.1 CI Log Retention

Workflow run logs and artifacts are retained for **90 days** by default.
Merkle root artifacts are uploaded by every `determinism` job run and
downloaded by the `compare-merkle-roots` job.

To retrieve them after a run:

```bash
gh run download <run-id> --name merkle-root-<os>-py<version>
```

### 5.2 Merkle Root Comparison Across OSes

The `compare-merkle-roots` job in `.github/workflows/pr28-determinism.yml`:

1. Waits for all six `determinism` jobs (3 OS × 2 Python versions) to complete.
2. Downloads all Merkle root artifacts.
3. Asserts that every file contains the same hash.
4. Exits non-zero if any mismatch is detected.

The canonical Merkle root is also available at
`merkle_roots/pr28_merkle_root_linux.txt` (written by the Linux runner and
committed for reference).

### 5.3 Falsification Test Documentation

Every falsification test (`test_f001_*` … `test_f005_*`) reports:

* Assumption ID
* OS (`sys.platform`)
* Python version (`sys.version`)
* Source file and line number of the failure

This information is available in CI logs under the step
**"Run falsification tests"**.

---

## 6. References

| Resource | Location |
|---|---|
| PR #26 — Original cross-platform determinism spec | GitHub PR #26 |
| PR #27 — Windows CI blockers fixed | GitHub PR #27 |
| PR #28 — Full verification implementation | GitHub PR #28 |
| Ontology report | `ontology/pr26_ontological_issues.json` |
| Cross-platform determinism tests | `tests/test_cross_platform_determinism.py` |
| Falsification tests | `tests/test_falsification.py` |
| CI workflow | `.github/workflows/pr28-determinism.yml` |
| Merkle roots directory | `merkle_roots/` |

---

*This document was created as part of PR #28.  All future AI agents and human
contributors must consult it before modifying or generating code in this
repository.*
