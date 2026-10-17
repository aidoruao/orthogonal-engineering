/**
 * Corpus custody check — local only.
 *
 * The published manifest is a commitment: 108 files, 108 hashes. This module
 * checks that the files actually held on disk are exactly that set. It closes
 * the loop between the commitment and the custody.
 *
 * It reports four kinds of divergence, none silently:
 *   - mismatch   a file whose bytes differ from the commitment
 *   - missing    a committed file that is not on disk
 *   - unlisted   a file on disk that the commitment does not cover
 *   - malformed  a manifest line that did not parse
 *
 * Usage:
 *   node dist/src/corpus.js --manifest <path> --sources <dir>
 *
 * Exit codes: 0 all four lists empty, 1 divergence found, 2 usage or I/O error.
 */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

import { loadManifest } from "./manifest.js";

export interface CorpusReport {
  readonly committed: number;
  readonly matched: number;
  readonly mismatched: readonly { readonly name: string; readonly expected: string; readonly actual: string }[];
  readonly missing: readonly string[];
  readonly unlisted: readonly string[];
  readonly malformed: readonly string[];
}

function sha256Of(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

/**
 * Compare a manifest against a directory.
 *
 * `ignore` names files that are expected on disk but deliberately not
 * committed — the manifest itself is the usual case.
 */
export function verifyCorpus(
  manifestPath: string,
  sourcesDir: string,
  ignore: readonly string[] = [],
): CorpusReport {
  const manifest = loadManifest(manifestPath);
  const ignoreSet = new Set(ignore);

  const mismatched: { name: string; expected: string; actual: string }[] = [];
  const missing: string[] = [];
  let matched = 0;

  for (const entry of manifest.entries) {
    const path = join(sourcesDir, entry.name);
    let size: number;
    try {
      size = statSync(path).size;
    } catch {
      missing.push(entry.name);
      continue;
    }
    if (size < 0) {
      missing.push(entry.name);
      continue;
    }
    const actual = sha256Of(path);
    if (actual === entry.sha256) {
      matched += 1;
    } else {
      mismatched.push({ name: entry.name, expected: entry.sha256, actual });
    }
  }

  const committedNames = new Set(manifest.entries.map((entry) => entry.name));
  const onDisk = readdirSync(sourcesDir).filter((name) => {
    try {
      return statSync(join(sourcesDir, name)).isFile();
    } catch {
      return false;
    }
  });
  const unlisted = onDisk
    .filter((name) => !committedNames.has(name) && !ignoreSet.has(name))
    .sort();

  return {
    committed: manifest.entries.length,
    matched,
    mismatched,
    missing: [...missing].sort(),
    unlisted,
    malformed: manifest.malformed,
  };
}

export function isClean(report: CorpusReport): boolean {
  return (
    report.mismatched.length === 0 &&
    report.missing.length === 0 &&
    report.unlisted.length === 0 &&
    report.malformed.length === 0
  );
}

function parseArgs(argv: readonly string[]): { manifest: string; sources: string } {
  let manifest: string | undefined;
  let sources: string | undefined;
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--manifest") {
      manifest = argv[i + 1];
      i += 1;
    } else if (arg === "--sources") {
      sources = argv[i + 1];
      i += 1;
    }
  }
  if (manifest === undefined || sources === undefined) {
    throw new Error("usage: corpus --manifest <path> --sources <dir>");
  }
  return { manifest, sources };
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("corpus.js");

if (invokedDirectly) {
  try {
    const args = parseArgs(process.argv.slice(2));
    const report = verifyCorpus(args.manifest, args.sources, [
      args.manifest.split("/").pop() ?? "",
    ]);
    console.log(`committed: ${report.committed}`);
    console.log(`matched:   ${report.matched}`);
    console.log(`mismatch:  ${report.mismatched.length}`);
    console.log(`missing:   ${report.missing.length}`);
    console.log(`unlisted:  ${report.unlisted.length}`);
    console.log(`malformed: ${report.malformed.length}`);
    for (const item of report.mismatched) {
      console.log(`  MISMATCH ${item.name} expected=${item.expected.slice(0, 12)}… actual=${item.actual.slice(0, 12)}…`);
    }
    for (const name of report.missing) console.log(`  MISSING ${name}`);
    for (const name of report.unlisted) console.log(`  UNLISTED ${name}`);
    for (const line of report.malformed) console.log(`  MALFORMED ${line}`);
    process.exitCode = isClean(report) ? 0 : 1;
  } catch (error) {
    console.error(`fatal: ${String(error)}`);
    process.exitCode = 2;
  }
}
