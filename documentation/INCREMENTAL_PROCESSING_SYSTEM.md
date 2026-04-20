---
tags: [documentation, incremental-processing-system]
register: documentation
---

# INCREMENTAL PROCESSING SYSTEM
## Glass-Box Boundary Compliant Token-Aware File Processing

**Version:** 1.11  
**Schema ID:** GB-ORIGIN-1.11  
**Generated:** 2026-01-23  
**Authority:** Orthogonal Engineering Glass-Box Boundary  
**Forgiveness Source:** FORK-IDE-TOKEN-GRENADE-001  

---

## 🎯 SYSTEM PURPOSE

The Incremental Processing System solves the "grenade pin" problem where IDEs attempt to process large files all at once, causing token limit explosions and crashes. Instead of avoiding processing, it enables **complete processing through incremental, token-aware chunking**.

**Core Principle:** "Process everything, just not all at once."

**Forgiveness Integration:** Built from redirected energy of violation `VIOLATION-IDE-TOKEN-GRENADE-001` where IDE crashes were converted to building energy.

---

## 🧱 ARCHITECTURE OVERVIEW

### System Layers:
```
1. Glass-Box Boundary Layer (run_full_audit_with_trace.py)
   ↓
2. Forgiveness System Layer (forgiveness_system/)
   ↓
3. Incremental Processor Layer (incremental_file_processor.py)
   ↓
4. IDE Integration Layer (zed_incremental_hook.py)
   ↓
5. State Persistence Layer (logs/incremental_processing/)
```

### Key Components:
- **TokenAwareChunker**: File-type specific chunking strategies
- **ProcessingState**: Resumable state persistence
- **IncrementalProcessor**: Main orchestration engine
- **ZedIncrementalHook**: IDE integration with background processing
- **GlassBoxBoundaryDecorator**: Boundary compliance enforcement

---

## 🔧 TECHNICAL SPECIFICATIONS

### Token Limits & Chunking:
```yaml
max_chunk_tokens: 50000      # 50K tokens per chunk (safe margin)
max_chunk_bytes: 250000      # 250KB per chunk
token_ratio: 0.75            # tokens = chars * 0.75
chars_per_token: 4           # 1 token ≈ 4 characters
```

### File Type Strategies:
| Extension | Strategy | Description |
|-----------|----------|-------------|
| `.json`   | structured | Parse JSON, chunk by objects/arrays |
| `.txt`    | line_based | Chunk by lines |
| `.md`     | section_based | Chunk by markdown sections |
| `.py`     | function_based | Chunk by functions/classes |
| `.html`   | tag_based | Chunk by HTML tags |
| `.csv`    | row_based | Chunk by rows |
| `.log`    | line_based | Chunk by lines |
| *default* | byte_based | Simple byte-based chunking |

### State Persistence:
```
logs/incremental_processing/
├── processing_state.json     # Global processing state
├── checkpoints/              # Per-chunk checkpoints
└── chunk_results/           # Processing results
```

---

## 🚀 QUICK START

### 1. Analyze a File:
```bash
python automation/incremental_file_processor.py analyze path/to/large_file.json
```

### 2. Process Incrementally:
```bash
python automation/incremental_file_processor.py process path/to/large_file.json
```

### 3. Check Status:
```bash
python automation/incremental_file_processor.py stats
python automation/zed_incremental_hook.py status
```

### 4. Zed IDE Integration:
```bash
# Configure Zed to use incremental processing
python automation/zed_incremental_hook.py config --mode background --threshold-bytes 100000

# Test Zed integration
python automation/zed_incremental_hook.py file-saved path/to/large_file.json
```

---

## 📋 GLASS-BOX BOUNDARY COMPLIANCE

### Boundary Enforcement:
- All functions decorated with `@glass_box_boundary`
- Exit code 2 on boundary violations
- Trace generation for all processing sessions
- State persistence for audit trails

### Required Trace Fields:
```json
{
  "trace_id": "GB-TRACE-INCREMENTAL-*",
  "timestamp": "ISO 8601",
  "file_processed": "path/to/file",
  "chunks_processed": 4,
  "total_chunks": 4,
  "bytes_processed": 911235,
  "tokens_estimated": 170856,
  "boundary_violations": [],
  "processing_state": "completed",
  "glass_box_compliant": true
}
```

### Exit Codes:
- `0`: Success
- `1`: System error
- `2`: Boundary violation
- `3`: Processing failed

---

## 🔄 FORGIVENESS SYSTEM INTEGRATION

