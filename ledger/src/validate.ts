/**
 * The admission gate.
 *
 * `admit` is the only way to construct a `ClaimRecord`. It takes untrusted
 * input (`unknown`), validates every field, enforces the cross-field rules,
 * and returns either the record or a sorted list of violations. It never
 * throws on bad input and never partially accepts.
 *
 * The gate is deliberately deny-by-default: an unknown key is a rejection,
 * not something to ignore. Silent tolerance of extra fields is how a record
 * grows a `name` field that nobody audited.
 */

import {
  ADJUDICATED_NATURES,
  MAX_QUOTE_CHARS,
  MIN_CORROBORATORS,
  NATURES,
  sortViolations,
} from "./types.js";
import type {
  AdmitResult,
  ClaimRecord,
  EvidenceTier,
  Nature,
  Violation,
  ViolationCode,
} from "./types.js";

const ALLOWED_KEYS = new Set([
  "claimId",
  "docket",
  "documentNumber",
  "page",
  "paragraph",
  "quote",
  "sourceSha256",
  "tier",
  "nature",
]);

const TIER_KEYS: Record<string, ReadonlySet<string>> = {
  fetched: new Set(["kind", "sha256"]),
  corroborated: new Set(["kind", "sources"]),
  located_blocked: new Set(["kind", "locator"]),
  retired: new Set(["kind", "reason"]),
  unverified: new Set(["kind"]),
};

const SHA256_HEX = /^[0-9a-f]{64}$/;
const CLAIM_ID = /^[A-Z0-9][A-Z0-9-]{2,63}$/;
const DOCKET = /^[0-9]:[0-9]{2}-cv-[0-9]{5}$/;

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

class Rejections {
  readonly items: Violation[] = [];

  add(code: ViolationCode, path: string, message: string): void {
    this.items.push({ code, path, message });
  }

