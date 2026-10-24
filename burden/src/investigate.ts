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
import { join, relative, resolve } from "node:path";

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

/** Stop collecting matches after this many. The cap is disclosed, not silent. */
const MATCH_CAP = 8;

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
  /**
   * Paths that are never evidence. The receipt ledger is the important one: it
   * contains the quotes it has already checked, so searching it for a quote
   * always finds it. A receipt that cites itself is circular evidence, and the
   * scanner refuses to consider its own notes.
   */
  readonly excludePaths: readonly string[];
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
  /** True only when absence, if reported, was established over the whole scope. */
  readonly measured: boolean;
};

type WalkResult = {
  readonly files: readonly string[];
  /** Skipped for a declared reason (extension, excluded directory). */
  readonly filtered: number;
  /**
   * Skipped for a reason that could hide the span: a directory that could not
   * be read, a file that could not be stat-ed, a file over the size limit.
   * Absence is not measurable while this is non-zero.
   */
  readonly opaque: number;
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
 * Deterministic traversal: entries sorted by name, files before directories.
 *
 * Skips are split in two, because they mean different things. A file excluded
 * by extension is outside the declared scope, so its absence is expected. A
 * directory that cannot be read is inside the scope and unexamined, so absence
 * establishes nothing. Collapsing those two into one counter is how a tool
 * reports a confident "not found" about a place it never looked.
 */
function walk(
  root: string,
  extensions: readonly string[],
  maxFiles: number,
  excludePaths: readonly string[],
): WalkResult {
  const files: string[] = [];
  let filtered = 0;
  let opaque = 0;
  let truncated = false;
  const excluded = new Set(excludePaths.map((path) => resolve(path)));

  const visit = (dir: string): boolean => {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      opaque += 1;
      return true;
    }
    entries.sort(byName);

    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const full = join(dir, entry.name);
      if (excluded.has(resolve(full))) {
        filtered += 1;
        continue;
      }
      if (!extensions.includes(extensionOf(entry.name))) {
        filtered += 1;
        continue;
      }
      let size = 0;
      try {
        size = statSync(full).size;
      } catch {
        opaque += 1;
        continue;
      }
      if (size > MAX_SOURCE_BYTES) {
        opaque += 1;
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
        filtered += 1;
        continue;
      }
      if (!visit(join(dir, entry.name))) return false;
    }
    return true;
  };

  visit(root);
  return { files, filtered, opaque, truncated };
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
      measured: false,
    };
  }

  const walked = walk(input.root, input.extensions, input.maxFiles, input.excludePaths);
  const matches: string[] = [];
  let scanned = 0;
  let opaque = walked.opaque;
  let matchCapReached = false;

  for (const file of walked.files) {
    let text: string;
    try {
      text = readFileSync(file, "utf8");
    } catch {
      opaque += 1;
      continue;
    }
    if (text.includes("\u0000")) {
      opaque += 1;
      continue;
    }
    scanned += 1;
    if (text.includes(input.quote)) {
      matches.push(file);
      if (matches.length >= MATCH_CAP) {
        matchCapReached = true;
        break;
      }
    }
  }

  const skipped = walked.filtered + opaque;
  const rootLabel = relative(process.cwd(), input.root) || ".";
  const scannedDetail = `${scanned} files scanned, ${walked.filtered} filtered, ${opaque} opaque, truncated=${String(
    walked.truncated || matchCapReached,
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
    // Absence is a measurement only if the whole scope was read. Zero files
    // scanned, an unreadable directory, an oversized file, or a walk that hit
    // its cap all mean the space was not covered — and an uncovered space
    // supports neither the claim nor its negation. Reporting that as
    // "falsified" would put a confident number behind an unexamined corpus,
    // which is the exact failure this tool inverts.
    const uncovered =
      scanned === 0
        ? "no file in the declared scope could be read"
        : walked.truncated
          ? `the walk stopped at the ${input.maxFiles}-file cap before covering the scope`
          : opaque > 0
            ? `${opaque} path(s) in scope could not be read (unreadable directory, stat failure, or file over the size limit)`
            : null;

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
          detail:
            uncovered === null
              ? "the span does not occur in any scanned file"
              : `not established: ${uncovered}`,
        },
      ],
      verdict:
        uncovered === null
          ? {
              kind: "falsified",
              code: "SPAN_NOT_FOUND_IN_CORPUS",
              detail: `the span does not occur in the ${scanned} files scanned under the corpus root`,
            }
          : {
              kind: "unmeasured",
              code: scanned === 0 ? "NO_SOURCES_SCANNED" : "SCOPE_INCOMPLETE",
              detail: `absence is not established: ${uncovered}`,
            },
    });
    return {
      receipt: admitOrThrow(receipt),
      scanned,
      skipped,
      matches: [],
      truncated: walked.truncated,
      measured: uncovered === null,
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
        kind: "unmeasured",
        code: "AMBIGUOUS_SOURCE",
        detail: `the span occurs in ${matches.length} files; refusing to guess which one the claim means, so the claim was not measured`,
      },
    });
    return {
      receipt: admitOrThrow(receipt),
      scanned,
      skipped,
      matches: matches.map((file) => relative(input.root, file)),
      truncated: walked.truncated,
      measured: false,
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
    measured: true,
  };
}
