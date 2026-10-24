/**
 * The audit engine — the part that carries the burden.
 *
 * Given a claim and a span, it reads the source bytes, hashes them, and looks
 * for the span. It does not ask the reader to do any of that. Its output is a
 * receipt, and the receipt is admitted only if it passes the same contract
 * that an outside reader would apply.
 *
 * Three outcomes matter, and they are kept distinct on purpose:
 *
 *   SPAN_EXACT            the span occurs contiguously in the named file
 *   SPAN_GUTTER_ARTIFACT  the span is contiguous only after a line-number
 *                         gutter is removed — disclosed, never stripped
 *   SPAN_NONCONTIGUOUS    each line occurs, but not as one span
 *
 * A near-match is a falsification of the verbatim claim, not a pass with a
 * warning. That distinction is the difference between this and a linter.
 */

import { readFileSync } from "node:fs";

import { sha256Hex } from "./canonical.js";
import {
  MAX_QUOTE_CHARS,
  type Bearing,
  type Checkability,
  type DerivationStep,
  type Environment,
  type Falsifier,
  type Receipt,
  type SourceRef,
  type Tier,
  type Verdict,
  type VerdictRecord,
} from "./types.js";
import { validateReceipt } from "./validate.js";

export type AuditInput = {
  readonly claimId: string;
  readonly claim: string;
  readonly bearing: Bearing;
  readonly checkability: Checkability;
  readonly missingMeasurement: string | null;
  readonly quote: string;
  /** Path on disk. */
  readonly sourcePath: string;
  /** Path as the receipt should name it (relative to a corpus root). */
  readonly displayPath: string;
  /** When set, the source must hash to this or the check fails. */
  readonly expectedSha256: string | null;
  readonly falsifierCommand: string;
  readonly actor: string;
};

export type SpanFinding =
  | { readonly kind: "exact"; readonly lineStart: number; readonly lineEnd: number }
  | {
      readonly kind: "gutter";
      readonly lineStart: number;
      readonly lineEnd: number;
      readonly removedGutters: number;
    }
  | {
      readonly kind: "noncontiguous";
      readonly linesFound: number;
      readonly linesTotal: number;
    }
  | { readonly kind: "absent" };

/** A pleading line-number gutter: leading digits, then whitespace. */
const GUTTER_PATTERN = /^[ \t]*\d{1,5}[ \t]+/;

function countNewlines(text: string): number {
  let count = 0;
  for (const character of text) {
    if (character === "\n") count += 1;
  }
  return count;
}

function lineRangeAt(text: string, index: number, span: string): {
  readonly lineStart: number;
  readonly lineEnd: number;
} {
  const lineStart = countNewlines(text.slice(0, index)) + 1;
  const lineEnd = lineStart + countNewlines(span);
  return { lineStart, lineEnd };
}

/**
 * Remove a leading line-number gutter from every line.
 *
 * This is used only to *diagnose* a failed exact match. The receipt records
 * that the gutter exists and how many lines carried one; it never presents the
 * normalized text as if it were the source.
 */
export function stripLineGutters(text: string): {
  readonly normalized: string;
  readonly removed: number;
} {
  const lines = text.split("\n");
  let removed = 0;
  const normalizedLines = lines.map((line) => {
    const match = GUTTER_PATTERN.exec(line);
    if (match === null) return line;
    if (line.slice(match[0].length).trim() === "") return line;
    removed += 1;
    return line.slice(match[0].length);
  });
  return { normalized: normalizedLines.join("\n"), removed };
}

function nonEmptyLines(text: string): readonly string[] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line !== "");
}

/** How many of the quote's lines occur, in order, somewhere in the source. */
function linewisePresence(
  sourceText: string,
  quoteText: string,
): { readonly found: number; readonly total: number } {
  const sourceLines = sourceText.split("\n").map((line) => line.trim());
  const quoteLines = nonEmptyLines(quoteText);
  let cursor = 0;
  let found = 0;
  for (const quoteLine of quoteLines) {
    let matched = false;
    while (cursor < sourceLines.length) {
      const sourceLine = sourceLines[cursor];
      cursor += 1;
      if (sourceLine !== undefined && sourceLine.includes(quoteLine)) {
        matched = true;
        break;
      }
    }
    if (matched) found += 1;
    else break;
  }
  return { found, total: quoteLines.length };
}

