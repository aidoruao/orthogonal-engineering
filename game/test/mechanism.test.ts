/**
 * Tests for the mechanism half: `incentive.ts` and `covenant.ts`.
 *
 * Every invariant is tested twice — once where it holds, and once where it is
 * *refuted and the refusal is the correct outcome*. A check that has only ever
 * passed is indistinguishable from a check that does nothing, which is the
 * whole of the arc's complaint about confident output.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  bondIsInert,
  falseNet,
  incentiveCompatible,
  incentiveIndependentOfEffort,
  inverted,
  inversionPays,
  totalBurden,
  unbonded,
  type Mechanism,
} from "../src/incentive.js";

import {
  applyGrace,
  classifyClaim,
  excuseChain,
  isBalanced,
  isInsolvent,
  settle,
  type Settlement,
} from "../src/covenant.js";

/* ---------------------------------------------------------------- incentive */

test("bond >= gain with a detector is incentive compatible", () => {
  const m: Mechanism = { bond: 100n, gain: 100n, detects: true };
  const e = incentiveCompatible(m);
  assert.equal(e.ok, true);
  assert.equal(falseNet(m), 0n);
  assert.ok(e.ok && e.derivation.length >= 4);
});

test("bond below gain is refused, and the shortfall is named", () => {
  const m: Mechanism = { bond: 99n, gain: 100n, detects: true };
  const e = incentiveCompatible(m);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "bond-below-gain");
  assert.match(e.detail, /nets 1/);
});

test("no detector: the bond is inert and no bond value repairs it", () => {
  // The point of the test is that the bond is large and still irrelevant.
  const m: Mechanism = { bond: 1_000_000_000n, gain: 1n, detects: false };
  assert.equal(falseNet(m), 1n);
  const inert = bondIsInert(m);
  assert.equal(inert.ok, true);

  const refused = incentiveCompatible(m);
  assert.equal(refused.ok, false);
  if (refused.ok) return;
  assert.equal(refused.failed, "no-detector");
});

test("bondIsInert refuses to report on a mechanism that has a detector", () => {
  // An inapplicable check reports inapplicable, not pass. Otherwise "bond is
  // inert" could be cited for a mechanism where it is not even in question.
  const e = bondIsInert({ bond: 5n, gain: 1n, detects: true });
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "detector-present");
});

test("degenerate gain is refused rather than treated as compatible", () => {
  const e = incentiveCompatible({ bond: 0n, gain: 0n, detects: true });
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "degenerate-gain");
});

test("incentive does not depend on verifier effort", () => {
  const m: Mechanism = { bond: 10n, gain: 10n, detects: true };
  const e = incentiveIndependentOfEffort(m, [1, 10, 1_000, 1_000_000]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.deepEqual(e.value.verdicts, [true, true, true, true]);
});

test("the effort-independence check refuses a single sample", () => {
  const e = incentiveIndependentOfEffort({ bond: 1n, gain: 1n, detects: true }, [1]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "insufficient-samples");
});

test("inversion pays only when the bond is below the labour it replaces", () => {
  // 1000 claims, 10 checked, 3 per check: labour 3000. Break-even bond 2970.
  const good = inversionPays(1000, 10, 3n, 0n);
  assert.equal(good.ok, true);
  if (!good.ok) return;
  assert.equal(good.value.breakEvenBond, 2970n);
  assert.equal(good.value.saved, 2970n);

  // Exactly at break-even the totals are equal, so nothing is saved.
  const boundary = inversionPays(1000, 10, 3n, 2970n);
  assert.equal(boundary.ok, false);
  if (boundary.ok) return;
  assert.equal(boundary.failed, "relocation-not-inversion");
  assert.match(boundary.detail, /2970/);

  // One unit more and it is a relocation, not an inversion.
  const bad = inversionPays(1000, 10, 3n, 2971n);
  assert.equal(bad.ok, false);
  if (bad.ok) return;
  assert.equal(bad.failed, "relocation-not-inversion");
});

test("a sample larger than the population is refused", () => {
  const e = inversionPays(10, 11, 1n, 0n);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "sample-exceeds-population");
});

