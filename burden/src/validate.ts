/**
 * The executable ontology.
 *
 * `validateReceipt` is the only constructor of an admitted receipt. It rejects
 * illegal states loudly, with a stable code and a dotted path. `describeContract`
 * publishes the same contract as data, and the test suite requires every code
 * in it to be reachable by a concrete fixture — a check with no falsifier is a
 * comment, and that rule applies to this file too.
 */

import type { Json } from "./canonical.js";
import {
  BEARINGS,
  CHECKABILITIES,
  CLAIM_ID_PATTERN,
  SCHEMA_ID,
  SHA256_PATTERN,
  TIERS,
  VERDICTS,
  VIOLATION_CODES,
  SUPPORTED_TIERS,
  UNSUPPORTED_TIERS,
  sortViolations,
  type Bearing,
  type Checkability,
  type DerivationStep,
  type Environment,
  type Falsifier,
  type Owner,
  type Receipt,
  type SourceRef,
  type Tier,
  type ValidationResult,
  type Verdict,
  type VerdictRecord,
  type Violation,
  type ViolationCode,
} from "./types.js";

const ALLOWED_FIELDS: readonly string[] = [
  "schema",
  "claimId",
  "claim",
  "bearing",
  "checkability",
  "missingMeasurement",
  "tier",
  "source",
  "derivation",
  "falsifier",
  "owner",
  "verdict",
];

const VERDICT_CODE_PATTERN = /^[A-Z][A-Z0-9_]{2,47}$/;