  get failed(): boolean {
    return this.items.length > 0;
  }
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isPositiveInt(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 1;
}

function isNature(value: unknown): value is Nature {
  return typeof value === "string" && (NATURES as readonly string[]).includes(value);
}

function checkUnknownKeys(
  value: Record<string, unknown>,
  allowed: ReadonlySet<string>,
  prefix: string,
  out: Rejections,
): void {
  for (const key of Object.keys(value).sort()) {
    if (!allowed.has(key)) {
      out.add(
        "unknown_field",
        prefix === "" ? key : `${prefix}.${key}`,
        `field "${key}" is not part of the claim schema`,
      );
    }
  }
}

function admitTier(
  raw: unknown,
  sourceSha256: string | undefined,
  out: Rejections,
): EvidenceTier | undefined {
  if (!isPlainObject(raw)) {
    out.add("wrong_type", "tier", "tier must be an object");
    return undefined;
  }
  const kind = raw["kind"];
  if (typeof kind !== "string" || !(kind in TIER_KEYS)) {
    out.add("unknown_tier", "tier.kind", "tier.kind must be one of the five known kinds");
    return undefined;
  }
  checkUnknownKeys(raw, TIER_KEYS[kind] ?? new Set(), "tier", out);

  switch (kind) {
    case "fetched": {
      const sha = raw["sha256"];
      if (!isNonEmptyString(sha)) {
        out.add("missing_field", "tier.sha256", "fetched tier requires a sha256");
        return undefined;
      }
      if (!SHA256_HEX.test(sha)) {
        out.add("bad_sha256", "tier.sha256", "sha256 must be 64 lowercase hex characters");
        return undefined;
      }
      if (sourceSha256 !== undefined && sourceSha256 !== sha) {
        out.add(
          "bad_sha256",
          "tier.sha256",
          "tier.sha256 must equal sourceSha256; a claim binds to one source",
        );
        return undefined;
      }
      return { kind: "fetched", sha256: sha };
    }
    case "corroborated": {
      const sources = raw["sources"];
      if (!Array.isArray(sources)) {
        out.add("wrong_type", "tier.sources", "corroborated tier requires a sources array");
        return undefined;
      }
      const clean: string[] = [];
      sources.forEach((entry: unknown, index: number) => {
        if (!isNonEmptyString(entry)) {
          out.add(
            "empty_value",
            `tier.sources[${index}]`,
            "every corroborating source must be a non-empty string",
          );
          return;
        }
        clean.push(entry);
      });
      if (clean.length < MIN_CORROBORATORS) {
        out.add(
          "too_few_corroborators",
          "tier.sources",
          `corroborated tier requires at least ${MIN_CORROBORATORS} sources; a single source is a lead, not a premise`,
        );
        return undefined;
      }
      const [first, second, ...rest] = clean;
      if (first === undefined || second === undefined) {
        out.add("too_few_corroborators", "tier.sources", "sources narrowed unexpectedly");
        return undefined;
      }
      return { kind: "corroborated", sources: [first, second, ...rest] };
    }
    case "located_blocked": {
      const locator = raw["locator"];
      if (!isNonEmptyString(locator)) {
        out.add("missing_field", "tier.locator", "located_blocked tier requires a locator");
        return undefined;
      }
      return { kind: "located_blocked", locator };
    }
    case "retired": {
      const reason = raw["reason"];
      if (!isNonEmptyString(reason)) {
        out.add("missing_field", "tier.reason", "retired tier requires a reason");
        return undefined;
      }
      return { kind: "retired", reason };
    }
    case "unverified":
      return { kind: "unverified" };
    default:
      return undefined;
  }
}

/**
 * Validate an untrusted value as a claim record.
 *
 * @param raw       untrusted input, typically parsed JSON
 * @param manifest  optional set of permitted source hashes; when supplied, a
 *                  record whose source hash is absent is rejected. Pass the
 *                  parsed `FLEITES_MANIFEST.sha256` so a claim cannot cite a
 *                  document the published manifest does not commit to.
 */
export function admit(raw: unknown, manifest?: ReadonlySet<string>): AdmitResult {
  const out = new Rejections();

  if (!isPlainObject(raw)) {
    return {
      ok: false,
      violations: [{ code: "not_an_object", path: "", message: "record must be an object" }],
    };
  }

  checkUnknownKeys(raw, ALLOWED_KEYS, "", out);

  const claimId = raw["claimId"];
  if (!isNonEmptyString(claimId)) {
    out.add("missing_field", "claimId", "claimId is required");
  } else if (!CLAIM_ID.test(claimId)) {
    out.add(
      "bad_claim_id",
      "claimId",
      "claimId must be 3-64 characters of A-Z, 0-9 and dash, starting alphanumeric",
    );
  }

  const docket = raw["docket"];
  if (!isNonEmptyString(docket)) {
    out.add("missing_field", "docket", "docket is required");
  } else if (!DOCKET.test(docket)) {
    out.add("bad_docket", "docket", 'docket must look like "2:21-cv-04920"');
  }

  const documentNumber = raw["documentNumber"];
  if (documentNumber === undefined) {
    out.add("missing_field", "documentNumber", "documentNumber is required");
  } else if (typeof documentNumber !== "number") {
    out.add("wrong_type", "documentNumber", "documentNumber must be a number");
  } else if (!isPositiveInt(documentNumber)) {
    out.add("bad_document_number", "documentNumber", "documentNumber must be an integer >= 1");
  }

  const page = raw["page"];
  if (page === undefined) {
    out.add("missing_field", "page", "page is required; an uncited quote is not evidence");
  } else if (typeof page !== "number") {
    out.add("wrong_type", "page", "page must be a number");
  } else if (!isPositiveInt(page)) {
    out.add("bad_page", "page", "page must be an integer >= 1");
  }

  const paragraph = raw["paragraph"];
  if (paragraph !== undefined) {
    if (typeof paragraph !== "number") {
      out.add("wrong_type", "paragraph", "paragraph must be a number when present");
    } else if (!isPositiveInt(paragraph)) {
      out.add("bad_paragraph", "paragraph", "paragraph must be an integer >= 1");
    }
  }

  const quote = raw["quote"];
  if (!isNonEmptyString(quote)) {
    out.add("missing_field", "quote", "quote is required; a claim without words is a summary");
  } else if (quote.length > MAX_QUOTE_CHARS) {
    out.add(
      "quote_too_long",
      "quote",
      `quote must be at most ${MAX_QUOTE_CHARS} characters; longer spans belong in L0 custody, not the ledger`,
    );
  }

  const sourceSha256 = raw["sourceSha256"];
  let validSourceSha: string | undefined;
  if (!isNonEmptyString(sourceSha256)) {
    out.add("missing_field", "sourceSha256", "sourceSha256 is required");
  } else if (!SHA256_HEX.test(sourceSha256)) {
    out.add("bad_sha256", "sourceSha256", "sourceSha256 must be 64 lowercase hex characters");
  } else {
    validSourceSha = sourceSha256;
    if (manifest !== undefined && !manifest.has(sourceSha256)) {
      out.add(
        "hash_not_in_manifest",
        "sourceSha256",
        "sourceSha256 is not committed to by the published manifest",
      );
    }
  }

  const tier = admitTier(raw["tier"], validSourceSha, out);

  const natureRaw = raw["nature"];
  let nature: Nature | undefined;
  if (natureRaw === undefined) {
    out.add(
      "missing_field",
      "nature",
      "nature is required; an allegation must not be able to pass as a finding",
    );
  } else if (!isNature(natureRaw)) {
    out.add("unknown_nature", "nature", "nature must be one of the five known kinds");
  } else {
    nature = natureRaw;
  }

  // Cross-field rule: an adjudicated outcome must rest on a document we have.
  if (nature !== undefined && tier !== undefined) {
    if (ADJUDICATED_NATURES.includes(nature) && tier.kind !== "fetched") {
      out.add(
        "adjudicated_requires_fetched",
        "nature",
        `nature "${nature}" asserts an adjudicated outcome and requires a fetched primary source, not "${tier.kind}"`,
      );
    }
  }

  if (out.failed) {
    return { ok: false, violations: sortViolations(out.items) };
  }

  // Narrowing: every field was validated above, so these casts are sound.
  const record: ClaimRecord = {
    claimId: claimId as string,
    docket: docket as string,
    documentNumber: documentNumber as number,
    page: page as number,
    ...(paragraph === undefined ? {} : { paragraph: paragraph as number }),
    quote: quote as string,
    sourceSha256: sourceSha256 as string,
    tier: tier as EvidenceTier,
    nature: nature as Nature,
  };
  return { ok: true, record };
}
