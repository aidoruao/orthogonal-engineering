/**
 * Parser for `FLEITES_MANIFEST.sha256`.
 *
 * The manifest is the published commitment over the L0 corpus. A claim record
 * that cites a hash absent from the manifest is citing a document nobody can
 * check, so the admission gate rejects it.
 *
 * Format is `sha256sum` output: `<64 hex>  <filename>` (two spaces).
 */

import { readFileSync } from "node:fs";

const LINE = /^([0-9a-f]{64})[ \t]+\*?(.+)$/;

export interface ManifestEntry {
  readonly sha256: string;
  readonly name: string;
}

export interface Manifest {
  readonly entries: readonly ManifestEntry[];
  readonly hashes: ReadonlySet<string>;
  /** Entries that did not parse. Never silently dropped. */
  readonly malformed: readonly string[];
}

/**
 * Parse manifest text. Malformed lines are reported, not ignored: a corpus
 * whose manifest silently loses entries is worse than one that fails loudly.
 */
export function parseManifest(text: string): Manifest {
  const entries: ManifestEntry[] = [];
  const malformed: string[] = [];
  const seen = new Set<string>();

  const lines = text.split(/\r?\n/);
  lines.forEach((line: string, index: number) => {
    const trimmed = line.trim();
    if (trimmed === "") return;
    const match = LINE.exec(trimmed);
    if (match === null) {
      malformed.push(`line ${index + 1}: ${trimmed.slice(0, 80)}`);
      return;
    }
    const sha256 = match[1];
    const name = match[2]?.trim() ?? "";
    if (sha256 === undefined || name === "") {
      malformed.push(`line ${index + 1}: missing hash or filename`);
      return;
    }
    if (seen.has(sha256)) {
      malformed.push(`line ${index + 1}: duplicate hash ${sha256.slice(0, 12)}…`);
      return;
    }
    seen.add(sha256);
    entries.push({ sha256, name });
  });

  return { entries, hashes: seen, malformed };
}

/** Read and parse a manifest from disk. Throws only on I/O failure. */
export function loadManifest(path: string): Manifest {
  const text = readFileSync(path, "utf8");
  return parseManifest(text);
}
