/**
 * Verification freshness — the operational form of `L1_DECAY.lean`.
 *
 * A gate run is a claim indexed by the environment it ran in. This module
 * records that environment and compares it to the one in which the last full
 * verification passed.
 *
 * The three outcomes, deliberately distinct:
 *
 *   VERIFIED  the environment is identical to the recorded one. The pass holds.
 *   STALE     the environment differs. The pass says nothing about this one —
 *             it is neither confirmed nor refuted. Re-run to restore VErIFIED.
 *   ABSENT    nothing has ever been recorded. Nothing is claimed.
 *
 * STALE is never reported as failure. That is the whole point of the decay
 * model: an outdated pass is not a lie, but treating it as current is.
 */

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

/** The environment dimensions that can invalidate a verification. */
export interface Fingerprint {
  /** Node major.minor.patch. */
  readonly node: string;
  /** TypeScript compiler version, or "absent". */
  readonly typescript: string;
  /** Lean toolchain version, or "absent". */
  readonly lean: string;
  /** SHA-256 of ledger/package-lock.json, or "absent". */
  readonly lockfile: string;
}

export type Freshness =
  | { readonly status: "verified"; readonly fingerprint: Fingerprint }
  | {
      readonly status: "stale";
      readonly recorded: Fingerprint;
      readonly current: Fingerprint;
      readonly differences: readonly string[];
    }
  | { readonly status: "absent"; readonly current: Fingerprint };

export const FINGERPRINT_FILE = "VERIFIED_ENVIRONMENT.json";

function run(command: string, args: readonly string[], cwd?: string): string | null {
  try {
    const output = execFileSync(command, args, {
      encoding: "utf8",
      timeout: 20_000,
      stdio: ["ignore", "pipe", "ignore"],
      ...(cwd === undefined ? {} : { cwd }),
    });
    return output.trim();
  } catch {
    return null;
  }
}

/** Extract a bare version number from tool output, or null. */
export function parseVersion(output: string | null): string | null {
  if (output === null) return null;
  const match = /(\d+\.\d+\.\d+)/.exec(output);
  return match?.[1] ?? null;
}

/** Compute the fingerprint of the current environment. */
export function computeFingerprint(root: string): Fingerprint {
  const node = parseVersion(process.version);
  // `npx tsc` resolves relative to the working directory. Pin it to the
  // ledger so the fingerprint is the same wherever this is invoked from —
  // otherwise the same environment measures as "absent" from the repo root
  // and "5.9.3" from the ledger, and every check reports STALE.
  const ledgerDir = join(root, "ledger");
  const typescript = parseVersion(run("npx", ["tsc", "--version"], ledgerDir));
  const leanOutput = run("lean", ["--version"]);
  const leanMatch = leanOutput === null ? null : /version (\d+\.\d+\.\d+)/.exec(leanOutput);
  const lean = leanMatch?.[1] ?? null;

  const lockPath = join(root, "ledger", "package-lock.json");
  let lockfile = "absent";
  if (existsSync(lockPath)) {
    lockfile = createHash("sha256").update(readFileSync(lockPath)).digest("hex");
  }

  return {
    node: node ?? "unknown",
    typescript: typescript ?? "absent",
    lean: lean ?? "absent",
    lockfile,
  };
}

const DIMENSIONS: readonly (keyof Fingerprint)[] = ["node", "typescript", "lean", "lockfile"];

/**
 * Compare a recorded fingerprint to the current one.
 *
 * Pure: no I/O, no clock. The same inputs always produce the same verdict,
 * which is what makes the result citable.
 */
export function compareFingerprint(
  recorded: Fingerprint | null,
  current: Fingerprint,
): Freshness {
  if (recorded === null) {
    return { status: "absent", current };
  }
  const differences: string[] = [];
  for (const dimension of DIMENSIONS) {
    if (recorded[dimension] !== current[dimension]) {
      differences.push(`${dimension}: recorded ${recorded[dimension]}, now ${current[dimension]}`);
    }
  }
  if (differences.length === 0) {
    return { status: "verified", fingerprint: current };
  }
  return { status: "stale", recorded, current, differences };
}

/** Read the recorded fingerprint, or null when absent or unreadable. */
export function readRecorded(path: string): Fingerprint | null {
  if (!existsSync(path)) return null;
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8")) as Partial<Fingerprint>;
    if (
      typeof parsed.node === "string" &&
      typeof parsed.typescript === "string" &&
      typeof parsed.lean === "string" &&
      typeof parsed.lockfile === "string"
    ) {
      return {
        node: parsed.node,
        typescript: parsed.typescript,
        lean: parsed.lean,
        lockfile: parsed.lockfile,
      };
    }
    return null;
  } catch {
    return null;
  }
}

/** Deterministic serialization: fixed key order, trailing newline. */
export function serializeFingerprint(fingerprint: Fingerprint): string {
  return (
    JSON.stringify(
      {
        node: fingerprint.node,
        typescript: fingerprint.typescript,
        lean: fingerprint.lean,
        lockfile: fingerprint.lockfile,
      },
      null,
      2,
    ) + "\n"
  );
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("freshness.js");

if (invokedDirectly) {
  const args = process.argv.slice(2);
  const rootIndex = args.indexOf("--root");
  const root = rootIndex >= 0 ? (args[rootIndex + 1] ?? ".") : ".";
  const path = join(root, "ledger", FINGERPRINT_FILE);
  const current = computeFingerprint(root);

  if (args.includes("--update")) {
    writeFileSync(path, serializeFingerprint(current));
    console.log(`recorded verification environment at ${path}`);
    for (const dimension of DIMENSIONS) console.log(`  ${dimension}: ${current[dimension]}`);
    process.exitCode = 0;
  } else {
    const verdict = compareFingerprint(readRecorded(path), current);
    if (verdict.status === "verified") {
      console.log("FRESH: environment matches the recorded verification");
      process.exitCode = 0;
    } else if (verdict.status === "absent") {
      console.log("ABSENT: no verification environment recorded; nothing is claimed");
      for (const dimension of DIMENSIONS) console.log(`  ${dimension}: ${current[dimension]}`);
      process.exitCode = 0;
    } else {
      console.log("STALE: this environment differs from the recorded one");
      for (const difference of verdict.differences) console.log(`  ${difference}`);
      console.log("");
      console.log("A stale pass is not a failure and not a pass. Re-run the gates");
      console.log("in this environment, then record it with --update.");
      // Deliberately exit 0: staleness is information, not a build failure.
      // Making it a failure would train operators to disable the check.
      process.exitCode = 0;
    }
  }
}
