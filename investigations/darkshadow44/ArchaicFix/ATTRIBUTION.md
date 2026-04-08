# Attribution

This directory contains a read-only copy of source code from:
- **Repository:** https://github.com/DarkShadow44/ArchaicFix
- **Author:** DarkShadow44 and contributors (forked from embeddedt/ArchaicFix)
- **License:** GNU Lesser General Public License v3.0 (with caveats)
- **Commit:** 85b33afdd7f08b0842d944b198b0de966a72d778
- **Cloned:** 2026-04-08T00:59:52Z

## Purpose

Forensic analysis copy for orthogonal-engineering investigations. This vendored
copy exists solely to make analysis claims falsifiable by providing byte-verifiable
source artifacts within the investigation repository.

## Special Licensing Note

ArchaicFix is licensed under the LGPL3; however, the occlusion culling module is
directly derived from CoFHTweaks, itself derived from Minecraft 1.8. As such that
component is not considered to be under LGPL3. Please refer to
`src/main/java/org/embeddedt/archaicfix/occlusion/LICENSE` for more information.

## Immutability Guarantee

No files in `src/` have been or will be modified. The source tree is an exact
byte-for-byte copy of the original repository at the specified commit.

## Verification

To verify this copy against the original:
```bash
git clone https://github.com/DarkShadow44/ArchaicFix.git
cd ArchaicFix
git checkout 85b33afdd7f08b0842d944b198b0de966a72d778
sha256sum $(find src -type f | sort) > /tmp/original_manifest.txt
diff /tmp/original_manifest.txt sha256_manifest.txt
```

## Non-affiliation

**aidoruao is not affiliated with, endorsed by, or collaborating with DarkShadow44.**
This copy exists solely to make analysis claims falsifiable by providing
byte-verifiable source artifacts within the investigation repository.

## License

The original source code is primarily licensed under the GNU Lesser General Public
License v3.0, with the exception of the occlusion culling module. See the
`LICENSE.md` file for the full license text and caveats.
