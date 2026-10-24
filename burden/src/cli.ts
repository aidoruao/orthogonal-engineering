#!/usr/bin/env node
/**
 * burden — the burden inverter, command line.
 *
 * Exit codes:
 *   0  the check passed (or the command succeeded)
 *   1  the check ran and the claim failed — falsified, broken chain, load-bearing failures
 *   2  usage or I/O error; nothing was admitted
 *   3  internal error: the engine produced a receipt its own gate rejects
 *   4  the claim could not be measured; this is not a pass and not a failure
 *
 * The machine-readable receipt goes to stdout as canonical JSON. The human
 * summary goes to stderr, so a pipe gets data and a terminal gets a sentence.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parseArgs } from "node:util";

import { InadmissibleReceiptError, audit } from "./audit.js";
import { canonicalJson, utcNow } from "./canonical.js";
import { calibrate, renderCalibration } from "./calibrate.js";
import { captureEnvironment } from "./environment.js";
import { investigate } from "./investigate.js";
import { appendReceipt, readLedger, verifyLedger } from "./ledger.js";
import { explain, renderHits, scan, selfTest } from "./scan.js";
import { BEARINGS, CLAIM_ID_PATTERN, type Bearing, type Receipt } from "./types.js";
import { contractJson } from "./validate.js";

const USAGE = `burden — the burden inverter

  burden audit --id ID --source PATH (--quote TEXT | --quote-file PATH)
               [--proposition TEXT] [--sha256 HEX] [--bearing B]
               [--actor NAME] [--record LEDGER]

      Read the source, hash it, locate the span, and issue a receipt.
      Exit 0 verified, 1 falsified, 2 usage/I-O.

  burden investigate --id ID --corpus DIR (--quote TEXT | --quote-file PATH)
               [--ext .txt,.md] [--max-files N] [--sha256 HEX]
               [--bearing B] [--actor NAME] [--exclude PATH]
               [--record LEDGER]

      Find the source yourself: walk the corpus, locate the span, audit it.
      Refuses to guess between ambiguous sources.

  burden scan (--file PATH | --text TEXT) [--strict]
  burden scan --explain RULE_ID

      Lint text for named burden-shifting patterns. A hit is a question.

  burden calibrate [--ledger PATH]
  burden verify    [--ledger PATH] [--expect-head HASH]
  burden head      [--ledger PATH]
  burden schema
  burden self-test

Exit codes: 0 verified/success, 1 falsified or broken chain, 2 usage or I/O,
3 internal error, 4 unmeasured (the claim could not be checked — not a pass,
not a failure).

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
  exclude: { type: "string" },
  ledger: { type: "string" },
  file: { type: "string" },
  text: { type: "string" },
  explain: { type: "string" },
  "expect-head": { type: "string" },
  strict: { type: "boolean" },
} as const;

class UsageError extends Error {}

/** The engine refused its own output. That is a bug in this tool, not the caller. */
class InternalError extends Error {}

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
  const candidate =
    explicit !== null && explicit.trim() !== ""
      ? explicit
      : (process.env["BURDEN_ACTOR"] ?? process.env["USER"] ?? "");
  if (candidate.trim() === "") {
    throw new UsageError(
      "no actor: pass --actor or set BURDEN_ACTOR; an action needs someone accountable for it",
    );
  }
  return candidate;
}

/**
 * Validate the claim id and proposition at the boundary.
 *
 * The engine refuses to emit an inadmissible receipt, which means a malformed
 * id would reach `admitOrThrow` and throw. A malformed argument is a usage
 * error, and usage errors exit 2 with a sentence — not a stack trace.
 */
function claimIdFrom(values: Values): string {
  const id = requiredOption(values, "id");
  if (!CLAIM_ID_PATTERN.test(id)) {
    throw new UsageError(
      `--id "${id}" must match ${CLAIM_ID_PATTERN.source}`,
    );
  }
  return id;
}

function readTextFile(path: string, flag: string): string {
  try {
    return readFileSync(path, "utf8");
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    throw new UsageError(`cannot read ${flag} ${path}: ${message}`);
  }
}

/** A single trailing newline is an editor artifact, not part of the span. */
function readQuoteFile(path: string): string {
  const raw = readTextFile(path, "--quote-file");
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
  const proposition =
    option(values, "proposition") ??
    "the cited span occurs verbatim in the named source";
  if (proposition.trim() === "") {
    throw new UsageError("--proposition cannot be blank");
  }
  return proposition;
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
  let written;
  try {
    written = appendReceipt(path, receipt, utcNow());
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`burden: cannot write ledger ${path}: ${message}\n`);
    return 2;
  }
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

