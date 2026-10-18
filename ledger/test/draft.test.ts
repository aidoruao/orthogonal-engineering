/**
 * Draft generator tests.
 *
 * The corpus-dependent path is exercised separately (and skipped where the
 * corpus is absent). These tests cover the parts that must hold everywhere:
 * local-only fields never reach a publishable record, and a missing source is
 * a named failure rather than a silent empty candidate.
 */

import { strict as assert } from "node:assert";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, describe, it } from "node:test";

import { draftBatch, draftOne, toPublic, type DraftSpec } from "../src/draft.js";

const root = mkdtempSync(join(tmpdir(), "oe-draft-"));
after(() => {
  rmSync(root, { recursive: true, force: true });
});

function spec(overrides: Partial<DraftSpec> = {}): DraftSpec {
  return {
    claimId: "CLM-TEST-1",
    documentNumber: 99999,
    anchor: "a phrase",
    nature: "allegation",
    ...overrides,
  };
}

describe("draftOne", () => {
  it("reports a missing source instead of inventing a candidate", async () => {
    const result = await draftOne(spec(), root);
    assert.equal(result.candidate, undefined);
    assert.equal(result.code, "source_missing");
    assert.match(result.detail ?? "", /99999/);
  });

  it("reports an empty anchor", async () => {
    const result = await draftOne(spec({ anchor: "   " }), root);
    assert.equal(result.candidate, undefined);
    assert.equal(result.code, "anchor_not_found");
  });
});

describe("draftBatch", () => {
  it("preserves input order in the failure report", async () => {
    const specs = [
      spec({ claimId: "CLM-A" }),
      spec({ claimId: "CLM-B" }),
      spec({ claimId: "CLM-C" }),
    ];
    const { candidates, failures } = await draftBatch(specs, root);
    assert.equal(candidates.length, 0);
    assert.deepEqual(
      failures.map((failure) => failure.claimId),
      ["CLM-A", "CLM-B", "CLM-C"],
    );
  });

  it("does not throw on a batch of one bad spec", async () => {
    const { failures } = await draftBatch([spec()], root);
    assert.equal(failures.length, 1);
    assert.equal(failures[0]?.code, "source_missing");
  });
});

describe("toPublic", () => {
  it("strips every local-only field", () => {
    const published = toPublic({
      claimId: "CLM-X",
      docket: "2:21-cv-04920",
      documentNumber: 385,
      page: 9,
      quote: "a verbatim span",
      sourceSha256: "a".repeat(64),
      tier: { kind: "fetched", sha256: "a".repeat(64) },
      nature: "allegation",
      sourceName: "gov.uscourts.cacd.823614.385.0_1.pdf",
      note: "reviewer note with local context",
    });
    assert.equal("sourceName" in published, false);
    assert.equal("note" in published, false);
    assert.equal(published["claimId"], "CLM-X");
  });

  it("keeps exactly the eight published fields", () => {
    const published = toPublic({
      claimId: "CLM-X",
      docket: "2:21-cv-04920",
      documentNumber: 385,
      page: 9,
      quote: "a span",
      sourceSha256: "a".repeat(64),
      tier: { kind: "fetched", sha256: "a".repeat(64) },
      nature: "allegation",
      sourceName: "file.pdf",
      note: "note",
    });
    assert.deepEqual(Object.keys(published).sort(), [
      "claimId",
      "docket",
      "documentNumber",
      "nature",
      "page",
      "quote",
      "sourceSha256",
      "tier",
    ]);
  });

  it("produces a record the admission gate accepts", async () => {
    const { admit } = await import("../src/validate.js");
    const published = toPublic({
      claimId: "CLM-X",
      docket: "2:21-cv-04920",
      documentNumber: 385,
      page: 9,
      quote: "a verbatim span long enough to be meaningful",
      sourceSha256: "a".repeat(64),
      tier: { kind: "fetched", sha256: "a".repeat(64) },
      nature: "allegation",
      sourceName: "file.pdf",
    });
    const result = admit(published);
    assert.equal(result.ok, true);
  });
});

describe("determinism", () => {
  it("a missing-source batch is stable across runs", async () => {
    const first = await draftBatch([spec({ claimId: "CLM-A" })], root);
    const second = await draftBatch([spec({ claimId: "CLM-A" })], root);
    assert.deepEqual(first.failures, second.failures);
  });
});
