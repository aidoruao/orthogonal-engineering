/**
 * Real-corpus falsifier.
 *
 * Runs only where the L0 corpus exists; otherwise it reports an explicit SKIP
 * so the count is honest rather than silently zero. It never prints corpus
 * content — only verdicts.
 *
 * The suite proves both directions:
 *   1. A quote genuinely taken from the cited page is ACCEPTED.
 *   2. A quote that is not on that page is REJECTED.
 *
 * Without (2), "verification" would be a function that returns true.
 *
 * Point it at a corpus with OE_CORPUS_DIR.
 */

import { strict as assert } from "node:assert";
import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { describe, it } from "node:test";

import { admit } from "../src/validate.js";
import { checkQuoteOnPage, extractPdf, normalizeForComparison } from "../src/extract.js";
import { loadManifest } from "../src/manifest.js";
import { sourceNameCandidates } from "../src/workbench.js";
import type { ClaimRecord } from "../src/types.js";

const SOURCES = process.env["OE_CORPUS_DIR"] ?? "/home/idor/oe-local/evidence/fleites";
const MANIFEST = join(SOURCES, "FLEITES_MANIFEST.sha256");
const DOC = 385;

function locate(): { path: string; sha256: string } | undefined {
  const path = sourceNameCandidates(DOC)
    .map((name) => join(SOURCES, name))
    .find((candidate) => existsSync(candidate));
  if (path === undefined) return undefined;
  const sha256 = createHash("sha256").update(readFileSync(path)).digest("hex");
  return { path, sha256 };
}

const located = existsSync(SOURCES) ? locate() : undefined;

if (located === undefined) {
  describe("real corpus — quote verification", () => {
    it(
      "corpus not present; real quote verification was not exercised",
      { skip: `no L0 corpus at ${SOURCES}` },
      () => {
        /* skipped */
      },
    );
  });
} else {
  const corpus = located;

  describe("real corpus — quote verification", () => {
    it("accepts a quote that is genuinely on the cited page", async () => {
      const doc = await extractPdf(corpus.path);

      const page = doc.pages.find((candidate) => candidate.text.trim().length > 800);
      assert.ok(page !== undefined, "expected at least one page with text");

      const normalized = normalizeForComparison(page.text);
      const span = normalized.slice(200, 320).trim();
      assert.ok(span.length >= 40, "expected a span long enough to be meaningful");

      const record: ClaimRecord = {
        claimId: "CLM-REAL-1",
        docket: "2:21-cv-04920",
        documentNumber: DOC,
        page: page.page,
        quote: span,
        sourceSha256: corpus.sha256,
        tier: { kind: "fetched", sha256: corpus.sha256 },
        nature: "allegation",
      };

      const check = checkQuoteOnPage(doc, record.page, record.quote);
      assert.equal(check.found, true, `expected the real span to be found: ${check.reason ?? ""}`);
    });

    it("rejects a fabricated quote on the same page", async () => {
      const doc = await extractPdf(corpus.path);
      const page = doc.pages.find((candidate) => candidate.text.trim().length > 800);
      assert.ok(page !== undefined);

      const fabricated =
        "this sentence was never written in the cited document and must be rejected";

      const check = checkQuoteOnPage(doc, page.page, fabricated);
      assert.equal(check.found, false, "a fabricated quote must not verify");
      assert.match(check.reason ?? "", /not found/);
    });

    it("rejects a real quote attributed to the wrong page", async () => {
      const doc = await extractPdf(corpus.path);

      const source = doc.pages.find((candidate) => candidate.text.trim().length > 800);
      assert.ok(source !== undefined);
      const span = normalizeForComparison(source.text).slice(200, 320).trim();

      const other = doc.pages.find(
        (candidate) =>
          candidate.page !== source.page &&
          !normalizeForComparison(candidate.text).includes(span),
      );
      if (other === undefined) return; // single-page document; nothing to test

      const check = checkQuoteOnPage(doc, other.page, span);
      assert.equal(check.found, false, "a real quote on the wrong page must not verify");
    });

    it("the manifest commits to the document hash the claim uses", () => {
      const manifest = loadManifest(MANIFEST);
      assert.equal(manifest.malformed.length, 0, "manifest should parse cleanly");
      assert.equal(
        manifest.hashes.has(corpus.sha256),
        true,
        "the local document hash must appear in the published manifest",
      );
    });

    it("admits a well-formed claim bound to the manifest", () => {
      const manifest = loadManifest(MANIFEST);
      const candidate = {
        claimId: "CLM-REAL-2",
        docket: "2:21-cv-04920",
        documentNumber: DOC,
        page: 1,
        quote: "a span",
        sourceSha256: corpus.sha256,
        tier: { kind: "fetched", sha256: corpus.sha256 },
        nature: "allegation",
      };
      const result = admit(candidate, manifest.hashes);
      assert.equal(result.ok, true);
    });
  });
}
