/**
 * Coverage analysis — the operational form of `L1_COVERAGE.lean`.
 *
 * Two numbers, deliberately separate:
 *
 *   claims        how many verified records the ledger holds
 *   documents     how many distinct docket documents they cite
 *
 * A ledger can grow the first without moving the second. Only the second
 * compounds: each dark document examined is a strict gain, and by
 * `snowball`, N distinct documents cover exactly N.
 *
 * Runs locally against the manifest and the drafts. Never publishes content.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { parseManifest } from "../src/manifest.js";

export interface ClaimLike {
  readonly claimId: string;
  readonly documentNumber: number;
}

export interface CoverageReport {
  /** Documents present in the manifest. */
  readonly manifestDocs: readonly number[];
  /** Documents cited by at least one claim. */
  readonly coveredDocs: readonly number[];
  /** Documents with no claim. */
  readonly darkDocs: readonly number[];
  readonly claimCount: number;
  /** Claims whose document is not in the manifest: a serious defect. */
  readonly unboundClaims: readonly string[];
  /** Claims per covered document, descending. */
  readonly perDocument: readonly { readonly doc: number; readonly claims: number }[];
}

/** Parse a JSONL file of claim records. Malformed lines are reported loudly. */
export function readClaims(path: string): { claims: ClaimLike[]; malformed: string[] } {
  const claims: ClaimLike[] = [];
  const malformed: string[] = [];
  if (!existsSync(path)) return { claims, malformed };

  readFileSync(path, "utf8")
    .split(/\r?\n/)
    .forEach((line, index) => {
      const trimmed = line.trim();
      if (trimmed === "") return;
      try {
        const parsed = JSON.parse(trimmed) as Record<string, unknown>;
        const claimId = parsed["claimId"];
        const documentNumber = parsed["documentNumber"];
        if (typeof claimId !== "string" || typeof documentNumber !== "number") {
          malformed.push(`line ${index + 1}: missing claimId or documentNumber`);
          return;
        }
        claims.push({ claimId, documentNumber });
      } catch {
        malformed.push(`line ${index + 1}: not JSON`);
      }
    });

  return { claims, malformed };
}

/** Document numbers present in the manifest text. */
export function manifestDocuments(manifestText: string): number[] {
  const docs = new Set<number>();
  for (const entry of parseManifest(manifestText).entries) {
    const match = /823614\.(\d+)\./.exec(entry.name);
    if (match?.[1] !== undefined) docs.add(Number(match[1]));
  }
  return [...docs].sort((a, b) => a - b);
}

/**
 * Compute coverage.
 *
 * Pure: no I/O, no clock, no environment. The same claims and manifest always
 * yield the same report, which is what makes the number citable.
 */
export function computeCoverage(
  claims: readonly ClaimLike[],
  manifestDocs: readonly number[],
): CoverageReport {
  const manifest = new Set(manifestDocs);
  const counts = new Map<number, number>();
  const unboundClaims: string[] = [];

  for (const claim of claims) {
    if (!manifest.has(claim.documentNumber)) {
      unboundClaims.push(claim.claimId);
      continue;
    }
    counts.set(claim.documentNumber, (counts.get(claim.documentNumber) ?? 0) + 1);
  }

  const coveredDocs = [...counts.keys()].sort((a, b) => a - b);
  const darkDocs = manifestDocs.filter((doc) => !counts.has(doc));
  const perDocument = [...counts.entries()]
    .map(([doc, claimCount]) => ({ doc, claims: claimCount }))
    .sort((a, b) => b.claims - a.claims || a.doc - b.doc);

  return {
    manifestDocs,
    coveredDocs,
    darkDocs,
    claimCount: claims.length,
    unboundClaims: unboundClaims.sort(),
    perDocument,
  };
}

/** Claims that duplicate an existing (document) — zero marginal coverage. */
export function redundantClaims(report: CoverageReport): number {
  return report.perDocument.reduce((sum, entry) => sum + Math.max(0, entry.claims - 1), 0);
}

export function formatReport(report: CoverageReport): string {
  const lines: string[] = [];
  const total = report.manifestDocs.length;
  const covered = report.coveredDocs.length;
  const pct = total === 0 ? 0 : Math.round((covered / total) * 100);

  lines.push(`claims:            ${report.claimCount}`);
  lines.push(`documents covered: ${covered}/${total} (${pct}%)`);
  lines.push(`documents dark:    ${report.darkDocs.length}`);
  lines.push(`redundant claims:  ${redundantClaims(report)} (zero marginal coverage)`);
  if (report.unboundClaims.length > 0) {
    lines.push(`unbound claims:    ${report.unboundClaims.join(", ")} — NOT in the manifest`);
  }
  lines.push("");
  lines.push("per document:");
  for (const entry of report.perDocument) {
    lines.push(`  doc ${String(entry.doc).padStart(4)}: ${entry.claims}`);
  }
  lines.push("");
  lines.push("dark:");
  lines.push(`  ${report.darkDocs.join(" ")}`);
  return lines.join("\n");
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("coverage.js");

if (invokedDirectly) {
  const arg = (name: string, fallback: string): string => {
    const index = process.argv.indexOf(`--${name}`);
    return index < 0 ? fallback : (process.argv[index + 1] ?? fallback);
  };
  const root = arg("root", "..");
  const manifestPath = arg("manifest", join(root, "evidence/fleites/FLEITES_MANIFEST.sha256"));
  const claimsPath = arg("claims", join(root, "ledger/drafts/verified.jsonl"));
  const json = process.argv.includes("--json");

  if (!existsSync(manifestPath)) {
    console.log(`SKIP: no manifest at ${manifestPath}`);
    process.exitCode = 0;
  } else {
    const manifestDocs = manifestDocuments(readFileSync(manifestPath, "utf8"));
    const { claims, malformed } = readClaims(claimsPath);
    const report = computeCoverage(claims, manifestDocs);

    if (json) {
      console.log(JSON.stringify({ ...report, malformed }, null, 2));
    } else {
      console.log(formatReport(report));
      if (malformed.length > 0) {
        console.log("");
        console.log("MALFORMED claim lines (not counted):");
        for (const line of malformed) console.log(`  ${line}`);
      }
    }

    // A claim citing a document outside the manifest is a hard failure: it
    // asserts something the published commitment does not cover.
    process.exitCode = report.unboundClaims.length === 0 && malformed.length === 0 ? 0 : 1;
  }
}
