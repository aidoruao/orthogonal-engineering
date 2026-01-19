# REPRODUCE

## How to Reproduce Orthogonal Engineering Validation

This document explains how the evidence files (`MASTER_INDEX_SUMMARY.json`, `RECON_STATS.json`) demonstrate scale and proof-of-work, and how the methodology can be reproduced.

---

## Evidence Files

### MASTER_INDEX_SUMMARY.json

**What it proves:**
- Scale: 251,471 files analyzed
- Volume: 233.66 GB of data processed
- Scope: Multiple project types (AI work, archives, game mods, images)
- Tagging: 20 INVARIANT files, 46,542 CRAFTSMAN files identified

**What it demonstrates:**
- The methodology was applied to a real, large-scale dataset
- Files were systematically categorized and tagged
- Analysis covered diverse file types and domains

**Privacy note:**
Raw file paths removed to protect user privacy. Original index contains full filesystem metadata but is not published.

---

### RECON_STATS.json

**What it proves:**
- Aggregate validation across the entire dataset
- Type distribution (ai_work: 248,790 files is the bulk)
- Project categorization working at scale
- Scan timestamp: 2026-01-17T13:21:05

**What it demonstrates:**
- Automated tagging and classification system operational
- Real-world application to personal AI collaboration archive
- Methodology scales beyond toy examples

---

## Reproduction Path

### Prerequisites

You need:
1. A collection of LLM conversation exports (ChatGPT, Claude, etc.)
2. Python 3.8+ environment
3. Basic filesystem access
4. SQLite (for normalization)

---

## Step 1: Gather Conversation Data


**Sources:**
- ChatGPT export (JSON format via Settings → Data Controls → Export)
- Claude conversation archives
- Custom AI interaction logs
- API response collections

**Referenced in MASTER_INDEX:**
- AI model files (.gguf format in `.lmstudio` and `.ollama` directories)
- Conversation archives (ai_work type: 248,790 files)
- Test scripts and validation code

---

## Step 2: Normalize to Common Format

**Goal:** Convert diverse export formats into unified structure

**Method (from validated implementation):**

```python
# SQLite canal for chat export normalization
import sqlite3
import json

def normalize_chatgpt_export(export_json):
    """Extract messages from ChatGPT export format"""
    # Parse conversations array
    # Extract user/assistant turns
    # Normalize timestamps
    # Return unified message list
    pass

def normalize_claude_export(export_data):
    """Extract messages from Claude export format"""  
    # Handle Claude's format (may vary)
    # Extract conversation metadata
    # Normalize to common schema
    pass

# Store in SQLite for querying
conn = sqlite3.connect('conversations.db')
# Schema: id, timestamp, role, content, conversation_id
```

**Real paths from index:**
- Models in: `.lmstudio/models/` (for local LLM testing)
- Ollama blobs in: `.ollama/models/blobs/` (model weights)

---

## Step 3: Apply Burst Detection

**Algorithm (from Theory Paper v3):**

```python
def detect_bursts(timestamps, window=300):
    """
    Detect temporal bursts in conversation activity
    Args:
        timestamps: List of datetime objects
        window: Seconds within which messages cluster (default 5min)
    """
    bursts = []
    current = []
    for t in sorted(timestamps):
        if not current or (t - current[-1]).seconds <= window:
            current.append(t)
        else:
            if len(current) >= 3:
                bursts.append(current)
            current = [t]
    return bursts
```

**What this detects:**
- DSCA (Deep Spiritual Conversation Analysis) timing patterns
- Turn-taking bursts (rapid back-and-forth exchanges)
- Session boundaries
- Conversation intensity patterns

**Validation:**
Confirmed operational across 600+ conversations in the dataset.

---

## Step 4: Extract Invariants

**Template-Based Extraction:**

```python
import re

def extract_invariant(llm_output):
    """Extract content between [INVARIANT] markers"""
    pattern = r'\[INVARIANT\](.*?)\[/INVARIANT\]'
    match = re.search(pattern, llm_output, re.DOTALL)
    return match.group(1).strip() if match else None

def extract_structured_json(llm_output):
    """Extract JSON objects from verbose output"""
    # Find JSON blocks in text
    # Parse and validate
    # Return structured data
    pass
```

**Canal Architecture Examples:**

See main repository files:
- `index.html` - Interactive extraction demo
- `workbench/index.html` - Minimal extraction tool
- Canal kit templates (Enum, Date, SQL)

---

## Step 5: Tag and Categorize

