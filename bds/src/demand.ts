/**
 * Demand, and the break-even that needs no invented constant.
 *
 * The temptation here is enormous and the arc names it directly. It would take
 * one number — "a custodian cleans X square feet per hour" — and produce a
 * verdict. That number is not in the district's specification, is not in its
 * audit, and inventing it would make the conclusion rest on an assumption the
 * instrument smuggled in.
 *
 * So the instrument computes the *reverse*: given the district's own published
 * area and the labor the district's own budget pays for, what average annual
 * task time per thousand square feet would the paid hours have to achieve for
 * the specification to be met?
 *
 *     implied minutes per 1000 sq ft per year = 1000 × paidMinutes / areaSqFt
 *
 * That number requires no external constant. It is arithmetic on two fetched
 * quantities. The reader can then judge whether the implied figure is plausible
 * for a list of 24 required tasks with frequencies from daily to annual — and
 * that judgement is theirs to make, on stated assumptions, rather than the
 * instrument's to assert.
 *
 * If a task-time profile IS supplied, with its own provenance declared, the
 * forward calculation is available too, and it is clearly labelled as resting
 * on that profile.
 */

import { FREQUENCY_BASIS, SPEC_TASKS, SERVICE_DAYS_PER_YEAR } from "./rfp.js";
import type { Feasibility, SpecTask } from "./types.js";

/** Labor minutes per thousand square feet, per single performance of a task. */
export type TaskTime = {
  readonly taskId: string;
  readonly minutesPerThousandSqFt: number;
};

/**
 * A declared task-time profile.
 *
 * `provenance` is mandatory. A profile without a stated origin is an invented
 * constant wearing a type annotation, and the instrument will not accept one.
 */
export type TaskTimeProfile = {
  readonly id: string;
  readonly provenance: string;
  readonly times: readonly TaskTime[];
};

/** Sum of (frequency × minutes) over the task list: minutes per year per
 *  thousand square feet. This is the scaled demand coefficient. */
export function demandCoefficient(
  tasks: readonly SpecTask[],
  profile: TaskTimeProfile,
): number | null {
  const byId = new Map(profile.times.map((t) => [t.taskId, t.minutesPerThousandSqFt]));
  let sum = 0;
  for (const task of tasks) {
    const minutes = byId.get(task.id);
    // A missing time is not zero. Treating it as zero would silently understate
    // demand; returning null forces the caller to report UNMEASURED.
    if (minutes === undefined) return null;
    sum += task.frequencyPerYear * minutes;
  }
  return sum;
}

/** Annual labor minutes the specification demands for an area, given a profile. */
export function demandedMinutes(
  areaSqFt: number,
  tasks: readonly SpecTask[],
  profile: TaskTimeProfile,
): number | null {
  const coefficient = demandCoefficient(tasks, profile);
  if (coefficient === null) return null;
  return (areaSqFt * coefficient) / 1000;
}

/**
 * The break-even figure: the average annual task time per thousand square feet
 * that the paid minutes would have to buy.
 *
 * Needs no task-time assumption at all. This is the instrument's honest core.
 */
export function impliedAnnualMinutesPerThousandSqFt(
  areaSqFt: number,
  paidMinutes: number,
): number | null {
  if (areaSqFt <= 0) return null;
  return (paidMinutes * 1000) / areaSqFt;
}

/**
 * The hours a dollar figure could buy, under a declared wage.
 *
 * This is an *upper bound* on labor, deliberately: plant-operations expenditure
 * also covers benefits, supplies, utilities, and purchased services, so the
 * true custodial wage share is smaller than the total. Using the whole function
 * budget as though it were all wages is the assumption most generous to the
 * district, which means any infeasibility found under it holds a fortiori.
 */
export function maxAffordableMinutes(
  functionBudgetUsd: number,
  hourlyWageUsd: number,
  wageShare: number,
): number | null {
  if (hourlyWageUsd <= 0 || wageShare <= 0 || wageShare > 1) return null;
  const laborUsd = functionBudgetUsd * wageShare;
  return (laborUsd / hourlyWageUsd) * 60;
}

/** Compare demand against paid minutes. Both must be known, or it is unmeasured. */
export function assess(
  areaSqFt: number | null,
  paidMinutes: number | null,
  tasks: readonly SpecTask[],
  profile: TaskTimeProfile | null,
): Feasibility {
  if (areaSqFt === null || areaSqFt <= 0) {
    return {
      kind: "unmeasured",
      code: "NO_AREA",
      detail: "no published square footage for this site was read from a fetched source",
    };
  }
  if (paidMinutes === null || paidMinutes <= 0) {
    return {
      kind: "unmeasured",
      code: "NO_PAID_HOURS",
      detail:
        "no fetched source states the labor minutes paid for this site, so feasibility is not computable",
    };
  }
  if (profile === null) {
    return {
      kind: "unmeasured",
      code: "NO_TASK_TIMES",
      detail:
        "the district does not publish task times per square foot; the break-even figure is reported instead",
    };
  }
  const demand = demandedMinutes(areaSqFt, tasks, profile);
  if (demand === null) {
    return {
      kind: "unmeasured",
      code: "NO_TASK_TIMES",
      detail: "the supplied task-time profile does not cover every required task",
    };
  }
  if (demand <= paidMinutes) {
    return {
      kind: "feasible",
      demandedMinutes: demand,
      paidMinutes,
      headroomMinutes: paidMinutes - demand,
    };
  }
  return {
    kind: "infeasible",
    demandedMinutes: demand,
    paidMinutes,
    shortfallMinutes: demand - paidMinutes,
  };
}

/** Total minimum performances per year across the specification. */
export function totalPerformancesPerYear(tasks: readonly SpecTask[]): number {
  return tasks.reduce((sum, task) => sum + task.frequencyPerYear, 0);
}

/** Tasks whose stated frequency is daily, for the service-day note. */
export function dailyTasks(tasks: readonly SpecTask[]): readonly SpecTask[] {
  return tasks.filter((task) => task.frequencyPerYear === SERVICE_DAYS_PER_YEAR);
}

export { FREQUENCY_BASIS, SPEC_TASKS, SERVICE_DAYS_PER_YEAR };
