/**
 * Coverage tests.
 *
 * The property under test: claims and documents are different numbers, and a
 * claim on an already-covered document moves neither. This is the operational
 * counterpart of `L1_COVERAGE.lean`'s `addDoc_zero_if_covered`.
 */

import { strict as assert } from "node:assert";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, describe, it } from "node:test";

import {
  computeCoverage,
  formatReport,
  manifestDocuments,
  readClaims,
  redundantClaims,
  type ClaimLike,
} from "../src/coverage.js";

const root = mkdtempSync(join(tmpdir(), "oe-cov-"));
after(() => {
  rmSync(root, { recursive: true, force: true });
});

function claim(id: string, doc: number): ClaimLike {
  return { claimId: id, documentNumber: doc };
}

const MANIFEST = [
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  gov.uscourts.cacd.823614.62.0.pdf",
  "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  gov.uscourts.cacd.823614.67.0.pdf",
  "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc  gov.uscourts.cacd.823614.385.0_1.pdf",
  "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd  Justia Dockets.txt",
].join("\n");

describe("manifestDocuments", () => {
  it("extracts sorted document numbers and ignores non-docket files", () => {
    assert.deepEqual(manifestDocuments(MANIFEST), [62, 67, 385]);
  });

  it("returns an empty list for an empty manifest", () => {
    assert.deepEqual(manifestDocuments(""), []);
  });
});

describe("computeCoverage", () => {
  const docs = [62, 67, 385];

  it("counts documents separately from claims", () => {
    const report = computeCoverage(
      [claim("CLM-A", 385), claim("CLM-B", 385), claim("CLM-C", 62)],
      docs,
    );
    assert.equal(report.claimCount, 3);
    assert.equal(report.coveredDocs.length, 2);
    assert.equal(report.darkDocs.length, 1);
  });

  it("reports the dark document by number", () => {
    const report = computeCoverage([claim("CLM-A", 385)], docs);
    assert.deepEqual(report.darkDocs, [62, 67]);
  });

  it("counts redundant claims as zero-marginal", () => {
    const report = computeCoverage(
      [claim("CLM-A", 385), claim("CLM-B", 385), claim("CLM-C", 385)],
      docs,
    );
    assert.equal(redundantClaims(report), 2);
  });

  it("orders per-document counts descending, then by document", () => {
    const report = computeCoverage(
      [claim("A", 62), claim("B", 385), claim("C", 385), claim("D", 67)],
      docs,
    );
    assert.deepEqual(
      report.perDocument.map((entry) => entry.doc),
      [385, 62, 67],
    );
  });

  it("flags a claim about a document outside the manifest", () => {
    const report = computeCoverage([claim("CLM-GHOST", 99999)], docs);
    assert.deepEqual(report.unboundClaims, ["CLM-GHOST"]);
    assert.equal(report.coveredDocs.length, 0);
    assert.equal(report.darkDocs.length, 3);
  });

  it("does not count an unbound claim toward coverage", () => {
    const report = computeCoverage([claim("A", 99999), claim("B", 62)], docs);
    assert.equal(report.claimCount, 2);
    assert.equal(report.coveredDocs.length, 1);
    assert.deepEqual(report.coveredDocs, [62]);
  });

  it("handles an empty claim set", () => {
    const report = computeCoverage([], docs);
    assert.equal(report.claimCount, 0);
    assert.equal(report.coveredDocs.length, 0);
    assert.equal(report.darkDocs.length, 3);
  });

  it("handles an empty manifest without dividing by zero", () => {
    const report = computeCoverage([claim("A", 62)], []);
    assert.equal(report.manifestDocs.length, 0);
    assert.deepEqual(report.unboundClaims, ["A"]);
    // formatReport must not throw on 0/0.
    assert.match(formatReport(report), /0\/0 \(0%\)/);
  });

  it("is deterministic", () => {
    const claims = [claim("B", 385), claim("A", 62)];
    assert.deepEqual(computeCoverage(claims, docs), computeCoverage(claims, docs));
  });
});

describe("readClaims", () => {
  it("reads well-formed JSONL", () => {
    const path = join(root, "claims.jsonl");
    writeFileSync(path, `${JSON.stringify(claim("A", 62))}\n${JSON.stringify(claim("B", 67))}\n`);
    const { claims, malformed } = readClaims(path);
    assert.equal(claims.length, 2);
    assert.equal(malformed.length, 0);
  });

  it("reports malformed lines instead of dropping them", () => {
    const path = join(root, "bad.jsonl");
    writeFileSync(path, `not json\n${JSON.stringify(claim("A", 62))}\n{"claimId":"B"}\n`);
    const { claims, malformed } = readClaims(path);
    assert.equal(claims.length, 1);
    assert.equal(malformed.length, 2);
  });

  it("returns empty for a missing file", () => {
    const { claims, malformed } = readClaims(join(root, "nope.jsonl"));
    assert.equal(claims.length, 0);
    assert.equal(malformed.length, 0);
  });
});

describe("formatReport", () => {
  it("shows both numbers and the dark list", () => {
    const report = computeCoverage([claim("A", 385)], [62, 67, 385]);
    const text = formatReport(report);
    assert.match(text, /claims:\s+1/);
    assert.match(text, /documents covered: 1\/3/);
    assert.match(text, /documents dark:\s+2/);
    assert.match(text, /dark:\n\s+62 67/);
  });
});
