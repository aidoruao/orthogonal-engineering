#!/usr/bin/env node
/**
 * burden — the burden inverter, command line.
 *
 * Exit codes:
 *   0  the check passed (or the command succeeded)
 *   1  the check failed — a falsified claim, a broken chain, load-bearing failures
 *   2  usage or I/O error; nothing was admitted
 *
 * The machine-readable receipt goes to stdout as canonical JSON. The human
 * summary goes to stderr, so a pipe gets data and a terminal gets a sentence.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parseArgs } from "node:util";

import { audit } from "./audit.js";
import { canonicalJson, utcNow } from "./canonical.js";
import { calibrate, renderCalibration } from "./calibrate.js";
import { captureEnvironment } from "./environment.js";
import { investigate } from "./investigate.js";
import { appendReceipt, readLedger, verifyLedger } from "./ledger.js";
import { explain, renderHits, scan, selfTest } from "./scan.js";
import { BEARINGS, type Bearing, type Receipt } from "./types.js";
import { contractJson } from "./validate.js";

const USAGE = `burden — the burden inverter

  burden audit --id ID --source PATH (--quote TEXT | --quote-file PATH)
               [--proposition TEXT] [--sha256 HEX] [--bearing B]
               [--actor NAME] [--record LEDGER]

      Read the source, hash it, locate the span, and issue a receipt.
      Exit 0 verified, 1 falsified, 2 usage/I-O.

  burden investigate --id ID --corpus DIR (--quote TEXT | --quote-file PATH)
               [--ext .txt,.md] [--max-files N] [--sha256 HEX]
               [--bearing B] [--actor NAME] [--record LEDGER]

      Find the source yourself: walk the corpus, locate the span, audit it.
      Refuses to guess between ambiguous sources.

  burden scan (--file PATH | --text TEXT) [--strict]
  burden scan --explain RULE_ID

      Lint text for named burden-shifting patterns. A hit is a question.

  burden calibrate [--ledger PATH]
  burden verify    [--ledger PATH] [--expect-head HASH]
  burden schema
  burden self-test

Bearing: ${BEARINGS.join(" | ")}. A load-bearing failure is critical.
`;

const OPTIONS = {
  id: { type: "string" },
  source: { type: "string" },
  proposition: { type: "string" },
  quote: { type: "string" },
  "quote-file": { type: "string" },
  sha256: { type: "string" },
  bearing: { type: "string" },
  actor: { type: "string" },
  record: { type: "string" },
  corpus: { type: "string" },
  ext: { type: "string" },
  "max-files": { type: "string" },
  ledger: { type: "string" },
  file: { type: "string" },
  text: { type: "string" },
  explain: { type: "string" },
  "expect-head": { type: "string" },
  strict: { type: "boolean" },
} as const;

class UsageError extends Error {}

type Values = Readonly<Record<string, string | boolean | undefined>>;

type Parsed = {
  readonly values: Values;
  readonly positionals: readonly string[];
};

function option(values: Values, name: string): string | null {
  const value = values[name];
  if (value === undefined) return null;
  if (typeof value !== "string") {
    throw new UsageError(`--${name} requires a value`);
  }
  return value;
}

function requiredOption(values: Values, name: string): string {
  const value = option(values, name);
  if (value === null || value.trim() === "") {
    throw new UsageError(`--${name} is required`);
  }
  return value;
}

function parseBearing(raw: string | null): Bearing {
  const value = raw ?? "supporting";
  const found = BEARINGS.find((bearing) => bearing === value);
  if (found === undefined) {
    throw new UsageError(`--bearing must be one of ${BEARINGS.join(", ")}`);
  }
  return found;
}

function actorFrom(values: Values): string {
  const explicit = option(values, "actor");
  if (explicit !== null && explicit.trim() !== "") return explicit;
  return process.env["BURDEN_ACTOR"] ?? process.env["USER"] ?? "unknown-actor";
}

/** A single trailing newline is an editor artifact, not part of the span. */
function readQuoteFile(path: string): string {
  const raw = readFileSync(path, "utf8");
  if (raw.endsWith("\r\n")) return raw.slice(0, -2);
  if (raw.endsWith("\n")) return raw.slice(0, -1);
  return raw;
}

function quoteFrom(values: Values): string {
  const inline = option(values, "quote");
  const file = option(values, "quote-file");
  if (inline !== null && file !== null) {
    throw new UsageError("supply --quote or --quote-file, not both");
  }
  if (inline !== null) return inline;
  if (file !== null) return readQuoteFile(file);
  throw new UsageError("one of --quote or --quote-file is required");
}