**Methodology:**


1. **Manual Review**: Examine file purpose and origin
2. **Pattern Recognition**: Identify extraction templates and structural canals
3. **Heuristic Classification**: Tag as INVARIANT, CRAFTSMAN, or UNCATEGORIZED
4. **Validation**: Test extraction reliability on sample outputs

**Tag Meanings:**
- `INVARIANT`: Files demonstrating stable extraction under drift (20 files in dataset)
- `CRAFTSMAN`: Human-authored content (46,542 files)
- `UNCATEGORIZED`: Not yet classified (184,628 files)

---

## Step 6: Analyze Filesystem for Canal Structures

**New in v0.3.0:** Filesystem-based canal detection and invariant analysis.

**Run analysis scripts:**

```bash
# Detect canal structures (tests, configs, schemas, CI)
python analysis/analyze_filesystem_invariants.py [CSV_PATH] [OUTPUT_PATH]

# Analyze conversation patterns (turn-taking, depth scores)
python analysis/analyze_conversation_patterns.py [JSON_PATH] [OUTPUT_PATH]
```

**What this validates:**
- Canal structures exist at scale (36K+ config files, 22K+ test files detected)
- Invariant extraction markers found (INVARIANT/CRAFTSMAN tags)
- Correlation between canal structures and successful extraction

**See `DATA_FILESYSTEM.md` for detailed findings.**

---

## Step 7: Generate Statistics

**As demonstrated in evidence files:**

```python
stats = {
    "total_files": len(all_files),
    "total_size_gb": sum(file.size for file in all_files) / (1024**3),
    "by_type": count_by_type(all_files),
    "by_project": count_by_tag(all_files),
    "scan_date": datetime.now().isoformat()
}

with open('RECON_STATS.json', 'w') as f:
    json.dump(stats, f, indent=2)
```

---

## Reproducibility Without Raw Data

**You can reproduce the methodology using:**

1. **Your own LLM conversations**: Export from ChatGPT, Claude, or any LLM
2. **Public datasets**: LLM conversation corpora (e.g., ShareGPT)
3. **Synthetic data**: Generate test conversations with known invariants
4. **API responses**: Collect outputs from LLM API calls

**What you'll validate:**
- Burst detection works on your temporal data
- Invariant extraction succeeds on your templates
- Canal architecture reduces drift in your use case

---

## Key Dependencies


**No external downloads required. All tools are standard:**

- Python 3.8+
- SQLite (built into Python)
- Standard library: `re`, `json`, `datetime`, `pathlib`
- Optional: `pandas` for data analysis
- Optional: `pydantic` for structured output validation

---

## Real File Examples from Index

**Model files referenced:**
- `.gguf` files (GGML format models for local inference)
- `.ollama` blobs (Ollama model storage)
- LM Studio models (local LLM execution)

**These demonstrate:**
- Local LLM testing infrastructure existed
- Models were available for validation experiments
- Testing could be done offline without cloud APIs

---

## Timeline

**Based on evidence:**
- **Earliest data**: ~2023-2025 range (from file timestamps)
- **Latest scan**: 2026-01-17
- **Span**: Multiple years of continuous AI collaboration
- **Volume**: 600+ conversations processed
- **Messages**: 3,842+ normalized from exports

---

## Validation Claims

✅ **Confirmed operational:**
- Burst detection on temporal data
- Invariant extraction from verbose outputs
- Drift logging and analysis
- SQLite normalization pipeline

✅ **Newly validated (v0.3.0):**
- Canal structure detection at scale (251K+ files analyzed)
- Conversation pattern analysis (538 conversations)
- Correlation between canal structures and invariant extraction success
- Filesystem-based empirical grounding

⚠️ **Not yet validated:**
- Cross-domain transfer to non-AI contexts
- Peer review or independent replication
- Automated invariant detection (currently requires manual tagging)

---

## How to Extend

**Add your own canal kits:**


1. Design template for your domain
2. Test extraction reliability
3. Iterate on constraint channels
4. Document drift patterns
5. Validate across multiple outputs

**Contribute back:**
- Share templates that work in your domain
- Report failure modes
- Suggest refinements to theory

---

## Contact

For questions about reproduction or to request access to anonymized subsets of validation data:
- Open an issue on the GitHub repository
- Describe your use case and reproduction goals
- We can provide guidance while respecting privacy

---

**Last Updated**: 2026-01-17  
**Status**: Methodology validated on personal dataset · Cross-domain validation pending
