/**
 * game/covenant — settlement, excuse, and the substitution theorem, executable.
 *
 * Mirrors `L5_COVENANT.lean`.
 *
 * The Lean file proves: an insolvent debtor whose ledger balances and who pays
 * within capacity did not pay the remainder. This file computes that, on the
 * actual figures, and refuses to record a settlement that claims otherwise.
 *
 * Two things are deliberately *not* modelled:
 *
 * - **Willingness.** It is not measurable here and a model that pretended to
 *   measure it would be the exact failure the arc documents: a confident number
 *   with no measurement behind it. `capacity` is means, not motive.
 * - **Guilt.** `Account` records what a ledger says is owed. Whether a person
 *   is guilty of anything is not a question a ledger can answer, and no
 *   function in this file returns such an answer.
 */

import { fail, pass, type Evidence, type Units } from "./types.js";

/** What the record says is owed, and what can actually be paid. */
export type Account = {
  readonly debt: Units;
  readonly capacity: Units;
};

/** Who paid what. The two streams are never summed at construction. */
export type Settlement = {
  readonly account: Account;
  readonly byViolator: Units;
  readonly byOther: Units;
};

export function isInsolvent(a: Account): boolean {
  return a.capacity < a.debt;
}

export function isFeasible(s: Settlement): boolean {
  return s.byViolator <= s.account.capacity;
}

/** **Justice** — every unit owed was paid by someone. */
export function isBalanced(s: Settlement): boolean {
  return s.account.debt <= s.byViolator + s.byOther;
}

/**
 * **Mercy** — the debtor's standing is restored.
 *
 * Deliberately the same predicate as `isBalanced`. This is the theorem
 * `cheap_mercy_is_uninhabited`: a restoration that leaves the ledger open is
 * not a restoration of this ledger but a different object, and there is no such
 * object in this model. Grace must therefore be a payment, not a waiver.
 */
export function isRestored(s: Settlement): boolean {
  return isBalanced(s);
}

/** Which of the three cases a settlement falls into. */
export type SettlementCase =
  /** The debtor covered it. No third party, and none needed. */
  | { readonly kind: "self_paid"; readonly paid: Units }
  /** The debtor is insolvent and another party covered the remainder. */
  | {
      readonly kind: "substitution";
      readonly paidByDebtor: Units;
      readonly paidByOther: Units;
      readonly shortfall: Units;
    }
  /** Nothing was settled. */
  | { readonly kind: "open"; readonly remaining: Units };

const SETTLE_FALSIFIER =
  "an insolvent debtor, within capacity, with a balanced ledger and no third-party payment";

/**
 * Classify a settlement.
 *
 * This is `L5_COVENANT.substitution_required` executed. The exhaustive case
 * analysis is not defensive style: the three branches are the trichotomy, and
 * the `open` branch is returned rather than thrown because an unsettled ledger
 * is a state of the world, not a programming error.
 */
export function settle(s: Settlement): Evidence<SettlementCase> {
  const check = "settle";
  if (s.byViolator < 0n || s.byOther < 0n || s.account.debt < 0n || s.account.capacity < 0n) {
    return fail(check, SETTLE_FALSIFIER, "negative-quantity", JSON.stringify(s, replacer));
  }
  if (!isFeasible(s)) {
    // An infeasible settlement is not a settlement. It is an overdraft, and it
    // is rejected here rather than silently classified.
    return fail(
      check,
      SETTLE_FALSIFIER,
      "infeasible",
      `byViolator=${s.byViolator} exceeds capacity=${s.account.capacity}: ` +
        `the debtor is being recorded as having paid what it does not have.`,
    );
  }
  if (!isBalanced(s)) {
    const remaining = s.account.debt - (s.byViolator + s.byOther);
    return pass(check, SETTLE_FALSIFIER, { kind: "open", remaining }, [
      `debt ${s.account.debt} > paid ${s.byViolator + s.byOther}`,
      `remaining ${remaining} — the ledger is open, so standing is not restored`,
    ]);
  }
  if (isInsolvent(s.account)) {
    // The substitution theorem, applied: insolvent + feasible + balanced
    // implies byOther > 0. The arithmetic is shown so the claim is auditable.
    const shortfall = s.account.debt - s.byViolator;
    if (s.byOther === 0n) {
      return fail(
        check,
        SETTLE_FALSIFIER,
        "substitution-theorem-violated",
        `debt=${s.account.debt} capacity=${s.account.capacity} byViolator=${s.byViolator} ` +
          `byOther=0 — unreachable if the arithmetic is sound. Reaching this line is a defect.`,
      );
    }
    return pass(
      check,
      SETTLE_FALSIFIER,
      {
        kind: "substitution",
        paidByDebtor: s.byViolator,
        paidByOther: s.byOther,
        shortfall,
      },
      [
        `insolvent: capacity ${s.account.capacity} < debt ${s.account.debt}`,
        `feasible: byViolator ${s.byViolator} <= capacity ${s.account.capacity}`,
        `balanced: debt ${s.account.debt} <= ${s.byViolator} + ${s.byOther}`,
        `therefore byOther ${s.byOther} > 0 — the remainder was paid by a non-debtor`,
      ],
    );
  }
  return pass(check, SETTLE_FALSIFIER, { kind: "self_paid", paid: s.byViolator }, [
    `solvent: debt ${s.account.debt} <= capacity ${s.account.capacity}`,
    `paid ${s.byViolator} from own means`,
    `byOther ${s.byOther} is not required by the arithmetic`,
  ]);
}

