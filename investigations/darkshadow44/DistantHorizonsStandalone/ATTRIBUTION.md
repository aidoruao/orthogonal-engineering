---
tags: [investigations, darkshadow44, distanthorizonsstandalone, attribution]
register: audit
---

# Attribution

This directory contains a read-only copy of source code from:
- **Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone
- **Author:** DarkShadow44 and contributors
- **License:** GNU General Public License v3.0
- **Commit:** 1abcd988fd4d350795f34dd2e9f678c14ba6162f
- **Cloned:** 2026-04-08T01:15:00Z

## Purpose

Forensic analysis copy for orthogonal-engineering investigations. This vendored
copy exists solely to make analysis claims falsifiable by providing byte-verifiable
source artifacts within the investigation repository.

## Immutability Guarantee

No files in `src/` have been or will be modified. The source tree is an exact
byte-for-byte copy of the original repository at the specified commit. Any
analysis artifacts, indices, or derived files are stored in sibling directories
or separate files.

## Verification

To verify this copy against the original:
```bash
git clone https://github.com/DarkShadow44/DistantHorizonsStandalone.git
cd DistantHorizonsStandalone
git checkout 1abcd988fd4d350795f34dd2e9f678c14ba6162f
sha256sum $(find src -type f | sort) > /tmp/original_manifest.txt
diff /tmp/original_manifest.txt sha256_manifest.txt
```

## Non-affiliation

**aidoruao is not affiliated with, endorsed by, or collaborating with DarkShadow44.**
This copy exists solely to make analysis claims falsifiable by providing
byte-verifiable source artifacts within the investigation repository.

This is not a fork, not a competing distribution, and not an attempt to
replace or supersede the original project.

## License

The original source code is licensed under the GNU General Public License v3.0.
See the `LICENSE` file for the full license text.
