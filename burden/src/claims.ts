/**
 * Batch claim audit — the tool applied to its own corpus.
 *
 * This is the out-of-box trial. It reads the ledger's published claim records
 * (`ledger/drafts/verified.jsonl`), locates each source in the L0 corpus by
 * hash, extracts the cited page, and checks that the quoted span is on that
 * page. Every claim yields a receipt; the receipts chain into their own
 * append-only ledger.
 *
 * Two rules of honesty govern this file:
 *
 * 1. **One quote matcher, not two.** `checkQuoteOnPage` and
 *    `normalizeForComparison` are imported from `ledger/`, not reimplemented.
 *    A second matcher would let the two tools disagree about the same claim,
 *    and this package exists precisely to catch disagreement. If the ledger's
 *    extractor is not built, the audit reports `unmeasured` — never a silent
 *    pass and never a false failure.
 *
 * 2. **A missing tool is not a failed claim.** No extractor, no corpus, or no
 *    manifest means the claim was not checked. That is `unmeasured`, and it
 *    does not enter the calibration denominator.
 *
 * Bearing is not in the claim records. Load-bearingness is a judgement about
 * consequence, not a property of the document, so it cannot be derived from
 * `nature` without inventing a rule. The operator supplies it and the summary
 * says so plainly.
 */

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

import { sha256Hex } from "./canonical.js";
import { composeReceipt, admitOrThrow } from "./audit.js";
import type {
  Bearing,
  DerivationStep,
  Environment,
  Receipt,
} from "./types.js";

/** One published claim record, as it appears in the ledger. */
export type ClaimInput = {
  readonly claimId: string;
  readonly docket: string;
  readonly documentNumber: number;
  readonly page: number;
  readonly paragraph?: number;
  readonly quote: string;
  readonly sourceSha256: string;
  readonly nature: string;
};

export type ParsedClaim = {
  readonly claim: ClaimInput | null;
  readonly error: string | null;
};

