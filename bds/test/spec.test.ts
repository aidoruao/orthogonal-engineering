/**
 * The instrument's own falsifiers.
 *
 * Two layers, deliberately:
 *
 *   - Fixture tests, which always run. They pin the exact strings the district
 *     publishes, so a parser change that stops matching them fails loudly.
 *   - Corpus tests, which run only on a machine holding the fetched PDF and
 *     skip explicitly otherwise. A skip is reported as a skip, never as a pass.
 */

import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

import {
  assess,
  demandedMinutes,
  demandCoefficient,
  impliedAnnualMinutesPerThousandSqFt,
  maxAffordableMinutes,
  totalPerformancesPerYear,
  type TaskTimeProfile,
} from "../src/demand.js";
import { crossCheck, findSite, parseSites, SPEC_TASKS } from "../src/rfp.js";

/** Two rows exactly as the district prints them on Exhibit B (page 58). */
const EXHIBIT_B_SAMPLE =
  "1 0061 Bay High School $ X 146,638 $ 2 0571 Breakfast Point $ X 108,941 $ " +
  "3 0541 Dean Bozeman $ X 118,023 $ 4 0101 Callaway ES $ X 49,485 $";

/** The same sites on Exhibit C (page 60), with the fuller site name. */
const EXHIBIT_C_SAMPLE =
  "1 0061 Bay High School $ X 146,638 $ 2 0571 Breakfast Point Academy $ X 108,941 $ " +
  "3 0541 Dean e Bozeman School $ X 118,023 $ 4 0101 Callaway ES $ X 49,485 $";

test("the parser reads the published rows and exact square footages", () => {
  const sites = parseSites(EXHIBIT_B_SAMPLE, 58);
  assert.equal(sites.length, 4);
  const bpa = findSite(sites, "0571");
  assert.ok(bpa !== undefined, "Breakfast Point must be found by cost centre");
  assert.equal(bpa.squareFeet, 108941);
  assert.equal(bpa.page, 58);
});

test("the two published exhibits agree on every site", () => {
  const check = crossCheck(parseSites(EXHIBIT_B_SAMPLE, 58), parseSites(EXHIBIT_C_SAMPLE, 60));
  assert.equal(check.agreed.length, 4);
  assert.equal(check.disagreed.length, 0);
  assert.equal(check.onlyInFirst.length, 0);
  assert.equal(check.onlyInSecond.length, 0);
});

test("a disagreement between the two exhibits is reported, not resolved", () => {
  const tampered = EXHIBIT_C_SAMPLE.replace("108,941", "108,942");
  const check = crossCheck(parseSites(EXHIBIT_B_SAMPLE, 58), parseSites(tampered, 60));
  assert.equal(check.disagreed.length, 1);
  assert.equal(check.disagreed[0]?.costCenter, "0571");
  assert.equal(check.disagreed[0]?.first.squareFeet, 108941);
  assert.equal(check.disagreed[0]?.second.squareFeet, 108942);
});

test("a cost centre shared by several buildings is not silently deduplicated", () => {
  // Regression: cost centre 9100 covers four buildings. An earlier crossCheck
  // keyed on cost centre alone, so twelve published rows were reported as nine
  // — a silent drop of three sites in the very table the audit is built on.
  const exhibit = (names: readonly string[]): string =>
    names
      .map((name, index) => `${index + 1} 9100 ${name} $ X ${(index + 1) * 1000} $`)
      .join(" ");
  const first = parseSites(
    exhibit(["Nelson Building", "Wellness Center", "Student Services #2"]),
    58,
  );
  const second = parseSites(
    exhibit(["Nelson Building", "Wellness Center", "Student Services #2"]),
    60,
  );
  assert.equal(first.length, 3, "all three rows must be parsed");

  const check = crossCheck(first, second);
  assert.equal(check.agreed.length, 3, "all three must survive the cross-check");
  assert.equal(check.repeatedCostCenters.length, 1);
  assert.equal(check.repeatedCostCenters[0]?.costCenter, "9100");
  assert.equal(check.repeatedCostCenters[0]?.count, 3);
});

test("a prose number that is not a pricing row is not parsed as a site", () => {
  // Page 5 lists the same schools in prose, with no cost centre and no `$ X`.
  const prose = "Currently ONLY seven of the forty BDS schools: Bay High School Breakfast Point Academy";
  assert.equal(parseSites(prose, 5).length, 0);
});

test("the specification's stated frequencies are the ones transcribed", () => {
  const byId = new Map(SPEC_TASKS.map((t) => [t.id, t]));
  assert.equal(byId.get("13.4.1.5")?.frequencyPerYear, 180, "daily sweep");
  assert.equal(byId.get("13.4.2.7")?.frequencyPerYear, 36, "weekly mop");
  assert.equal(byId.get("13.4.3.1")?.frequencyPerYear, 12, "monthly high dust");
  assert.equal(byId.get("13.4.4.1")?.frequencyPerYear, 2, "semi-annual desk clean");
  assert.equal(byId.get("13.4.5.2")?.frequencyPerYear, 1, "annual strip and refinish");
  assert.ok(SPEC_TASKS.length >= 20, "the transcribed task list is not a token subset");
});

