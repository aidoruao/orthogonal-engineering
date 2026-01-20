# ORTHOGONAL ENGINEERING - TOOL COMPENDIUM
**Glass Box Methodology Documentation**
**Version:** 1.0.0
**Date:** 2026-01-20
**Methodology:** Orthogonal Engineering with Popperian Falsification
**Audit Principle:** Every tool action corresponds to verifiable filesystem/git state
**Transparency:** Complete visibility into all operations and outputs

## EXECUTIVE SUMMARY

This document catalogs all tools, scripts, and commands available in the Orthogonal Engineering (OE) repository. Each tool is documented with:
- **Purpose:** What the tool does
- **Usage:** How to execute it
- **Outputs:** What it produces
- **Audit Trail:** How to verify its execution
- **Falsifiability:** How to test its claims

## GLASS BOX PRINCIPLES

### Core Invariants:
1. **No Black Boxes:** All operations are transparent and inspectable
2. **Popperian Falsification:** Every claim can be independently tested and falsified
3. **Atomic Audit:** Every action produces timestamped, hashed artifacts
4. **Correspondence Validation:** Outputs must match expected filesystem state
5. **Git Integration:** All changes committed with traceable history

### Audit Requirements:
- ✅ Every execution must be timestamped (ISO 8601)
- ✅ Every output must be hashed (SHA256)
- ✅ Every change must be committed to git
- ✅ Every claim must have explicit falsification test
- ✅ Every tool must produce verifiable correspondence evidence

## REPOSITORY ASSESSMENT TOOLS

### 1. `assess_repository.py`
**Purpose:** Evaluate repository health and select canonical version
**Usage:**
```bash
python assess_repository.py [path_to_repository]
```
**Outputs:**
- Console: Health score, file count, git status
- JSON: `repository_assessments_YYYYMMDD_HHMMSS.json`
**Audit Trail:**
- Timestamp in JSON filename
- Hash of assessment file
- Git commit with assessment results
**Falsifiability:**
- Claim: "Repository health score is X%"
- Test: Manual verification of file existence and git status
- Condition: If manual count differs by >10% from automated score

### 2. `filesystem_scanner.py`
**Purpose:** Scan filesystem for AI conversation files and clusters
**Usage:**
```bash
python filesystem_scanner.py [scan_path]
```
**Outputs:**
- JSON: `aidor_filesystem_scan.json` (complete scan results)
- Console: File counts, cluster identification
**Audit Trail:**
- Scan timestamp in JSON metadata
- File hashes for key conversation files
- Git commit of scan results
**Falsifiability:**
- Claim: "Found X AI conversation files in Y clusters"
- Test: Manual directory listing and counting
- Condition: If manual count differs from scan results

## AI CONVERSATION PROCESSING TOOLS

### 3. `ai_conversation_processor.py`
**Purpose:** Batch process AI conversation files with canal detection
**Usage:**
```bash
python ai_conversation_processor.py [input_directory] [output_directory]
```
**Outputs:**
- JSON: Batch processing reports with cluster analysis
- CSV: Canal candidate inventories
- Console: Processing statistics and progress
**Audit Trail:**
- Processing timestamps for each file
- Hash verification of input/output files
- Git commit of analysis results
**Falsifiability:**
- Claim: "Processed X files with Y canal candidates"
- Test: Manual review of random sample (10% of files)
- Condition: If manual canal count differs by >25% from automated count

### 4. `analyze_ai_files.py`
**Purpose:** Direct analysis of individual AI conversation files
**Usage:**
```bash
python analyze_ai_files.py [file1.txt] [file2.txt] ...
```
**Outputs:**
- JSON: `ai_file_analysis_YYYYMMDD_HHMMSS.json`
- Console: Canal density, model detection, pattern counts
**Audit Trail:**
- Analysis timestamp in JSON
- Hash of analyzed files
- Git commit of analysis results
**Falsifiability:**
- Claim: "File X has canal density Y%"
- Test: Manual canal counting in same file
- Condition: If manual density differs by >15% from automated

### 5. `process_conversation_files.py`
**Purpose:** Process conversation files with invariant extraction
**Usage:**
```bash
python process_conversation_files.py [input_file_or_directory]
```
**Outputs:**
- JSON: Conversation analysis with invariant mapping
- Console: Invariant extraction statistics
**Audit Trail:**
- Processing timestamp
- Hash of processed files
- Git commit of invariant mappings
**Falsifiability:**
- Claim: "Extracted X invariants from conversation"
- Test: Manual invariant identification
- Condition: If manual count differs from automated extraction

