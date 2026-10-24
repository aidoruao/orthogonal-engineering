/**
 * The autonomous mode.
 *
 * `audit` checks a claim against a source you name. `investigate` finds the
 * source itself: it walks a corpus, locates the file containing the span,
 * hashes it, and issues the receipt. That is the burden inverted — you supply
 * the claim, not the evidence trail.
 *
 * It refuses to guess. Two files containing the same span, with no hash to
 * disambiguate them, is `AMBIGUOUS_SOURCE`, not a coin flip.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

import { audit, composeReceipt, admitOrThrow } from "./audit.js";
import { sha256Hex } from "./canonical.js";
import {
  MAX_QUOTE_CHARS,
  MAX_SOURCE_BYTES,
  type Bearing,
  type Checkability,
  type DerivationStep,
  type Environment,
  type Receipt,
} from "./types.js";

/** Directories that are never evidence. */
const SKIP_DIRECTORIES: readonly string[] = [
  ".git",
  "node_modules",
  "dist",
  "__pycache__",
  ".codewhale",
  ".venv",
  "venv",
  ".cache",
];

export type InvestigateInput = {
  readonly claimId: string;
  readonly claim: string;
  readonly bearing: Bearing;
  readonly checkability: Checkability;
  readonly missingMeasurement: string | null;
  readonly quote: string;
  readonly root: string;
  readonly extensions: readonly string[];
  readonly maxFiles: number;
  readonly expectedSha256: string | null;
  readonly falsifierCommand: string;
  readonly actor: string;
};

export type Investigation = {
  readonly receipt: Receipt;
  readonly scanned: number;
  readonly skipped: number;
  readonly matches: readonly string[];
  readonly truncated: boolean;
};

type WalkResult = {
  readonly files: readonly string[];
  readonly skipped: number;
  readonly truncated: boolean;
};

function extensionOf(name: string): string {
  const index = name.lastIndexOf(".");
  return index <= 0 ? "" : name.slice(index).toLowerCase();
}

function byName(
  left: { readonly name: string },
  right: { readonly name: string },
): number {
  if (left.name === right.name) return 0;
  return left.name < right.name ? -1 : 1;
}

/**
 * Deterministic traversal: entries sorted by name, files before directories,
 * skipped directories counted rather than silently ignored.
 */
function walk(root: string, extensions: readonly string[], maxFiles: number): WalkResult {
  const files: string[] = [];
  let skipped = 0;
  let truncated = false;

  const visit = (dir: string): boolean => {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      // Unreadable directory: counted, never silently treated as empty.
      skipped += 1;
      return true;
    }
    entries.sort(byName);

    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const full = join(dir, entry.name);
      if (!extensions.includes(extensionOf(entry.name))) {
        skipped += 1;
        continue;
      }
      let size = 0;
      try {
        size = statSync(full).size;
      } catch {
        skipped += 1;
        continue;
      }
      if (size > MAX_SOURCE_BYTES) {
        skipped += 1;
        continue;
      }
      files.push(full);
      if (files.length >= maxFiles) {
        truncated = true;
        return false;
      }
    }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (SKIP_DIRECTORIES.includes(entry.name)) {
        skipped += 1;
        continue;
      }
      if (!visit(join(dir, entry.name))) return false;
    }
    return true;
  };

  visit(root);
  return { files, skipped, truncated };
}