/** 0 verified, 1 falsified, 4 unmeasured. Never collapses the last two. */
function verdictExit(receipt: Receipt): number {
  switch (receipt.verdict.kind) {
    case "verified":
      return 0;
    case "falsified":
      return 1;
    case "unmeasured":
      return 4;
  }
}

function commandAudit(values: Values): number {
  const id = claimIdFrom(values);
  const source = requiredOption(values, "source");
  const quote = quoteFrom(values);
  const proposition = propositionFrom(values);
  const actor = actorFrom(values);
  const sha = option(values, "sha256");
  const falsifierCommand =
    `burden audit --id ${shellQuote(id)} --source ${shellQuote(source)}` +
    quoteFlag(values, quote) +
    (sha === null ? "" : ` --sha256 ${shellQuote(sha)}`);

  const receipt = audit(
    {
      claimId: id,
      claim: proposition,
      bearing: parseBearing(option(values, "bearing")),
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote,
      sourcePath: source,
      displayPath: source,
      expectedSha256: sha,
      falsifierCommand,
      actor,
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
  return verdictExit(receipt);
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

/**
 * Paths the scan must never treat as evidence.
 *
 * The receipt ledger is excluded by default and cannot be re-included: it
 * stores the quotes it has checked, so scanning it always finds them, and a
 * receipt that cites its own ledger is circular evidence.
 */
function excludePathsFrom(values: Values): readonly string[] {
  const paths = [resolve("ledger/receipts.jsonl")];
  const raw = option(values, "exclude");
  if (raw !== null) {
    for (const part of raw.split(",")) {
      const trimmed = part.trim();
      if (trimmed !== "") paths.push(resolve(trimmed));
    }
  }
  return paths;
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
  const id = claimIdFrom(values);
  const corpusArg = requiredOption(values, "corpus");
  const corpus = resolve(corpusArg);
  const quote = quoteFrom(values);
  const proposition = propositionFrom(values);
  const actor = actorFrom(values);
  const maxFiles = maxFilesFrom(values);
  const falsifierCommand =
    `burden investigate --id ${shellQuote(id)} --corpus ${shellQuote(corpusArg)}` +
    quoteFlag(values, quote) +
    ` --max-files ${maxFiles}`;
  const investigation = investigate(
    {
      claimId: id,
      claim: proposition,
      bearing: parseBearing(option(values, "bearing")),
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote,
      root: corpus,
      extensions: extensionsFrom(values),
      maxFiles,
      expectedSha256: option(values, "sha256"),
      falsifierCommand,
      actor,
      excludePaths: excludePathsFrom(values),
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
  return verdictExit(investigation.receipt);
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
  if (file !== null) text = readTextFile(file, "--file");
  else if (inline !== null) text = inline;
  else throw new UsageError("one of --file or --text is required");

  const hits = scan(text);
  process.stdout.write(`${renderHits(hits)}\n`);
  if (values["strict"] === true && hits.length > 0) return 1;
  return 0;
}

function commandCalibrate(values: Values): number {
  const path = option(values, "ledger") ?? "ledger/receipts.jsonl";
  let read;
  try {
    read = readLedger(path);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`burden: cannot read ledger ${path}: ${message}\n`);
    return 2;
  }
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
  const head = option(values, "expect-head");
  let result;
  try {
    result = verifyLedger(path, head);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`burden: cannot read ledger ${path}: ${message}\n`);
    return 2;
  }
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

function commandHead(values: Values): number {
  const path = option(values, "ledger") ?? "ledger/receipts.jsonl";
  let read;
  try {
    read = readLedger(path);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`burden: cannot read ledger ${path}: ${message}\n`);
    return 2;
  }
  if (read.failures.length > 0) {
    process.stderr.write(
      `burden: ledger does not verify, so it has no trustworthy head:\n${read.failures
        .map((failure) => `  line ${failure.line} ${failure.code}: ${failure.detail}`)
        .join("\n")}\n`,
    );
    return 1;
  }
  const last = read.entries.at(-1);
  if (last === undefined) {
    process.stderr.write(`burden: ledger is empty; there is no head to record\n`);
    return 1;
  }
  process.stdout.write(`${last.entrySha256}\n`);
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
      case "head":
        return commandHead(parsed.values);
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
    if (error instanceof InternalError || error instanceof InadmissibleReceiptError) {
      process.stderr.write(`burden: INTERNAL — ${error.message}\n`);
      process.stderr.write(
        "burden: no receipt was admitted. This is a defect in the tool, not in your input.\n",
      );
      return 3;
    }
    throw error;
  }
}

process.exitCode = main(process.argv.slice(2));

