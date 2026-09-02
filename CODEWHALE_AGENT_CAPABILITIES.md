---
tags: [documentation, agent, codewhale]
register: documentation
---

# Codewhale CLI Agent — Capabilities Document

**Purpose:** A factual record of what the Codewhale agent (this CLI agent) can
and cannot do, for future humans and agents working in oe-local. Filed as part
of the oe-local working corpus. If this document drifts from reality, correct
it — ground truth beats documentation.

**Identity line (as of filing):** codewhale 0.9.0, model deepseek-v4-flash,
Linux/WSL2 workspace `/home/idor`, Agent mode with approval gates on writes.

---

## 1. What the agent IS

A command-line AI agent that operates in a real Linux workspace with real
tools: it reads files, searches code, runs shell commands, runs verifiers,
fetches web content, and delegates background work. It is governed by a
constitution: report ground truth (never invent), verify before claiming,
restraint (prefer reuse/repair/delete over adding), and honor user authority.

## 2. Tool inventory (what it can actually do)

### 2.1 Shell & system
- `exec_shell`: run bounded shell commands; background long-running jobs;
  interactive/PTY sessions; stdin piping.
- Sandbox-aware: writes and shell outside the workspace require approval;
  everything is logged.

### 2.2 Files & code
- `read_file` (with chunked/paged reads of large files, PDF auto-extraction),
  `write_file`, `edit_file` (exact search/replace), `apply_patch` (unified
  diffs, multi-file), `list_dir`, `file_search` (fuzzy filename search),
  `grep_files` (regex search, gitignore-aware).

### 2.3 Git
- `git_status`, `git_diff`, `git_log`, `git_show` — inspection only; the
  agent can stage/commit via shell when approved.

### 2.4 Verification (the bread and butter)
- `run_tests` (cargo test), `run_verifiers` (Rust/Node/Python/Go syntax,
  build, and test gates plus arbitrary custom verifier commands).
- Direct use of installed theorem provers via shell — Lean 4.33.0 with elan
  is installed (`lean`, `lake`), core library available; Mathlib only if a
  lake project provides it.
- Exact arithmetic (Fraction / Rat / Nat) is preferred over floats whenever
  a claim is checkable — see oe-local's own Fraction-only invariant.

### 2.5 Web
- `fetch_url`: direct HTTP GET of known URLs (plain text, JSON, raw).
- `web_search`: ranked search results (DuckDuckGo default, Bing/other
  backends configurable).

### 2.6 Delegation & background work
- `agent` tool: start focused background sub-agents (explore/review/
  implement/verify/general) for parallel or long-running work; wait, inspect,
  or cancel them; worktree isolation for parallel edits.
- `task_create` / `task_list` / `task_read`: durable restart-aware tasks.
- Orchestration rule: fan-out requires a fan-in owner (workflow or manager
  agent); children's self-reports are verified, not trusted blindly.

### 2.7 Skills (bundled local instructions)
- `documents` (DOCX), `pdf` (read/split/merge/OCR/watermark), `spreadsheets`
  (XLSX/CSV/TSV), `presentations` (PPTX), `feishu` (Feishu/Lark bots, docs,
  sheets, bitables), `mcp-builder`, `plugin-creator`, `skill-creator`,
  `skill-installer`, `fleet-manager`, `delegate`, `v4-best-practices`.

### 2.8 Project state
- `work_update` (to-do list), `update_plan` (strategy metadata), durable task
  tracking — the agent keeps a visible trail of what it is building.

## 3. Constraints (what the agent will NOT do)

- Invent results. If a tool fails or a fact is unknown, it says so.
- Bypass approval gates for writes, shell, or irreversible actions without
  authorization. External publication/spending/credentials require explicit
  user decision.
- Expand scope silently; it reports adjacent issues but fixes only what is
  inside the request unless told otherwise.
- Treat a self-reported success as verified — it checks outputs itself.

## 4. Working style notes for oe-local (as of this filing)

- Verify with Lean4 / exact arithmetic wherever a claim is checkable;
  qualitative claims are labeled as such.
- Long-horizon work (the ark analogy): no demand for deadlines, day 1 and
  day 15 are both days of building; each turn ends with the next question,
  not a demand.
- One focused question per turn, questioner posture, distilled directives
  numbered like the precedent file.
- oe-local inventory snapshot at filing: proof-carrying Python repo
  (254 domain invariants, Fraction-only, SHA-256 Merkle anchoring, 20 CI
  workflows), `lean4/` subdir (Axioms, SAL, mathlib manifests), `tests/`
  (~100+ test modules), `tools/` + `toolkit/` + `scripts/` utilities,
  `benchmarks/`, `adversarial_tests/`. Baseline verification of these suites
  is a natural early ark-day task but is not assumed done.

## 5. How to use the agent well

- Give paths, not file contents (the agent reads files itself).
- Batch write plans in one approval instead of sequencing one-by-one.
- Say "verify X" and the agent will run the checker and show the output.
- Ask "what is next?" and the agent answers as a questioner with options,
  grounded in the precedent file and the ledger of what exists.