export function locateSpan(text: string, quote: string): SpanFinding {
  const exactIndex = text.indexOf(quote);
  if (exactIndex >= 0) {
    const range = lineRangeAt(text, exactIndex, quote);
    return { kind: "exact", lineStart: range.lineStart, lineEnd: range.lineEnd };
  }

  const stripped = stripLineGutters(text);
  if (stripped.removed > 0) {
    const gutterIndex = stripped.normalized.indexOf(quote);
    if (gutterIndex >= 0) {
      const range = lineRangeAt(stripped.normalized, gutterIndex, quote);
      return {
        kind: "gutter",
        lineStart: range.lineStart,
        lineEnd: range.lineEnd,
        removedGutters: stripped.removed,
      };
    }
  }

  const presence = linewisePresence(text, quote);
  if (presence.total > 0 && presence.found === presence.total) {
    return {
      kind: "noncontiguous",
      linesFound: presence.found,
      linesTotal: presence.total,
    };
  }
  if (presence.found > 0) {
    return {
      kind: "noncontiguous",
      linesFound: presence.found,
      linesTotal: presence.total,
    };
  }
  return { kind: "absent" };
}

function falsifierFor(
  input: AuditInput,
  source: SourceRef | null,
  code: string,
): Falsifier {
  const command = input.falsifierCommand;
  const hashNote =
    source === null ? "the named source" : `the file whose SHA-256 is ${source.sha256}`;
  const refutes: Record<string, string> = {
    SPAN_EXACT: `the span does not occur contiguously in ${hashNote}`,
    SPAN_GUTTER_ARTIFACT: `the span occurs contiguously in ${hashNote} without removing a line-number gutter`,
    SPAN_NONCONTIGUOUS: `the span occurs as one contiguous run in ${hashNote}`,
    SPAN_NOT_FOUND: `the span occurs in ${hashNote} at all`,
    SOURCE_HASH_MISMATCH: `the file at ${input.displayPath} hashes to the value the claim names`,
    SOURCE_MISSING: `the file at ${input.displayPath} exists and is readable`,
    QUOTE_EMPTY: `a non-empty span was supplied`,
    QUOTE_TOO_LONG: `the span is ${MAX_QUOTE_CHARS} characters or fewer`,
  };
  return {
    command,
    refutes: refutes[code] ?? `the check ${code} is reproducible`,
  };
}

export function composeReceipt(args: {
  readonly input: AuditInput;
  readonly env: Environment;
  readonly tier: Tier;
  readonly source: SourceRef | null;
  readonly derivation: readonly DerivationStep[];
  readonly verdict: VerdictRecord;
}): Receipt {
  const receipt: Receipt = {
    schema: "burden.receipt/1",
    claimId: args.input.claimId,
    claim: args.input.claim,
    bearing: args.input.bearing,
    checkability: args.input.checkability,
    missingMeasurement: args.input.missingMeasurement,
    tier: args.tier,
    source: args.source,
    derivation: args.derivation,
    falsifier: falsifierFor(args.input, args.source, args.verdict.code),
    owner: {
      actor: args.input.actor,
      tool: "burden/0.1.0",
      environment: args.env,
    },
    verdict: args.verdict,
  };
  return receipt;
}

/**
 * The engine cannot emit a receipt its own gate would reject. If it ever does,
 * that is a bug in this file, and it fails loudly rather than writing a
 * plausible-looking record.
 */
export function admitOrThrow(receipt: Receipt): Receipt {
  const admitted = validateReceipt(receipt);
  if (!admitted.ok) {
    const lines = admitted.violations
      .map((violation) => `${violation.code} at ${violation.path || "<root>"}`)
      .join("; ");
    throw new Error(`burden: engine produced an inadmissible receipt: ${lines}`);
  }
  return admitted.receipt;
}

function verdict(kind: Verdict, code: string, detail: string): VerdictRecord {
  return { kind, code, detail };
}

