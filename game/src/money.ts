/**
 * game/money — where the money went, as a walk rather than an assertion.
 *
 * The standing instruction is a question, not a verdict: *where is the money
 * going, why, how, is it going appropriately to human beings, or is there
 * something shady.* A question phrased that way cannot be answered by a
 * summary. It can only be answered by a trace in which every unit is accounted
 * for at every step, and in which the steps that cannot be taken are named as
 * unmeasured rather than filled in.
 *
 * Four invariants, and each is checked rather than assumed:
 *
 * 1. **Conservation.** For every line, `allocated - spent = residual`, and over
 *    the whole budget `sum(allocated) = sum(spent) + sum(residual)`. Money does
 *    not vanish; if a caller supplies data that loses some, the arithmetic
 *    catches it.
 * 2. **An overrun requires an authority.** Spending above allocation without a
 *    recorded board action is a finding. This is not a moral claim: it is the
 *    difference between a variance and an unauthorised transfer.
 * 3. **A residual must be owned.** A non-zero residual with no named owner is a
 *    finding. Anonymous residual is where money goes when nobody is looking,
 *    and requiring the owner is the only thing that stops "other" from becoming
 *    a category.
 * 4. **No denominator, no rate.** A per-pupil or percentage figure computed with
 *    nothing underneath it is `unmeasured`. Mirrors `L1_BURDEN.ratePercent`:
 *    `ratePercent n 0 = none`. There is no vacuous 100%.
 *
 * The one thing this module refuses to do is infer. It reports what the records
 * say and where they stop. "Appropriate" and "shady" are conclusions a reader
 * draws from a complete trace; they are not fields on a record, and an
 * instrument that emitted them would be doing exactly what the arc objects to.
 */

import { fail, pass, type Evidence, type Units } from "./types.js";

/** How a line came to be allowed to spend what it spent. */
export type Authority =
  /** Within the adopted budget. No separate action was needed. */
  | { readonly kind: "within_budget" }
  /** Above the adopted budget, with a recorded board action. */
  | { readonly kind: "amended"; readonly reference: string; readonly recordedOn: string }
  /** Above the adopted budget, with nothing on record. */
  | { readonly kind: "none" };

export type BudgetLine = {
  /** The object code or account. Stable, not a label. */
  readonly code: string;
  /** Human-readable purpose. Never used as a key. */
  readonly label: string;
  readonly allocated: Units;
  readonly spent: Units;
  readonly authority: Authority;
  /**
   * Who or what holds the unspent remainder, when there is one.
   *
   * `undefined` means nobody has been named. That is a finding, not a default,
   * and it is the whole reason this field exists: an unowned residual is money
   * with no responsible party, and it is the most common place for a figure to
   * stop being traceable.
   */
  readonly residualOwner?: string;
};

export type MoneyFindingKind =
  | "overrun_without_authority"
  | "residual_unowned"
  | "negative_line"
  | "authority_not_recorded";

export type MoneyFinding = {
  readonly kind: MoneyFindingKind;
  readonly code: string;
  readonly amount: Units;
  readonly detail: string;
  /** What would make this finding wrong. Required, as everywhere in this package. */
  readonly falsifier: string;
};

export type MoneyTrace = {
  readonly lines: readonly BudgetLine[];
  readonly totalAllocated: Units;
  readonly totalSpent: Units;
  readonly totalResidual: Units;
  /** True only when conservation holds and no line produced a finding. */
  readonly closed: boolean;
  readonly findings: readonly MoneyFinding[];
};

const TRACE_FALSIFIER =
  "a trace reported as closed in which some unit is neither spent nor assigned an owner, or in which spending exceeded allocation with no recorded authority";

/**
 * Walk a budget and report every place it stops being traceable.
 *
 * Returns `ok: false` only for input that cannot be a budget at all — a
 * negative allocation, a duplicate code. A trace with findings is a *successful*
 * trace: it worked, and what it found is that the record has holes. Conflating
 * "the instrument failed" with "the account failed" would be the same error as
 * reporting a falsified claim as an unverified one.
 */
