/**
 * L1 claim ledger — core types.
 *
 * Design rule: a claim is evidence only if it can be checked AND can fail.
 * That means every record must commit to (a) which document, (b) where in it,
 * (c) the exact words, and (d) the hash of the source it was taken from.
 * A record missing any of those is not a weak claim; it is not a claim.
 *
 * See docs/DATA_ISOLATION_BOUNDARY.md for the layer model.
 */

/** Maximum length of a verbatim quote. Guards against pasting a whole
 *  document into the ledger, which would defeat the L0 custody boundary. */
export const MAX_QUOTE_CHARS = 2000;

/** Minimum independent sources for a corroborated tier. */
export const MIN_CORROBORATORS = 2;

/**
 * How well the claim is evidenced.
 *
 * `fetched` carries the SHA-256 of the exact source file examined, so a
 * reader can re-fetch and compare bytes.
 */
export type EvidenceTier =
  | { readonly kind: "fetched"; readonly sha256: string }
  | {
      readonly kind: "corroborated";
      readonly sources: readonly [string, string, ...string[]];
    }
  | { readonly kind: "located_blocked"; readonly locator: string }
  | { readonly kind: "retired"; readonly reason: string }
  | { readonly kind: "unverified" };

/**
 * What kind of statement the claim is.
 *
 * This field exists because a complaint asserts and a court decides. Treating
 * those as the same thing is the single easiest way to publish something
 * false while every quote is accurate. `nature` is therefore required, and
 * `finding` / `order` may only rest on a fetched primary.
 *
 * `party_filing` exists because a docket holds more than allegations and
 * orders: it holds motions, notices, and objections. A motion caption
 * establishes who filed what; it asserts nothing about the world. Calling
 * that an "allegation" would be a quiet misclassification, so it gets its own
 * category — and, like an allegation, it is not an adjudicated outcome.
 */
export type Nature =
  | "allegation"
  | "party_filing"
  | "order"
  | "finding"
  | "settlement"
  | "stated_intent";

export const NATURES: readonly Nature[] = [
  "allegation",
  "party_filing",
  "order",
  "finding",
  "settlement",
  "stated_intent",
] as const;

/** Natures that assert an adjudicated outcome, not a party's assertion. */
export const ADJUDICATED_NATURES: readonly Nature[] = ["order", "finding"] as const;

/** A claim that has passed the admission gate. Construct only via `admit`. */
export interface ClaimRecord {
  readonly claimId: string;
  /** Court docket identifier, e.g. "2:21-cv-04920". */
  readonly docket: string;
  /** Docket entry number. */
  readonly documentNumber: number;
  /** 1-based page within the document. */
  readonly page: number;
  /** Optional paragraph, when the source is numbered. */
  readonly paragraph?: number;
  /** Verbatim quoted span from the source. */
  readonly quote: string;
  /** SHA-256 (lowercase hex) of the source file the quote was taken from. */
  readonly sourceSha256: string;
  readonly tier: EvidenceTier;
  readonly nature: Nature;
}

/** Stable, machine-readable rejection codes. Never freeform prose. */
export type ViolationCode =
  | "not_an_object"
  | "unknown_field"
  | "missing_field"
  | "wrong_type"
  | "empty_value"
  | "bad_claim_id"
  | "bad_docket"
  | "bad_document_number"
  | "bad_page"
  | "bad_paragraph"
  | "bad_sha256"
  | "quote_too_long"
  | "unknown_nature"
  | "unknown_tier"
  | "too_few_corroborators"
  | "adjudicated_requires_fetched"
  | "hash_not_in_manifest";

export interface Violation {
  readonly code: ViolationCode;
  /** Dotted path into the record, e.g. "tier.sha256". */
  readonly path: string;
  readonly message: string;
}

export type AdmitResult =
  | { readonly ok: true; readonly record: ClaimRecord }
  | { readonly ok: false; readonly violations: readonly Violation[] };

/** Errors are values, never exceptions. Violations sort deterministically. */
export function sortViolations(violations: Violation[]): Violation[] {
  return [...violations].sort((a, b) => {
    if (a.path !== b.path) return a.path < b.path ? -1 : 1;
    if (a.code !== b.code) return a.code < b.code ? -1 : 1;
    return a.message < b.message ? -1 : a.message > b.message ? 1 : 0;
  });
}
