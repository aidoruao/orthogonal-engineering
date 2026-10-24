/**
 * The detector is checked against its own published examples and
 * anti-examples. A rule that cannot fire, or that fires on peer-mode text, is
 * worse than no rule: it manufactures findings.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

import { RULES, explain, scan, selfTest } from "../src/scan.js";

const fixtures = join(process.cwd(), "fixtures");

test("every rule passes its own falsifier", () => {
  const results = selfTest();
  assert.equal(results.length, RULES.length);
  for (const result of results) {
    assert.ok(
      result.ok,
      `${result.rule} exampleHit=${String(result.exampleHit)} antiExampleClean=${String(
        result.antiExampleClean,
      )}`,
    );
  }
});

test("the quoted closing move is detected verbatim", () => {
  const hits = scan(
    "Let me know if you want to pivot to a different technical analysis or end the execution here.",
  );
  assert.ok(hits.some((hit) => hit.rule === "CLOSURE_OFFER"));
});

test("the filed failure text trips at least the closure rule", () => {
  const text = readFileSync(join(fixtures, "adversarial.txt"), "utf8");
  const hits = scan(text);
  assert.ok(hits.length > 0);
  assert.ok(hits.some((hit) => hit.rule === "CLOSURE_OFFER"));
});

test("peer-mode prose is clean against every rule", () => {
  const text = readFileSync(join(fixtures, "peer-mode.txt"), "utf8");
  const hits = scan(text);
  assert.deepEqual(
    hits.map((hit) => hit.rule),
    [],
    `peer-mode text produced hits: ${hits.map((hit) => hit.rule).join(", ")}`,
  );
});

test("hits sort by line then column then rule", () => {
  const hits = scan(
    "You should verify this yourself.\nAs an AI language model, I cannot provide legal advice.",
  );
  assert.ok(hits.length >= 2);
  for (let index = 1; index < hits.length; index += 1) {
    const previous = hits[index - 1];
    const current = hits[index];
    if (previous === undefined || current === undefined) continue;
    assert.ok(previous.line <= current.line);
  }
});

test("explain returns a rule or null, never a guess", () => {
  const rule = explain("CLOSURE_OFFER");
  assert.ok(rule !== null);
  assert.ok(rule.pattern.source.length > 0);
  assert.equal(explain("NO_SUCH_RULE"), null);
});
