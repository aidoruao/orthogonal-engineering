/**
 * Admission workbench — local only.
 *
 * Takes a candidate claim, binds it to the published manifest, and (when the
 * L0 source directory is available) verifies that the quoted span actually
 * appears on the cited page of the hashed source.
 *
 * The split matters:
 *   - CI can check structure and manifest binding (no L0 needed).
 *   - Quote verification needs L0, so it runs here, on the machine that holds
 *     the corpus, before a claim is ever committed.
 *
 * Usage:
 *   node dist/src/workbench.js <candidate.json> --sources <dir> [--manifest <path>]
 *
 * Exit codes:
 *   0  claim admitted and quote verified
 *   1  claim rejected (structure, manifest binding, or quote)
 *   2  usage or I/O error
 */

import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

import { loadManifest } from "./manifest.js";
import { admit } from "./validate.js";
import { checkQuoteOnPage, extractPdf } from "./extract.js";
import type { ClaimRecord } from "./types.js";

/** Map a docket entry number to the corpus filename. */
export function sourceNameCandidates(documentNumber: number): string[] {
  return [
    `gov.uscourts.cacd.823614.${documentNumber}.0.pdf`,
    `gov.uscourts.cacd.823614.${documentNumber}.0_1.pdf`,
    `gov.uscourts.cacd.823614.${documentNumber}.0_2.pdf`,
    `gov.uscourts.cacd.823614.${documentNumber}.0_3.pdf`,
  ];
}

export interface QuoteVerification {
  readonly verified: boolean;
  readonly sourcePath?: string;
  readonly reason?: string;
  readonly sha256?: string;
}

/**
 * Verify a claim's quote against its local source.
 *
 * The hash is recomputed from the file actually read, so a claim cannot bind
 * to one document and quote another.
 */
export async function verifyQuote(
  record: ClaimRecord,
  sourcesDir: string,
): Promise<QuoteVerification> {
  const candidates = sourceNameCandidates(record.documentNumber);
  const found = candidates
    .map((name) => join(sourcesDir, name))
    .find((path) => existsSync(path));

  if (found === undefined) {
    return {
      verified: false,
      reason: `no local source for document ${record.documentNumber} in ${sourcesDir}`,
    };
  }

  const actual = createHash("sha256").update(readFileSync(found)).digest("hex");
  if (actual !== record.sourceSha256) {
    return {
      verified: false,
      sourcePath: found,
      sha256: actual,
      reason: `source hash mismatch: claim cites ${record.sourceSha256.slice(0, 12)}… but the file is ${actual.slice(0, 12)}…`,
    };
  }

  const doc = await extractPdf(found);
  const check = checkQuoteOnPage(doc, record.page, record.quote);
  if (!check.found) {
    return {
      verified: false,
      sourcePath: found,
      sha256: actual,
      reason: check.reason ?? "quote not found",
    };
  }

  return { verified: true, sourcePath: found, sha256: actual };
}

interface CliArgs {
  readonly candidate: string;
  readonly sources?: string;
  readonly manifest: string;
}

function parseArgs(argv: readonly string[]): CliArgs {
  const positional: string[] = [];
  let sources: string | undefined;
  let manifest = "evidence/fleites/FLEITES_MANIFEST.sha256";

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--sources") {
      const next = argv[i + 1];
      if (next === undefined) throw new Error("--sources requires a directory");
      sources = next;
      i += 1;
    } else if (arg === "--manifest") {
      const next = argv[i + 1];
      if (next === undefined) throw new Error("--manifest requires a path");
      manifest = next;
      i += 1;
    } else if (arg !== undefined) {
      positional.push(arg);
    }
  }

  const candidate = positional[0];
  if (candidate === undefined) {
    throw new Error("usage: workbench <candidate.json> [--sources DIR] [--manifest PATH]");
  }
  return sources === undefined ? { candidate, manifest } : { candidate, sources, manifest };
}

async function main(): Promise<number> {
  let args: CliArgs;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(String(error instanceof Error ? error.message : error));
    return 2;
  }

  let candidate: unknown;
  try {
    candidate = JSON.parse(readFileSync(args.candidate, "utf8")) as unknown;
  } catch (error) {
    console.error(`cannot read candidate: ${String(error)}`);
    return 2;
  }

  const manifest = loadManifest(args.manifest);
  if (manifest.malformed.length > 0) {
    console.error("manifest has malformed lines; refusing to admit against it:");
    for (const line of manifest.malformed) console.error(`  ${line}`);
    return 2;
  }

  const result = admit(candidate, manifest.hashes);
  if (!result.ok) {
    console.error("REJECTED — structural");
    for (const violation of result.violations) {
      console.error(`  ${violation.code} at ${violation.path}: ${violation.message}`);
    }
    return 1;
  }

  console.log(`admitted structurally: ${result.record.claimId}`);

  if (args.sources === undefined) {
    console.log("quote NOT verified (no --sources given); local verification is required before commit");
    return 0;
  }

  const verification = await verifyQuote(result.record, args.sources);
  if (!verification.verified) {
    console.error(`REJECTED — quote: ${verification.reason ?? "unknown"}`);
    if (verification.sourcePath !== undefined) {
      console.error(`  source: ${verification.sourcePath}`);
    }
    return 1;
  }

  console.log(`quote VERIFIED on page ${result.record.page} of ${verification.sourcePath ?? ""}`);
  console.log(`  source sha256: ${verification.sha256 ?? ""}`);
  return 0;
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("workbench.js");

if (invokedDirectly) {
  main()
    .then((code) => {
      process.exitCode = code;
    })
    .catch((error: unknown) => {
      console.error(`fatal: ${String(error)}`);
      process.exitCode = 2;
    });
}
