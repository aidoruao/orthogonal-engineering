# Attribution

This directory contains a read-only copy of source code from:
- **Repository:** https://github.com/DarkShadow44/Angelica
- **Author:** DarkShadow44 and contributors
- **License:** GNU Lesser General Public License v3.0
- **Commit:** cd42307ba9ec7745013bb4bdb2718d08cea37adf
- **Cloned:** 2026-04-08T00:59:52Z

## Purpose

Forensic analysis copy for orthogonal-engineering investigations. This vendored
copy exists solely to make analysis claims falsifiable by providing byte-verifiable
source artifacts within the investigation repository.

## Special Licensing Note

The original license from `java/shadersmodcore/client/Shaders.java` was relicensed
by GTNH developers under LGPL. Code written by daxnitro, modified by id_miner and
karyonix.

## Immutability Guarantee

No files in `src/` have been or will be modified. The source tree is an exact
byte-for-byte copy of the original repository at the specified commit.

## Verification

To verify this copy against the original:
```bash
git clone https://github.com/DarkShadow44/Angelica.git
cd Angelica
git checkout cd42307ba9ec7745013bb4bdb2718d08cea37adf
sha256sum $(find src -type f | sort) > /tmp/original_manifest.txt
diff /tmp/original_manifest.txt sha256_manifest.txt
```

## Non-affiliation

**aidoruao is not affiliated with, endorsed by, or collaborating with DarkShadow44.**
This copy exists solely to make analysis claims falsifiable by providing
byte-verifiable source artifacts within the investigation repository.

## License

The original source code is licensed under the GNU Lesser General Public License v3.0.
See the `LICENSE` file for the full license text.
