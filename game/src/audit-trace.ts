/**
 * game/audit-trace — real findings through the money walk.
 *
 * `money.ts` assumes a budget: an allocation, a spend, a residual. The auditors
 * do not publish that. They publish **amounts**, and the amounts mean different
 * things in different findings. So this module carries two things the money walk
 * does not: a `Measure`, which may be absent with a stated reason, and an
 * `AmountRole`, which says what the number *is* before anything is concluded
 * from it.
 *
 * ## Why the role field exists — a correction
 *
 * The first version of this file had a single field, `statedOverrun`, and
 * concluded "over budget with no board amendment" wherever it was present. Run
 * against the real findings, that produced four `overrun_without_authority`
 * findings. **Two of them were false.**
 *
 * `2024-002` states $773,629 paid to two contractors whose contracts lacked
 * Davis-Bacon clauses and who submitted no certified payrolls. That is a
 * compliance deficiency about *missing detection*. It is not a budget overrun,
 * and reporting it as one inflates the severity above what the evidence
 * warrants — the exact failure `L5_COVENANT` and the indignation-proportion
 * clause forbid.
 *
 * The same holds for `2022-002` ($530,000 year-end payables understated) and
 * `2022-005` ($1,200,000 Schedule of Expenditures understated). Those are
 * reporting errors, not overspends.
 *
 * The repair is structural, not a patch: a number without its role is not
 * evidence. `AmountRole` is required, and `traceLine` branches on it.
 *
 * ## What is realised here, and what is only mapped
 *
 * - **Realised.** `2024-003` states an excess over budget of $1,162,601 with no
 *   board amendment. That is exactly the shape `money.ts` tests for, and the
 *   auditor's own text supplies both operands.
 * - **Realised.** Every allocation is absent, and the module says so rather
 *   than assigning "other".
 * - **Mapped, not realised.** `2024-002` maps onto `L6_GAME`'s mechanism: the
 *   Davis-Bacon clause is the detector, its absence is `detects = false`, and
 *   `bond_without_detection_is_inert` says no bond repairs a missing detector.
 *   The mapping is sound in structure. It is **not** a finding that anyone lied,
 *   and it is **not** a finding that anyone was underpaid.
 */

import { fail, pass, type Evidence, type Units } from "./types.js";
import type { MoneyFinding } from "./money.js";

/**
 * A quantity the record may or may not state.
 *
 * `unmeasured` carries its reason, so a reader sees why rather than merely that.
 * There is no `default`, no `0n`, and no `null` — the three ways an absent
 * measurement usually becomes an invented one.
 */
export type Measure =
  | { readonly kind: "known"; readonly value: Units }
  | { readonly kind: "unmeasured"; readonly why: string };

export function known(value: Units): Measure {
  return { kind: "known", value };
}

export function unmeasured(why: string): Measure {
  return { kind: "unmeasured", why };
}

/**
 * What the stated amount **is**.
 *
 * A dollar figure is not self-interpreting. This field is the difference
 * between "the district overspent by $773,629" (not stated by anyone) and "the
 * district paid $773,629 to contractors whose contracts carried no wage-rate
 * clause" (stated at p.102). Only the second appears in the record, and only
 * `excess_over_budget` licenses an overrun conclusion.
 *
 * The finding kinds are the auditor's, not this instrument's:
 *
 * - `excess_over_budget` — an expenditure above the adopted budget. 2024-003.
 * - `questioned_cost` — a cost the auditor questions. 2024-002.
 * - `reported_understatement` — a figure reported lower than it was. 2022-002,
 *   2022-005.
 * - `none_stated` — a deficiency with no dollar figure at all. 2022-001,
 *   2024-001.
 */
export type AmountRole =
  | "excess_over_budget"
  | "questioned_cost"
  | "reported_understatement"
  | "none_stated";