export function investigate(input: InvestigateInput, env: Environment): Investigation {
  const base = {
    claimId: input.claimId,
    claim: input.claim,
    bearing: input.bearing,
    checkability: input.checkability,
    missingMeasurement: input.missingMeasurement,
    quote: input.quote,
    expectedSha256: input.expectedSha256,
    falsifierCommand: input.falsifierCommand,
    actor: input.actor,
  };

  // An empty span matches every file; a span longer than the limit is not a
  // quotation. Both are rejected before the corpus is touched.
  const quoteIsEmpty = input.quote.trim() === "";
  const quoteIsTooLong = input.quote.length > MAX_QUOTE_CHARS;
  if (quoteIsEmpty || quoteIsTooLong) {
    const receipt = composeReceipt({
      input: { ...base, sourcePath: "", displayPath: "<corpus>" },
      env,
      tier: "unverified",
      source: null,
      derivation: [
        {
          check: "quote_present",
          ok: false,
          detail: quoteIsEmpty
            ? "the supplied span is empty"
            : `${input.quote.length} characters exceeds the ${MAX_QUOTE_CHARS} limit`,
        },
        {
          check: "corpus_scan",
          ok: false,
          detail: "not run: the span was rejected before the corpus walk",
        },
      ],
      verdict: {
        kind: "falsified",
        code: quoteIsEmpty ? "QUOTE_EMPTY" : "QUOTE_TOO_LONG",
        detail: quoteIsEmpty
          ? "an empty span would match every file, so nothing was searched"
          : "a span this long is a document, not a quotation",
      },
    });
    return {
      receipt: admitOrThrow(receipt),
      scanned: 0,
      skipped: 0,
      matches: [],
      truncated: false,
    };
  }

  const walked = walk(input.root, input.extensions, input.maxFiles);
  const matches: string[] = [];
  let scanned = 0;
  let skipped = walked.skipped;

  for (const file of walked.files) {
    let text: string;
    try {
      text = readFileSync(file, "utf8");
    } catch {
      skipped += 1;
      continue;
    }
    scanned += 1;
    if (text.includes("\u0000")) {
      skipped += 1;
      continue;
    }
    if (text.includes(input.quote)) {
      matches.push(file);
      if (matches.length >= 8) break;
    }
  }

  const rootLabel = relative(process.cwd(), input.root) || ".";
  const scannedDetail = `${scanned} files scanned, ${skipped} skipped, truncated=${String(
    walked.truncated,
  )}, root=${rootLabel}`;

  const scanStep: DerivationStep = {
    check: "corpus_scan",
    ok: matches.length > 0,
    detail:
      matches.length === 0
        ? scannedDetail
        : `${scannedDetail}; matched ${matches
            .map((file) => relative(input.root, file))
            .join(", ")}`,
  };


  if (matches.length === 0) {
    const receipt = composeReceipt({
      input: { ...base, sourcePath: "", displayPath: "<corpus>" },
      env,
      tier: "unverified",
      source: null,
      derivation: [
        scanStep,
        {
          check: "span_exact",
          ok: false,
          detail: "the span does not occur in any scanned file",
        },
      ],
      verdict: {
        kind: "falsified",
        code: "SPAN_NOT_FOUND_IN_CORPUS",
        detail: `the span does not occur in the ${scanned} files scanned under the corpus root`,
      },
    });
    return {
      receipt: admitOrThrow(receipt),
      scanned,
      skipped,
      matches: [],
      truncated: walked.truncated,
    };
  }

  let chosen: string | undefined = matches.length === 1 ? matches[0] : undefined;
  let hashReadFailures = 0;

  if (chosen === undefined && input.expectedSha256 !== null) {
    const hashMatches: string[] = [];
    for (const file of matches) {
      try {
        if (sha256Hex(readFileSync(file)) === input.expectedSha256) {
          hashMatches.push(file);
        }
      } catch {
        // A matched file that cannot be re-read cannot disambiguate by hash.
        // Counted, and disclosed in the ambiguity step below.
        hashReadFailures += 1;
      }
    }
    if (hashMatches.length === 1) chosen = hashMatches[0];
  }

  if (chosen === undefined) {
    const receipt = composeReceipt({
      input: { ...base, sourcePath: "", displayPath: "<corpus>" },
      env,
      tier: "unverified",
      source: null,
      derivation: [
        scanStep,
        {
          check: "source_unambiguous",
          ok: false,
          detail: `${matches.length} files contain the span and none could be selected by hash${
            hashReadFailures === 0
              ? ""
              : `; ${hashReadFailures} matched files could not be re-read`
          }`,
        },
      ],
      verdict: {
        kind: "falsified",
        code: "AMBIGUOUS_SOURCE",
        detail: `the span occurs in ${matches.length} files; refusing to guess which one the claim means`,
      },
    });
    return {
      receipt: admitOrThrow(receipt),
      scanned,
      skipped,
      matches: matches.map((file) => relative(input.root, file)),
      truncated: walked.truncated,
    };
  }

  const audited = audit(
    { ...base, sourcePath: chosen, displayPath: relative(input.root, chosen) },
    env,
  );
  const withScan: Receipt = {
    ...audited,
    derivation: [scanStep, ...audited.derivation],
  };
  return {
    receipt: admitOrThrow(withScan),
    scanned,
    skipped,
    matches: matches.map((file) => relative(input.root, file)),
    truncated: walked.truncated,
  };
}
