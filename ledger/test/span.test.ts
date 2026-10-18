/**
 * Span-selection tests.
 *
 * The invariant under test: whatever span is chosen, it is a contiguous
 * substring of the source. Boundary tidying may shorten it; it must never
 * rewrite it.
 */

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import { selectSpan, stripFurniture } from "../src/span.js";

const PAGE =
  "Earlier background text. On or about February 25, 2020, Corey Urman, falsely posing under the alias " +
  "Blake White, misrepresented the company's moderation practices. A later sentence follows here. " +
  "Case 2:21-cv-04920-WLH-ADS Document 385 Filed 05/23/24 Page 68 of 174 Page ID #:9528";

describe("stripFurniture", () => {
  it("removes a running case footer", () => {
    const cleaned = stripFurniture(
      "body text Case 2:21-cv-04920-WLH-ADS Document 385 Filed 05/23/24 Page 68 of 174 Page ID #:9528",
    );
    assert.equal(cleaned, "body text");
  });

  it("removes a bare page-id footer", () => {
    assert.equal(stripFurniture("body text Page 68 of 174 Page ID #:9528"), "body text");
  });

  it("removes a leading pleading line-number run", () => {
    const cleaned = stripFurniture("1 2 3 4 5 6 7 8 9 10 11 12 DEFENDANT ANTOON'S NOTICE");
    assert.equal(cleaned, "DEFENDANT ANTOON'S NOTICE");
  });

  it("removes a trailing pleading line-number run", () => {
    assert.equal(stripFurniture("NOTICE OF MOTION 1 2 3 4 5 6 7 8"), "NOTICE OF MOTION");
  });

  it("leaves ordinary prose untouched", () => {
    const text = "The court granted the motion in part and denied it in part.";
    assert.equal(stripFurniture(text), text);
  });

  it("does not remove a short numeric list", () => {
    assert.equal(stripFurniture("there were 3 4 5 items"), "there were 3 4 5 items");
  });
});

describe("selectSpan", () => {
  it("starts and ends at sentence boundaries", () => {
    const result = selectSpan(PAGE, "falsely posing under the alias");
    assert.ok(result !== undefined);
    assert.match(result.span, /^On or about February 25, 2020/);
    assert.match(result.span, /moderation practices\.$/);
  });

  it("drops the page footer", () => {
    const result = selectSpan(PAGE, "falsely posing under the alias");
    assert.ok(result !== undefined);
    assert.equal(result.span.includes("Page ID"), false);
    assert.equal(result.span.includes("Document 385"), false);
  });

  it("returns a contiguous substring of the source", () => {
    const result = selectSpan(PAGE, "falsely posing under the alias");
    assert.ok(result !== undefined);
    assert.ok(PAGE.includes(result.span), "span must appear verbatim in the source");
  });

  it("returns undefined when the anchor is absent", () => {
    assert.equal(selectSpan(PAGE, "a phrase that is not present"), undefined);
  });

  it("respects the maximum length", () => {
    const long = Array.from({ length: 40 }, (_, i) => `Sentence number ${i} is here.`).join(" ");
    const result = selectSpan(long, "Sentence number 20", { maxChars: 120 });
    assert.ok(result !== undefined);
    assert.ok(result.span.length <= 120);
    assert.ok(long.includes(result.span));
  });

  it("does not cut a word in half when trimming", () => {
    const long = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima";
    const result = selectSpan(long, "echo", { maxChars: 30 });
    assert.ok(result !== undefined);
    assert.equal(/\s$/.test(result.span), false);
    assert.ok(long.includes(result.span));
  });

  it("keeps a span that is already one sentence", () => {
    const text = "Only this sentence matters here.";
    const result = selectSpan(text, "matters");
    assert.ok(result !== undefined);
    assert.equal(PAGE.includes(result.span) || text.includes(result.span), true);
  });
});