/** One auditor-stated finding, as a line the walk can carry. */
export type FindingLine = {
  /** Auditor's finding number. Stable key. */
  readonly id: string;
  readonly fiscalYear: number;
  readonly heading: string;
  /** The document and page the finding is quoted from. */
  readonly document: string;
  readonly page: number;
  /** What the stated amount is. Required: a figure without a role is not evidence. */
  readonly role: AmountRole;
  /** The amount the auditor states, in the role given above. */
  readonly stated: Measure;
  /** The allocation, where the record states one. */
  readonly allocated: Measure;
  /** The total spent, where the record states one. */
  readonly spent: Measure;
  /** The board amendment authorising an excess, where one exists. */
  readonly amendment: Measure;
  /** Whether the auditor's own text marks this as previously reported. */
  readonly repeatOfPriorYear: boolean;
};

export type TraceStatus =
  /** Every quantity needed is known and no rule is breached. */
  | "closed"
  /** Every quantity needed is known and a rule is breached. A finding. */
  | "finding"
  /** A quantity is absent, so the line cannot be closed either way. */
  | "unmeasured";

export type TracedLine = {
  readonly id: string;
  readonly role: AmountRole;
  readonly status: TraceStatus;
  readonly findings: readonly MoneyFinding[];
  readonly gaps: readonly { readonly field: string; readonly why: string }[];
  /** What a reader must fetch to convert this line from unmeasured to measured. */
  readonly wouldMeasure: readonly string[];
};

export type AuditTrace = {
  readonly lines: readonly TracedLine[];
  /** Sum of the stated amounts across every role. Not an overrun total. */
  readonly statedTotal: Units;
  /** The stated amounts split by role, so no two meanings are added together. */
  readonly byRole: Readonly<Record<AmountRole, Units>>;
  readonly measuredCount: number;
  readonly unmeasuredCount: number;
  readonly findingCount: number;
  /** True only when every line is closed and no rule is breached. */
  readonly closed: boolean;
};

const TRACE_FALSIFIER =
  "an audit trace reported as closed while any line rests on a quantity the schedule does not state";

const OVERRUN_FALSIFIER =
  "a board minute, amendment, or resolution authorising this excess for this object code and fiscal year";

const DETECTOR_FALSIFIER =
  "a certified payroll or wage-rate certification for the contracts underlying this payment, " +
  "produced from the district's own contract files";

/**
 * Extract the numeric value of a measure, or zero, without pretending the
 * absence was a zero. Only used where the caller has already branched on
 * `kind === "known"`.
 */
function valueOf(m: Measure): Units {
  return m.kind === "known" ? m.value : 0n;
}

/**
 * Trace one finding line.
 *
 * The branch on `role` is the correction described in the file header. A
 * questioned cost does not become an overrun because both are numbers, and a
 * reporting understatement does not become either.
 */
export function traceLine(l: FindingLine): TracedLine {
  const gaps: { field: string; why: string }[] = [];
  const findings: MoneyFinding[] = [];
  const wouldMeasure: string[] = [];

  for (const [field, m] of [
    ["stated", l.stated],
    ["allocated", l.allocated],
    ["spent", l.spent],
    ["amendment", l.amendment],
  ] as const) {
    if (m.kind === "unmeasured") gaps.push({ field, why: m.why });
  }

  const amount = valueOf(l.stated);

  switch (l.role) {
    case "excess_over_budget": {
      // The only role that licenses an overrun conclusion.
      if (l.stated.kind !== "known") {
        wouldMeasure.push(
          `the excess over budget for ${l.id}: this line claims the role but states no amount`,
        );
        break;
      }
      if (l.amendment.kind !== "known") {
        findings.push({
          kind: "overrun_without_authority",
          code: l.id,
          amount,
          detail:
            `${l.heading}: ${amount} expended over budget with no board amendment recorded. ` +
            `${l.document} p.${l.page}.`,
          falsifier: OVERRUN_FALSIFIER,
        });
        wouldMeasure.push(
          `a board amendment for ${l.id} naming the amount, the meeting, and the minute`,
        );
      }
      break;
    }
    case "questioned_cost": {
      // A payment the auditor questions. The structural finding is that the
      // control which would have detected a problem was not present — not that
      // the money was misspent, which nobody has established.
      findings.push({
        kind: "control_absent",
        code: l.id,
        amount,
        detail:
          `${l.heading}: ${amount} paid where the control that would have detected ` +
          `misconduct was absent. This is NOT an overrun and NOT a finding that the money ` +
          `was misspent. ${l.document} p.${l.page}.`,
        falsifier: DETECTOR_FALSIFIER,
      });
      wouldMeasure.push(
        `the executed contract for ${l.id}, to establish whether a wage-rate clause was present`,
        `certified payrolls for the same period, which would convert "no detector" into a measurement`,
      );
      break;
    }
    case "reported_understatement": {
      // A figure reported too low. Not a spend, not an overrun. Named as what
      // it is so it cannot be summed into an expenditure total by a reader.
      wouldMeasure.push(
        `the corrected figure for ${l.id}, from the audited statement it appears in`,
        `the restatement or management response, which would show the correction was made`,
      );
      break;
    }
    case "none_stated": {
      // A deficiency with no dollar figure. There is nothing to trace and
      // saying so is the whole content of the line.
      wouldMeasure.push(
        `the staffing level or control this deficiency concerns, so the deficiency can be sized`,
      );
      break;
    }
    default: {
      // Exhaustiveness is enforced by the type; this branch is unreachable and
      // exists so a future role addition fails to compile rather than silently
      // falling through to no finding.
      const never: never = l.role;
      throw new Error(`unhandled role: ${String(never)}`);
    }
  }

  if (l.allocated.kind === "unmeasured") {
    wouldMeasure.push(
      `the adopted allocation for ${l.id}, from the object-code budget adopted by the board`,
    );
  }

  const status: TraceStatus =
    findings.length > 0 ? "finding" : gaps.length > 0 ? "unmeasured" : "closed";

  return { id: l.id, role: l.role, status, findings, gaps, wouldMeasure };
}

