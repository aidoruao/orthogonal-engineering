/**
 * The contract's own falsifiers.
 *
 * A violation code with no fixture that triggers it is a comment. This file
 * asserts set equality between the published codes and the codes the fixtures
 * actually reach, so adding a rule without a way to fail it breaks the build.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { contractJson, describeContract, validateReceipt } from "../src/validate.js";
import { canonicalJson } from "../src/canonical.js";
import {
  VIOLATION_CODES,
  type Environment,
  type Receipt,
  type SourceRef,
  type ViolationCode,
} from "../src/types.js";

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

const SOURCE: SourceRef = {
  path: "fixtures/source.txt",
  sha256: "a".repeat(64),
  bytes: 128,
};

const GOOD: Receipt = {
  schema: "burden.receipt/1",
  claimId: "CLM-CONTRACT-1",
  claim: "the span occurs verbatim in the named source",
  bearing: "supporting",
  checkability: "machine_checkable",
  missingMeasurement: null,
  tier: "fetched",
  source: SOURCE,
  derivation: [
    { check: "source_read", ok: true, detail: "128 bytes read" },
    { check: "span_exact", ok: true, detail: "contiguous span at lines 1-1" },
  ],
  falsifier: {
    command: "burden audit --claim CLM-CONTRACT-1 --source fixtures/source.txt",
    refutes: "the span does not occur contiguously in the source",
  },
  owner: {
    actor: "contract-test",
    tool: "burden/test",
    environment: ENV,
  },
  verdict: {
    kind: "verified",
    code: "SPAN_EXACT",
    detail: "the span occurs contiguously",
  },
};

type Fixture = {
  readonly code: ViolationCode;
  readonly make: () => unknown;
};

function mutated(overrides: Readonly<Record<string, unknown>>): unknown {
  return { ...GOOD, ...overrides };
}

const missingClaimId = (): unknown => {
  const copy: Record<string, unknown> = { ...GOOD };
  delete copy["claimId"];
  return copy;
};

const FIXTURES: readonly Fixture[] = [
  { code: "not_an_object", make: () => "not an object" },
  { code: "unknown_field", make: () => mutated({ extra: true }) },
  { code: "missing_field", make: missingClaimId },
  { code: "wrong_type", make: () => mutated({ claim: 42 }) },
  { code: "empty_value", make: () => mutated({ claim: "   " }) },
  { code: "bad_schema", make: () => mutated({ schema: "burden.receipt/2" }) },
  { code: "bad_claim_id", make: () => mutated({ claimId: "bad id!" }) },
  { code: "bad_tier", make: () => mutated({ tier: "great" }) },
  { code: "bad_bearing", make: () => mutated({ bearing: "critical" }) },
  {
    code: "bad_verdict",
    make: () => mutated({ verdict: { kind: "maybe", code: "SPAN_EXACT", detail: "x" } }),
  },
  {
    code: "bad_verdict_code",
    make: () => mutated({ verdict: { kind: "verified", code: "lower_case", detail: "x" } }),
  },
  { code: "bad_checkability", make: () => mutated({ checkability: "sometimes" }) },
  {
    code: "bad_sha256",
    make: () => mutated({ source: { ...SOURCE, sha256: "abc" } }),
  },
  {
    code: "bad_bytes",
    make: () => mutated({ source: { ...SOURCE, bytes: -1 } }),
  },
  {
    code: "anonymous_action",
    make: () => mutated({ owner: { ...GOOD.owner, actor: "  " } }),
  },
  {
    code: "human_only_requires_named_measurement",
    make: () => mutated({ checkability: "human_only", missingMeasurement: null }),
  },
  {
    code: "falsified_requires_unsupported_tier",
    make: () =>
      mutated({
        verdict: { kind: "falsified", code: "SPAN_NOT_FOUND", detail: "absent" },
      }),
  },
  {
    code: "unmeasured_requires_unsupported_tier",
    make: () =>
      mutated({
        verdict: { kind: "unmeasured", code: "NOT_RUN", detail: "not run" },
      }),
  },
  {
    code: "verified_requires_supported_tier",
    make: () => mutated({ tier: "unverified" }),
  },
  { code: "supported_requires_source", make: () => mutated({ source: null }) },
  { code: "derivation_empty", make: () => mutated({ derivation: [] }) },
  {
    code: "derivation_step_undocumented",
    make: () => mutated({ derivation: [{ check: "span_exact", ok: true, detail: "  " }] }),
  },
  {
    code: "bad_environment",
    make: () =>
      mutated({
        owner: {
          ...GOOD.owner,
          environment: { ...ENV, lean: "  " },
        },
      }),
  },
];

test("a well-formed receipt is admitted unchanged", () => {
  const result = validateReceipt(GOOD);
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(canonicalJson(result.receipt), canonicalJson(GOOD));
  }
});

test("every published violation code is reachable by a fixture", () => {
  const published = describeContract()
    .codes.map((entry) => entry.code)
    .sort();
  const covered = FIXTURES.map((fixture) => fixture.code).sort();
  assert.deepEqual(covered, published);
});

test("every fixture triggers the code it claims", () => {
  for (const fixture of FIXTURES) {
    const result = validateReceipt(fixture.make());
    assert.equal(result.ok, false, `${fixture.code} was admitted`);
    if (!result.ok) {
      const codes = result.violations.map((violation) => violation.code);
      assert.ok(
        codes.includes(fixture.code),
        `${fixture.code} not reached; got ${codes.join(", ")}`,
      );
    }
  }
});

test("the published code list and the contract agree", () => {
  assert.deepEqual(
    [...VIOLATION_CODES].sort(),
    describeContract()
      .codes.map((entry) => entry.code)
      .sort(),
  );
});

test("violations sort deterministically by path then code", () => {
  const result = validateReceipt({
    ...GOOD,
    claim: 42,
    bearing: "sometimes",
  });
  assert.equal(result.ok, false);
  if (!result.ok) {
    const paths = result.violations.map((violation) => violation.path);
    const sorted = [...paths].sort();
    assert.deepEqual(paths, sorted);
  }
});

test("the contract is printable as canonical JSON", () => {
  const text = canonicalJson(contractJson());
  assert.ok(text.startsWith('{"codes":'));
  assert.ok(text.includes('"schema":"burden.receipt/1"'));
  assert.ok(text.includes('"falsified_requires_unsupported_tier"'));
});
