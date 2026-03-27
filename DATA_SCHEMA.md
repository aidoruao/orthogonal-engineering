# Data Schema Documentation

This directory contains empirical evidence files that ground the Orthogonal Engineering methodology in real-world data.

## Files

### External Data Sources (Not Included)

- **MASTER_INDEX.csv** (251,472 rows, ~233 GB indexed)
  - Location: `c:\Users\Aidor\Desktop\MASTER_INDEX.csv`
  - Schema: `filepath,filename,size_mb,size_bytes,type,project_tag,extension,last_modified,parent_dir`
  - Privacy: Contains full file paths; sanitized summary included in `MASTER_INDEX_SUMMARY.json`
  
- **depth_analysis_FULL.json** (~5,920 conversation records)
  - Location: `c:\Users\Aidor\Desktop\depth_analysis_FULL.json`
  - Schema: Array of conversation objects with:
    - `id`: Conversation identifier
    - `title`: Conversation title
    - `msg_count`: Total message count
    - `user_msgs`: User message count
    - `assistant_msgs`: Assistant message count
    - `duration_hours`: Conversation duration
    - `turn_ratio`: user_msgs / assistant_msgs (canal structure proxy)
    - `create_time`: Unix timestamp
    - `depth_score`: Invariant extraction success proxy (0-1)

### Generated Analysis Files

- **filesystem_invariants_analysis.json**: Canal structure detection and invariant marker analysis
- **conversation_patterns_analysis.json**: Turn-taking patterns and depth score validation

## Usage

Run analysis scripts from the `analysis/` directory:

```bash
python analysis/analyze_filesystem_invariants.py [CSV_PATH] [OUTPUT_PATH]
python analysis/analyze_conversation_patterns.py [JSON_PATH] [OUTPUT_PATH]
```

## Privacy Notes

Raw data files are not included in the repository to protect user privacy. Only aggregate statistics and analysis outputs are included.
