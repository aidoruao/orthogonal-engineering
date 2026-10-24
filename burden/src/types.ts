/**
 * burden — the burden inverter. Core types.
 *
 * Design rule: a verdict is evidence only if it names (a) who checked it,
 * (b) what the check was, (c) what would have refuted it, and (d) how much
 * weight the claim carries. A verdict missing any of those is not a weak
 * verdict; it is not a verdict.
 *
 * These are type aliases rather than interfaces on purpose: an alias of an
 * object type is structurally assignable to a JSON object, so a receipt can be
 * canonically serialized without a single unchecked cast.
 *
 * See docs/BURDEN_INVERSION.md for the ontology this file implements.
 */

/** The receipt schema identifier. Changing the shape means changing this. */
export const SCHEMA_ID = "burden.receipt/1";

/** Maximum length of a checked span. Guards against pasting a whole document
 *  in as a "quote", which would make the span check meaningless. */
export const MAX_QUOTE_CHARS = 2000;

/** Largest file the autonomous investigator will hash and search. */
export const MAX_SOURCE_BYTES = 2 * 1024 * 1024;

/**
 * How well the claim is evidenced *after* the check.
 *
 * `fetched` means the exact source bytes were read and hashed. `corroborated`
 * means at least two independent sources were named. Neither may be worn by a
 * claim whose check failed: see `falsified_requires_unsupported_tier`.
 */
export type Tier =
  | "unverified"
  | "located_blocked"
  | "corroborated"
  | "fetched"
  | "retired";

export const TIERS: readonly Tier[] = [
  "unverified",
  "located_blocked",
  "corroborated",
  "fetched",
  "retired",
] as const;

/** Strength rank. `retired` is terminal, not strong, and shares rank 0. */
export const TIER_RANK: Readonly<Record<Tier, number>> = {
  unverified: 0,
  located_blocked: 1,
  corroborated: 2,
  fetched: 3,
  retired: 0,
};

/**
 * The upgrade relation, mirrored by `mayUpgrade` in `L1_BURDEN.lean`.
 *
 * Same tier is idempotent. `retired` is terminal in both directions and
 * `fetched` has no stronger tier, so neither can be "upgraded". Everything
 * else may only move to a tier of equal or greater rank.
 */
export function mayUpgrade(from: Tier, to: Tier): boolean {
  if (from === to) return true;
  if (from === "retired" || to === "retired" || from === "fetched") return false;
  return TIER_RANK[from] <= TIER_RANK[to];
}

/** Tiers that assert a checked, supported source. */
export const SUPPORTED_TIERS: readonly Tier[] = ["fetched", "corroborated"] as const;

/** Tiers a falsified verdict is allowed to leave behind. */
export const UNSUPPORTED_TIERS: readonly Tier[] = ["unverified", "located_blocked"] as const;

/** How much the claim carries. A load-bearing failure is critical; nothing
 *  else is. This is what stops passive neutrality from being available. */
export type Bearing = "load_bearing" | "supporting" | "illustrative";

export const BEARINGS: readonly Bearing[] = [
  "load_bearing",
  "supporting",
  "illustrative",
] as const;

/** The outcome of the check itself. */
export type Verdict = "verified" | "falsified" | "unmeasured";

export const VERDICTS: readonly Verdict[] = [
  "verified",
  "falsified",
  "unmeasured",
] as const;

/**
 * Whether the claim can be checked by a machine.
 *
 * `machine_checkable` puts the burden on the tool by definition.
 * `human_only` may leave it with the person, but only if the receipt names the
 * specific missing measurement. "Unverified" is not an answer.
 */
export type Checkability = "machine_checkable" | "human_only";

export const CHECKABILITIES: readonly Checkability[] = [
  "machine_checkable",
  "human_only",
] as const;

/** Where the burden sits. The inversion is this function's definition. */
export type Holder = "tool" | "user";

export type SourceRef = {
  /** Path as reported to the reader, relative to the corpus root. */
  readonly path: string;
  /** SHA-256 of the exact bytes read, lowercase hex. */
  readonly sha256: string;
  readonly bytes: number;
};

