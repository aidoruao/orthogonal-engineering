# Evidence Files

This directory contains sanitized validation data for the Orthogonal Engineering methodology.

---

## Files

### RECON_STATS.json
**Aggregate statistics from full dataset scan**

Contains:
- Total files analyzed: 251,471
- Total size: 233.66 GB
- Distribution by file type
- Distribution by project tag
- Scan timestamp

**Privacy:** Safe - contains only aggregate counts, no file paths or personal data

---

### MASTER_INDEX_SUMMARY.json
**Sanitized summary of full file index**

Contains:
- Scale validation (file counts, size totals)
- Tag distribution (INVARIANT, CRAFTSMAN, etc.)
- File type statistics
- Temporal range information
- **Does NOT contain**: Raw file paths, filenames, or personal identifiers

**Privacy:** Safe - aggregated statistics only

**Note:** Raw MASTER_INDEX.csv exists but is not published to protect user privacy. It contains full file paths including personal/medical information.

---

## What This Evidence Proves

✅ **Scale**: Methodology applied to 251,471+ real files  
✅ **Volume**: 233.66 GB of actual data processed  
✅ **Scope**: Multiple file types and project categories  
✅ **Validation**: Tags applied systematically across dataset  
✅ **Timeline**: Multi-year span of AI collaboration data

---

## What This Evidence Does NOT Prove

❌ Cross-domain applicability beyond AI conversations  
❌ Formal mathematical properties of invariants  
❌ Independent replication by other researchers  
❌ Production system reliability at scale

---

## Privacy & Ethics

Raw file paths were intentionally removed because they contained:
- Personal directory names
- Medical/health-related filenames
- Private project identifiers
- User-identifiable information

**This is standard practice in research involving personal data.**

Sanitization preserves proof-of-work while respecting privacy.

---

## Reproducibility

See `REPRODUCE.md` in the parent directory for instructions on how to:
- Apply the methodology to your own data
- Generate similar statistics
- Validate the approach in your domain

---

**Last Updated**: 2026-01-17