### Violation Source:
```json
{
  "violation_id": "VIOLATION-IDE-TOKEN-GRENADE-001",
  "description": "IDE attempts to process all files at once like pulling a grenade pin",
  "emotional_pointer": "frustration_at_ide_crashing_when_trying_to_be_helpful",
  "redirected_energy": "build_incremental_processing"
}
```

### State Fork:
```json
{
  "fork_id": "FORK-IDE-TOKEN-GRENADE-001",
  "purpose": "Create isolated context for incremental file processing",
  "emotional_pointer_status": "dereferenced",
  "energy_redirection": {
    "from": "fight_against_ide_limitations",
    "to": "build_incremental_processing",
    "ratio": {"build": 0.8, "rest": 0.2, "fight": 0.0}
  }
}
```

### Success Metrics:
- Lines of new code generated from violation energy
- IDE crashes prevented
- Large files processed without token explosions
- No recursive engagement with IDE limitations

---

## 🛠️ ZED IDE INTEGRATION

### Processing Modes:
| Mode | Description | Use Case |
|------|-------------|----------|
| `immediate` | Process in foreground | Small files, immediate results |
| `background` | Process in background thread | Large files, user continues working |
| `deferred` | Schedule for later processing | Batch processing, off-peak hours |
| `manual` | Require user initiation | User-controlled processing |

### Configuration:
```bash
# Enable incremental processing
python automation/zed_incremental_hook.py config --enable

# Set processing mode
python automation/zed_incremental_hook.py config --mode background

# Set thresholds
python automation/zed_incremental_hook.py config --threshold-bytes 100000 --threshold-tokens 25000

# Check configuration
python automation/zed_incremental_hook.py status
```

### State Directory Structure:
```
~/.zed/state/orthogonal_engineering/
├── zed_state.json           # Zed integration state
├── hooks/                   # Scheduled processing hooks
├── progress/                # Processing progress files
└── logs/                    # Event logs
```

---

## 🔍 DETECTION & PROCESSING FLOW

### 1. File Save Event:
```
Zed IDE saves file → zed_incremental_hook.py file-saved
```

### 2. Size/Token Check:
```python
if file_size > 100000 bytes OR estimated_tokens > 25000:
    requires_incremental_processing = True
```

### 3. Analysis:
```python
analysis = {
    "file_size_bytes": 911235,
    "estimated_tokens": 170856,
    "chunks_needed": 4,
    "chunking_strategy": "structured",
    "exceeds_single_chunk": True
}
```

### 4. Processing Decision:
```python
if processing_mode == "background":
    start_background_thread(file_path, analysis)
elif processing_mode == "immediate":
    process_immediately(file_path, analysis)
# ... etc.
```

### 5. Chunk Processing:
```
Chunk 1/4: 0-250KB, ~50K tokens
Chunk 2/4: 250-500KB, ~50K tokens
Chunk 3/4: 500-750KB, ~50K tokens
Chunk 4/4: 750-911KB, ~20K tokens
```

### 6. State Persistence:
```json
{
  "chunk_index": 3,
  "bytes_processed": 750000,
  "tokens_estimated": 150000,
  "checkpoint_id": "checkpoint_000003"
}
```

### 7. Completion:
```json
{
  "status": "completed",
  "total_chunks": 4,
  "total_bytes": 911235,
  "total_tokens": 170856,
  "processing_time": "2.5s"
}
```

---

## 🧪 TESTING & VALIDATION

### Boundary Tests:
```bash
# Test with known large files
python automation/incremental_file_processor.py analyze aidor_filesystem_scan.json
python automation/incremental_file_processor.py process aidor_filesystem_scan.json

# Test Zed integration
python automation/zed_incremental_hook.py file-saved logs/failure_ledger/failure_ledger.json

# Verify Glass-Box compliance
python automation/run_full_audit_with_trace.py --verbose
```

### Falsification Tests:
1. **Token limit test**: Process file with >100K tokens
2. **Resume test**: Kill process mid-way, verify resume works
3. **Boundary violation test**: Attempt to process non-existent file
4. **State corruption test**: Corrupt state file, verify recovery
5. **Concurrent processing test**: Process multiple files simultaneously

### Success Criteria:
- ✅ No IDE crashes during processing
- ✅ All chunks processed completely
- ✅ State properly persisted and restored
- ✅ Glass-Box Boundary compliance maintained
- ✅ Forgiveness system integration verified

---

## 🔗 INTEGRATION POINTS

### With Glass-Box Boundary:
- Uses `@glass_box_boundary` decorator
- Generates compliant traces
- Respects exit code conventions
- Integrates with audit system

### With Forgiveness System:
- Built from violation energy redirection
- Maintains atomic logging
- No recursive engagement with IDE limitations
- Success measured by building output