/**
 * Trace a set of auditor-stated findings.
 *
 * The output separates four quantities that are usually collapsed into one: how
 * much is stated, how much is stated *in each role*, how much is measured, and
 * how much cannot be said. Adding a $773,629 questioned cost to a $1,162,601
 * overrun produces a number that means nothing, so `byRole` is kept and
 * `statedTotal` is labelled as what it is: a sum of stated amounts, not an
 * overrun and not a loss.
 */
export function traceFindings(lines: readonly FindingLine[]): Evidence<AuditTrace> {
  const check = "trace-audit-findings";
  const seen = new Set<string>();
  for (const l of lines) {
    if (seen.has(l.id)) {
      return fail(
        check,
        TRACE_FALSIFIER,
        "duplicate-finding-id",
        `finding "${l.id}" appears more than once; one would be silently dropped by any grouping.`,
      );
    }
    seen.add(l.id);
    if (l.stated.kind === "known" && l.stated.value < 0n) {
      return fail(
        check,
        TRACE_FALSIFIER,
        "negative-amount",
        `${l.id}: stated=${l.stated.value}. A negative amount is a credit or a typo and ` +
          `belongs in neither this field nor this trace.`,
      );
    }
    if (l.role === "excess_over_budget" && l.stated.kind === "unmeasured") {
      return fail(
        check,
        TRACE_FALSIFIER,
        "role-without-amount",
        `${l.id} declares role excess_over_budget but states no amount. The role is a claim ` +
          `about a number that is not there.`,
      );
    }
  }

  const traced = lines.map(traceLine);

  const byRole: Record<AmountRole, Units> = {
    excess_over_budget: 0n,
    questioned_cost: 0n,
    reported_understatement: 0n,
    none_stated: 0n,
  };
  let statedTotal = 0n;
  for (const l of lines) {
    if (l.stated.kind === "known") {
      byRole[l.role] += l.stated.value;
      statedTotal += l.stated.value;
    }
  }

  const measuredCount = traced.filter((t) => t.status !== "unmeasured").length;
  const unmeasuredCount = traced.filter((t) => t.status === "unmeasured").length;
  const findingCount = traced.reduce((n, t) => n + t.findings.length, 0);

  const trace: AuditTrace = {
    lines: traced,
    statedTotal,
    byRole,
    measuredCount,
    unmeasuredCount,
    findingCount,
    closed: unmeasuredCount === 0 && findingCount === 0,
  };

  return pass(check, TRACE_FALSIFIER, trace, [
    `${lines.length} finding lines traced`,
    `stated total ${statedTotal} — a sum of stated amounts, NOT an overrun and NOT a loss`,
    `  excess over budget:   ${byRole.excess_over_budget}`,
    `  questioned cost:      ${byRole.questioned_cost}`,
    `  reported understated: ${byRole.reported_understatement}`,
    `${findingCount} structural finding(s) established without needing an absent quantity`,
    `${unmeasuredCount} line(s) cannot be closed: a quantity no fetched document supplies`,
    trace.closed
      ? "every line closed"
      : `NOT closed — ${unmeasuredCount} line(s) rest on an absent quantity, ` +
        `and the four roles are kept apart because adding them is meaningless`,
  ]);
}