export function traceMoney(lines: readonly BudgetLine[]): Evidence<MoneyTrace> {
  const check = "trace-money";
  const seen = new Set<string>();
  for (const l of lines) {
    if (seen.has(l.code)) {
      return fail(
        check,
        TRACE_FALSIFIER,
        "duplicate-code",
        `object code "${l.code}" appears more than once. Two lines with one key means ` +
          `one of them is silently dropped when anything groups by code.`,
      );
    }
    seen.add(l.code);
    if (l.allocated < 0n || l.spent < 0n) {
      return fail(
        check,
        TRACE_FALSIFIER,
        "negative_line",
        `${l.code}: allocated=${l.allocated} spent=${l.spent}. A negative appropriation is a ` +
          `credit and belongs in a different account, not in this one.`,
      );
    }
  }

  const findings: MoneyFinding[] = [];
  let totalAllocated = 0n;
  let totalSpent = 0n;
  let totalResidual = 0n;

  for (const l of lines) {
    totalAllocated += l.allocated;
    totalSpent += l.spent;
    const residual = l.allocated - l.spent;
    totalResidual += residual;

    // 2. An overrun requires a recorded authority.
    //
    // The test is "is there a recorded amendment", not "which authority is
    // claimed". A line that claims `within_budget` while spending above its
    // allocation is not a line with authority — it is a line whose own record
    // contradicts itself, and the arithmetic wins.
    if (l.spent > l.allocated) {
      const overrun = l.spent - l.allocated;
      if (l.authority.kind === "within_budget") {
        findings.push({
          kind: "overrun_without_authority",
          code: l.code,
          amount: overrun,
          detail:
            `${l.label} spent ${l.spent} against ${l.allocated} allocated, ` +
            `${overrun} above, while its record claims the spend was within budget. ` +
            `Those two statements cannot both be true and no amendment is on record.`,
          falsifier:
            "a board minute, amendment, or resolution authorising the excess for this object code and period",
        });
      } else if (l.authority.kind === "none") {
        findings.push({
          kind: "overrun_without_authority",
          code: l.code,
          amount: overrun,
          detail:
            `${l.label} spent ${l.spent} against ${l.allocated} allocated, ` +
            `${overrun} above, with no recorded board action.`,
          falsifier:
            "a board minute, amendment, or resolution authorising the excess for this object code and period",
        });
      } else if (l.authority.reference.trim() === "") {
        findings.push({
          kind: "authority_not_recorded",
          code: l.code,
          amount: overrun,
          detail:
            `${l.label} claims an amendment for ${overrun} above allocation, but the ` +
            `reference is empty. An unnamed authority is not a record of one.`,
          falsifier: "a resolvable reference — minute number, date, and page — for the amendment",
        });
      }
    }

    // 3. A residual must be owned.
    if (residual > 0n && (l.residualOwner === undefined || l.residualOwner.trim() === "")) {
      findings.push({
        kind: "residual_unowned",
        code: l.code,
        amount: residual,
        detail:
          `${l.label} has ${residual} unspent and no named holder. ` +
          `Anonymous residual is where a figure stops being traceable.`,
        falsifier:
          "a named line, fund, or responsible officer to whom the remainder is assigned, " +
          "or a recorded return of the funds",
      });
    }

    // Conservation, per line. This cannot fail if the arithmetic above is used,
    // but it is asserted because the alternative is trusting the code to be
    // right about its own arithmetic.
    if (l.allocated !== l.spent + residual) {
      return fail(
        check,
        TRACE_FALSIFIER,
        "per-line-conservation",
        `${l.code}: allocated ${l.allocated} != spent ${l.spent} + residual ${residual}. ` +
          `Reaching this line is a defect in this module.`,
      );
    }
  }

  // Conservation, whole budget.
  if (totalAllocated !== totalSpent + totalResidual) {
    return fail(
      check,
      TRACE_FALSIFIER,
      "budget-conservation",
      `allocated ${totalAllocated} != spent ${totalSpent} + residual ${totalResidual}`,
    );
  }

  const trace: MoneyTrace = {
    lines,
    totalAllocated,
    totalSpent,
    totalResidual,
    closed: findings.length === 0,
    findings,
  };

  const derivation: string[] = [
    `${lines.length} object codes walked`,
    `allocated ${totalAllocated} = spent ${totalSpent} + residual ${totalResidual}`,
    findings.length === 0
      ? `no finding: every unit is either spent or owned, and every overrun has an authority`
      : `${findings.length} finding(s): ${findings.map((f) => f.kind).join(", ")}`,
  ];

  return pass(check, TRACE_FALSIFIER, trace, derivation);
}

export type RatioResult =
  | { readonly kind: "measured"; readonly value: Units; readonly denominator: Units }
  | { readonly kind: "unmeasured"; readonly why: string };

/**
 * A ratio with a named denominator, or the refusal to produce one.
 *
 * `L1_BURDEN.zero_denominator_is_unmeasured` and `no_vacuous_perfect_rate` make
 * the same point in Lean: with nothing underneath, there is no rate. This is
 * that rule at the money layer, where the temptation is strongest — a percentage
 * of a budget spent on labour looks like a finding and is not one when the
 * labour total was never separated out.
 */
export function ratio(numerator: Units, denominator: Units): RatioResult {
  if (denominator === 0n) {
    return {
      kind: "unmeasured",
      why:
        "denominator is zero: the rate does not exist. This is not 0% and not 100%, " +
        "it is the absence of a measurement, and reporting it as a figure would be " +
        "the smallest instance of the failure this package exists to prevent.",
    };
  }
  if (denominator < 0n) {
    return { kind: "unmeasured", why: `negative denominator ${denominator}` };
  }
  // Integer basis points, so the result is exact and never a float.
  return { kind: "measured", value: (numerator * 10_000n) / denominator, denominator };
}

/**
 * The labour share of an expenditure, or a refusal.
 *
 * The question the user keeps asking — *is it going appropriately to human
 * beings* — reduces, in the record, to this: of every unit spent, how many
 * reach a person, and how many reach a thing. The record can answer it only if
 * labour was separated. Where it was not, the answer is `unmeasured`, and *that*
 * is the finding: an account that cannot distinguish wages from equipment is an
 * account that cannot answer the only question that matters about it.
 */
export function labourShare(
  labour: Units,
  total: Units,
): Evidence<RatioResult> {
  const check = "labour-share";
  const FALSIFIER =
    "a labour share reported as measured where labour and non-labour were never separated in the record";
  if (labour < 0n || total < 0n) {
    return fail(check, FALSIFIER, "negative-quantity", `labour=${labour} total=${total}`);
  }
  if (labour > total) {
    return fail(
      check,
      FALSIFIER,
      "labour-exceeds-total",
      `labour ${labour} > total ${total}: the parts exceed the whole, so one of the two ` +
        `figures is wrong and neither can be used.`,
    );
  }
  const r = ratio(labour, total);
  if (r.kind === "unmeasured") {
    return fail(check, FALSIFIER, "unmeasured", r.why);
  }
  return pass(check, FALSIFIER, r, [
    `labour ${labour} of total ${total}`,
    `share ${r.value} basis points (exact integer division, no float)`,
    `denominator ${r.denominator} is the expenditure actually recorded, not an estimate`,
  ]);
}
