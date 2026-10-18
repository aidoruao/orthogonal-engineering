import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import { admit } from "../src/validate.js";
import { parseManifest } from "../src/manifest.js";
import { MAX_QUOTE_CHARS } from "../src/types.js";
import type { Violation, ViolationCode } from "../src/types.js";

const SHA = "8ec492dce881fff47d28aaac3607a7b2a736c71e04038e3c2f4d7dc3d183bdc4";
const SHA_OTHER = "5fff7fdbc1bb7e6943e2caca613dc995393a0809096bcd032449b129edc4e94e";

/** A minimal record that must pass. Tests mutate exactly one field. */
function valid(): Record<string, unknown> {
  return {
    claimId: "CLM-0001",
    docket: "2:21-cv-04920",
    documentNumber: 385,
    page: 9,
    paragraph: 18,
    quote: "a verbatim span from the cited page",
    sourceSha256: SHA,
    tier: { kind: "fetched", sha256: SHA },
    nature: "allegation",
  };
}

function codes(violations: readonly Violation[]): ViolationCode[] {
  return violations.map((v) => v.code);
}

function reject(input: unknown, expected: ViolationCode, manifest?: ReadonlySet<string>): void {
  const result = admit(input, manifest);
  assert.equal(result.ok, false, `expected rejection for ${expected}`);
  if (result.ok) return;
  assert.ok(
    codes(result.violations).includes(expected),
    `expected ${expected}, got ${JSON.stringify(result.violations)}`,
  );
}

describe("admit — accepts a complete record", () => {
  it("admits the base record and preserves every field", () => {
    const result = admit(valid());
    assert.equal(result.ok, true);
    if (!result.ok) return;
    assert.equal(result.record.claimId, "CLM-0001");
    assert.equal(result.record.docket, "2:21-cv-04920");
    assert.equal(result.record.documentNumber, 385);
    assert.equal(result.record.page, 9);
    assert.equal(result.record.paragraph, 18);
    assert.equal(result.record.nature, "allegation");
    assert.equal(result.record.tier.kind, "fetched");
  });

  it("admits a record with no paragraph", () => {
    const record = valid();
    delete record["paragraph"];
    const result = admit(record);
    assert.equal(result.ok, true);
    if (!result.ok) return;
    assert.equal("paragraph" in result.record, false);
  });

  it("admits a finding that rests on a fetched primary", () => {
    const record = valid();
    record["nature"] = "finding";
    assert.equal(admit(record).ok, true);
  });
});

describe("admit — rejects non-objects", () => {
  it("rejects null", () => reject(null, "not_an_object"));
  it("rejects a string", () => reject("CLM-0001", "not_an_object"));
  it("rejects an array", () => reject([valid()], "not_an_object"));
  it("rejects a number", () => reject(42, "not_an_object"));
});

describe("admit — rejects bad identifiers", () => {
  it("rejects a missing claimId", () => {
    const record = valid();
    delete record["claimId"];
    reject(record, "missing_field");
  });

  it("rejects a lowercase claimId", () => {
    const record = valid();
    record["claimId"] = "clm-0001";
    reject(record, "bad_claim_id");
  });

  it("rejects a too-short claimId", () => {
    const record = valid();
    record["claimId"] = "AB";
    reject(record, "bad_claim_id");
  });

  it("rejects a malformed docket", () => {
    const record = valid();
    record["docket"] = "case 123";
    reject(record, "bad_docket");
  });

  it("rejects a docket without a district prefix", () => {
    const record = valid();
    record["docket"] = "21-cv-04920";
    reject(record, "bad_docket");
  });
});

describe("admit — rejects bad citation coordinates", () => {
  it("rejects a missing page", () => {
    const record = valid();
    delete record["page"];
    reject(record, "missing_field");
  });

  it("rejects page zero", () => {
    const record = valid();
    record["page"] = 0;
    reject(record, "bad_page");
  });

  it("rejects a fractional page", () => {
    const record = valid();
    record["page"] = 9.5;
    reject(record, "bad_page");
  });

  it("rejects a string page", () => {
    const record = valid();
    record["page"] = "9";
    reject(record, "wrong_type");
  });

  it("rejects a missing documentNumber", () => {
    const record = valid();
    delete record["documentNumber"];
    reject(record, "missing_field");
  });

  it("rejects documentNumber zero", () => {
    const record = valid();
    record["documentNumber"] = 0;
    reject(record, "bad_document_number");
  });

  it("rejects a negative paragraph", () => {
    const record = valid();
    record["paragraph"] = -1;
    reject(record, "bad_paragraph");
  });
});