/**
 * The BDS FY2022/FY2024 findings as `FindingLine`s.
 *
 * Every figure and every heading is quoted from `bds/src/findings.ts`, which
 * quotes the audited financial statements at the page cited. Nothing is added
 * here. Allocations are `unmeasured` because the schedules do not publish them.
 */
export const BDS_FINDING_LINES: readonly FindingLine[] = [
  {
    id: "2024-001",
    fiscalYear: 2024,
    heading: "Material weakness: lack of appropriate staffing in the finance department",
    document: "dsb_audit_2024.pdf",
    page: 101,
    role: "none_stated",
    stated: unmeasured("a material weakness states no dollar amount"),
    allocated: unmeasured("staffing weakness, not a budget line"),
    spent: unmeasured("not stated for this finding"),
    amendment: unmeasured("not a variance; no amendment applies"),
    repeatOfPriorYear: true,
  },
  {
    id: "2024-002",
    fiscalYear: 2024,
    heading:
      "Significant deficiency: two contractors paid without Davis-Bacon clauses or certified payrolls",
    document: "dsb_audit_2024.pdf",
    page: 102,
    role: "questioned_cost",
    stated: known(773_629n),
    allocated: unmeasured(
      "the schedule states the amount paid, not the amount budgeted for these contracts",
    ),
    spent: unmeasured("the schedule states an amount paid, not a total expenditure"),
    amendment: unmeasured("not a budget variance in the auditor's framing"),
    repeatOfPriorYear: false,
  },
  {
    id: "2024-003",
    fiscalYear: 2024,
    heading: "Noncompliance: expenditures exceeded budget without required amendment",
    document: "dsb_audit_2024.pdf",
    page: 103,
    role: "excess_over_budget",
    stated: known(1_162_601n),
    allocated: unmeasured(
      "the adopted allocation is not published in the audit schedule; only the excess is stated",
    ),
    spent: unmeasured("spent = allocated + 1,162,601, and allocated is absent"),
    amendment: unmeasured(
      "the auditor states the amendment required by state law was not made; a record of a " +
        "non-made amendment does not exist and cannot be supplied",
    ),
    repeatOfPriorYear: false,
  },
  {
    id: "2022-001",
    fiscalYear: 2022,
    heading: "Material weakness: lack of appropriate staffing in the finance department",
    document: "dsb_audit_2022.pdf",
    page: 88,
    role: "none_stated",
    stated: unmeasured("a material weakness states no dollar amount"),
    allocated: unmeasured("staffing weakness, not a budget line"),
    spent: unmeasured("not stated for this finding"),
    amendment: unmeasured("not a variance"),
    repeatOfPriorYear: true,
  },
  {
    id: "2022-002",
    fiscalYear: 2022,
    heading: "Material weakness: year-end payables understated",
    document: "dsb_audit_2022.pdf",
    page: 89,
    role: "reported_understatement",
    stated: known(530_000n),
    allocated: unmeasured("a reporting weakness, not a budget line"),
    spent: unmeasured("not stated"),
    amendment: unmeasured("not a budget variance"),
    repeatOfPriorYear: true,
  },
  {
    id: "2022-005",
    fiscalYear: 2022,
    heading: "Noncompliance: Schedule of Expenditures of Federal Awards understated",
    document: "dsb_audit_2022.pdf",
    page: 90,
    role: "reported_understatement",
    stated: known(1_200_000n),
    allocated: unmeasured("the schedule states the understatement, not the allocation"),
    spent: unmeasured("not stated"),
    amendment: unmeasured("not a budget variance"),
    repeatOfPriorYear: true,
  },
];
