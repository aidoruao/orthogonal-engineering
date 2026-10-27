/**
 * The addendum and FISH layers.
 *
 * The load-bearing tests are the ones that would catch the two mistakes this
 * pass actually made: reporting a site the addendum had deleted, and a parser
 * that lost rows while appearing to work.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { ADDENDUM_1, AMENDMENTS, applyAmendments, operativeSquareFeet } from "../src/addendum.js";
import {
  compareArea,
  floorCoveringTotals,
  parseFish,
  parsedRoomArea,
  permanentTotalArea,
  reconcile,
  roomsMatching,
  stripColumnCaptions,
  trimToRow,
  type FishReport,
} from "../src/fish.js";
import { parseSites } from "../src/rfp.js";
import type { Site } from "../src/types.js";

/** The base pricing table as the district prints it, Exhibit B p.58. */
const EXHIBIT_B =
  "1 0061 Bay High School $ X 146,638 $ 2 0571 Breakfast Point $ X 108,941 $ " +
  "3 0541 Dean Bozeman $ X 118,023 $ 4 0101 Callaway ES $ X 49,485 $ " +
  "5 9260 R.L. Young Center $ X 16,123 $";

function sites(): readonly Site[] {
  return parseSites(EXHIBIT_B, 58);
}

test("Addendum 1 deletes the site the base document lists", () => {
  const applied = applyAmendments(sites(), AMENDMENTS);
  assert.equal(applied.operative.length, 4);
  assert.equal(applied.removed.length, 1);
  assert.equal(applied.removed[0]?.site.costCenter, "0061");
  assert.equal(applied.removed[0]?.site.name, "Bay High School");
  assert.equal(applied.removed[0]?.by, "RFP-19-10-ADDENDUM-1");
  assert.ok(!applied.operative.some((s) => s.costCenter === "0061"));
});

test("the operative area excludes the deleted site's square footage", () => {
  const applied = applyAmendments(sites(), AMENDMENTS);
  const base = sites().reduce((sum, s) => sum + s.squareFeet, 0);
  assert.equal(operativeSquareFeet(applied), base - 146_638);
});

test("an amendment naming a site the table lacks is reported, not ignored", () => {
  // A deletion that matches nothing means either the parse missed a row or the
  // amendment refers to a different revision. Both are worth knowing.
  const onlyBreakfast = parseSites("2 0571 Breakfast Point $ X 108,941 $", 58);
  const applied = applyAmendments(onlyBreakfast, AMENDMENTS);
  assert.equal(applied.unresolvedDeletions.length, 1);
  assert.equal(applied.unresolvedDeletions[0]?.costCenter, "0061");
});

test("the addendum records the exact text that performs the deletion", () => {
  assert.ok(ADDENDUM_1.text.includes("delete Bay High School from services"));
  assert.deepEqual([...ADDENDUM_1.affectsPages], [5, 58, 60]);
  assert.equal(ADDENDUM_1.date, "2019-05-16");
});

/** A miniature FISH document with the exact textual shape of the real one,
 *  including the two page-break artifacts that broke the first parser. */
const FISH_SAMPLE = [
  "DISTRICT: 3 BAY COUNTY SCHOOL DISTRICT FACILITY: 51-A TEST SCHOOL",
  "MSID Name Status 571 TEST SCHOOL ACADEMY Default",
  "BUILDING: 1 - Administration/Media Owner Light: ADEQUATE",
  "ROOM NET SQ FT DESIGN CODE DESCRIPTION STU STA FLR LOC FLOOR COVER YEAR CONST CONDITION BLDG PAR FAC",
  "100 3392 701 COVERED WALKWAY 0 01 CONCRETE 2008 SATISFACTORY 1 55 51",
  "101 835 304 RECEPTION AREA 0 01 CERAMIC TILE 2008 SATISFACTORY 1 55 51",
  "Permanent 4,227 0",
  // Page break: caption truncated to "CODE DESCRIPTION ..." with preamble glued on.
  "DISTRICT: 3 BAY COUNTY SCHOOL DISTRICT FACILITY: 51-A TEST SCHOOL BUILDING: 2 - Classrooms Owner",
  "CODE DESCRIPTION STU STA FLR LOC FLOOR COVER YEAR CONST CONDITION BLDG PAR FAC",
  "122 971 10 PRIMARY SKILLS LAB (K-3) 0 01 CARPET 2008 SATISFACTORY 2 55 51",
  "123 500 815 STUDENT RESTROOM (MALE) 0 01 CERAMIC TILE 2008 SATISFACTORY 2 55 51",
  "Permanent 1,471 0",
].join(" ");

test("the FISH parser reads every row, including across a page-break caption", () => {
  const report = parseFish(FISH_SAMPLE);
  assert.equal(report.msid, "571");
  // 4 rows: the walkway, the reception, the skills lab, the restroom.
  assert.equal(report.rooms.length, 4, `parsed ${String(report.rooms.length)}`);
  const rooms = report.rooms.map((r) => r.room).sort();
  assert.deepEqual(rooms, ["100", "101", "122", "123"]);
});

test("a one- and two-digit design code is a row, not a parse failure", () => {
  // Three-digit-only matching dropped 87 rows of the real Breakfast Point report.
  const report = parseFish(FISH_SAMPLE);
  const lab = report.rooms.find((r) => r.room === "122");
  assert.ok(lab !== undefined, "row 122 with design code 10 must be parsed");
  assert.equal(lab.designCode, "10");
  assert.equal(lab.netSqFt, 971);
  assert.equal(lab.floorCover, "CARPET");
});