/** A claim about what is owed, against what the record says is owed. */
export type Claim = {
  readonly recorded: Units;
  readonly stated: Units;
};

export type ClaimVerdict =
  | { readonly kind: "accurate" }
  | { readonly kind: "excuse"; readonly understated: Units }
  | { readonly kind: "idle" }
  | { readonly kind: "inflates"; readonly overstated: Units };

const CLAIM_FALSIFIER =
  "a claim that understates the record and nevertheless matches it";

/**
 * Classify a claim.
 *
 * `excuse_is_false_or_idle` in Lean; here it is exhaustive. An understatement
 * is never accurate, and an idle claim is not an excuse. There is no fourth
 * branch, and the absence of one is the point: "excuse" is not a matter of tone
 * or sincerity, it is a relation between two numbers.
 */
export function classifyClaim(c: Claim): Evidence<ClaimVerdict> {
  const check = "classify-claim";
  if (c.recorded < 0n || c.stated < 0n) {
    return fail(check, CLAIM_FALSIFIER, "negative-quantity", JSON.stringify(c, replacer));
  }
  if (c.stated === c.recorded) {
    return pass(check, CLAIM_FALSIFIER, { kind: "accurate" }, [
      `stated ${c.stated} equals recorded ${c.recorded}`,
    ]);
  }
  if (c.stated < c.recorded) {
    if (c.recorded === 0n) {
      return pass(check, CLAIM_FALSIFIER, { kind: "idle" }, [
        `recorded 0: there is nothing owed, so the understatement is idle and costs nothing`,
      ]);
    }
    return pass(check, CLAIM_FALSIFIER, { kind: "excuse", understated: c.recorded - c.stated }, [
      `stated ${c.stated} < recorded ${c.recorded}`,
      `understated by ${c.recorded - c.stated}`,
      `an understatement is not an accuracy: it is a second entry against the record`,
    ]);
  }
  return pass(check, CLAIM_FALSIFIER, { kind: "inflates", overstated: c.stated - c.recorded }, [
    `stated ${c.stated} > recorded ${c.recorded}, overstated by ${c.stated - c.recorded}`,
    `this is a different falsehood and is not treated as an excuse`,
  ]);
}

/**
 * The cost of a chain of excuses.
 *
 * `L5_COVENANT.no_finite_excuse_chain_discharges` proves no finite chain reaches
 * zero. Here the growth is computed so the claim is visible: a chain of `n`
 * excuses costs `n * penalty` on top of the original debt, which is strictly
 * worse than the debt it was meant to answer.
 */
export function excuseChain(
  debt: Units,
  n: number,
  penalty: Units,
): Evidence<{ readonly finalDebt: Units; readonly growth: Units }> {
  const check = "excuse-chain";
  const FALSIFIER = "an excuse sequence that leaves the outstanding debt at or below its starting value";
  if (!Number.isInteger(n) || n < 0) {
    return fail(check, FALSIFIER, "bad-length", `n=${n}`);
  }
  if (penalty < 0n) {
    return fail(check, FALSIFIER, "negative-penalty", `penalty=${penalty}`);
  }
  if (debt <= 0n || (n > 0 && penalty <= 0n)) {
    return fail(
      check,
      FALSIFIER,
      "no-growth",
      `debt=${debt} penalty=${penalty}: the chain cannot be shown to grow, so the theorem ` +
        `is not being exercised. An inapplicable check reports inapplicable, not pass.`,
    );
  }
  const growth = BigInt(n) * penalty;
  return pass(check, FALSIFIER, { finalDebt: debt + growth, growth }, [
    `debt ${debt} plus ${n} excuses at ${penalty} each`,
    `growth ${growth} — strictly positive, so no finite chain discharges`,
    `final ${debt + growth} > initial ${debt}`,
  ]);
}

/**
 * Grace, as a settlement component.
 *
 * The distinction the Lean file proves is preserved here in the type: grace
 * supplies `byOther`. It never touches `debt`. A function that returned a
 * discounted `debt` would be a write-down, which is a different mechanism and
 * one that `cheap_mercy_is_uninhabited` forecloses.
 */
export type Grace = {
  readonly base: Settlement;
  readonly supplied: Units;
};

export function applyGrace(g: Grace): Evidence<Settlement> {
  const check = "apply-grace";
  const FALSIFIER = "a grace whose application lowers account.debt";
  if (g.supplied < 0n) {
    return fail(check, FALSIFIER, "negative-supply", `supplied=${g.supplied}`);
  }
  const applied: Settlement = {
    account: g.base.account,
    byViolator: g.base.byViolator,
    byOther: g.supplied,
  };
  if (applied.account.debt !== g.base.account.debt) {
    return fail(check, FALSIFIER, "debt-moved", `debt changed from ${g.base.account.debt}`);
  }
  return pass(check, FALSIFIER, applied, [
    `debt unchanged at ${applied.account.debt} — grace is not a write-down`,
    `byOther set to ${g.supplied}`,
    isBalanced(applied) ? `ledger balances` : `ledger still open — grace did not cover it`,
  ]);
}

/** JSON with bigints rendered exactly. Never `Number(bigint)`. */
function replacer(_key: string, value: unknown): unknown {
  return typeof value === "bigint" ? value.toString() : value;
}