/** One performed check. `detail` says what actually happened, never "ok". */
export type DerivationStep = {
  readonly check: string;
  readonly ok: boolean;
  readonly detail: string;
};

/** What would refute the claim, and the command that would do it. */
export type Falsifier = {
  readonly command: string;
  readonly refutes: string;
};

export type Environment = {
  readonly node: string;
  readonly lean: string;
  readonly platform: string;
};

/** The named actor. There is no anonymous path to a receipt. */
export type Owner = {
  readonly actor: string;
  readonly tool: string;
  readonly environment: Environment;
};

export type VerdictRecord = {
  readonly kind: Verdict;
  /** Stable machine-readable code, e.g. SPAN_EXACT. Never prose. */
  readonly code: string;
  /** Human-readable detail, including the failing check when falsified. */
  readonly detail: string;
};

/**
 * The receipt. Every field is required; `source` and `missingMeasurement` are
 * explicitly `null` when absent, so absence is recorded rather than omitted.
 */
export type Receipt = {
  readonly schema: typeof SCHEMA_ID;
  readonly claimId: string;
  /** The proposition, in words. The receipt checks a span, not this sentence. */
  readonly claim: string;
  readonly bearing: Bearing;
  readonly checkability: Checkability;
  readonly missingMeasurement: string | null;
  readonly tier: Tier;
  readonly source: SourceRef | null;
  readonly derivation: readonly DerivationStep[];
  readonly falsifier: Falsifier;
  readonly owner: Owner;
  readonly verdict: VerdictRecord;
};

/** Stable rejection codes. Never freeform prose. */
export type ViolationCode =
  | "not_an_object"
  | "unknown_field"
  | "missing_field"
  | "wrong_type"
  | "empty_value"
  | "bad_schema"
  | "bad_claim_id"
  | "bad_tier"
  | "bad_bearing"
  | "bad_verdict"
  | "bad_verdict_code"
  | "bad_checkability"
  | "bad_sha256"
  | "bad_bytes"
  | "anonymous_action"
  | "human_only_requires_named_measurement"
  | "falsified_requires_unsupported_tier"
  | "unmeasured_requires_unsupported_tier"
  | "verified_requires_supported_tier"
  | "supported_requires_source"
  | "derivation_empty"
  | "derivation_step_undocumented"
  | "bad_environment";

export const VIOLATION_CODES: readonly ViolationCode[] = [
  "not_an_object",
  "unknown_field",
  "missing_field",
  "wrong_type",
  "empty_value",
  "bad_schema",
  "bad_claim_id",
  "bad_tier",
  "bad_bearing",
  "bad_verdict",
  "bad_verdict_code",
  "bad_checkability",
  "bad_sha256",
  "bad_bytes",
  "anonymous_action",
  "human_only_requires_named_measurement",
  "falsified_requires_unsupported_tier",
  "unmeasured_requires_unsupported_tier",
  "verified_requires_supported_tier",
  "supported_requires_source",
  "derivation_empty",
  "derivation_step_undocumented",
  "bad_environment",
] as const;

export type Violation = {
  readonly code: ViolationCode;
  readonly path: string;
  readonly message: string;
};

export type ValidationResult =
  | { readonly ok: true; readonly receipt: Receipt }
  | { readonly ok: false; readonly violations: readonly Violation[] };

/** Errors are values. Violations sort deterministically. */
export function sortViolations(violations: readonly Violation[]): Violation[] {
  return [...violations].sort((a, b) => {
    if (a.path !== b.path) return a.path < b.path ? -1 : 1;
    if (a.code !== b.code) return a.code < b.code ? -1 : 1;
    return a.message < b.message ? -1 : a.message > b.message ? 1 : 0;
  });
}

/** The claim identifier grammar. Documented so IDs cannot drift. */
export const CLAIM_ID_PATTERN = /^[A-Z0-9][A-Z0-9._-]{2,63}$/;

/** Lowercase hex SHA-256. */
export const SHA256_PATTERN = /^[0-9a-f]{64}$/;