## CORRESPONDENCE VALIDATION TOOLS

### 6. `correspondence_validator.py`
**Purpose:** Validate correspondence between expected and actual filesystem state
**Usage:**
```bash
python correspondence_validator.py [validation_config.json]
```
**Outputs:**
- JSON: `correspondence_validation_YYYYMMDD_HHMMSS.json`
- Console: Match rates, missing files, hash mismatches
**Audit Trail:**
- Validation timestamp
- Hash of validation configuration
- Git commit of validation results
**Falsifiability:**
- Claim: "100% of expected files exist with correct hashes"
- Test: Manual file existence and hash checking
- Condition: If any expected file missing or hash mismatched

### 7. `correspondence_validator_final.py`
**Purpose:** Final correspondence validation with truth anchors
**Usage:**
```bash
python correspondence_validator_final.py
```
**Outputs:**
- JSON: `correspondence_validation_final_YYYYMMDD_HHMMSS.json`
- Truth anchors with SHA256 hashes
**Audit Trail:**
- Creation timestamp for truth anchors
- Hash chains for verification
- Git commit of final validation
**Falsifiability:**
- Claim: "Created X truth anchors with consistent hashes"
- Test: Recalculate hashes of anchored files
- Condition: If recalculated hashes differ

### 8. `complete_correspondence.py`
**Purpose:** Complete correspondence checking with comprehensive validation
**Usage:**
```bash
python complete_correspondence.py
```
**Outputs:**
- JSON: Complete correspondence report
- Console: Validation summary
**Audit Trail:**
- Complete validation log
- Hash verification chain
- Git commit of complete validation
**Falsifiability:**
- Claim: "All tool outputs correspond to filesystem state"
- Test: Independent verification of all outputs
- Condition: If any output doesn't match filesystem

## STATISTICAL VALIDATION TOOLS

### 9. `calculate_statistics.py`
**Purpose:** Calculate statistical significance and effect sizes
**Usage:**
```bash
python calculate_statistics.py [data_file.csv]
```
**Outputs:**
- JSON: `statistical_validation.json`
- Console: p-values, effect sizes, confidence intervals
**Audit Trail:**
- Statistical calculation timestamp
- Hash of input data
- Git commit of statistical results
**Falsifiability:**
- Claim: "Effect size is X with p-value Y"
- Test: Independent statistical calculation
- Condition: If independent calculation yields different results

### 10. `test_confounds.py`
**Purpose:** Test for confounding variables in analysis
**Usage:**
```bash
python test_confounds.py [analysis_data.json]
```
**Outputs:**
- JSON: `confound_analysis.json`
- Console: Confound test results
**Audit Trail:**
- Confound testing timestamp
- Hash of analysis data
- Git commit of confound results
**Falsifiability:**
- Claim: "X confounding variables tested and ruled out"
- Test: Independent confound analysis
- Condition: If independent analysis finds different confounds

## PIPELINE INFRASTRUCTURE TOOLS

### 11. `validate_input.py`
**Purpose:** Validate input CSV schema and data integrity
**Usage:**
```bash
python validate_input.py [input.csv]
```
**Outputs:**
- Console: Validation status, error messages
- Log: Validation details in pipeline log
**Audit Trail:**
- Validation timestamp
- Hash of validated file
- Git commit of validation status
**Falsifiability:**
- Claim: "Input file has valid schema with X rows"
- Test: Manual schema verification
- Condition: If manual verification finds schema errors

### 12. `input_guard.py`
**Purpose:** Guard against unexpected CSV column changes
**Usage:**
```bash
python input_guard.py
```
**Outputs:**
- Console: Column validation, warnings
- Log: Guard check results
**Audit Trail:**
- Guard check timestamp
- Hash of checked files
- Git commit of guard status
**Falsifiability:**
- Claim: "All CSV files have expected columns"
- Test: Manual column checking
- Condition: If any file has unexpected columns