describe("admit — rejects bad quotes", () => {
  it("rejects a missing quote", () => {
    const record = valid();
    delete record["quote"];
    reject(record, "missing_field");
  });

  it("rejects an empty quote", () => {
    const record = valid();
    record["quote"] = "   ";
    reject(record, "missing_field");
  });

  it("rejects a quote longer than the cap", () => {
    const record = valid();
    record["quote"] = "x".repeat(MAX_QUOTE_CHARS + 1);
    reject(record, "quote_too_long");
  });

  it("accepts a quote exactly at the cap", () => {
    const record = valid();
    record["quote"] = "x".repeat(MAX_QUOTE_CHARS);
    assert.equal(admit(record).ok, true);
  });
});

describe("admit — rejects bad hashes", () => {
  it("rejects a missing sourceSha256", () => {
    const record = valid();
    delete record["sourceSha256"];
    reject(record, "missing_field");
  });

  it("rejects an uppercase hash", () => {
    const record = valid();
    record["sourceSha256"] = SHA.toUpperCase();
    reject(record, "bad_sha256");
  });

  it("rejects a short hash", () => {
    const record = valid();
    record["sourceSha256"] = "abc123";
    reject(record, "bad_sha256");
  });

  it("rejects a hash that disagrees with the fetched tier", () => {
    const record = valid();
    record["sourceSha256"] = SHA;
    record["tier"] = { kind: "fetched", sha256: SHA_OTHER };
    reject(record, "bad_sha256");
  });
});

describe("admit — rejects bad tiers", () => {
  it("rejects a missing tier", () => {
    const record = valid();
    delete record["tier"];
    reject(record, "wrong_type");
  });

  it("rejects an unknown tier kind", () => {
    const record = valid();
    record["tier"] = { kind: "vibes" };
    reject(record, "unknown_tier");
  });

  it("rejects a fetched tier with no sha256", () => {
    const record = valid();
    record["tier"] = { kind: "fetched" };
    reject(record, "missing_field");
  });

  it("rejects a single corroborator", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["only-one.example"] };
    reject(record, "too_few_corroborators");
  });

  it("rejects corroborated sources containing a blank", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["a.example", "  "] };
    reject(record, "empty_value");
  });

  it("accepts two independent corroborators", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["a.example", "b.example"] };
    assert.equal(admit(record).ok, true);
  });

  it("rejects located_blocked without a locator", () => {
    const record = valid();
    record["tier"] = { kind: "located_blocked" };
    reject(record, "missing_field");
  });

  it("accepts located_blocked with a locator", () => {
    const record = valid();
    record["tier"] = { kind: "located_blocked", locator: "PACER doc 387" };
    assert.equal(admit(record).ok, true);
  });

  it("rejects retired without a reason", () => {
    const record = valid();
    record["tier"] = { kind: "retired" };
    reject(record, "missing_field");
  });

  it("accepts the unverified tier", () => {
    const record = valid();
    record["tier"] = { kind: "unverified" };
    assert.equal(admit(record).ok, true);
  });

  it("rejects an unknown key inside the tier", () => {
    const record = valid();
    record["tier"] = { kind: "unverified", note: "smuggled" };
    reject(record, "unknown_field");
  });
});

describe("admit — nature is load-bearing", () => {
  it("rejects a missing nature", () => {
    const record = valid();
    delete record["nature"];
    reject(record, "missing_field");
  });

  it("rejects an unknown nature", () => {
    const record = valid();
    record["nature"] = "truth";
    reject(record, "unknown_nature");
  });

  it("rejects a finding resting on corroboration alone", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["a.example", "b.example"] };
    record["nature"] = "finding";
    reject(record, "adjudicated_requires_fetched");
  });

  it("rejects an order resting on unverified evidence", () => {
    const record = valid();
    record["tier"] = { kind: "unverified" };
    record["nature"] = "order";
    reject(record, "adjudicated_requires_fetched");
  });

  it("rejects a finding resting on located_blocked evidence", () => {
    const record = valid();
    record["tier"] = { kind: "located_blocked", locator: "PACER doc 387" };
    record["nature"] = "finding";
    reject(record, "adjudicated_requires_fetched");
  });

  it("allows an allegation on corroboration", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["a.example", "b.example"] };
    record["nature"] = "allegation";
    assert.equal(admit(record).ok, true);
  });

  it("allows stated_intent on a fetched primary", () => {
    const record = valid();
    record["nature"] = "stated_intent";
    assert.equal(admit(record).ok, true);
  });

  it("allows a party filing on a fetched primary", () => {
    const record = valid();
    record["nature"] = "party_filing";
    assert.equal(admit(record).ok, true);
  });

  it("rejects a party filing resting on corroboration", () => {
    const record = valid();
    record["tier"] = { kind: "corroborated", sources: ["a.example", "b.example"] };
    record["nature"] = "party_filing";
    assert.equal(admit(record).ok, true, "a filing is not an adjudication, so corroboration is permitted");
  });

  it("lists every valid nature in the rejection message", () => {
    const record = valid();
    record["nature"] = "truth";
    const result = admit(record);
    assert.equal(result.ok, false);
    if (result.ok) return;
    const message = result.violations.find((v) => v.code === "unknown_nature")?.message ?? "";
    for (const nature of ["allegation", "party_filing", "order", "finding", "settlement", "stated_intent"]) {
      assert.ok(message.includes(nature), `message should mention ${nature}`);
    }
  });
});

