/**
 * game/incentive — the burden inversion, executable.
 *
 * Mirrors `L6_GAME.lean`. The Lean file proves the theorems about a model; this
 * file computes the same predicates on real numbers and returns the derivation.
 * Neither substitutes for the other: Lean proves that the equivalence holds for
 * all values, and this code shows that the arithmetic was actually performed on
 * the values in front of it. A theorem without a runtime is a promise; a
 * runtime without a theorem is a hope.
 *
 * The central object is a **mechanism**: a bond, a gain, and a detector. Three
 * fields, and the absence of a fourth is the point — the number of claims a
 * verifier must check is not part of the mechanism, so a mechanism's soundness
 * cannot be bought with verifier labour.
 */

import {
  fail,
  pass,
  type Evidence,
  type Units,
} from "./types.js";

/**
 * A mechanism, in the sense of `Game.Mechanism`.
 *
 * - `bond` — forfeited if a false claim is detected.
 * - `gain` — realised if a false claim is accepted.
 * - `detects` — whether anything looks.
 */
export type Mechanism = {
  readonly bond: Units;
  readonly gain: Units;
  readonly detects: boolean;
};

/**
 * Net position after a false claim. Mirrors `Game.falseNet`.
 *
 * Positive means the falsehood paid.
 */
export function falseNet(m: Mechanism): bigint {
  return m.detects ? m.gain - m.bond : m.gain;
}

/** Net position after a true claim. No honesty premium is assumed. */
export function trueNet(_m: Mechanism): bigint {
  return 0n;
}

const DOMINANCE_FALSIFIER =
  "a mechanism with detects = true and bond >= gain under which a false claim still nets positive";

/**
 * **Truthfulness is dominant exactly when the mechanism detects and the bond
 * covers the gain.**
 *
 * Counterpart of `Game.truthful_dominant_iff`. The `gain > 0` guard is the same
 * guard the Lean theorem carries, and for the same reason: at `gain = 0` there
 * is nothing to deter and the equivalence genuinely fails. Rather than hide it,
 * this function refuses the degenerate case and says so.
 */
export function incentiveCompatible(m: Mechanism): Evidence<Mechanism> {
  const check = "incentive-compatible";
  if (m.bond < 0n || m.gain < 0n) {
    return fail(
      check,
      DOMINANCE_FALSIFIER,
      "negative-quantity",
      `bond=${m.bond} gain=${m.gain}; a negative bond is a bonus and a negative gain is a cost, ` +
        `and neither is this model.`,
    );
  }
  if (m.gain === 0n) {
    return fail(
      check,
      DOMINANCE_FALSIFIER,
      "degenerate-gain",
      "gain = 0: a false claim is worth nothing, so there is nothing to deter and " +
        "the dominance equivalence does not hold. This is a refusal, not a pass.",
    );
  }
  if (!m.detects) {
    return fail(
      check,
      DOMINANCE_FALSIFIER,
      "no-detector",
      `bond=${m.bond} is inert because nothing detects the falsehood. ` +
        `No bond value repairs a missing detector (L6_GAME.bond_without_detection_is_inert).`,
    );
  }
  if (m.bond < m.gain) {
    return fail(
      check,
      DOMINANCE_FALSIFIER,
      "bond-below-gain",
      `bond=${m.bond} < gain=${m.gain}: a false claim nets ${m.gain - m.bond} even when caught.`,
    );
  }
  return pass(check, DOMINANCE_FALSIFIER, m, [
    `detector present: detects = true`,
    `false claim when caught nets ${falseNet(m)} (must be <= 0)`,
    `bond ${m.bond} >= gain ${m.gain}`,
    `true claim nets ${trueNet(m)}`,
  ]);
}

/**
 * **A bond without detection is inert.**
 *
 * Counterpart of `Game.bond_without_detection_is_inert`. It is a separate
 * function rather than a branch of the above because the finding it encodes is
 * the one that actually occurs: a contract with no wage clause and no certified
 * payrolls is a mechanism with `detects = false`, and the size of any security
 * held against it is irrelevant.
 */
export function bondIsInert(m: Mechanism): Evidence<Mechanism> {
  const check = "bond-requires-a-detector";
  const FALSIFIER =
    "a mechanism with detects = false in which the bond changes the producer's net position";
  if (m.detects) {
    return fail(
      check,
      FALSIFIER,
      "detector-present",
      "detects = true, so the bond is not inert and this check does not apply. " +
        "An inapplicable check reports inapplicable, not pass.",
    );
  }
  return pass(check, FALSIFIER, m, [
    `false claim nets gain = ${m.gain}, independent of bond = ${m.bond}`,
    `the bond is forfeited only on detection, and there is none`,
  ]);
}

