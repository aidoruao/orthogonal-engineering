---
tags: [campaigns, registry, infrastructure, canonical]
register: technical
---

# Campaign Registry

All canonical campaigns for the Orthogonal Engineering repository.  
Zero scope reduction is the invariant. Every campaign has a machine-readable `*_spec.json` that `scope_reduction_detector.py` can verify.

---

## Campaign Summary

| Campaign | ID | Status | Branch | Spec File | Scope Reduction? |
|---|---|---|---|---|---|
| Depositive Part 1 | DEPOSITIVE-001 | ARCHIVED | — | `campaigns/depositive_part1_spec.json` | No |
| Depositive Part 2 | DEPOSITIVE-002 | ARCHIVED | — | `campaigns/depositive_part2_spec.json` | No |
| Depositive Part 3 | DEPOSITIVE-003 | ARCHIVED | — | `campaigns/depositive_part3_spec.json` | No |
| GDSII Photonic | PHOTONIC-001 | ARCHIVED | — | `campaigns/photonic_spec.json` | No |
| Part 3 Stages H-Z | PART3-HZ-001 | ACTIVE | `kimi/part3-hz` | `campaigns/part3_hz_spec.json` | Yes (73/83 missing) |
| Forensic Offensive | CAMPAIGN-FORENSIC-OFFENSIVE-001 | IN PROGRESS | `kimi/forensic-offensive-*` | `campaigns/forensic_offensive_spec.json` | TBD |

---

## Quick Start

### Verify a single campaign

```bash
python3 audit/scope_reduction_detector.py campaigns/part3_hz_spec.json
```

### Audit all campaigns at once

```bash
python3 tools/campaign_auditor.py
```

This discovers every `*_spec.json` under `campaigns/`, runs `scope_reduction_detector.py` against each, and writes `audit/CAMPAIGN_AUDIT_REPORT.json`.

---

## Archive

Historical campaign source documents live in `campaigns/archive/`:

- `depositive_part1.md` -- Original Depositive Campaign Part 1
- `depositive_part2.md` -- Original Depositive Campaign Part 2
- `depositive_part3.md` -- Original Depositive Campaign Part 3
- `photonic_part2.md` -- GDSII Photonic computation campaign part 2
- `photonic_part3.md` -- GDSII Photonic computation campaign part 3
- `photonic_part4.md` -- GDSII Photonic computation campaign part 4
- `photonic_campaign_4-21-26.md` -- Full GDSII Photonic campaign 2026-04-21

---

## Schema

See `campaigns/CAMPAIGN_SCHEMA.md` for the canonical format that every campaign must follow.

---

*Last updated: 2026-04-23*