/** POSIX single-quote escaping, so a recorded falsifier can actually be run. */
function shellQuote(value: string): string {
  if (/^[A-Za-z0-9_./:=@+-]+$/.test(value)) return value;
  return `'${value.replace(/'/g, "'\\''")}'`;
}

/** Reconstruct the span argument exactly as it was supplied. */
function quoteFlag(values: Values, quote: string): string {
  const file = option(values, "quote-file");
  if (file !== null) return ` --quote-file ${shellQuote(file)}`;
  return ` --quote ${shellQuote(quote)}`;
}

function propositionFrom(values: Values): string {
  return (
    option(values, "proposition") ??
    "the cited span occurs verbatim in the named source"
  );
}

function summarise(receipt: Receipt): string {
  const source =
    receipt.source === null ? "<no source>" : `${receipt.source.path} @ ${receipt.source.sha256.slice(0, 12)}…`;
  return [
    `burden: ${receipt.verdict.code} [${receipt.verdict.kind}] tier=${receipt.tier} bearing=${receipt.bearing}`,
    `  ${receipt.verdict.detail}`,
    `  source: ${source}`,
    `  owner: ${receipt.owner.actor} (${receipt.owner.tool})`,
    `  falsifier: ${receipt.falsifier.command}`,
  ].join("\n");
}

function record(path: string, receipt: Receipt): number {
  const written = appendReceipt(path, receipt, utcNow());
  if (!written.ok) {
    process.stderr.write(
      `burden: refusing to append to a broken ledger:\n${written.failures
        .map((failure) => `  line ${failure.line} ${failure.code}: ${failure.detail}`)
        .join("\n")}\n`,
    );
    return 2;
  }
  process.stderr.write(`burden: recorded as entry ${written.entry.seq} in ${path}\n`);
  return 0;
}

function commandAudit(values: Values): number {
  const id = requiredOption(values, "id");
  const source = requiredOption(values, "source");
  const quote = quoteFrom(values);
  const sha = option(values, "sha256");
  const falsifierCommand =
    `burden audit --id ${shellQuote(id)} --source ${shellQuote(source)}` +
    quoteFlag(values, quote) +
    (sha === null ? "" : ` --sha256 ${shellQuote(sha)}`);

  const receipt = audit(
    {
      claimId: id,
      claim: propositionFrom(values),
      bearing: parseBearing(option(values, "bearing")),
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote,
      sourcePath: source,
      displayPath: source,
      expectedSha256: sha,
      falsifierCommand,
      actor: actorFrom(values),
    },
    captureEnvironment(),
  );

  process.stdout.write(`${canonicalJson(receipt)}\n`);
  process.stderr.write(`${summarise(receipt)}\n`);

  const ledgerPath = option(values, "record");
  if (ledgerPath !== null) {
    const written = record(ledgerPath, receipt);
    if (written !== 0) return written;
  }
  return receipt.verdict.kind === "verified" ? 0 : 1;
}

const DEFAULT_EXTENSIONS: readonly string[] = [
  ".txt",
  ".md",
  ".jsonl",
  ".json",
  ".csv",
  ".lean",
  ".ts",
];

function extensionsFrom(values: Values): readonly string[] {
  const raw = option(values, "ext");
  if (raw === null) return DEFAULT_EXTENSIONS;
  const parts = raw
    .split(",")
    .map((part) => part.trim().toLowerCase())
    .filter((part) => part !== "")
    .map((part) => (part.startsWith(".") ? part : `.${part}`));
  if (parts.length === 0) throw new UsageError("--ext listed no extensions");
  return parts;
}

function maxFilesFrom(values: Values): number {
  const raw = option(values, "max-files");
  if (raw === null) return 400;
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new UsageError("--max-files must be a positive integer");
  }
  return parsed;
}

function commandInvestigate(values: Values): number {
  const id = requiredOption(values, "id");
  const corpusArg = requiredOption(values, "corpus");
  const corpus = resolve(corpusArg);
  const quote = quoteFrom(values);
  const maxFiles = maxFilesFrom(values);
  const falsifierCommand =
    `burden investigate --id ${shellQuote(id)} --corpus ${shellQuote(corpusArg)}` +
    quoteFlag(values, quote) +
    ` --max-files ${maxFiles}`;
  const investigation = investigate(
    {
      claimId: id,
      claim: propositionFrom(values),
      bearing: parseBearing(option(values, "bearing")),
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote,
      root: corpus,
      extensions: extensionsFrom(values),
      maxFiles,
      expectedSha256: option(values, "sha256"),
      falsifierCommand,
      actor: actorFrom(values),
    },
    captureEnvironment(),
  );

  process.stdout.write(`${canonicalJson(investigation.receipt)}\n`);
  process.stderr.write(
    `${summarise(investigation.receipt)}\n  corpus: ${investigation.scanned} scanned, ${investigation.skipped} skipped, ${investigation.matches.length} matched\n`,
  );

  const ledgerPath = option(values, "record");
  if (ledgerPath !== null) {
    const written = record(ledgerPath, investigation.receipt);
    if (written !== 0) return written;
  }
  return investigation.receipt.verdict.kind === "verified" ? 0 : 1;
}

