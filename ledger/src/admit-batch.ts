/**
 * Admit and verify every drafted candidate — local only.
 *
 * Each candidate goes through both gates:
 *   1. `admit` — structural, manifest-bound.
 *   2. `verifyQuote` — the quoted span must appear on the cited page of the
 *      file whose hash the claim names.
 *
 * Produces two files:
 *   drafts/verified.jsonl   candidates that passed both gates
 *   drafts/rejected.jsonl   candidates that failed, with the reason code
 *
 * Nothing is published. This is the local pre-commit check.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

import { loadManifest } from "./manifest.js";
import { admit } from "./validate.js";
import { verifyQuote } from "./workbench.js";
import type { ClaimRecord } from "./types.js";

interface CandidateWithLocal extends Record<string, unknown> {
  readonly claimId: string;
}

/**
 * Local review aids that must never reach a publishable record. Stripping them
 * here is not a convenience: the admission gate rejects unknown fields by
 * design, so a candidate carrying these would fail structurally. That is the
 * intended behaviour — it proves the local layer cannot leak upward by
 * accident.
 */
const LOCAL_ONLY_FIELDS = ["sourceName", "note"] as const;

export interface AdmitOutcome {
  readonly claimId: string;
  readonly accepted: boolean;
  readonly code?: string;
  readonly detail?: string;
  readonly record?: ClaimRecord;
}

export async function admitAll(
  candidates: readonly CandidateWithLocal[],
  manifestPath: string,
  sourcesDir: string,
): Promise<AdmitOutcome[]> {
  const manifest = loadManifest(manifestPath);
  const outcomes: AdmitOutcome[] = [];

  for (const candidate of candidates) {
    const stripped: Record<string, unknown> = { ...candidate };
    for (const field of LOCAL_ONLY_FIELDS) {
      delete stripped[field];
    }

    const structural = admit(stripped, manifest.hashes);
    if (!structural.ok) {
      outcomes.push({
        claimId: candidate.claimId,
        accepted: false,
        code: "structure_invalid",
        detail: structural.violations
          .map((violation) => `${violation.code}@${violation.path}`)
          .join(", "),
      });
      continue;
    }

    const quote = await verifyQuote(structural.record, sourcesDir);
    if (!quote.verified) {
      outcomes.push({
        claimId: candidate.claimId,
        accepted: false,
        code: quote.reason?.includes("hash mismatch")
          ? "source_hash_mismatch"
          : "quote_not_found",
        detail: quote.reason ?? "",
      });
      continue;
    }

    outcomes.push({
      claimId: candidate.claimId,
      accepted: true,
      record: structural.record,
    });  }

  return outcomes;
}

function parseArgs(argv: readonly string[]): {
  in: string;
  manifest: string;
  sources: string;
  out: string;
  merge: boolean;
} {
  let input: string | undefined;
  let manifest: string | undefined;
  let sources: string | undefined;
  let out = "drafts";
  let merge = false;
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--in") {
      input = argv[i + 1];
      i += 1;
    } else if (arg === "--manifest") {
      manifest = argv[i + 1];
      i += 1;
    } else if (arg === "--sources") {
      sources = argv[i + 1];
      i += 1;
    } else if (arg === "--out-dir") {
      out = argv[i + 1] ?? out;
      i += 1;
    } else if (arg === "--merge") {
      merge = true;
    }
  }
  if (input === undefined || manifest === undefined || sources === undefined) {
    throw new Error("usage: admit-batch --in <candidates.jsonl> --manifest <path> --sources <dir> [--out-dir <dir>] [--merge]");
  }
  return { in: input, manifest, sources, out, merge };
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("admit-batch.js");

if (invokedDirectly) {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (!existsSync(args.in)) {
      throw new Error(`no such file: ${args.in}`);
    }
    const lines = readFileSync(args.in, "utf8")
      .split(/\r?\n/)
      .filter((line) => line.trim() !== "");
    const candidates = lines.map((line) => JSON.parse(line) as CandidateWithLocal);

    const outcomes = await admitAll(candidates, args.manifest, args.sources);

    mkdirSync(args.out, { recursive: true });
    const accepted = outcomes.filter((outcome) => outcome.accepted && outcome.record !== undefined);
    const rejected = outcomes.filter((outcome) => !outcome.accepted);

    const verifiedPath = `${args.out}/verified.jsonl`;
    const rejectedPath = `${args.out}/rejected.jsonl`;

    // Merge mode appends and dedupes by claimId. Without it, a second batch
    // silently overwrites the first — which happened once, and cost a
    // re-admission of six claims to recover. Default stays overwrite for
    // single-batch use; accumulating ledgers pass --merge.
    const mergeRecords = (
      path: string,
      incoming: readonly unknown[],
      id: (value: unknown) => string,
    ): unknown[] => {
      const existing: unknown[] = [];
      if (existsSync(path)) {
        for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
          if (line.trim() === "") continue;
          try {
            existing.push(JSON.parse(line) as unknown);
          } catch {
            // A malformed existing line is a finding, not something to drop.
            console.error(`WARN: malformed line in ${path} ignored during merge`);
          }
        }
      }
      const byId = new Map<string, unknown>();
      for (const record of existing) byId.set(id(record), record);
      for (const record of incoming) byId.set(id(record), record);
      return [...byId.entries()].sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0)).map(([, v]) => v);
    };

    const claimIdOf = (value: unknown): string => {
      if (typeof value === "object" && value !== null) {
        const candidate = (value as Record<string, unknown>)["claimId"];
        if (typeof candidate === "string") return candidate;
      }
      return "UNIDENTIFIED";
    };

    const verifiedOut = args.merge
      ? mergeRecords(verifiedPath, accepted.map((o) => o.record), claimIdOf)
      : accepted.map((o) => o.record);
    const rejectedOut = args.merge
      ? mergeRecords(
          rejectedPath,
          rejected.map((o) => ({
            claimId: o.claimId,
            code: o.code ?? "unknown",
            detail: o.detail ?? "",
          })),
          claimIdOf,
        )
      : rejected.map((o) => ({
          claimId: o.claimId,
          code: o.code ?? "unknown",
          detail: o.detail ?? "",
        }));

    writeFileSync(
      verifiedPath,
      verifiedOut.map((record) => JSON.stringify(record)).join("\n") +
        (verifiedOut.length === 0 ? "" : "\n"),
    );
    writeFileSync(
      rejectedPath,
      rejectedOut.map((record) => JSON.stringify(record)).join("\n") +
        (rejectedOut.length === 0 ? "" : "\n"),
    );

    console.log(`candidates: ${outcomes.length}`);
    console.log(`accepted:   ${accepted.length}`);
    console.log(`rejected:   ${rejected.length}`);
    if (args.merge) {
      console.log(`verified total after merge: ${verifiedOut.length}`);
    }
    for (const outcome of accepted) {
      console.log(`  OK   ${outcome.claimId}`);
    }
    for (const outcome of rejected) {
      console.log(`  REJ  ${outcome.claimId}: ${outcome.code} — ${outcome.detail}`);
    }
    process.exitCode = rejected.length === 0 ? 0 : 1;
  } catch (error) {
    console.error(`fatal: ${String(error)}`);
    process.exitCode = 2;
  }
}