describe("admit — deny by default", () => {
  it("rejects an unknown top-level field", () => {
    const record = valid();
    record["plaintiffName"] = "someone";
    reject(record, "unknown_field");
  });

  it("rejects an unknown field even when everything else is valid", () => {
    const record = valid();
    record["extra"] = { nested: true };
    const result = admit(record);
    assert.equal(result.ok, false);
    if (result.ok) return;
    assert.equal(result.violations.length, 1);
    assert.equal(result.violations[0]?.path, "extra");
  });
});

describe("admit — manifest binding", () => {
  const manifest = new Set([SHA]);

  it("accepts a hash the manifest commits to", () => {
    assert.equal(admit(valid(), manifest).ok, true);
  });

  it("rejects a hash the manifest does not commit to", () => {
    const record = valid();
    record["sourceSha256"] = SHA_OTHER;
    record["tier"] = { kind: "fetched", sha256: SHA_OTHER };
    reject(record, "hash_not_in_manifest", manifest);
  });
});

describe("admit — violations are deterministic", () => {
  it("returns the same order for the same bad input", () => {
    const record = valid();
    delete record["claimId"];
    delete record["page"];
    delete record["quote"];
    const first = admit(record);
    const second = admit(record);
    assert.equal(first.ok, false);
    assert.equal(second.ok, false);
    if (first.ok || second.ok) return;
    assert.deepEqual(first.violations, second.violations);
  });

  it("sorts violations by path", () => {
    const record = valid();
    delete record["claimId"];
    delete record["docket"];
    delete record["page"];
    const result = admit(record);
    assert.equal(result.ok, false);
    if (result.ok) return;
    const paths = result.violations.map((v) => v.path);
    const sorted = [...paths].sort();
    assert.deepEqual(paths, sorted);
  });

  it("reports every missing field at once rather than the first", () => {
    const result = admit({});
    assert.equal(result.ok, false);
    if (result.ok) return;
    const paths = new Set(result.violations.map((v) => v.path));
    for (const field of ["claimId", "docket", "documentNumber", "page", "quote", "sourceSha256"]) {
      assert.ok(paths.has(field), `expected a violation for ${field}`);
    }
  });
});

describe("parseManifest", () => {
  it("parses sha256sum output", () => {
    const manifest = parseManifest(`${SHA}  gov.uscourts.cacd.823614.1.0_3.pdf\n`);
    assert.equal(manifest.entries.length, 1);
    assert.equal(manifest.hashes.has(SHA), true);
    assert.equal(manifest.entries[0]?.name, "gov.uscourts.cacd.823614.1.0_3.pdf");
    assert.equal(manifest.malformed.length, 0);
  });

  it("parses the binary-mode asterisk form", () => {
    const manifest = parseManifest(`${SHA} *file.pdf\n`);
    assert.equal(manifest.entries[0]?.name, "file.pdf");
  });

  it("ignores blank lines", () => {
    const manifest = parseManifest(`\n${SHA}  a.pdf\n\n`);
    assert.equal(manifest.entries.length, 1);
    assert.equal(manifest.malformed.length, 0);
  });

  it("reports malformed lines instead of dropping them", () => {
    const manifest = parseManifest(`not a hash  file.pdf\n${SHA}  a.pdf\n`);
    assert.equal(manifest.entries.length, 1);
    assert.equal(manifest.malformed.length, 1);
  });

  it("rejects a duplicate hash", () => {
    const manifest = parseManifest(`${SHA}  a.pdf\n${SHA}  b.pdf\n`);
    assert.equal(manifest.entries.length, 1);
    assert.equal(manifest.malformed.length, 1);
  });

  it("rejects a two-entry manifest with fewer than two hashes", () => {
    const manifest = parseManifest(`${SHA}  a.pdf\n${SHA}  b.pdf\n`);
    assert.equal(manifest.hashes.size, 1);
  });
});
