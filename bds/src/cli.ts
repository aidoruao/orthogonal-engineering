#!/usr/bin/env node
/**
 * bds — the Bay District Schools instrument, command line.
 *
 * Exit codes:
 *   0  the report was produced
 *   1  a declared invariant was violated (a figure did not verify, a
 *      cross-check disagreed, a finding was inadmissible)
 *   2  usage or I/O error
 *
 * The instrument does not render verdicts on people. `L3_JURISDICTION.lean`
 * establishes the boundary and this code cannot cross it: `Subject` has no
 * condemnation member, so a finding against a person's soul is not
 * representable, let alone printable.
 */

import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { AUDIT_FINDINGS, FINDING_LIMITS, INFERENTIAL_LINK, questionedCosts, recurrences } from "./findings.js";
import { ATTRIBUTION_LIMITS, OFFICE_HOLDINGS, officialsIn, periods, superintendentIn } from "./actors.js";
import { AMENDMENTS, applyAmendments, operativeSquareFeet } from "./addendum.js";
import {
  compareArea,
  floorCoveringTotals,
  parseFish,
  parsedRoomArea,
  permanentTotalArea,
  reconcile,
  roomsMatching,
} from "./fish.js";
import {
  assess,
  impliedAnnualMinutesPerThousandSqFt,
  maxAffordableMinutes,
  totalPerformancesPerYear,
} from "./demand.js";
import { FIGURES, PLANT_OPS_FY2024_ID, SCOPE_STATEMENT, figure } from "./figures.js";
import { FREQUENCY_BASIS, SERVICE_DAYS_BASIS, SERVICE_DAYS_PER_YEAR, SPEC_TASKS, crossCheck, findSite, parseSites } from "./rfp.js";
import { admissible, sortViolations, type Finding } from "./types.js";

const USAGE = `bds — Bay District Schools / Breakfast Point Academy instrument

  bds figures
      Print every audited figure with its page and source text.

  bds spec
      Print the transcribed task list and the frequency basis for each number.

  bds sites --extract PATH
      Parse the published square-footage table from an extracted RFP text file
      and cross-check Exhibit B against Exhibit C.

  bds breakeven --area N --paid-minutes N
      The annual task time per thousand sq ft that the paid minutes allow.
      Requires no task-time assumption.

  bds report --extract PATH
      Everything above, plus the scope statement that bounds the claims.

Nothing here renders a verdict about any person. See L3_JURISDICTION.lean.
`;

function usd(value: number): string {
  return `$${value.toLocaleString("en-US")}`;
}

