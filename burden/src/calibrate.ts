/**
 * Calibration — the second inversion.
 *
 * The failure mode says the system never calibrates: no error rate survives
 * the session, so the same breakdown returns mechanically. Here the number is
 * recomputed from the append-only ledger every time it is asked for. It has a
 * denominator. With no denominator it reports `UNMEASURED`, never 100%.
 *
 * Load-bearing failures are listed separately and are never averaged away.
 */

import type { LedgerEntry } from "./ledger.js";
import { TIERS, type Tier } from "./types.js";

export type TierStat = {
  readonly tier: Tier;
  readonly audited: number;
  readonly verified: number;
  readonly falsified: number;
  /** Falsification rate in percent, or null when nothing was audited. */
  readonly ratePercent: number | null;
};

export type Calibration = {
  readonly audited: number;
  readonly verified: number;
  readonly falsified: number;
  readonly unmeasured: number;
  readonly falsificationRatePercent: number | null;
  readonly byTier: readonly TierStat[];
  readonly loadBearingFailures: readonly string[];
};

function ratePercent(falsified: number, audited: number): number | null {
  if (audited === 0) return null;
  return Math.round((falsified * 1000) / audited) / 10;
}

/**
 * `audited` counts measured checks only: verified plus falsified. An
 * `unmeasured` verdict is recorded, and it is not a measurement.
 */
export function calibrate(entries: readonly LedgerEntry[]): Calibration {
  let verified = 0;
  let falsified = 0;
  let unmeasured = 0;
  const loadBearingFailures: string[] = [];
  const perTier = new Map<Tier, { verified: number; falsified: number }>();

  for (const tier of TIERS) {
    perTier.set(tier, { verified: 0, falsified: 0 });
  }

  for (const entry of entries) {
    const receipt = entry.receipt;
    const bucket = perTier.get(receipt.tier);
    if (bucket === undefined) continue;

    if (receipt.verdict.kind === "verified") {
      verified += 1;
      bucket.verified += 1;
    } else if (receipt.verdict.kind === "falsified") {
      falsified += 1;
      bucket.falsified += 1;
      if (receipt.bearing === "load_bearing") {
        loadBearingFailures.push(receipt.claimId);
      }
    } else {
      unmeasured += 1;
    }
  }

  const byTier: TierStat[] = [];
  for (const tier of TIERS) {
    const bucket = perTier.get(tier);
    if (bucket === undefined) continue;
    const audited = bucket.verified + bucket.falsified;
    byTier.push({
      tier,
      audited,
      verified: bucket.verified,
      falsified: bucket.falsified,
      ratePercent: ratePercent(bucket.falsified, audited),
    });
  }

  const audited = verified + falsified;
  return {
    audited,
    verified,
    falsified,
    unmeasured,
    falsificationRatePercent: ratePercent(falsified, audited),
    byTier,
    loadBearingFailures: [...loadBearingFailures].sort(),
  };
}

function percent(value: number | null): string {
  return value === null ? "UNMEASURED" : `${value.toFixed(1)}%`;
}

/** Deterministic text. No timestamps: the ledger carries those. */
export function renderCalibration(calibration: Calibration): string {
  const lines: string[] = [];
  lines.push("calibration — recomputed from the ledger, not remembered");
  lines.push(
    `  audited: ${calibration.audited}  verified: ${calibration.verified}  falsified: ${calibration.falsified}  unmeasured: ${calibration.unmeasured}`,
  );
  lines.push(
    `  falsification rate: ${percent(calibration.falsificationRatePercent)} (denominator ${calibration.audited})`,
  );
  lines.push("  by tier:");
  for (const stat of calibration.byTier) {
    if (stat.audited === 0) {
      lines.push(`    ${stat.tier.padEnd(16)} UNMEASURED (denominator 0)`);
      continue;
    }
    lines.push(
      `    ${stat.tier.padEnd(16)} audited ${stat.audited}  falsified ${stat.falsified}  rate ${percent(stat.ratePercent)}`,
    );
  }
  if (calibration.loadBearingFailures.length === 0) {
    lines.push("  load-bearing failures: none recorded");
  } else {
    lines.push(`  load-bearing failures: ${calibration.loadBearingFailures.join(", ")}`);
  }
  return lines.join("\n");
}
