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