function isUnknownRecord(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isUnknownArray(value: unknown): value is readonly unknown[] {
  return Array.isArray(value);
}

function checkFields(
  record: Readonly<Record<string, unknown>>,
  allowed: readonly string[],
  path: string,
  violations: Violation[],
): void {
  for (const key of Object.keys(record)) {
    if (!allowed.includes(key)) {
      violations.push({
        code: "unknown_field",
        path: path === "" ? key : `${path}.${key}`,
        message: `unknown field "${key}"`,
      });
    }
  }
}

function text(
  record: Readonly<Record<string, unknown>>,
  key: string,
  path: string,
  violations: Violation[],
): string | null {
  const value = record[key];
  if (value === undefined) {
    violations.push({
      code: "missing_field",
      path,
      message: `required field "${key}" is absent`,
    });
    return null;
  }
  if (typeof value !== "string") {
    violations.push({
      code: "wrong_type",
      path,
      message: `"${key}" must be a string, got ${typeof value}`,
    });
    return null;
  }
  if (value.trim() === "") {
    violations.push({ code: "empty_value", path, message: `"${key}" is empty` });
    return null;
  }
  return value;
}

function wholeNumber(
  record: Readonly<Record<string, unknown>>,
  key: string,
  path: string,
  violations: Violation[],
): number | null {
  const value = record[key];
  if (value === undefined) {
    violations.push({
      code: "missing_field",
      path,
      message: `required field "${key}" is absent`,
    });
    return null;
  }
  if (typeof value !== "number" || !Number.isInteger(value)) {
    violations.push({
      code: "wrong_type",
      path,
      message: `"${key}" must be an integer`,
    });
    return null;
  }
  if (value < 0) {
    violations.push({ code: "bad_bytes", path, message: `"${key}" must be >= 0` });
    return null;
  }
  return value;
}

function enumeration<T extends string>(
  record: Readonly<Record<string, unknown>>,
  key: string,
  allowed: readonly T[],
  path: string,
  code: ViolationCode,
  violations: Violation[],
): T | null {
  const value = record[key];
  if (value === undefined) {
    violations.push({
      code: "missing_field",
      path,
      message: `required field "${key}" is absent`,
    });
    return null;
  }
  if (typeof value !== "string") {
    violations.push({
      code: "wrong_type",
      path,
      message: `"${key}" must be a string`,
    });
    return null;
  }
  const found = allowed.find((candidate) => candidate === value);
  if (found === undefined) {
    violations.push({
      code,
      path,
      message: `"${key}" must be one of ${allowed.join(", ")}`,
    });
    return null;
  }
  return found;
}

function record(
  value: unknown,
  path: string,
  violations: Violation[],
): Readonly<Record<string, unknown>> | null {
  if (!isUnknownRecord(value)) {
    violations.push({
      code: "wrong_type",
      path,
      message: "must be an object",
    });
    return null;
  }
  return value;
}

function validateSource(
  value: unknown,
  path: string,
  violations: Violation[],
): SourceRef | null {
  const source = record(value, path, violations);
  if (source === null) return null;
  checkFields(source, ["path", "sha256", "bytes"], path, violations);
  const sourcePath = text(source, "path", `${path}.path`, violations);
  const sha256 = text(source, "sha256", `${path}.sha256`, violations);
  if (sha256 !== null && !SHA256_PATTERN.test(sha256)) {
    violations.push({
      code: "bad_sha256",
      path: `${path}.sha256`,
      message: "must be 64 lowercase hex characters",
    });
    return null;
  }
  const bytes = wholeNumber(source, "bytes", `${path}.bytes`, violations);
  if (sourcePath === null || sha256 === null || bytes === null) return null;
  return { path: sourcePath, sha256, bytes };
}

function validateDerivation(
  value: unknown,
  path: string,
  violations: Violation[],
): readonly DerivationStep[] | null {
  if (!isUnknownArray(value)) {
    violations.push({ code: "wrong_type", path, message: "must be an array" });
    return null;
  }
  if (value.length === 0) {
    violations.push({
      code: "derivation_empty",
      path,
      message: "a verdict must record at least one performed check",
    });
    return null;
  }
  const steps: DerivationStep[] = [];
  for (let index = 0; index < value.length; index += 1) {
    const stepPath = `${path}[${index}]`;
    const step = record(value[index], stepPath, violations);
    if (step === null) return null;
    checkFields(step, ["check", "ok", "detail"], stepPath, violations);
    const check = text(step, "check", `${stepPath}.check`, violations);
    const okValue = step["ok"];
    if (typeof okValue !== "boolean") {
      violations.push({
        code: "wrong_type",
        path: `${stepPath}.ok`,
        message: '"ok" must be a boolean',
      });
      return null;
    }
    const detailValue = step["detail"];
    if (typeof detailValue !== "string") {
      violations.push({
        code: "wrong_type",
        path: `${stepPath}.detail`,
        message: '"detail" must be a string',
      });
      return null;
    }
    if (detailValue.trim() === "") {
      violations.push({
        code: "derivation_step_undocumented",
        path: `${stepPath}.detail`,
        message: "a performed check must say what it observed",
      });
      return null;
    }
    if (check === null) return null;
    steps.push({ check, ok: okValue, detail: detailValue });
  }
  return steps;
}

function validateFalsifier(
  value: unknown,
  path: string,
  violations: Violation[],
): Falsifier | null {
  const falsifier = record(value, path, violations);
  if (falsifier === null) return null;
  checkFields(falsifier, ["command", "refutes"], path, violations);
  const command = text(falsifier, "command", `${path}.command`, violations);
  const refutes = text(falsifier, "refutes", `${path}.refutes`, violations);
  if (command === null || refutes === null) return null;
  return { command, refutes };
}

function validateEnvironment(
  value: unknown,
  path: string,
  violations: Violation[],
): Environment | null {
  const environment = record(value, path, violations);
  if (environment === null) return null;
  checkFields(environment, ["node", "lean", "platform"], path, violations);
  const node = text(environment, "node", `${path}.node`, violations);
  const lean = text(environment, "lean", `${path}.lean`, violations);
  const platform = text(environment, "platform", `${path}.platform`, violations);
  if (node === null || lean === null || platform === null) {
    violations.push({
      code: "bad_environment",
      path,
      message: "node, lean, and platform must all be recorded; none may be blank",
    });
    return null;
  }
  return { node, lean, platform };
}

function validateOwner(
  value: unknown,
  path: string,
  violations: Violation[],
): Owner | null {
  const owner = record(value, path, violations);
  if (owner === null) return null;
  checkFields(owner, ["actor", "tool", "environment"], path, violations);
  const actor = owner["actor"];
  if (typeof actor !== "string") {
    violations.push({
      code: "wrong_type",
      path: `${path}.actor`,
      message: '"actor" must be a string',
    });
    return null;
  }
  if (actor.trim() === "") {
    violations.push({
      code: "anonymous_action",
      path: `${path}.actor`,
      message: "an action with no named actor is not an action",
    });
    return null;
  }
  const tool = text(owner, "tool", `${path}.tool`, violations);
  const environment = validateEnvironment(
    owner["environment"],
    `${path}.environment`,
    violations,
  );
  if (tool === null || environment === null) return null;
  return { actor, tool, environment };
}

function validateVerdict(
  value: unknown,
  path: string,
  violations: Violation[],
): VerdictRecord | null {
  const verdict = record(value, path, violations);
  if (verdict === null) return null;
  checkFields(verdict, ["kind", "code", "detail"], path, violations);
  const kind = enumeration<Verdict>(
    verdict,
    "kind",
    VERDICTS,
    `${path}.kind`,
    "bad_verdict",
    violations,
  );
  const code = text(verdict, "code", `${path}.code`, violations);
  if (code !== null && !VERDICT_CODE_PATTERN.test(code)) {
    violations.push({
      code: "bad_verdict_code",
      path: `${path}.code`,
      message: "must be uppercase A-Z, 0-9, or underscore, 3-48 characters",
    });
    return null;
  }
  const detail = text(verdict, "detail", `${path}.detail`, violations);
  if (kind === null || code === null || detail === null) return null;
  return { kind, code, detail };
}

function requireValue<T>(value: T | null, path: string): T {
  if (value === null) {
    // Unreachable: callers check violations before assembling.
    throw new Error(`burden: internal validation gap at ${path}`);
  }
  return value;
}

/**
 * The admission gate. Returns either a receipt whose every field was checked,
 * or the deterministic list of violations. It never repairs, defaults, or
 * upgrades anything.
 */
export function validateReceipt(candidate: unknown): ValidationResult {
  const violations: Violation[] = [];
  if (!isUnknownRecord(candidate)) {
    return {
      ok: false,
      violations: [
        {
          code: "not_an_object",
          path: "",
          message: "a receipt must be an object",
        },
      ],
    };
  }
  checkFields(candidate, ALLOWED_FIELDS, "", violations);

  const schema = candidate["schema"];
  if (schema !== SCHEMA_ID) {
    violations.push({
      code: "bad_schema",
      path: "schema",
      message: `must be "${SCHEMA_ID}"`,
    });
  }

  const claimId = text(candidate, "claimId", "claimId", violations);
  if (claimId !== null && !CLAIM_ID_PATTERN.test(claimId)) {
    violations.push({
      code: "bad_claim_id",
      path: "claimId",
      message: "must match ^[A-Z0-9][A-Z0-9._-]{2,63}$",
    });
    return { ok: false, violations: sortViolations(violations) };
  }

  const claim = text(candidate, "claim", "claim", violations);
  const bearing = enumeration<Bearing>(
    candidate,
    "bearing",
    BEARINGS,
    "bearing",
    "bad_bearing",
    violations,
  );
  const checkability = enumeration<Checkability>(
    candidate,
    "checkability",
    CHECKABILITIES,
    "checkability",
    "bad_checkability",
    violations,
  );
  const tier = enumeration<Tier>(
    candidate,
    "tier",
    TIERS,
    "tier",
    "bad_tier",
    violations,
  );

  const missingRaw = candidate["missingMeasurement"];
  let missingMeasurement: string | null = null;
  if (missingRaw === null) {
    missingMeasurement = null;
  } else if (typeof missingRaw !== "string") {
    violations.push({
      code: "wrong_type",
      path: "missingMeasurement",
      message: '"missingMeasurement" must be a string or null',
    });
  } else if (missingRaw.trim() === "") {
    violations.push({
      code: "empty_value",
      path: "missingMeasurement",
      message: '"missingMeasurement" must be null or a named measurement',
    });
  } else {
    missingMeasurement = missingRaw;
  }

  const sourceRaw = candidate["source"];
  const source =
    sourceRaw === null ? null : validateSource(sourceRaw, "source", violations);

  const derivation = validateDerivation(
    candidate["derivation"],
    "derivation",
    violations,
  );
  const falsifier = validateFalsifier(
    candidate["falsifier"],
    "falsifier",
    violations,
  );
  const owner = validateOwner(candidate["owner"], "owner", violations);
  const verdict = validateVerdict(candidate["verdict"], "verdict", violations);

  if (violations.length > 0) {
    return { ok: false, violations: sortViolations(violations) };
  }

  const admitted: Receipt = {
    schema: SCHEMA_ID,
    claimId: requireValue(claimId, "claimId"),
    claim: requireValue(claim, "claim"),
    bearing: requireValue(bearing, "bearing"),
    checkability: requireValue(checkability, "checkability"),
    missingMeasurement,
    tier: requireValue(tier, "tier"),
    source,
    derivation: requireValue(derivation, "derivation"),
    falsifier: requireValue(falsifier, "falsifier"),
    owner: requireValue(owner, "owner"),
    verdict: requireValue(verdict, "verdict"),
  };

  // Cross-field rules. These are the ontology's actual content: the shape is
  // necessary, not sufficient.
  const crossViolations: Violation[] = [];

  if (
    admitted.checkability === "human_only" &&
    (admitted.missingMeasurement === null ||
      admitted.missingMeasurement.trim() === "")
  ) {
    crossViolations.push({
      code: "human_only_requires_named_measurement",
      path: "missingMeasurement",
      message:
        "a human-only burden must name the specific missing measurement, not merely say unverified",
    });
  }

  if (
    admitted.verdict.kind === "falsified" &&
    SUPPORTED_TIERS.includes(admitted.tier)
  ) {
    crossViolations.push({
      code: "falsified_requires_unsupported_tier",
      path: "tier",
      message: `tier "${admitted.tier}" cannot survive a falsified verdict`,
    });
  }

  if (
    admitted.verdict.kind === "unmeasured" &&
    SUPPORTED_TIERS.includes(admitted.tier)
  ) {
    crossViolations.push({
      code: "unmeasured_requires_unsupported_tier",
      path: "tier",
      message: `tier "${admitted.tier}" asserts support that was never measured`,
    });
  }

  if (
    admitted.verdict.kind === "verified" &&
    !SUPPORTED_TIERS.includes(admitted.tier)
  ) {
    crossViolations.push({
      code: "verified_requires_supported_tier",
      path: "tier",
      message: `a verified verdict cannot rest on tier "${admitted.tier}"`,
    });
  }

  if (
    SUPPORTED_TIERS.includes(admitted.tier) &&
    admitted.source === null
  ) {
    crossViolations.push({
      code: "supported_requires_source",
      path: "source",
      message: `tier "${admitted.tier}" requires the exact source that supports it`,
    });
  }

  if (crossViolations.length > 0) {
    return { ok: false, violations: sortViolations(crossViolations) };
  }

  return { ok: true, receipt: admitted };
}

/** Human-readable one-line rendering of a rejection. */
export function renderViolations(violations: readonly Violation[]): string {
  return violations
    .map((violation) => `${violation.code} at ${violation.path || "<root>"}: ${violation.message}`)
    .join("\n");
}

/** The receipt contract, published as data so `burden schema` can print it. */
export type FieldSpec = {
  readonly name: string;
  readonly type: string;
  readonly required: boolean;
  readonly rule: string;
};

export type CodeSpec = {
  readonly code: ViolationCode;
  readonly meaning: string;
  readonly falsifier: string;
};

const FIELDS: readonly FieldSpec[] = [
  { name: "schema", type: "string", required: true, rule: `exactly "${SCHEMA_ID}"` },
  { name: "claimId", type: "string", required: true, rule: "^[A-Z0-9][A-Z0-9._-]{2,63}$" },
  { name: "claim", type: "string", required: true, rule: "the proposition in words; non-empty" },
  { name: "bearing", type: "enum", required: true, rule: BEARINGS.join(" | ") },
  { name: "checkability", type: "enum", required: true, rule: CHECKABILITIES.join(" | ") },
  { name: "missingMeasurement", type: "string|null", required: true, rule: "non-empty when checkability is human_only" },
  { name: "tier", type: "enum", required: true, rule: TIERS.join(" | ") },
  { name: "source", type: "object|null", required: true, rule: "path, sha256 (64 hex), bytes >= 0; required for supported tiers" },
  { name: "derivation", type: "array", required: true, rule: "at least one {check, ok, detail} step; detail non-empty" },
  { name: "falsifier", type: "object", required: true, rule: "command and refutes, both non-empty" },
  { name: "owner", type: "object", required: true, rule: "actor and tool non-empty; environment {node, lean, platform} all non-empty" },
  { name: "verdict", type: "object", required: true, rule: "kind verified|falsified|unmeasured; code ^[A-Z][A-Z0-9_]{2,47}$; detail non-empty" },
];

const CODES: readonly CodeSpec[] = [
  { code: "not_an_object", meaning: "the candidate is not a JSON object", falsifier: "test: not_an_object" },
  { code: "unknown_field", meaning: "a field outside the published contract is present", falsifier: "test: unknown_field" },
  { code: "missing_field", meaning: "a required field is absent", falsifier: "test: missing_field" },
  { code: "wrong_type", meaning: "a field has the wrong JSON type", falsifier: "test: wrong_type" },
  { code: "empty_value", meaning: "a required string is blank", falsifier: "test: empty_value" },
  { code: "bad_schema", meaning: "the schema identifier is not the published one", falsifier: "test: bad_schema" },
  { code: "bad_claim_id", meaning: "the claim id violates its grammar", falsifier: "test: bad_claim_id" },
  { code: "bad_tier", meaning: "the tier is not in the published set", falsifier: "test: bad_tier" },
  { code: "bad_bearing", meaning: "the bearing is not in the published set", falsifier: "test: bad_bearing" },
  { code: "bad_verdict", meaning: "the verdict kind is not in the published set", falsifier: "test: bad_verdict" },
  { code: "bad_verdict_code", meaning: "the verdict code violates its grammar", falsifier: "test: bad_verdict_code" },
  { code: "bad_checkability", meaning: "the checkability is not in the published set", falsifier: "test: bad_checkability" },
  { code: "bad_sha256", meaning: "the source hash is not 64 lowercase hex characters", falsifier: "test: bad_sha256" },
  { code: "bad_bytes", meaning: "the source byte count is negative or not an integer", falsifier: "test: bad_bytes" },
  { code: "anonymous_action", meaning: "the actor is blank; the action has no owner", falsifier: "test: anonymous_action" },
  { code: "human_only_requires_named_measurement", meaning: "a human-only burden did not name the missing measurement", falsifier: "test: human_only_requires_named_measurement" },
  { code: "falsified_requires_unsupported_tier", meaning: "a falsified claim still wears a supported tier", falsifier: "test: falsified_requires_unsupported_tier" },
  { code: "unmeasured_requires_unsupported_tier", meaning: "an unmeasured claim wears a supported tier", falsifier: "test: unmeasured_requires_unsupported_tier" },
  { code: "verified_requires_supported_tier", meaning: "a verified verdict rests on an unsupported tier", falsifier: "test: verified_requires_supported_tier" },
  { code: "supported_requires_source", meaning: "a supported tier carries no source reference", falsifier: "test: supported_requires_source" },
  { code: "derivation_empty", meaning: "no performed check is recorded", falsifier: "test: derivation_empty" },
  { code: "derivation_step_undocumented", meaning: "a performed check does not say what it observed", falsifier: "test: derivation_step_undocumented" },
  { code: "bad_environment", meaning: "the environment is incomplete; the verdict is not located", falsifier: "test: bad_environment" },
];

export function describeContract(): {
  readonly schema: string;
  readonly fields: readonly FieldSpec[];
  readonly codes: readonly CodeSpec[];
} {
  return { schema: SCHEMA_ID, fields: FIELDS, codes: CODES };
}

/** Contract as canonical-JSON-compatible data, for `burden schema`. */
export function contractJson(): Json {
  const fields = FIELDS.map((field) => ({
    name: field.name,
    type: field.type,
    required: field.required,
    rule: field.rule,
  }));
  const codes = CODES.map((entry) => ({
    code: entry.code,
    meaning: entry.meaning,
    falsifier: entry.falsifier,
  }));
  return { schema: SCHEMA_ID, fields, codes };
}

/** Every published code, in contract order. Used by the fixture-coverage test. */
export const PUBLISHED_CODES: readonly ViolationCode[] = VIOLATION_CODES;
