/**
 * Synthetic tests for quote checking and normalization.
 *
 * These run anywhere, including CI, with no corpus present. They test the
 * comparison logic itself: line wrapping, hyphenation, ligatures, smart
 * quotes, and the page boundary.
 */

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import {
  checkQuoteOnPage,
  normalizeForComparison,
  type ExtractedDocument,
} from "../src/extract.js";

function doc(pages: readonly string[]): ExtractedDocument {
  return {
    pages: pages.map((text, index) => ({ page: index + 1, text })),
    totalPages: pages.length,
  };
}

describe("normalizeForComparison", () => {
  it("collapses whitespace and newlines", () => {
    assert.equal(normalizeForComparison("a\n\n  b\t c"), "a b c");
  });

  it("joins a hyphenated line break", () => {
    assert.equal(normalizeForComparison("extrac-\ntion"), "extraction");
  });

  it("does not join a hyphen that is not a line break", () => {
    assert.equal(normalizeForComparison("well-known"), "well-known");
  });

  it("normalizes ligatures", () => {
    assert.equal(normalizeForComparison("\uFB01nding"), "finding");
    assert.equal(normalizeForComparison("\uFB02ow"), "flow");
  });

  it("normalizes smart quotes and dashes", () => {
    assert.equal(normalizeForComparison("\u201Cquoted\u201D"), '"quoted"');
    assert.equal(normalizeForComparison("a\u2014b"), "a-b");
  });

  it("normalizes non-breaking spaces", () => {
    assert.equal(normalizeForComparison("a\u00A0b"), "a b");
  });

  it("is idempotent", () => {
    const once = normalizeForComparison("  A\u2014B \n C ");
    assert.equal(normalizeForComparison(once), once);
  });
});

describe("checkQuoteOnPage", () => {
  const sample = doc([
    "First page text that mentions the settlement figure.",
    "Second page says the court granted the motion in part.",
    "",
  ]);

  it("finds an exact quote on the right page", () => {
    const check = checkQuoteOnPage(sample, 1, "mentions the settlement figure");
    assert.equal(check.found, true);
    assert.equal(check.page, 1);
  });

  it("finds a quote split across a line break in the source", () => {
    const wrapped = doc(["the court granted\nthe motion in part"]);
    assert.equal(checkQuoteOnPage(wrapped, 1, "granted the motion").found, true);
  });

  it("rejects a quote on the wrong page", () => {
    const check = checkQuoteOnPage(sample, 2, "settlement figure");
    assert.equal(check.found, false);
    assert.match(check.reason ?? "", /not found/);
  });

  it("rejects a fabricated quote", () => {
    assert.equal(checkQuoteOnPage(sample, 1, "a sentence never written").found, false);
  });

  it("rejects page zero", () => {
    const check = checkQuoteOnPage(sample, 0, "First page");
    assert.equal(check.found, false);
    assert.match(check.reason ?? "", /outside/);
  });

  it("rejects a page past the end", () => {
    const check = checkQuoteOnPage(sample, 99, "First page");
    assert.equal(check.found, false);
    assert.match(check.reason ?? "", /outside/);
  });

  it("rejects an empty quote", () => {
    assert.equal(checkQuoteOnPage(sample, 1, "   ").found, false);
  });

  it("does not match across a page boundary", () => {
    const split = doc(["the settled amount", "was undisclosed"]);
    assert.equal(checkQuoteOnPage(split, 1, "amount was undisclosed").found, false);
  });

  it("is case sensitive", () => {
    assert.equal(checkQuoteOnPage(sample, 1, "MENTIONS THE SETTLEMENT FIGURE").found, false);
  });
});