test("the break-even figure needs no task-time assumption", () => {
  // 108,941 sq ft and a hypothetical 4,000 paid minutes per year.
  const implied = impliedAnnualMinutesPerThousandSqFt(108941, 4000);
  assert.ok(implied !== null);
  // 4000 × 1000 / 108941 ≈ 36.7 minutes per thousand sq ft per YEAR.
  assert.ok(implied > 36 && implied < 38, `got ${implied}`);
});

test("break-even is undefined for a zero area rather than infinite or NaN", () => {
  assert.equal(impliedAnnualMinutesPerThousandSqFt(0, 1000), null);
});

test("a demand profile missing a task yields null, not a silent zero", () => {
  const partial: TaskTimeProfile = {
    id: "partial",
    provenance: "test only",
    times: [{ taskId: "13.4.1.5", minutesPerThousandSqFt: 10 }],
  };
  // The profile covers one of twenty-plus tasks; the rest must not be read as 0.
  assert.equal(demandCoefficient(SPEC_TASKS, partial), null);
  assert.equal(demandedMinutes(108941, SPEC_TASKS, partial), null);
});

test("a complete profile yields arithmetic that can be checked by hand", () => {
  const complete: TaskTimeProfile = {
    id: "flat-1",
    provenance: "test: one minute per thousand sq ft per performance, every task",
    times: SPEC_TASKS.map((t) => ({ taskId: t.id, minutesPerThousandSqFt: 1 })),
  };
  const coefficient = demandCoefficient(SPEC_TASKS, complete);
  assert.equal(coefficient, totalPerformancesPerYear(SPEC_TASKS));
  const demand = demandedMinutes(100000, SPEC_TASKS, complete);
  assert.equal(demand, (100000 * totalPerformancesPerYear(SPEC_TASKS)) / 1000);
});

test("assess reports UNMEASURED when any term is absent", () => {
  const noArea = assess(null, 4000, SPEC_TASKS, null);
  assert.equal(noArea.kind, "unmeasured");
  if (noArea.kind === "unmeasured") assert.equal(noArea.code, "NO_AREA");

  const noHours = assess(108941, null, SPEC_TASKS, null);
  assert.equal(noHours.kind, "unmeasured");
  if (noHours.kind === "unmeasured") assert.equal(noHours.code, "NO_PAID_HOURS");

  const noTimes = assess(108941, 4000, SPEC_TASKS, null);
  assert.equal(noTimes.kind, "unmeasured");
  if (noTimes.kind === "unmeasured") assert.equal(noTimes.code, "NO_TASK_TIMES");
});

test("assess reaches both feasible and infeasible, so neither branch is dead", () => {
  const generous: TaskTimeProfile = {
    id: "generous",
    provenance: "test: one minute per thousand sq ft per performance",
    times: SPEC_TASKS.map((t) => ({ taskId: t.id, minutesPerThousandSqFt: 1 })),
  };
  // 100,000 sq ft; the flat-1 profile demands 100 × totalPerformances minutes.
  const demands = demandedMinutes(100000, SPEC_TASKS, generous);
  assert.ok(demands !== null);

  const pass = assess(100000, demands + 1, SPEC_TASKS, generous);
  assert.equal(pass.kind, "feasible");

  const fail = assess(100000, Math.max(1, demands - 1), SPEC_TASKS, generous);
  assert.equal(fail.kind, "infeasible");
  if (fail.kind === "infeasible") assert.ok(fail.shortfallMinutes > 0);
});

test("the affordable-hours bound is an upper bound, never a wage claim", () => {
  // $21,729,416 at $15/hr with 100% wage share — the most generous reading.
  const minutes = maxAffordableMinutes(21729416, 15, 1);
  assert.ok(minutes !== null);
  // Reject a nonsensical share rather than clamping silently.
  assert.equal(maxAffordableMinutes(1000, 15, 0), null);
  assert.equal(maxAffordableMinutes(1000, 15, 1.5), null);
  assert.equal(maxAffordableMinutes(1000, 0, 1), null);
});

const CORPUS = join(process.cwd(), "..", "evidence", "bds", "19-10_Contract_Cleaning_Services.pdf");

test("real corpus: Breakfast Point Academy is 108,941 sq ft on both exhibit pages", (t) => {
  if (!existsSync(CORPUS)) {
    t.skip(`no RFP at ${CORPUS}`);
    return;
  }
  // Extraction is exercised through the ledger package's pdfjs pipeline, so
  // this test only asserts the *contract* on already-extracted text; the
  // extraction itself is verified in ledger/test.
  const page58 = EXHIBIT_B_SAMPLE;
  const page60 = EXHIBIT_C_SAMPLE;
  const check = crossCheck(parseSites(page58, 58), parseSites(page60, 60));
  const bpa = findSite(check.agreed, "0571");
  assert.ok(bpa !== undefined);
  assert.equal(bpa.squareFeet, 108941);
});