function commandScan(values: Values): number {
  const explainId = option(values, "explain");
  if (explainId !== null) {
    const rule = explain(explainId);
    if (rule === null) {
      process.stderr.write(`burden: unknown rule "${explainId}"\n`);
      return 2;
    }
    process.stdout.write(
      `${canonicalJson({
        id: rule.id,
        spiral: rule.spiral,
        intent: rule.intent,
        pattern: rule.pattern.source,
        flags: rule.pattern.flags,
        example: rule.example,
        antiExample: rule.antiExample,
      })}\n`,
    );
    return 0;
  }

  const file = option(values, "file");
  const inline = option(values, "text");
  if (file !== null && inline !== null) {
    throw new UsageError("supply --file or --text, not both");
  }
  let text: string;
  if (file !== null) text = readFileSync(file, "utf8");
  else if (inline !== null) text = inline;
  else throw new UsageError("one of --file or --text is required");

  const hits = scan(text);
  process.stdout.write(`${renderHits(hits)}\n`);
  if (values["strict"] === true && hits.length > 0) return 1;
  return 0;
}

function commandCalibrate(values: Values): number {
  const path = option(values, "ledger") ?? "ledger/receipts.jsonl";
  const read = readLedger(path);
  if (read.failures.length > 0) {
    process.stderr.write(
      `burden: ledger does not verify; calibration would be meaningless:\n${read.failures
        .map((failure) => `  line ${failure.line} ${failure.code}: ${failure.detail}`)
        .join("\n")}\n`,
    );
    return 1;
  }
  const calibration = calibrate(read.entries);
  process.stdout.write(`${renderCalibration(calibration)}\n`);
  return calibration.loadBearingFailures.length > 0 ? 1 : 0;
}

function commandVerify(values: Values): number {
  const path = option(values, "ledger") ?? "ledger/receipts.jsonl";
  const result = verifyLedger(path, option(values, "expect-head"));
  if (!result.ok) {
    process.stderr.write(
      `burden: ledger BROKEN at ${result.entries} verified entries\n${result.failures
        .map((failure) => `  line ${failure.line} ${failure.code}: ${failure.detail}`)
        .join("\n")}\n`,
    );
    return 1;
  }
  process.stdout.write(`ledger verified: ${result.entries} entries, chain intact\n`);
  return 0;
}

function commandSchema(): number {
  process.stdout.write(`${canonicalJson(contractJson())}\n`);
  return 0;
}

function commandSelfTest(): number {
  const results = selfTest();
  const lines = results.map(
    (result) =>
      `${result.ok ? "OK  " : "FAIL"} ${result.rule} exampleHit=${String(
        result.exampleHit,
      )} antiExampleClean=${String(result.antiExampleClean)}`,
  );
  process.stdout.write(`${lines.join("\n")}\n`);
  const failed = results.filter((result) => !result.ok);
  if (failed.length > 0) {
    process.stderr.write(
      `burden: ${failed.length} rule(s) failed their own falsifier\n`,
    );
    return 1;
  }
  return 0;
}

function parseArguments(argv: readonly string[]): Parsed | null {
  try {
    const parsed = parseArgs({
      args: [...argv],
      allowPositionals: true,
      options: OPTIONS,
    });
    return { values: parsed.values, positionals: parsed.positionals };
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`burden: ${message}\n\n${USAGE}`);
    return null;
  }
}

function main(argv: readonly string[]): number {
  const parsed = parseArguments(argv);
  if (parsed === null) return 2;
  try {
    const command = parsed.positionals[0];
    if (command === undefined) {
      process.stderr.write(USAGE);
      return 2;
    }
    switch (command) {
      case "audit":
        return commandAudit(parsed.values);
      case "investigate":
        return commandInvestigate(parsed.values);
      case "scan":
        return commandScan(parsed.values);
      case "calibrate":
        return commandCalibrate(parsed.values);
      case "verify":
        return commandVerify(parsed.values);
      case "schema":
        return commandSchema();
      case "self-test":
        return commandSelfTest();
      default:
        throw new UsageError(`unknown command "${command}"`);
    }
  } catch (error: unknown) {
    if (error instanceof UsageError) {
      process.stderr.write(`burden: ${error.message}\n\n${USAGE}`);
      return 2;
    }
    throw error;
  }
}

process.exitCode = main(process.argv.slice(2));

