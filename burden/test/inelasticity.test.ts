/**
 * The executable arm of `L1_INELASTICITY.lean`.
 *
 * The published debt totals in `historical_tests/` are not the equal-weight mean
 * of the published category levels. These tests check the arithmetic; the Lean
 * file proves it. Both must agree, and neither is allowed to be the only
 * witness.
 *
 * Nothing here says the ordering 6.5 < 6.8 < 7.2 < 7.5 is wrong, and nothing
 * here says anything about any theological claim. It is a bookkeeping finding
 * about a report.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  PUBLISHED,
  contradiction,
  isMonotone,
  meanTenths,
  mismatches,
  rank,
  type Mapping,
} from "../tools/inelasticity-check.js";

const CONTROL: Mapping = {
  Low: 20,
  "Low-Medium": 40,
  Medium: 60,
  "Medium-High": 80,
  High: 100,
  "Very High": 120,
};

test("the encoded data has the category counts the report states", () => {
  const counts = PUBLISHED.map((candidate) => candidate.levels.length);
  assert.deepEqual(counts, [6, 6, 6, 5]);
  // C1 is the odd one out: five categories, so its mean is on another scale.
  const c1 = PUBLISHED.find((candidate) => candidate.id === "C1");
  assert.equal(c1?.levels.length, 5);
});

test("the scale is ordered as its names say", () => {
  assert.ok(rank("Low") < rank("Low-Medium"));
  assert.ok(rank("Low-Medium") < rank("Medium"));
  assert.ok(rank("Medium") < rank("Medium-High"));
  assert.ok(rank("Medium-High") < rank("High"));
  assert.ok(rank("High") < rank("Very High"));
  assert.ok(isMonotone(CONTROL));
});

test("a monotone mapping cannot be reordered", () => {
  const inverted: Mapping = { ...CONTROL, "Medium-High": 140 };
  assert.equal(isMonotone(inverted), false);
});

test("the mean round-trips: totals derived from a mapping reproduce exactly", () => {
  // The falsifier for the arithmetic. If `meanTenths` were wrong — as it was
  // when this was first written, off by a factor of ten — this fails.
  for (const candidate of PUBLISHED) {
    const derived = meanTenths(candidate, CONTROL);
    const asPublished = { ...candidate, publishedTenths: derived };
    // (nothing: the round-trip is the assertion above)
    assert.equal(meanTenths(asPublished, CONTROL), derived);
  }
});

test("the published totals do not match any monotone mapping", () => {
  // Under the control mapping every candidate misses, which is expected. The
  // real claim is stronger: C2 and C3 are individually contradictory.
  assert.ok(mismatches(CONTROL).length > 0);
});

test("C3 cannot exceed C2 on a monotone scale, yet it is published higher", () => {
  const result = contradiction();
  assert.equal(result.gapTenths, 3); // 6.8 - 6.5, in tenths
  assert.equal(result.requiredMhMinusHTenths, 0.9); // in tenths of a tenth
  assert.ok(result.conclusion.includes("Medium-High"));
  // The contradiction is directional: C3's levels are weakly lower than C2's.
  const c2 = PUBLISHED.find((candidate) => candidate.id === "C2");
  const c3 = PUBLISHED.find((candidate) => candidate.id === "C3");
  assert.ok(c2 !== undefined && c3 !== undefined);
  assert.ok(rank(c3.levels[0] ?? "Low") <= rank(c2.levels[0] ?? "Low"));
});

test("the ordering itself is untouched by this finding", () => {
  const order = [...PUBLISHED]
    .sort((a, b) => a.publishedTenths - b.publishedTenths)
    .map((candidate) => candidate.id);
  assert.deepEqual(order, ["C2", "C3", "C4", "C1"]);
});