test("page preamble is not absorbed into the row that follows it", () => {
  const report = parseFish(FISH_SAMPLE);
  for (const room of report.rooms) {
    assert.ok(
      /^[A-Z]/.test(room.description),
      `description should start uppercase, got "${room.description}"`,
    );
    assert.ok(
      !room.description.includes("BUILDING"),
      `preamble leaked into description: "${room.description}"`,
    );
  }
});

test("caption stripping and row trimming are the two named repairs", () => {
  assert.equal(
    stripColumnCaptions("ROOM NET SQ FT DESIGN CODE DESCRIPTION STU STA FLR LOC FLOOR COVER YEAR CONST CONDITION BLDG PAR FAC").trim(),
    "",
  );
  assert.equal(
    trimToRow("DISTRICT: 3 FACILITY: 51-A BUILDING: 1 - Admin 101 835 304 RECEPTION AREA 0 01"),
    "101 835 304 RECEPTION AREA 0 01",
  );
});

test("rows are attributed to the building they appear under", () => {
  const report = parseFish(FISH_SAMPLE);
  assert.equal(report.rooms.find((r) => r.room === "100")?.building, "1");
  assert.equal(report.rooms.find((r) => r.room === "122")?.building, "2");
});

test("parsed area reconciles with the report's own printed subtotals", () => {
  const report = parseFish(FISH_SAMPLE);
  assert.equal(parsedRoomArea(report.rooms), 3392 + 835 + 971 + 500);
  assert.equal(permanentTotalArea(report), 4227 + 1471);
  assert.equal(parsedRoomArea(report.rooms), permanentTotalArea(report));
});

test("floor coverings are totalled by area, not by room count", () => {
  const report = parseFish(FISH_SAMPLE);
  const totals = floorCoveringTotals(report.rooms);
  assert.equal(totals.get("CARPET"), 971);
  assert.equal(totals.get("CERAMIC TILE"), 835 + 500);
  assert.equal(totals.get("CONCRETE"), 3392);
});

test("restrooms and classrooms are countable task surfaces", () => {
  const report = parseFish(FISH_SAMPLE);
  assert.equal(roomsMatching(report.rooms, /RESTROOM/).length, 1);
  assert.equal(roomsMatching(report.rooms, /SKILLS LAB/).length, 1);
});

test("an area that agrees is reported as agreeing", () => {
  const report = parseFish(FISH_SAMPLE);
  const comparison = compareArea(parsedRoomArea(report.rooms), report);
  assert.equal(comparison.verdict, "AGREE_WITHIN_ONE_PERCENT");
  assert.equal(comparison.difference, 0);
});

test("an area that disagrees is reported as disagreeing", () => {
  const report = parseFish(FISH_SAMPLE);
  const comparison = compareArea(1000, report);
  assert.equal(comparison.verdict, "DISAGREE");
  assert.ok(comparison.difference > 0);
});

test("reconciliation reports every exclusion and refuses to force a match", () => {
  const report = parseFish(FISH_SAMPLE);
  // Bid area far below the gross net area, so the exclusions cannot close it.
  const rec = reconcile(1000, report);
  assert.equal(rec.grossNetSqFt, 3392 + 835 + 971 + 500);
  assert.equal(rec.steps.length, 4);
  assert.equal(rec.closesGap, false);
  assert.ok(rec.residualSqFt > 0);
  // The walkway is excluded; the restrooms are not silently dropped.
  const walkwayStep = rec.steps[0];
  assert.ok(walkwayStep !== undefined);
  assert.equal(walkwayStep.excludedSqFt, 3392);
  assert.ok(rec.unresolvedBecause.includes("bid area"));
});

/** An empty report, for the degenerate cases. */
const EMPTY: FishReport = {
  facilityCode: "",
  facilityName: "",
  msid: "",
  buildings: [],
  rooms: [],
};

test("reconciliation on an empty report is not a silent pass", () => {
  const rec = reconcile(1000, EMPTY);
  assert.equal(rec.grossNetSqFt, 0);
  assert.equal(rec.closesGap, false);
});

/**
 * Real corpus. Skips explicitly when the FISH report is absent, so a machine
 * without it reports a skip rather than a silent zero.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const REPORT = join(process.cwd(), "..", "evidence", "bds", "site-reports", "B. Point 5-16-19.pdf");
const EXTRACT = join(process.cwd(), "..", "evidence", "bds", "site-reports", "B. Point 5-16-19.txt");

test("real corpus: Breakfast Point FISH reconciles to its own subtotals", (t) => {
  if (!existsSync(REPORT) || !existsSync(EXTRACT)) {
    t.skip(`no FISH extract at ${EXTRACT}`);
    return;
  }
  const report = parseFish(readFileSync(EXTRACT, "utf8"));
  assert.equal(report.msid, "571");

  // Every building that prints a subtotal must match the sum of its own rooms.
  // This is the check that caught the parser losing rows.
  for (const building of report.buildings) {
    if (building.permanentSqFt === null) continue;
    const parsed = report.rooms
      .filter((room) => room.building === building.id)
      .reduce((sum, room) => sum + room.netSqFt, 0);
    assert.equal(
      parsed,
      building.permanentSqFt,
      `building ${building.id}: parsed ${String(parsed)} vs printed ${String(building.permanentSqFt)}`,
    );
  }

  assert.ok(report.rooms.length >= 380, `only ${String(report.rooms.length)} rooms parsed`);
  assert.ok(roomsMatching(report.rooms, /RESTROOM/).length >= 80);
});