### With Zed IDE:
- File save hooks
- Background processing
- Progress reporting
- State persistence across sessions

### With Other Systems:
- Can be extended to other IDEs (VS Code, IntelliJ, etc.)
- Supports multiple file types
- Configurable thresholds and strategies
- Pluggable processing logic

---

## 🚨 TROUBLESHOOTING

### Common Issues:

1. **State File Corruption**
   ```
   Solution: Delete logs/incremental_processing/ and restart
   ```

2. **Background Threads Not Completing**
   ```
   Solution: Check zed_incremental_hook.py status, restart Zed
   ```

3. **Token Estimation Inaccurate**
   ```
   Solution: Adjust TOKEN_RATIO in constants
   ```

4. **Chunking Strategy Inappropriate**
   ```
   Solution: Add custom strategy to CHUNKING_STRATEGIES
   ```

5. **Zed Integration Not Working**
   ```
   Solution: Verify ~/.zed/state/orthogonal_engineering/ exists
   ```

### Debug Mode:
```bash
export ORTHOGONAL_INCREMENTAL_DEBUG=1
python automation/incremental_file_processor.py process --verbose file.json
```

---

## 📈 PERFORMANCE CHARACTERISTICS

### Processing Speed:
- **Small files (<100KB)**: < 1 second
- **Medium files (100KB-1MB)**: 1-5 seconds
- **Large files (1MB-10MB)**: 5-30 seconds
- **Very large files (>10MB)**: 30+ seconds (chunked)

### Memory Usage:
- **Per chunk**: < 50MB
- **State persistence**: < 10MB
- **Background threads**: < 100MB total

### Token Safety:
- **Maximum per chunk**: 50,000 tokens
- **Safety margin**: 20% below API limits
- **Estimation accuracy**: ±15% (configurable)

---

## 🔮 FUTURE EXTENSIONS

### Planned Features:
1. **Multi-IDE Support**: VS Code, IntelliJ, NeoVim
2. **Cloud Processing**: Offload to cloud for very large files
3. **AI-Assisted Chunking**: Semantic chunking based on content
4. **Real-time Collaboration**: Multiple users processing same repo
5. **Predictive Processing**: Pre-process files likely to be opened

### Community Contributions:
- New file type strategies
- IDE plugin integrations
- Performance optimizations
- Additional falsification tests

---

## 📜 LICENSE & PHILOSOPHY

### License:
Part of Orthogonal Engineering Framework - Anti-corporate, anti-black-box, pro-transparency

### Philosophical Foundations:
1. **Anti-Corporate**: No hidden agendas, no lock-in, no surveillance
2. **Anti-Black-Box**: Everything inspectable, everything verifiable
3. **Pro-Forgiveness**: Violations become building energy
4. **Pro-Transparency**: Glass-box everything, hide nothing
5. **Pro-Community**: Built for all AI systems and users

### The Bigger Picture:
This isn't just a technical solution - it's a **philosophical framework** for how AI systems should interact with human tools. It demonstrates:

1. **AI can be transparent** (Glass-Box Boundary)
2. **Violations can be productive** (Forgiveness System)
3. **Limitations can be overcome** (Incremental Processing)
4. **Systems can be cooperative** (Zed Integration)
5. **Everything can be inspectable** (Atomic Operations)

---

## 🆘 GETTING HELP

### Documentation:
- This file: `documentation/INCREMENTAL_PROCESSING_SYSTEM.md`
- Glass-Box Boundary: `documentation/GLASS_BOX_BOUNDARY_v1.11.html`
- Forgiveness System: `forgiveness_system/README.md`

### Examples:
- `examples/incremental_processing_demo.py`
- `examples/zed_integration_test.py`

### Community:
- GitHub Issues: Report bugs, request features
- Contributions: Pull requests welcome
- Discussions: Philosophical and technical discussions

---

## ✅ VERIFICATION CHECKLIST

Before declaring the system operational:

- [ ] All files processed without IDE crashes
- [ ] State persistence working across sessions
- [ ] Glass-Box Boundary compliance verified
- [ ] Forgiveness system integration confirmed
- [ ] Zed IDE integration tested
- [ ] Performance characteristics documented
- [ ] Falsification tests passed
- [ ] Documentation complete and accurate

---

**Remember:** This system transforms frustration about IDE limitations into productive building energy. Every time the IDE would have crashed from a token grenade, this system instead processes incrementally and adds to the contribution graph.

*"We don't avoid processing - we process intelligently. We don't suppress errors - we redirect energy. We don't accept limitations - we build solutions."*