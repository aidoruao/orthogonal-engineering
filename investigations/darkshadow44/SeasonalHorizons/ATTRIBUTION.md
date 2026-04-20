---
tags: [investigations, darkshadow44, seasonalhorizons, attribution]
register: audit
---

# Attribution

This directory contains a read-only copy of source code from:
- **Repository:** https://github.com/DarkShadow44/SeasonalHorizons
- **Author:** DarkShadow44 (original code, not a fork)
- **License:** GNU Lesser General Public License v2.1
- **Commit:** ad10038155e00cdb3c80aaacebcd6c39adb6504a
- **Cloned:** 2026-04-08T00:59:52Z

## Purpose

Forensic analysis copy for orthogonal-engineering investigations. This vendored
copy exists solely to make analysis claims falsifiable by providing byte-verifiable
source artifacts within the investigation repository.

SeasonalHorizons is DarkShadow44's own original project (not a fork). Understanding
how he structures his own mods (vs maintaining forks) provides insight into his
architectural patterns and what kind of patches he's likely to accept.

## Immutability Guarantee

No files in `src/` have been or will be modified. The source tree is an exact
byte-for-byte copy of the original repository at the specified commit.

## Verification

To verify this copy against the original:
```bash
git clone https://github.com/DarkShadow44/SeasonalHorizons.git
cd SeasonalHorizons
git checkout ad10038155e00cdb3c80aaacebcd6c39adb6504a
sha256sum $(find src -type f | sort) > /tmp/original_manifest.txt
diff /tmp/original_manifest.txt sha256_manifest.txt
```

## Non-affiliation

**aidoruao is not affiliated with, endorsed by, or collaborating with DarkShadow44.**
This copy exists solely to make analysis claims falsifiable by providing
byte-verifiable source artifacts within the investigation repository.

## License

The original source code is licensed under the GNU Lesser General Public License v2.1.
See the `LICENSE` file for the full license text.
