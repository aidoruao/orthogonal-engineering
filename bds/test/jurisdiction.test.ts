/**
 * The jurisdiction gate's own falsifiers.
 *
 * `admissible()` is the runtime twin of `Righteous` in `L3_JURISDICTION.lean`.
 * Saying so in a comment is not a check: these tests pin every violation code to
 * a fixture that reaches it, and `TS_JURISDICTION.lean` additionally proves the
 * two implementations agree by construction.
 *
 * The rule applied here is the same one `burden/` applies to its own contract:
 * a code with no fixture that triggers it is a comment wearing a code's clothes.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  SEVERITY_WEIGHT,
  admissible,
  sortViolations,
  type Finding,
  type Severity,
  type Source,
  type Subject,
  type Tier,
  type ViolationCode,
} from "../src/types.js";

const SOURCE: Source = {
  path: "evidence/bds/19-10_Contract_Cleaning_Services.pdf",
  sha256: "7a2d44935f1a12efd6738076e67d53bac6170801077ac5dbec1fb9f14f9ea661",
  bytes: 1399397,
  pages: [58, 60],
};

/** A finding that satisfies every condition. Anything admissible must look like
 *  this on the axes the gate checks. */
const GOOD: Finding = {
  id: "FND-TEST-1",
  subject: "structure",
  claim:
    "Breakfast Point Academy is listed at 108,941 sq ft on both Exhibit B p.58 and Exhibit C p.60",
  severity: "minor",
  warrantedSeverity: "major",
  evidence: "fetched",
  source: SOURCE,
  falsifier:
    "re-extract RFP 19-10 and show a different square footage on either exhibit page",
  detail: "read from two pages of the same fetched document",
};

function mutated(overrides: Partial<Finding>): Finding {
  return { ...GOOD, ...overrides };
}

const FIXTURES: readonly { code: ViolationCode; make: () => Finding }[] = [
  { code: "empty_claim", make: () => mutated({ claim: "   " }) },
  { code: "no_falsifier", make: () => mutated({ falsifier: "" }) },
  {
    code: "severity_exceeds_warrant",
    make: () => mutated({ severity: "critical", warrantedSeverity: "minor" }),
  },
  {
    code: "unsupported_severity",
    make: () => mutated({ severity: "critical", warrantedSeverity: "critical", evidence: "unmeasured" }),
  },
  {
    code: "fetched_requires_source",
    make: () => mutated({ source: null }),
  },
];

test("a proportionate, falsifiable, sourced finding is admissible", () => {
  assert.deepEqual(admissible(GOOD), []);
});

test("every violation code is reachable by a fixture", () => {
  const reached = new Set<string>();
  for (const fixture of FIXTURES) {
    const codes = admissible(fixture.make()).map((v) => v.code);
    assert.ok(
      codes.includes(fixture.code),
      `${fixture.code} not reached; got ${codes.join(", ") || "none"}`,
    );
    for (const code of codes) reached.add(code);
  }
  assert.deepEqual([...reached].sort(), [...FIXTURES.map((f) => f.code)].sort());
});

test("severity may not exceed warrant, at every boundary", () => {
  const sev: readonly Severity[] = ["critical", "major", "minor", "none"];
  for (const claimed of sev) {
    for (const warranted of sev) {
      const found = admissible(
        mutated({ severity: claimed, warrantedSeverity: warranted, evidence: "fetched" }),
      ).map((v) => v.code);
      const inflated = SEVERITY_WEIGHT[claimed] > SEVERITY_WEIGHT[warranted];
      assert.equal(
        found.includes("severity_exceeds_warrant"),
        inflated,
        `${claimed} vs ${warranted}: weights are ${SEVERITY_WEIGHT[claimed]}/${SEVERITY_WEIGHT[warranted]}`,
      );
    }
  }
});

test("a critical or major finding cannot rest on unmeasured or blocked evidence", () => {
  const tiers: readonly Tier[] = ["unmeasured", "located_blocked", "corroborated", "fetched", "retired"];
  for (const tier of tiers) {
    for (const severity of ["critical", "major"] as const) {
      const found = admissible(
        mutated({ severity, warrantedSeverity: severity, evidence: tier }),
      ).map((v) => v.code);
      const supported = tier === "fetched" || tier === "corroborated";
      assert.equal(
        found.includes("unsupported_severity"),
        !supported,
        `${severity} on ${tier}`,
      );
    }
  }
});

test("a fetched finding always commits to a source", () => {
  const found = admissible(mutated({ source: null })).map((v) => v.code);
  assert.ok(found.includes("fetched_requires_source"));
});

test("minor and none findings need no source to be admissible", () => {
  // Not an endorsement of unsourced findings: it records that the gate's
  // source requirement is proportional to severity, which is deliberate.
  const found = admissible(
    mutated({ severity: "none", warrantedSeverity: "none", evidence: "unmeasured", source: null }),
  );
  assert.deepEqual(found, []);
});

test("violations sort deterministically", () => {
  const found = sortViolations(admissible(mutated({ claim: "", falsifier: "", source: null })));
  const paths = found.map((v) => v.path);
  assert.deepEqual(paths, [...paths].sort());
});

test("the gate never returns a code outside its published union", () => {
  // Exhaustive over the small axes: a typo'd code string would fail here.
  const subjects: readonly Subject[] = ["structure", "attribution"];
  const sev: readonly Severity[] = ["critical", "major", "minor", "none"];
  const tiers: readonly Tier[] = ["unmeasured", "located_blocked", "corroborated", "fetched", "retired"];
  const known = new Set<string>(FIXTURES.map((f) => f.code));
  for (const subject of subjects) {
    for (const severity of sev) {
      for (const warranted of sev) {
        for (const tier of tiers) {
          for (const falsifier of ["", "refuted by re-reading the page"]) {
            for (const source of [null, SOURCE]) {
              const codes = admissible({
                ...GOOD,
                subject,
                severity,
                warrantedSeverity: warranted,
                evidence: tier,
                falsifier,
                source,
              }).map((v) => v.code);
              for (const code of codes) {
                assert.ok(known.has(code), `undocumented code ${code}`);
              }
            }
          }
        }
      }
    }
  }
});