/** Run the check. Always returns an admissible receipt, including on failure. */
export function audit(input: AuditInput, env: Environment): Receipt {
  const quote = input.quote;

  if (quote.trim() === "") {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source: null,
        derivation: [
          { check: "quote_present", ok: false, detail: "the supplied span is empty" },
        ],
        verdict: verdict("falsified", "QUOTE_EMPTY", "nothing was checked: the span is empty"),
      }),
    );
  }

  if (quote.length > MAX_QUOTE_CHARS) {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source: null,
        derivation: [
          {
            check: "quote_length",
            ok: false,
            detail: `${quote.length} characters exceeds the ${MAX_QUOTE_CHARS} limit`,
          },
        ],
        verdict: verdict(
          "falsified",
          "QUOTE_TOO_LONG",
          "a span this long is a document, not a quotation",
        ),
      }),
    );
  }

  let bytes: Uint8Array;
  try {
    bytes = readFileSync(input.sourcePath);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source: null,
        derivation: [{ check: "source_read", ok: false, detail: message }],
        verdict: verdict(
          "falsified",
          "SOURCE_MISSING",
          `the source could not be read, so the span was not checked: ${message}`,
        ),
      }),
    );
  }

  const text = Buffer.from(bytes).toString("utf8");
  const sha256 = sha256Hex(bytes);
  const source: SourceRef = {
    path: input.displayPath,
    sha256,
    bytes: bytes.byteLength,
  };

  const hashStep: DerivationStep = {
    check: "source_sha256",
    ok: input.expectedSha256 === null || input.expectedSha256 === sha256,
    detail:
      input.expectedSha256 === null
        ? `computed ${sha256}; no expected hash was supplied`
        : `computed ${sha256}; expected ${input.expectedSha256}`,
  };

  if (!hashStep.ok) {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source,
        derivation: [
          {
            check: "source_read",
            ok: true,
            detail: `${bytes.byteLength} bytes read from ${input.displayPath}`,
          },
          hashStep,
        ],
        verdict: verdict(
          "falsified",
          "SOURCE_HASH_MISMATCH",
          "the file is not the one the claim names, so its span proves nothing about that claim",
        ),
      }),
    );
  }

  const span = locateSpan(text, quote);
  const readStep: DerivationStep = {
    check: "source_read",
    ok: true,
    detail: `${bytes.byteLength} bytes read from ${input.displayPath}`,
  };

  if (span.kind === "exact") {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "fetched",
        source,
        derivation: [
          readStep,
          hashStep,
          {
            check: "span_exact",
            ok: true,
            detail: `contiguous span at lines ${span.lineStart}-${span.lineEnd} of ${input.displayPath}`,
          },
        ],
        verdict: verdict(
          "verified",
          "SPAN_EXACT",
          `the span occurs contiguously at lines ${span.lineStart}-${span.lineEnd}`,
        ),
      }),
    );
  }

  if (span.kind === "gutter") {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source,
        derivation: [
          readStep,
          hashStep,
          {
            check: "span_exact",
            ok: false,
            detail: "the span does not occur contiguously in the raw source bytes",
          },
          {
            check: "gutter_diagnosis",
            ok: false,
            detail: `the span becomes contiguous only after removing a line-number gutter from ${span.removedGutters} source lines (lines ${span.lineStart}-${span.lineEnd}); the gutter is disclosed, not stripped`,
          },
        ],
        verdict: verdict(
          "falsified",
          "SPAN_GUTTER_ARTIFACT",
          "the quotation crosses a line-number gutter; as filed it is not a verbatim contiguous span",
        ),
      }),
    );
  }

  if (span.kind === "noncontiguous") {
    return admitOrThrow(
      composeReceipt({
        input,
        env,
        tier: "unverified",
        source,
        derivation: [
          readStep,
          hashStep,
          {
            check: "span_exact",
            ok: false,
            detail: "the span does not occur contiguously",
          },
          {
            check: "linewise_presence",
            ok: false,
            detail: `${span.linesFound} of ${span.linesTotal} quote lines occur, but not as one run`,
          },
        ],
        verdict: verdict(
          "falsified",
          "SPAN_NONCONTIGUOUS",
          "the lines occur separately; the quotation as a single span does not",
        ),
      }),
    );
  }

  return admitOrThrow(
    composeReceipt({
      input,
      env,
      tier: "unverified",
      source,
      derivation: [
        readStep,
        hashStep,
        {
          check: "span_exact",
          ok: false,
          detail: "the span does not occur anywhere in the source",
        },
      ],
      verdict: verdict(
        "falsified",
        "SPAN_NOT_FOUND",
        "the span does not occur in the file whose hash the receipt records",
      ),
    }),
  );
}