### 13. `canal_detector.py`
**Purpose:** Detect canal patterns in conversation files
**Usage:**
```bash
python canal_detector.py [input_file]
```
**Outputs:**
- Console: Canal detection results
- CSV: Canal candidate list
**Audit Trail:**
- Detection timestamp
- Hash of input file
- Git commit of detection results
**Falsifiability:**
- Claim: "Detected X canal candidates"
- Test: Manual pattern detection
- Condition: If manual detection finds different count

### 14. `canal_refiner.py`
**Purpose:** Refine canal candidates into verified invariants
**Usage:**
```bash
python canal_refiner.py [canal_candidates.csv]
```
**Outputs:**
- CSV: `refined_inventory.csv`
- Console: Refinement statistics
**Audit Trail:**
- Refinement timestamp
- Hash of input/output files
- Git commit of refined inventory
**Falsifiability:**
- Claim: "Refined X candidates into Y verified invariants"
- Test: Manual verification of refinement
- Condition: If manual verification differs

## SYSTEM ANALYSIS TOOLS

### 15. `system_analyzer_agent.py`
**Purpose:** Analyze codebase structure and tool composition
**Usage:**
```bash
python system_analyzer_agent.py [analysis_directory]
```
**Outputs:**
- JSON: `system_analysis_YYYYMMDD_HHMMSS.json`
- Console: Codebase statistics
**Audit Trail:**
- Analysis timestamp
- Hash of analyzed files
- Git commit of analysis results
**Falsifiability:**
- Claim: "Codebase has X functions and Y classes"
- Test: Independent code analysis
- Condition: If independent analysis finds different counts

### 16. `foolproof_file_inspection.py`
**Purpose:** Inspect file integrity and detect corruption
**Usage:**
```bash
python foolproof_file_inspection.py [file_to_inspect]
```
**Outputs:**
- Console: Integrity check results
- Log: Inspection details
**Audit Trail:**
- Inspection timestamp
- Hash of inspected file
- Git commit of inspection results
**Falsifiability:**
- Claim: "File has integrity with hash X"
- Test: Recalculate file hash
- Condition: If recalculated hash differs

### 17. `monitor_pipeline.py`
**Purpose:** Monitor pipeline execution and log progress
**Usage:**
```bash
python monitor_pipeline.py
```
**Outputs:**
- Log: `pipeline_run_log.txt`
- Console: Pipeline status
**Audit Trail:**
- Continuous timestamp logging
- Hash of log file
- Git commit of pipeline status
**Falsifiability:**
- Claim: "Pipeline executed X steps successfully"
- Test: Manual verification of log entries
- Condition: If log entries don't match actual execution

### 18. `output_validator.py`
**Purpose:** Validate pipeline outputs against expectations
**Usage:**
```bash
python output_validator.py [output_directory]
```
**Outputs:**
- Console: Validation results
- JSON: Validation report
**Audit Trail:**
- Validation timestamp
- Hash of validated outputs
- Git commit of validation results
**Falsifiability:**
- Claim: "All outputs valid with expected formats"
- Test: Manual output inspection
- Condition: If any output invalid

### 19. `rollback_manager.py`
**Purpose:** Manage rollback operations with audit trail
**Usage:**
```bash
python rollback_manager.py [rollback_target]
```
**Outputs:**
- Console: Rollback status
- Log: Rollback audit trail
**Audit Trail:**
- Rollback timestamp
- Hash of rollback state
- Git commit of rollback operation
**Falsifiability:**
- Claim: "Rollback completed to state X"
- Test: Verify filesystem matches rollback state
- Condition: If filesystem doesn't match expected state

## MCP SERVER TEMPLATES (PLANNED)

### 20. `oe-basic.mcp`
**Purpose:** Basic MCP server for atomic operations
**Commands:**
- `echo`: Test command with audit trail
- `timestamp`: Generate ISO timestamp
- `hash_string`: Hash input string
**Audit Requirements:**
- Every command must log timestamp and hash
- Every output must be verifiable
- Every operation must be atomic

### 21. `oe-filesystem.mcp`
**Purpose:** Filesystem operations with correspondence validation
**Commands:**
- `scan_path`: Scan directory with hash verification
- `check_existence`: Verify file existence
- `read_content`: Read file with hash verification
**Audit Requirements:**
- Every scan must produce hash chain
- Every check must be timestamped
- Every read must verify integrity

### 22. `oe-git.mcp`
**Purpose:** Git operations with atomic audit trail
**Commands:**
- `commit`: Atomic commit with hash
- `diff`: Diff with verification
- `status`: Status with timestamp
**Audit Requirements:**
- Every commit must include hash
- Every diff must be verifiable
- Every status must be timestamped