function isRecord(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function str(record: Readonly<Record<string, unknown>>, key: string): string | null {
  const value = record[key];
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

function num(record: Readonly<Record<string, unknown>>, key: string): number | null {
  const value = record[key];
  return typeof value === "number" && Number.isInteger(value) ? value : null;
}

/**
 * Parse one claim line. A malformed line is an error, never a silent skip:
 * a claim the tool cannot read is a claim nobody has checked.
 */
export function parseClaim(line: string): ParsedClaim {
  let raw: unknown;
  try {
    raw = JSON.parse(line);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return { claim: null, error: `unparseable JSON: ${message}` };
  }
  if (!isRecord(raw)) return { claim: null, error: "not a JSON object" };

  const claimId = str(raw, "claimId");
  const docket = str(raw, "docket");
  const documentNumber = num(raw, "documentNumber");
  const page = num(raw, "page");
  const quote = str(raw, "quote");
  const sourceSha256 = str(raw, "sourceSha256");
  const nature = str(raw, "nature");

  const missing: string[] = [];
  if (claimId === null) missing.push("claimId");
  if (docket === null) missing.push("docket");
  if (documentNumber === null) missing.push("documentNumber");
  if (page === null) missing.push("page");
  if (quote === null) missing.push("quote");
  if (sourceSha256 === null) missing.push("sourceSha256");
  if (nature === null) missing.push("nature");
  if (missing.length > 0) {
    return { claim: null, error: `missing or invalid: ${missing.join(", ")}` };
  }

  const paragraph = num(raw, "paragraph");
  const base = {
    claimId: claimId as string,
    docket: docket as string,
    documentNumber: documentNumber as number,
    page: page as number,
    quote: quote as string,
    sourceSha256: sourceSha256 as string,
    nature: nature as string,
  };
  return {
    claim: paragraph === null ? base : { ...base, paragraph },
    error: null,
  };
}

/** Parse a manifest (`sha256  path` per line) into hash → file name. */
export function parseManifest(text: string): Map<string, string> {
  const map = new Map<string, string>();
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (trimmed === "" || trimmed.startsWith("#")) continue;
    const match = /^([0-9a-f]{64})\s+\*?(.+)$/.exec(trimmed);
    if (match === null) continue;
    const [, hash, path] = match;
    if (hash === undefined || path === undefined) continue;
    map.set(hash, path.trim());
  }
  return map;
}

/** The shape burden needs from the ledger's extractor. Structural, not a cast. */
type PageTextLike = { readonly page: number; readonly text: string };
type DocumentLike = { readonly pages: readonly PageTextLike[]; readonly totalPages: number };
type QuoteCheckLike = { readonly found: boolean; readonly page: number; readonly reason?: string };

export type Extractor = {
  readonly extractPdf: (path: string) => Promise<DocumentLike>;
  readonly checkQuoteOnPage: (doc: DocumentLike, page: number, quote: string) => QuoteCheckLike;
};

/**
 * Load the ledger's extractor.
 *
 * Returns a reason string instead of throwing when it is unavailable, because
 * an absent capability is a fact about this machine — recorded as `unmeasured`,
 * not raised as an error and not reported as a failed claim.
 */
export async function loadExtractor(
  modulePath: string,
): Promise<{ readonly extractor: Extractor | null; readonly error: string | null }> {
  let loaded: unknown;
  try {
    loaded = await import(pathToFileURL(modulePath).href);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return { extractor: null, error: `cannot load extractor at ${modulePath}: ${message}` };
  }
  if (!isRecord(loaded)) {
    return { extractor: null, error: `extractor module at ${modulePath} is not an object` };
  }
  const extractPdf = loaded["extractPdf"];
  const checkQuoteOnPage = loaded["checkQuoteOnPage"];
  if (typeof extractPdf !== "function" || typeof checkQuoteOnPage !== "function") {
    return {
      extractor: null,
      error: `extractor module at ${modulePath} does not export extractPdf and checkQuoteOnPage`,
    };
  }
  return {
    extractor: {
      extractPdf: extractPdf as Extractor["extractPdf"],
      checkQuoteOnPage: checkQuoteOnPage as Extractor["checkQuoteOnPage"],
    },
    error: null,
  };
}

export type ClaimAuditInput = {
  readonly claim: ClaimInput;
  readonly corpusDir: string;
  /** The corpus path as the operator typed it, for a portable falsifier command. */
  readonly corpusLabel: string;
  readonly manifest: ReadonlyMap<string, string>;
  readonly bearing: Bearing;
  readonly actor: string;
  readonly instrument: string;
};

/** Build a receipt for a claim that was not checked, and say why. */
function unmeasured(args: {
  readonly input: ClaimAuditInput;
  readonly env: Environment;
  readonly code: string;
  readonly detail: string;
  readonly steps: readonly DerivationStep[];
}): Receipt {
  const { input } = args;
  return admitOrThrow(
    composeReceipt({
      input: {
        claimId: input.claim.claimId,
        claim: `page ${input.claim.page} of doc ${input.claim.documentNumber} contains the quoted span`,
        bearing: input.bearing,
        checkability: "machine_checkable",
        missingMeasurement: args.detail,
        quote: input.claim.quote,
        sourcePath: "",
        displayPath: `${input.claim.docket} doc ${input.claim.documentNumber} p.${input.claim.page}`,
        expectedSha256: input.claim.sourceSha256,
        falsifierCommand: `${input.instrument} claims --claims <file> --corpus ${input.corpusLabel}`,
        actor: input.actor,
      },
      env: args.env,
      tier: "unverified",
      source: null,
      derivation: args.steps,
      verdict: { kind: "unmeasured", code: args.code, detail: args.detail },
    }),
  );
}

/**
 * Audit one claim. Always returns an admissible receipt: verified, falsified,
 * or unmeasured, each with the check that produced it.
 */
export async function auditClaim(
  input: ClaimAuditInput,
  env: Environment,
  extractor: Extractor,
): Promise<Receipt> {
  const display = `${input.claim.docket} doc ${input.claim.documentNumber} p.${input.claim.page}`;
  const claimText = `${display} contains the quoted span`;
  const falsifierCommand = `${input.instrument} claims --claims <file> --corpus ${input.corpusLabel}`;

  const fileName = input.manifest.get(input.claim.sourceSha256);
  if (fileName === undefined) {
    return unmeasured({
      input,
      env,
      code: "SOURCE_NOT_IN_MANIFEST",
      detail: `no file in the manifest hashes to ${input.claim.sourceSha256}; the claim cites a document the published commitment does not contain`,
      steps: [
        {
          check: "manifest_lookup",
          ok: false,
          detail: `hash ${input.claim.sourceSha256} is absent from the manifest`,
        },
      ],
    });
  }

  const path = `${input.corpusDir}/${fileName}`;
  let bytes: Uint8Array;
  try {
    bytes = readFileSync(path);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return unmeasured({
      input,
      env,
      code: "SOURCE_MISSING",
      detail: `the manifest names ${fileName} but it could not be read: ${message}`,
      steps: [
        { check: "manifest_lookup", ok: true, detail: `hash maps to ${fileName}` },
        { check: "source_read", ok: false, detail: message },
      ],
    });
  }

  const actual = sha256Hex(bytes);
  const hashStep: DerivationStep = {
    check: "source_sha256",
    ok: actual === input.claim.sourceSha256,
    detail: `computed ${actual}; claim names ${input.claim.sourceSha256}`,
  };
  if (!hashStep.ok) {
    return admitOrThrow(
      composeReceipt({
        input: {
          claimId: input.claim.claimId,
          claim: claimText,
          bearing: input.bearing,
          checkability: "machine_checkable",
          missingMeasurement: null,
          quote: input.claim.quote,
          sourcePath: path,
          displayPath: fileName,
          expectedSha256: input.claim.sourceSha256,
          falsifierCommand,
          actor: input.actor,
        },
        env,
        tier: "unverified",
        source: { path: fileName, sha256: actual, bytes: bytes.byteLength },
        derivation: [
          { check: "manifest_lookup", ok: true, detail: `hash maps to ${fileName}` },
          {
            check: "source_read",
            ok: true,
            detail: `${bytes.byteLength} bytes read from ${fileName}`,
          },
          hashStep,
        ],
        verdict: {
          kind: "falsified",
          code: "SOURCE_HASH_MISMATCH",
          detail: `${fileName} is not the file the claim names, so its page proves nothing about this claim`,
        },
      }),
    );
  }

  let doc: DocumentLike;
  try {
    doc = await extractor.extractPdf(path);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return unmeasured({
      input,
      env,
      code: "EXTRACTION_FAILED",
      detail: `the cited document could not be text-extracted, so the page was not read: ${message}`,
      steps: [
        { check: "manifest_lookup", ok: true, detail: `hash maps to ${fileName}` },
        { check: "source_sha256", ok: true, detail: `matches ${actual}` },
        { check: "page_extract", ok: false, detail: message },
      ],
    });
  }

  const extractStep: DerivationStep = {
    check: "page_extract",
    ok: true,
    detail: `${doc.totalPages} pages extracted from ${fileName}`,
  };

  const check = extractor.checkQuoteOnPage(doc, input.claim.page, input.claim.quote);
  const quoteStep: DerivationStep = {
    check: "quote_on_page",
    ok: check.found,
    detail: check.found
      ? `the span occurs on page ${check.page} of ${fileName}`
      : (check.reason ?? `the span does not occur on page ${input.claim.page}`),
  };

  const source = { path: fileName, sha256: actual, bytes: bytes.byteLength };
  const base = {
    claimId: input.claim.claimId,
    claim: claimText,
    bearing: input.bearing,
    checkability: "machine_checkable" as const,
    missingMeasurement: null,
    quote: input.claim.quote,
    sourcePath: path,
    displayPath: fileName,
    expectedSha256: input.claim.sourceSha256,
    falsifierCommand,
    actor: input.actor,
  };

  if (check.found) {
    return admitOrThrow(
      composeReceipt({
        input: base,
        env,
        tier: "fetched",
        source,
        derivation: [
          { check: "manifest_lookup", ok: true, detail: `hash maps to ${fileName}` },
          { check: "source_sha256", ok: true, detail: `matches ${actual}` },
          extractStep,
          quoteStep,
        ],
        verdict: {
          kind: "verified",
          code: "QUOTE_ON_CITED_PAGE",
          detail: `the span occurs on page ${input.claim.page} of ${fileName}`,
        },
      }),
    );
  }

  return admitOrThrow(
    composeReceipt({
      input: base,
      env,
      tier: "unverified",
      source,
      derivation: [
        { check: "manifest_lookup", ok: true, detail: `hash maps to ${fileName}` },
        { check: "source_sha256", ok: true, detail: `matches ${actual}` },
        extractStep,
        quoteStep,
      ],
      verdict: {
        kind: "falsified",
        code: "QUOTE_NOT_ON_CITED_PAGE",
        detail: `the span does not occur on page ${input.claim.page} of the file the claim names`,
      },
    }),
  );
}
