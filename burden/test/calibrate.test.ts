/**
 * Calibration must never produce a number without a denominator.
 * This is the second inversion, and it is checked the same way as the first.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { admitOrThrow } from "../src/audit.js";
import { calibrate, renderCalibration } from "../src/calibrate.js";
import type { LedgerEntry } from "../src/ledger.js";
import type {
  Bearing,
  Environment,
  Receipt,
  Tier,
  Verdict,
} from "../src/types.js";

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

function receipt(args: {
  readonly claimId: string;
  readonly tier: Tier;
  readonly kind: Verdict;
  readonly bearing: Bearing;
  readonly code: string;
}): Receipt {
  return admitOrThrow({
    schema: "burden.receipt/1",
    claimId: args.claimId,
    claim: "a calibration test claim",
    bearing: args.bearing,
    checkability: "machine_checkable",
    missingMeasurement: null,
    tier: args.tier,
    source: { path: "x.txt", sha256: "a".repeat(64), bytes: 1 },
    derivation: [{ check: "span_exact", ok: true, detail: "checked" }],
    falsifier: { command: "burden audit", refutes: "the span is absent" },
    owner: { actor: "calibration-test", tool: "burden/test", environment: ENV },
    verdict: { kind: args.kind, code: args.code, detail: "recorded" },
  });
}

function entry(seq: number, value: Receipt): LedgerEntry {
  return {
    seq,
    recordedAtUtc: "2026-10-24T09:00:00.000Z",
    prev: "0".repeat(64),
    receipt: value,
    entrySha256: "b".repeat(64),
  };
}

test("an empty ledger reports UNMEASURED, not 100%", () => {
  const calibration = calibrate([]);
  assert.equal(calibration.audited, 0);
  assert.equal(calibration.falsificationRatePercent, null);
  const text = renderCalibration(calibration);
  assert.ok(text.includes("falsification rate: UNMEASURED (denominator 0)"));
  assert.ok(!text.includes("100.0%"));
});

test("the rate is falsified over audited, with a denominator", () => {
  const entries = [
    entry(
      0,
      receipt({
        claimId: "CLM-CAL-1",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
    ),
    entry(
      1,
      receipt({
        claimId: "CLM-CAL-2",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
    ),
    entry(
      2,
      receipt({
        claimId: "CLM-CAL-3",
        tier: "unverified",
        kind: "falsified",
        bearing: "supporting",
        code: "SPAN_NOT_FOUND",
      }),
    ),
  ];
  const calibration = calibrate(entries);
  assert.equal(calibration.audited, 3);
  assert.equal(calibration.verified, 2);
  assert.equal(calibration.falsified, 1);
  assert.equal(calibration.falsificationRatePercent, 33.3);
  const fetched = calibration.byTier.find((stat) => stat.tier === "fetched");
  assert.equal(fetched?.audited, 2);
  assert.equal(fetched?.falsified, 0);
});

test("unmeasured verdicts are recorded but are not measurements", () => {
  const calibration = calibrate([
    entry(
      0,
      receipt({
        claimId: "CLM-CAL-4",
        tier: "unverified",
        kind: "unmeasured",
        bearing: "supporting",
        code: "NOT_RUN",
      }),
    ),
  ]);
  assert.equal(calibration.unmeasured, 1);
  assert.equal(calibration.audited, 0);
  assert.equal(calibration.falsificationRatePercent, null);
});

test("an empty-checked claim never enters the denominator", () => {
  // The regression this pins: an investigator run against an empty corpus used
  // to record `falsified`, which calibrate counted as an audited check and
  // reported as a confident 100%. A rate over nothing is the exact failure the
  // package exists to invert.
  const calibration = calibrate([
    entry(
      0,
      receipt({
        claimId: "CLM-CAL-7",
        tier: "unverified",
        kind: "unmeasured",
        bearing: "load_bearing",
        code: "NO_SOURCES_SCANNED",
      }),
    ),
  ]);
  assert.equal(calibration.audited, 0);
  assert.equal(calibration.falsificationRatePercent, null);
  assert.equal(calibration.unmeasured, 1);
  assert.ok(renderCalibration(calibration).includes("UNMEASURED"));
});

test("load-bearing failures are listed, never averaged away", () => {
  const calibration = calibrate([
    entry(
      0,
      receipt({
        claimId: "CLM-CAL-5",
        tier: "unverified",
        kind: "falsified",
        bearing: "load_bearing",
        code: "SPAN_NOT_FOUND",
      }),
    ),
    entry(
      1,
      receipt({
        claimId: "CLM-CAL-6",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
    ),
  ]);
  assert.deepEqual(calibration.loadBearingFailures, ["CLM-CAL-5"]);
  assert.ok(renderCalibration(calibration).includes("CLM-CAL-5"));
});

test("a load-bearing failure is reported as critical, not as routine", () => {
  // The third inversion: weight is a function of bearing and verdict, so a
  // critical failure cannot be filed with the same passive neutrality as a
  // trivial one.
  const calibration = calibrate([
    entry(
      0,
      receipt({
        claimId: "CLM-W-1",
        tier: "unverified",
        kind: "falsified",
        bearing: "illustrative",
        code: "SPAN_NOT_FOUND",
      }),
    ),
    entry(
      1,
      receipt({
        claimId: "CLM-W-2",
        tier: "unverified",
        kind: "falsified",
        bearing: "load_bearing",
        code: "SPAN_NOT_FOUND",
      }),
    ),
  ]);

  assert.deepEqual(
    calibration.weightedFailures.map((failure) => [failure.claimId, failure.severity]),
    [
      ["CLM-W-2", "critical"],
      ["CLM-W-1", "minor"],
    ],
  );
  // Weights do not cancel: one critical plus one minor is 4, not 0.
  assert.equal(calibration.failureWeight, 4);
  const rendered = renderCalibration(calibration);
  assert.ok(rendered.includes("CRITICAL CLM-W-2"));
  assert.ok(rendered.includes("MINOR    CLM-W-1"));
});

test("an unmeasured entry carries no failure weight", () => {
  const calibration = calibrate([
    entry(
      0,
      receipt({
        claimId: "CLM-W-3",
        tier: "unverified",
        kind: "unmeasured",
        bearing: "load_bearing",
        code: "NO_SOURCES_SCANNED",
      }),
    ),
  ]);
  assert.equal(calibration.failureWeight, 0);
  assert.deepEqual(calibration.weightedFailures, []);
});