## PIPELINE EXECUTION SCRIPTS

### 23. `RUN_PIPELINE.ps1`
**Purpose:** Execute complete OE pipeline on Windows
**Usage:**
```powershell
.\RUN_PIPELINE.ps1
```
**Execution Order:**
1. Validate inputs
2. Run canal detection
3. Process conversations
4. Validate outputs
5. Commit results
**Audit Trail:**
- PowerShell execution log
- Timestamp for each step
- Git commit of final results

### 24. `RUN_AGENT.bat`
**Purpose:** Batch execution of system analyzer agent
**Usage:**
```batch
RUN_AGENT.bat
```
**Audit Trail:**
- Batch execution log
- Analysis timestamp
- Git commit of analysis

### 25. `copy_files.ps1`
**Purpose:** Copy files with hash verification
**Usage:**
```powershell
.\copy_files.ps1 [source] [destination]
```
**Audit Trail:**
- Copy operation timestamp
- Source/destination hashes
- Git commit of copy operation

## UTILITY SCRIPTS

### 26. `analyze_conversation_patterns.py`
**Purpose:** Analyze conversation patterns and structures
**Usage:**
```bash
python analyze_conversation_patterns.py [conversation_file]
```
**Audit Trail:**
- Analysis timestamp
- Pattern hash verification
- Git commit of pattern analysis

### 27. `analyze_filesystem_invariants.py`
**Purpose:** Analyze filesystem for invariant patterns
**Usage:**
```bash
python analyze_filesystem_invariants.py [scan_path]
```
**Audit Trail:**
- Invariant analysis timestamp
- Filesystem hash chain
- Git commit of invariant analysis

### 28. `analyze_conversations_simple.py`
**Purpose:** Simple conversation analysis for quick verification
**Usage:**
```bash
python analyze_conversations_simple.py [conversation_files...]
```
**Audit Trail:**
- Simple analysis timestamp
- Quick hash verification
- Git commit of simple analysis

## AUDIT PROTOCOLS

### Standard Audit Procedure:
1. **Timestamp Generation:**
   ```python
   from datetime import datetime
   timestamp = datetime.utcnow().isoformat() + 'Z'
   ```

2. **Hash Generation:**
   ```python
   import hashlib
   def hash_file(filepath):
       with open(filepath, 'rb') as f:
           return hashlib.sha256(f.read()).hexdigest()
   ```

3. **Git Integration:**
   ```bash
   git add [output_files]
   git commit -m "Tool: [tool_name] - [timestamp] - [hash_prefix]"
   ```

4. **Correspondence Validation:**
   ```bash
   python correspondence_validator.py --verify [output_files]
   ```

### Falsification Test Protocol:
1. **Claim Identification:** Extract specific claim from tool output
2. **Test Design:** Create independent verification method
3. **Execution:** Perform verification independently
4. **Comparison:** Compare results with tool output
5. **Documentation:** Record verification results and any discrepancies

## GLASS BOX VERIFICATION CHECKLIST

### For Every Tool Execution:
- [ ] Tool executed with explicit command
- [ ] Execution timestamp recorded
- [ ] Input files hashed and recorded
- [ ] Output files created with hashes
- [ ] Git commit created with tool name and timestamp
- [ ] Correspondence validation performed
- [ ] Falsification test documented

### For Every Tool Output:
- [ ] Output format documented
- [ ] Output hash recorded
- [ ] Output corresponds to filesystem state
- [ ] Output claims are falsifiable
- [ ] Output includes verification instructions

### For Every Git Commit:
- [ ] Commit message includes tool name
- [ ] Commit message includes timestamp
- [ ] Commit message includes output hash prefix
- [ ] Commit includes all output files
- [ ] Commit can be independently verified

## CONTINUOUS IMPROVEMENT

### Tool Enhancement Protocol:
1. **Identify Need:** Document tool limitation or enhancement opportunity
2. **Design Change:** Create specification with audit requirements
3. **Implement:** Code change with full audit trail
4. **Test:** Execute with falsification tests
5. **Document:** Update this compendium
6. **Commit:** Git commit with enhancement details

### New Tool Integration:
1. **Specification:** Document purpose, inputs, outputs, audit requirements
2. **Development:** Implement