function commandFigures(): number {
  const lines: string[] = ["audited figures — every number carries its page", ""];
  const byYear = [...FIGURES].sort((a, b) => {
    if (a.fiscalYear !== b.fiscalYear) return b.fiscalYear - a.fiscalYear;
    return a.label < b.label ? -1 : 1;
  });
  for (const entry of byYear) {
    lines.push(
      `  FY${entry.fiscalYear}  ${entry.label.padEnd(24)} ${usd(entry.amountUsd).padStart(14)}` +
        `   ${entry.document} p.${entry.page}`,
    );
    lines.push(`          "${entry.text.slice(0, 100)}"`);
  }
  lines.push("");
  lines.push("  SCOPE: these are FUNCTION totals (salaries + benefits + supplies +");
  lines.push("  utilities + purchased services). They are not custodial wage spend.");
  lines.push("  Any labor bound derived from them is an upper bound, by construction.");
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

function commandSpec(): number {
  const lines: string[] = ["the specification, as the district states it", ""];
  lines.push(`  service days per year: ${SERVICE_DAYS_PER_YEAR}`);
  lines.push(`    ${SERVICE_DAYS_BASIS}`);
  lines.push("");
  lines.push("  frequency basis (Section 13):");
  for (const basis of FREQUENCY_BASIS) {
    lines.push(`    ${basis.label.padEnd(14)} ${String(basis.perYear).padStart(3)}/yr  §${basis.section}`);
    lines.push(`      "${basis.quote.slice(0, 110)}"`);
  }
  lines.push("");
  lines.push(`  transcribed tasks: ${SPEC_TASKS.length}`);
  lines.push(`  total minimum performances per year: ${totalPerformancesPerYear(SPEC_TASKS)}`);
  lines.push("");
  for (const task of SPEC_TASKS) {
    lines.push(`    ${task.id.padEnd(10)} ${String(task.frequencyPerYear).padStart(3)}/yr  ${task.description.slice(0, 78)}`);
  }
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

type ExtractPages = ReadonlyMap<number, string>;

/**
 * Read the "=== PAGE n ===" format `ledger`'s extractor emits, so this tool
 * consumes the same intermediate form rather than re-running pdfjs. One
 * extractor, one definition of what the document says.
 */
function readExtract(path: string): ExtractPages {
  const text = readFileSync(path, "utf8");
  const pages = new Map<number, string>();
  const pattern = /^=== PAGE (\d+) ===$/gm;
  const matches = [...text.matchAll(pattern)];
  for (let index = 0; index < matches.length; index += 1) {
    const match = matches[index];
    if (match === undefined) continue;
    const pageNumber = Number.parseInt(match[1] ?? "", 10);
    const start = (match.index ?? 0) + match[0].length;
    const nextMatch = matches[index + 1];
    const end = nextMatch?.index ?? text.length;
    pages.set(pageNumber, text.slice(start, end));
  }
  return pages;
}

function commandSites(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const path = values["extract"];
  if (typeof path !== "string") throw new Error("--extract is required");
  const pages = readExtract(path);

  const exhibitB = parseSites(pages.get(58) ?? "", 58);
  const exhibitC = parseSites(pages.get(60) ?? "", 60);

  if (exhibitB.length === 0 || exhibitC.length === 0) {
    process.stderr.write(
      "bds: no site rows found. The extract does not contain the pricing tables, " +
        "so this is a parse gap and not an absence of sites in the document.\n",
    );
    return 1;
  }

  const check = crossCheck(exhibitB, exhibitC);
  const lines: string[] = [];
  lines.push("published square-footage table, cross-checked");
  lines.push(`  Exhibit B (p.58): ${exhibitB.length} rows`);
  lines.push(`  Exhibit C (p.60): ${exhibitC.length} rows`);
  lines.push(`  agreed: ${check.agreed.length}`);
  if (check.disagreed.length > 0) {
    lines.push(`  DISAGREED: ${check.disagreed.length}`);
    for (const row of check.disagreed) {
      lines.push(
        `    ${row.costCenter}  p.58=${row.first.squareFeet}  p.60=${row.second.squareFeet}`,
      );
    }
  }
  if (check.onlyInFirst.length > 0) {
    lines.push(`  only in Exhibit B: ${check.onlyInFirst.map((s) => s.costCenter).join(", ")}`);
  }
  if (check.onlyInSecond.length > 0) {
    lines.push(`  only in Exhibit C: ${check.onlyInSecond.map((s) => s.costCenter).join(", ")}`);
  }
  if (check.repeatedCostCenters.length > 0) {
    // Reported, not collapsed: the district really does put several buildings
    // under one cost centre, and a dedupe by cost centre would drop sites.
    const detail = check.repeatedCostCenters
      .map((entry) => `${entry.costCenter}×${entry.count}`)
      .join(", ");
    lines.push(`  cost centres covering several buildings: ${detail}`);
  }
  lines.push("");
  for (const site of check.agreed) {
    lines.push(`  ${site.costCenter}  ${site.name.padEnd(30)} ${site.squareFeet.toLocaleString("en-US").padStart(10)} sq ft`);
  }
  process.stdout.write(`${lines.join("\n")}\n`);

  if (check.disagreed.length > 0) {
    process.stderr.write(
      "bds: the two exhibits disagree. That is a finding about the document, " +
        "and this tool reports it rather than choosing which page to believe.\n",
    );
    return 1;
  }
  return 0;
}

function commandBreakeven(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const area = Number.parseInt(String(values["area"] ?? ""), 10);
  const paid = Number.parseInt(String(values["paid-minutes"] ?? ""), 10);
  if (!Number.isFinite(area) || area <= 0) throw new Error("--area must be a positive integer");
  if (!Number.isFinite(paid) || paid <= 0) {
    throw new Error("--paid-minutes must be a positive integer");
  }

  const implied = impliedAnnualMinutesPerThousandSqFt(area, paid);
  if (implied === null) return 1;

  const lines: string[] = [];
  lines.push("break-even — no task-time assumption is used here");
  lines.push(`  area:              ${area.toLocaleString("en-US")} sq ft`);
  lines.push(`  paid labor:        ${paid.toLocaleString("en-US")} minutes/yr`);
  lines.push(`  implied allowance: ${implied.toFixed(2)} min per 1,000 sq ft per YEAR`);
  lines.push("");
  lines.push("  Read this as: for the specification to be met within the paid");
  lines.push("  minutes, ALL of these tasks, at their stated frequencies, must");
  lines.push("  together average the figure above.");
  lines.push("");
  for (const task of SPEC_TASKS.slice(0, 6)) {
    lines.push(`    ${task.id.padEnd(10)} ${String(task.frequencyPerYear).padStart(3)}/yr  ${task.description.slice(0, 62)}`);
  }
  lines.push(`    … and ${Math.max(0, SPEC_TASKS.length - 6)} more`);
  lines.push("");
  lines.push("  Whether that allowance is plausible is a judgement the reader makes");
  lines.push("  on stated assumptions. This tool does not make it for them.");
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}




function commandFindings(): number {
  const lines: string[] = [];
  const total = questionedCosts();
  lines.push("audit findings — the auditor's own conclusions, not this tool's");
  lines.push("");
  lines.push(`  findings recorded: ${AUDIT_FINDINGS.length}`);
  lines.push(`  dollar amounts stated by the auditor: ${usd(total)}`);
  lines.push("");
  for (const year of [...new Set(AUDIT_FINDINGS.map((f) => f.fiscalYear))].sort()) {
    lines.push(`  FY${String(year)}`);
    for (const finding of AUDIT_FINDINGS.filter((f) => f.fiscalYear === year)) {
      const amount = finding.amountUsd === null ? "" : `  ${usd(finding.amountUsd)}`;
      lines.push(`    ${finding.id}  [${finding.kind}]${amount}`);
      lines.push(`      ${finding.heading.slice(0, 88)}`);
      lines.push(`      ${finding.document} p.${String(finding.page)}${finding.repeatOfPriorYear ? "  (previously reported)" : ""}`);
    }
    lines.push("");
  }
  const recurring = recurrences();
  if (recurring.length > 0) {
    lines.push("  RECURRING ACROSS AUDIT CYCLES");
    for (const r of recurring) {
      lines.push(`    ${r.heading}: ${r.occurrences.map((o) => o.id).join(", ")}`);
    }
    lines.push("");
  }
  lines.push("  CONVERGENT WITH THE LABOUR QUESTION, NOT PROOF OF IT");
  for (const fact of INFERENTIAL_LINK.convergentFacts) lines.push(`    + ${fact}`);
  lines.push("  what would establish the specific claim:");
  for (const item of INFERENTIAL_LINK.whatWouldEstablishTheThesis) lines.push(`    - ${item}`);
  lines.push(`  status: ${INFERENTIAL_LINK.status}`);
  lines.push("");
  lines.push("  WHAT THESE FINDINGS DO NOT ESTABLISH");
  for (const limit of FINDING_LIMITS) lines.push(`    - ${limit}`);
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

function commandActors(): number {
  const lines: string[] = [];
  lines.push("officials of record — attribution, not verdict");
  lines.push("");
  lines.push("  Each row is checkable: open the document, turn to the page, and find");
  lines.push("  the name beside the office. Nothing here asserts fault, knowledge, or");
  lines.push("  causation. See L3_JURISDICTION.lean for why that boundary is structural.");
  lines.push("");
  for (const period of periods()) {
    lines.push(`  ${period}`);
    for (const holding of officialsIn(period)) {
      const district = holding.district === null ? "" : ` (District ${holding.district})`;
      lines.push(`    ${holding.name.padEnd(24)} ${holding.office}${district}`);
      lines.push(`      ${holding.document} p.${String(holding.page)}  [${holding.attributedWith}]`);
    }
    const sup = superintendentIn(period);
    lines.push(`    superintendent of record: ${sup === null ? "none or ambiguous" : sup.name}`);
    lines.push("");
  }
  lines.push("  WHAT THIS LAYER CANNOT PRODUCE");
  for (const limit of ATTRIBUTION_LIMITS) lines.push(`    - ${limit}`);
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

function commandFish(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const path = values["fish"];
  if (typeof path !== "string") throw new Error("--fish is required");
  const report = parseFish(readFileSync(path, "utf8"));
  const lines: string[] = [];
  lines.push(`FISH report — ${report.facilityName || "unknown facility"} (MSID ${report.msid || "?"})`);
  lines.push(`  buildings: ${report.buildings.length}`);
  for (const b of report.buildings) {
    const pretty = b.permanentSqFt === null ? "(no printed subtotal)" : `${b.permanentSqFt.toLocaleString("en-US")} sq ft`;
    lines.push(`    bldg ${b.id.padEnd(4)} ${b.name.padEnd(24)} ${pretty}`);
  }
  lines.push(`  rooms parsed: ${report.rooms.length}`);
  lines.push(`  parsed room area: ${parsedRoomArea(report.rooms).toLocaleString("en-US")} sq ft`);
  lines.push(`  printed subtotal area: ${permanentTotalArea(report).toLocaleString("en-US")} sq ft`);
  lines.push("");
  lines.push("  floor coverings (rooms parsed):");
  for (const [cover, area] of [...floorCoveringTotals(report.rooms)].sort((a, b) => b[1] - a[1])) {
    lines.push(`    ${cover.padEnd(18)} ${area.toLocaleString("en-US").padStart(9)} sq ft`);
  }
  lines.push("");
  lines.push(`  restrooms: ${roomsMatching(report.rooms, /RESTROOM/).length}`);
  lines.push(`  classrooms: ${roomsMatching(report.rooms, /CLASSROOM/).length}`);
  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

function commandReconcile(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const fishPath = values["fish"];
  const bid = Number.parseInt(String(values["bid-sqft"] ?? ""), 10);
  if (typeof fishPath !== "string") throw new Error("--fish is required");
  if (!Number.isFinite(bid) || bid <= 0) throw new Error("--bid-sqft must be a positive integer");
  const report = parseFish(readFileSync(fishPath, "utf8"));
  const rec = reconcile(bid, report);
  const lines: string[] = [];
  lines.push("area reconciliation — FISH against the bid table");
  lines.push(`  bid area:            ${bid.toLocaleString("en-US")} sq ft`);
  lines.push(`  FISH gross net:      ${rec.grossNetSqFt.toLocaleString("en-US")} sq ft`);
  lines.push("  excluding space a cleaning contract would not normally service:");
  for (const step of rec.steps) {
    lines.push(
      `    - ${step.label.padEnd(18)} ${step.excludedSqFt.toLocaleString("en-US").padStart(8)} → ${step.remainingSqFt.toLocaleString("en-US")}`,
    );
  }
  lines.push("");
  lines.push(`  residual: ${rec.residualSqFt.toLocaleString("en-US")} sq ft (${rec.residualRatio.toFixed(3)}x the bid area)`);
  lines.push(`  closes the gap: ${String(rec.closesGap)}`);
  lines.push("");
  lines.push("  UNRESOLVED. " + rec.unresolvedBecause);
  process.stdout.write(`${lines.join("\n")}\n`);
  return rec.closesGap ? 0 : 1;
}

function commandScope(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const path = values["extract"];
  if (typeof path !== "string") throw new Error("--extract is required");
  const pages = readExtract(path);
  const base = [...parseSites(pages.get(58) ?? "", 58)];
  const applied = applyAmendments(base, AMENDMENTS);
  const lines: string[] = [];
  lines.push("operative scope — the base document as amended");
  lines.push(`  base table rows:      ${base.length}`);
  lines.push(`  removed by addendum:  ${applied.removed.length}`);
  for (const r of applied.removed) {
    lines.push(`    - ${r.site.costCenter} ${r.site.name} (${r.site.squareFeet.toLocaleString("en-US")} sq ft) by ${r.by}`);
  }
  lines.push(`  operative sites:      ${applied.operative.length}`);
  lines.push(`  operative area:       ${operativeSquareFeet(applied).toLocaleString("en-US")} sq ft`);
  if (applied.unresolvedDeletions.length > 0) {
    lines.push("  UNRESOLVED deletions (amendment names a site the table lacks):");
    for (const u of applied.unresolvedDeletions) lines.push(`    - ${u.costCenter} ${u.siteName} by ${u.by}`);
  }
  lines.push("");
  for (const site of applied.operative) {
    lines.push(`  ${site.costCenter}  ${site.name.padEnd(28)} ${site.squareFeet.toLocaleString("en-US").padStart(9)} sq ft`);
  }
  process.stdout.write(`${lines.join("\n")}\n`);
  return applied.unresolvedDeletions.length > 0 ? 1 : 0;
}

function commandReport(values: Readonly<Record<string, string | boolean | undefined>>): number {
  const path = values["extract"];
  const lines: string[] = [];

  lines.push("=".repeat(72));
  lines.push("BAY DISTRICT SCHOOLS — structural report");
  lines.push("=".repeat(72));
  lines.push("");

  lines.push("SCOPE, from the district's own document:");
  lines.push(`  RFP 19-10 p.${SCOPE_STATEMENT.page}`);
  lines.push(`  "${SCOPE_STATEMENT.text.replace(/\s+/g, " ").trim()}"`);
  lines.push("");
  lines.push(`  ${SCOPE_STATEMENT.note}`);
  lines.push("");

  if (typeof path === "string") {
    const pages = readExtract(path);
    const exhibitB = parseSites(pages.get(58) ?? "", 58);
    const exhibitC = parseSites(pages.get(60) ?? "", 60);
    if (exhibitB.length > 0 && exhibitC.length > 0) {
      const check = crossCheck(exhibitB, exhibitC);
      const bpa = findSite(check.agreed, "0571");
      lines.push("AREA, from the published bidding table:");
      lines.push(`  rows agreeing across two exhibit pages: ${check.agreed.length}`);
      if (bpa !== undefined) {
        lines.push(`  Breakfast Point Academy (0571): ${bpa.squareFeet.toLocaleString("en-US")} sq ft`);
        lines.push(`    read from Exhibit B p.${bpa.page} and confirmed on Exhibit C p.60`);
      }
      lines.push("");
    }
  }

  const plant = figure(PLANT_OPS_FY2024_ID);
  if (plant !== undefined) {
    lines.push("FUNDING, from the district's audited statements:");
    lines.push(`  Plant operations FY2024: ${usd(plant.amountUsd)}  (${plant.document} p.${plant.page})`);
    lines.push(`  This is a FUNCTION total, not custodial wages.`);
    lines.push("");
    // The most generous bound the instrument will state.
    for (const wage of [15, 20]) {
      const minutes = maxAffordableMinutes(plant.amountUsd, wage, 1);
      if (minutes === null) continue;
      lines.push(
        `  upper bound at $${wage}/hr, 100% of the function being wages: ` +
          `${Math.round(minutes).toLocaleString("en-US")} min/yr district-wide`,
      );
    }
    lines.push("  (100% is impossible — benefits, supplies and utilities are in this");
    lines.push("   total — so the real figure is lower. The bound is generous on purpose.)");
    lines.push("");
  }

  lines.push("WHAT IS NOT MEASURED:");
  lines.push("  custodial headcount, hourly rates, and hours paid per site are not");
  lines.push("  published in any document fetched so far. Until they are, feasibility");
  lines.push("  is UNMEASURED — not favourable, not unfavourable, unmeasured.");
  lines.push("");

  lines.push("JURISDICTION:");
  lines.push("  This report files structural findings about plans and published");
  lines.push("  numbers. It names no person and reaches no conclusion about any");
  lines.push("  person's conduct. See L3_JURISDICTION.lean for why that boundary is");
  lines.push("  structural rather than a matter of restraint.");

  process.stdout.write(`${lines.join("\n")}\n`);
  return 0;
}

function main(argv: readonly string[]): number {
  let parsed;
  try {
    parsed = parseArgs({
      args: [...argv],
      allowPositionals: true,
      options: {
        extract: { type: "string" },
        area: { type: "string" },
        "paid-minutes": { type: "string" },
        fish: { type: "string" },
        "bid-sqft": { type: "string" },
      },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`bds: ${message}\n\n${USAGE}`);
    return 2;
  }

  const command = parsed.positionals[0];
  if (command === undefined) {
    process.stderr.write(USAGE);
    return 2;
  }

  try {
    switch (command) {
      case "figures":
        return commandFigures();
      case "spec":
        return commandSpec();
      case "sites":
        return commandSites(parsed.values);
      case "breakeven":
        return commandBreakeven(parsed.values);
      case "findings":
        return commandFindings();
      case "actors":
        return commandActors();
      case "fish":
        return commandFish(parsed.values);
      case "reconcile":
        return commandReconcile(parsed.values);
      case "scope":
        return commandScope(parsed.values);
      case "report":
        return commandReport(parsed.values);
      default:
        process.stderr.write(`bds: unknown command "${command}"\n\n${USAGE}`);
        return 2;
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`bds: ${message}\n`);
    return 2;
  }
}

process.exitCode = main(process.argv.slice(2));

// Referenced so the jurisdiction gate is part of the built surface even when no
// command exercises it directly. The tests drive it.
export { admissible, sortViolations };
export type { Finding };