test("total burden arithmetic matches the Lean model", () => {
  assert.equal(totalBurden(unbonded(100, 5n)), 500n);
  assert.equal(totalBurden(inverted(50n, 10, 5n)), 100n);
});

/* ----------------------------------------------------------------- covenant */

test("solvent debtor pays in full: self-paid, no third party needed", () => {
  const s: Settlement = {
    account: { debt: 10n, capacity: 40n },
    byViolator: 10n,
    byOther: 0n,
  };
  assert.equal(isInsolvent(s.account), false);
  const e = settle(s);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "self_paid");
});

test("insolvent debtor, balanced ledger: substitution is forced and reported", () => {
  const s: Settlement = {
    account: { debt: 10n, capacity: 3n },
    byViolator: 3n,
    byOther: 7n,
  };
  assert.equal(isInsolvent(s.account), true);
  assert.equal(isBalanced(s), true);
  const e = settle(s);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "substitution");
  if (e.value.kind !== "substitution") return;
  assert.equal(e.value.paidByOther, 7n);
  assert.equal(e.value.shortfall, 7n);
});

test("insolvent debtor with no third party: the ledger stays open", () => {
  const s: Settlement = {
    account: { debt: 10n, capacity: 3n },
    byViolator: 3n,
    byOther: 0n,
  };
  const e = settle(s);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "open");
  if (e.value.kind !== "open") return;
  assert.equal(e.value.remaining, 7n);
});

test("paying more than capacity is refused, not silently classified", () => {
  const s: Settlement = {
    account: { debt: 10n, capacity: 3n },
    byViolator: 10n,
    byOther: 0n,
  };
  const e = settle(s);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "infeasible");
});

test("negative quantities are refused", () => {
  const e = settle({
    account: { debt: 10n, capacity: 3n },
    byViolator: -1n,
    byOther: 0n,
  });
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "negative-quantity");
});

test("an understatement is never accurate", () => {
  const e = classifyClaim({ recorded: 100n, stated: 40n });
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "excuse");
  if (e.value.kind !== "excuse") return;
  assert.equal(e.value.understated, 60n);
});

test("an idle claim costs nothing and is not an excuse", () => {
  const e = classifyClaim({ recorded: 0n, stated: 0n });
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "accurate");

  const idle = classifyClaim({ recorded: 0n, stated: 0n });
  assert.equal(idle.ok, true);
});

test("a claim above the record is a different falsehood, not an excuse", () => {
  const e = classifyClaim({ recorded: 10n, stated: 30n });
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "inflates");
});

test("excuses compound: no finite chain discharges", () => {
  const e = excuseChain(100n, 5, 1n);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.growth, 5n);
  assert.equal(e.value.finalDebt, 105n);
  // Strictly greater than the debt it was meant to answer.
  assert.ok(e.value.finalDebt > 100n);
});

test("the excuse-chain check refuses a case it cannot exercise", () => {
  const zeroDebt = excuseChain(0n, 3, 1n);
  assert.equal(zeroDebt.ok, false);
  if (zeroDebt.ok) return;
  assert.equal(zeroDebt.failed, "no-growth");

  const zeroPenalty = excuseChain(100n, 3, 0n);
  assert.equal(zeroPenalty.ok, false);
});

test("grace changes byOther and never debt", () => {
  const base: Settlement = {
    account: { debt: 10n, capacity: 3n },
    byViolator: 3n,
    byOther: 0n,
  };
  const e = applyGrace({ base, supplied: 7n });
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.account.debt, 10n);
  assert.equal(e.value.byOther, 7n);
  assert.equal(isBalanced(e.value), true);
});

test("grace that does not cover leaves the ledger open, and says so", () => {
  const base: Settlement = {
    account: { debt: 10n, capacity: 3n },
    byViolator: 3n,
    byOther: 0n,
  };
  const e = applyGrace({ base, supplied: 2n });
  assert.equal(e.ok, true);
  if (!e.ok) return;
  // The function still succeeds — it applied grace correctly — but the ledger
  // does not balance, and the derivation records that rather than glossing it.
  assert.equal(isBalanced(e.value), false);
  assert.ok(e.derivation.some((d) => d.includes("still open")));
});