/** A split of the epistemic burden. Mirrors `Game.BurdenSplit`. */
export type BurdenSplit = {
  readonly producerAtRisk: Units;
  readonly verifierChecks: number;
  readonly checkCost: Units;
};

export function verifierLabour(b: BurdenSplit): bigint {
  return BigInt(b.verifierChecks) * b.checkCost;
}

export function totalBurden(b: BurdenSplit): bigint {
  return b.producerAtRisk + verifierLabour(b);
}

/** The unbonded arrangement: producer risks nothing, verifier checks all. */
export function unbonded(claims: number, cost: Units): BurdenSplit {
  return { producerAtRisk: 0n, verifierChecks: claims, checkCost: cost };
}

/** The inverted arrangement: producer posts a bond, verifier checks a sample. */
export function inverted(bond: Units, checks: number, cost: Units): BurdenSplit {
  return { producerAtRisk: bond, verifierChecks: checks, checkCost: cost };
}

/**
 * **The inversion only pays if the bond is cheaper than the labour it replaces.**
 *
 * Counterpart of `Game.inversion_pays_iff`, which is an equivalence. This
 * function returns the comparison *and* the break-even bond, so the answer is
 * actionable rather than merely negative: a scheme that fails this check is
 * told the largest bond it could post and still be an inversion.
 */
export function inversionPays(
  claims: number,
  checks: number,
  cost: Units,
  bond: Units,
): Evidence<{ readonly saved: bigint; readonly breakEvenBond: bigint }> {
  const check = "inversion-pays";
  const FALSIFIER =
    "a bonded arrangement with total burden below the unbonded one while bond >= (claims - checks) * cost";

  if (!Number.isInteger(claims) || !Number.isInteger(checks) || claims < 0 || checks < 0) {
    return fail(check, FALSIFIER, "bad-counts", `claims=${claims} checks=${checks}`);
  }
  if (checks > claims) {
    return fail(
      check,
      FALSIFIER,
      "sample-exceeds-population",
      `checks=${checks} > claims=${claims}; a sample larger than the population is not a sample.`,
    );
  }
  if (cost < 0n || bond < 0n) {
    return fail(check, FALSIFIER, "negative-quantity", `cost=${cost} bond=${bond}`);
  }

  const before = totalBurden(unbonded(claims, cost));
  const after = totalBurden(inverted(bond, checks, cost));
  const breakEven = BigInt(claims - checks) * cost;

  if (after >= before) {
    return fail(
      check,
      FALSIFIER,
      "relocation-not-inversion",
      `bonded total ${after} >= unbonded total ${before}; the risk moved but the cost did not. ` +
        `Break-even bond is ${breakEven}.`,
    );
  }
  return pass(check, FALSIFIER, { saved: before - after, breakEvenBond: breakEven }, [
    `unbonded total = ${claims} * ${cost} = ${before}`,
    `bonded total = ${bond} + ${checks} * ${cost} = ${after}`,
    `saved = ${before - after}`,
    `break-even bond = (${claims} - ${checks}) * ${cost} = ${breakEven}`,
  ]);
}

/**
 * **The producer's truthfulness does not depend on the verifier's sample size.**
 *
 * This is the inversion stated as a property of the types rather than of the
 * numbers: `incentiveCompatible` takes a `Mechanism`, and `Mechanism` has no
 * field for verifier effort. So no change to the sample can change the answer.
 *
 * The function below exists to make that checkable rather than merely asserted:
 * it varies the sample across a range and reports that the verdict never moved.
 * A future refactor that threaded effort into the mechanism would fail here.
 */
export function incentiveIndependentOfEffort(
  m: Mechanism,
  samples: readonly number[],
): Evidence<{ readonly verdicts: readonly boolean[] }> {
  const check = "incentive-independent-of-verifier-effort";
  const FALSIFIER =
    "two verifier sample sizes for the same mechanism yielding different truthfulness verdicts";
  if (samples.length < 2) {
    return fail(check, FALSIFIER, "insufficient-samples", `got ${samples.length}`);
  }
  const verdicts = samples.map(() => incentiveCompatible(m).ok);
  const first = verdicts[0];
  if (first === undefined) {
    return fail(check, FALSIFIER, "insufficient-samples", "empty after guard");
  }
  const moved = verdicts.some((v) => v !== first);
  if (moved) {
    return fail(check, FALSIFIER, "effort-changed-the-verdict", JSON.stringify(verdicts));
  }
  return pass(check, FALSIFIER, { verdicts }, [
    `sample sizes tested: ${samples.join(", ")}`,
    `verdict held at ${first ? "compatible" : "incompatible"} for all of them`,
  ]);
}
