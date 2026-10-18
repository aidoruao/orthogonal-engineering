/**
 * Claim draft generator — local only.
 *
 * Takes an anchor phrase and a document number, finds the page where the
 * phrase actually appears, and extracts a **verbatim** span around it. The
 * span is copied from the extracted text, never retyped, so it cannot drift
 * from the source.
 *
 * This is the opposite of the older practice of writing a quote from memory
 * and hoping it matches. A paraphrase cannot survive this step: if the words
 * are not in the document, no candidate is produced.
 *
 * Drafts are written to a local, git-ignored directory. Nothing here
 * publishes anything.
 *
 * Usage:
 *   node dist/src/draft.js --spec drafts/spec.json --out drafts/candidates.jsonl
 */

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

import { extractPdf, normalizeForComparison } from "./extract.js";
import { selectSpan } from "./span.js";
import { sourceNameCandidates } from "./workbench.js";
import type { Nature } from "./types.js";

export interface DraftSpec {
  /** Stable claim identifier. */
  readonly claimId: string;
  /** Docket entry number. */
  readonly documentNumber: number;
  /** A distinctive phrase that must appear in the source. */
  readonly anchor: string;
  /** What kind of statement the span is. */
  readonly nature: Nature;
  /** Characters of context to include on each side of the anchor. */
  readonly context?: number;
  /** Exact phrase the quote must begin at. */
  readonly startAnchor?: string;
  /** Exact phrase the quote must end after. */
  readonly endAnchor?: string;
  /** Optional note for the reviewer; never published. */
  readonly note?: string;
}

export interface DraftCandidate {
  readonly claimId: string;
  readonly docket: string;
  readonly documentNumber: number;
  readonly page: number;
  readonly quote: string;
  readonly sourceSha256: string;
  readonly tier: { readonly kind: "fetched"; readonly sha256: string };
  readonly nature: Nature;
  /** Local review aids — stripped before publication. */
  readonly sourceName: string;
  readonly note?: string;
}

export interface DraftResult {
  readonly candidate?: DraftCandidate;
  readonly code?:
    | "anchor_not_found"
    | "source_missing"
    | "quote_too_short"
    | "quote_too_long";
  readonly detail?: string;
}

const DOCKET = "2:21-cv-04920";
const MIN_QUOTE = 40;
const MAX_QUOTE = 900;

/**
 * Produce one candidate, or explain why the anchor could not be honoured.
 *
 * Determinism: the same spec against the same bytes yields the same quote.
 */
export async function draftOne(
  spec: DraftSpec,
  sourcesDir: string,
): Promise<DraftResult> {
  // Validate the spec before touching the filesystem: a malformed spec is a
  // spec error, and reporting "source missing" for it would misdiagnose it.
  const needle = normalizeForComparison(spec.anchor);
  if (needle === "") {
    return { code: "anchor_not_found", detail: "anchor is empty after normalization" };
  }

  const sourceName = sourceNameCandidates(spec.documentNumber).find((name) =>
    existsSync(join(sourcesDir, name)),
  );
  if (sourceName === undefined) {
    return {
      code: "source_missing",
      detail: `no local source for document ${spec.documentNumber}`,
    };
  }
  const sourcePath = join(sourcesDir, sourceName);
  const sha256 = createHash("sha256").update(readFileSync(sourcePath)).digest("hex");

  const doc = await extractPdf(sourcePath);
  for (const page of doc.pages) {
    const text = normalizeForComparison(page.text);
    if (!text.includes(needle)) continue;

    const selected = selectSpan(text, needle, {
      margin: spec.context ?? 240,
      maxChars: MAX_QUOTE,
      ...(spec.startAnchor === undefined ? {} : { startAnchor: normalizeForComparison(spec.startAnchor) }),
      ...(spec.endAnchor === undefined ? {} : { endAnchor: normalizeForComparison(spec.endAnchor) }),
    });
    if (selected === undefined) continue;
    const quote = selected.span;

    if (quote.length < MIN_QUOTE) {
      return {
        code: "quote_too_short",
        detail: `span is ${quote.length} chars; need ${MIN_QUOTE}`,
      };
    }

    return {
      candidate: {
        claimId: spec.claimId,
        docket: DOCKET,
        documentNumber: spec.documentNumber,
        page: page.page,
        quote,
        sourceSha256: sha256,
        tier: { kind: "fetched", sha256 },
        nature: spec.nature,
        sourceName,
        ...(spec.note === undefined ? {} : { note: spec.note }),
      },
    };
  }

  return {
    code: "anchor_not_found",
    detail: `"${spec.anchor}" does not appear in document ${spec.documentNumber}`,
  };
}

/** Run a batch deterministically and preserve input order in the report. */
export async function draftBatch(
  specs: readonly DraftSpec[],
  sourcesDir: string,
): Promise<{ candidates: DraftCandidate[]; failures: { claimId: string; code: string; detail: string }[] }> {
  const candidates: DraftCandidate[] = [];
  const failures: { claimId: string; code: string; detail: string }[] = [];
  for (const spec of specs) {
    const result = await draftOne(spec, sourcesDir);
    if (result.candidate !== undefined) {
      candidates.push(result.candidate);
    } else {
      failures.push({
        claimId: spec.claimId,
        code: result.code ?? "unknown",
        detail: result.detail ?? "",
      });
    }
  }
  return { candidates, failures };
}

/** Strip local-only fields before anything could be published. */
export function toPublic(candidate: DraftCandidate): Record<string, unknown> {
  return {
    claimId: candidate.claimId,
    docket: candidate.docket,
    documentNumber: candidate.documentNumber,
    page: candidate.page,
    quote: candidate.quote,
    sourceSha256: candidate.sourceSha256,
    tier: candidate.tier,
    nature: candidate.nature,
  };
}

function parseArgs(argv: readonly string[]): { spec: string; out: string; sources: string } {
  let spec: string | undefined;
  let out: string | undefined;
  let sources = process.env["OE_CORPUS_DIR"] ?? "evidence/fleites";
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--spec") {
      spec = argv[i + 1];
      i += 1;
    } else if (arg === "--out") {
      out = argv[i + 1];
      i += 1;
    } else if (arg === "--sources") {
      sources = argv[i + 1] ?? sources;
      i += 1;
    }
  }
  if (spec === undefined || out === undefined) {
    throw new Error("usage: draft --spec <spec.json> --out <candidates.jsonl> [--sources DIR]");
  }
  return { spec, out, sources };
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("draft.js");

if (invokedDirectly) {
  try {
    const args = parseArgs(process.argv.slice(2));
    const specs = JSON.parse(readFileSync(args.spec, "utf8")) as DraftSpec[];
    const { candidates, failures } = await draftBatch(specs, args.sources);

    mkdirSync(dirname(args.out), { recursive: true });
    writeFileSync(
      args.out,
      candidates.map((candidate) => JSON.stringify(candidate)).join("\n") +
        (candidates.length === 0 ? "" : "\n"),
    );

    console.log(`drafted: ${candidates.length}/${specs.length}`);
    for (const candidate of candidates) {
      console.log(
        `  ${candidate.claimId}: doc ${candidate.documentNumber} p${candidate.page}, ${candidate.quote.length} chars`,
      );
    }
    for (const failure of failures) {
      console.log(`  FAILED ${failure.claimId}: ${failure.code} — ${failure.detail}`);
    }
    process.exitCode = failures.length === 0 ? 0 : 1;
  } catch (error) {
    console.error(`fatal: ${String(error)}`);
    process.exitCode = 2;
  }
}
