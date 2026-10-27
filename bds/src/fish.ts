/**
 * FISH report parser — the Florida Inventory of School Houses.
 *
 * The FISH report is the state facility inventory: per building, room by room,
 * with net square footage, room function, floor covering, student stations, and
 * construction year. It is a different document from the RFP's pricing table and
 * was produced independently of it, which makes it useful for two things:
 *
 *   1. **Room-level task surfaces.** The RFP's specification states tasks per
 *      room type ("sweep and/or dust mop all composition floors", "vacuum all
 *      carpets"). Counting rooms and floor coverings converts that specification
 *      into countable units, which is more informative than a single area figure.
 *
 *   2. **An independent area for the same campus.** The pricing table gives
 *      108,941 sq ft for Breakfast Point Academy. The FISH report totals 175,675
 *      net sq ft across five buildings. Both are the district's own documents
 *      from the same solicitation period. The discrepancy is reported, not
 *      reconciled — reconciling it would require knowing which rooms the bid
 *      area excludes, and no fetched document says.
 *
 * Parsing note. The extracted text runs each row together with no delimiter:
 *
 *     `100 3392 701 COVERED WALKWAY 0 01 CONCRETE 2008 SATISFACTORY 1 55 51`
 *
 * A regex anchored at the left over-matches, because the description is free
 * text. So rows are located by their **tail** — floor covering, year, condition,
 * and three trailing codes — and the block before each tail is one row. That is
 * the only anchor whose position does not depend on the description's length.
 */

import type { Site } from "./types.js";

/** Floor coverings the FISH inventory prints. Order matters for reporting only. */
export const FLOOR_COVERINGS = [
  "CARPET",
  "CERAMIC TILE",
  "COMPOSITION TILE",
  "QUARRY TILE",
  "CONCRETE",
  "VINYL",
  "TERRAZZO",
  "WOOD",
  "OTHER",
] as const;

export type FloorCovering = (typeof FLOOR_COVERINGS)[number];

export type FishRoom = {
  /** Room number as printed, e.g. "104A". */
  readonly room: string;
  /** Net square footage as printed. */
  readonly netSqFt: number;
  /** Three-digit FISH design code. */
  readonly designCode: string;
  /** Room function, uppercase, as printed. */
  readonly description: string;
  readonly studentStations: number;
  readonly staffStations: number;
  readonly floorCover: FloorCovering;
  readonly yearConstructed: number;
  readonly condition: string;
  readonly building: string;
};

export type FishBuilding = {
  readonly id: string;
  readonly name: string;
  /** Total from the "Permanent N" line, when the report prints one. */
  readonly permanentSqFt: number | null;
  readonly permanentStudentStations: number | null;
};

export type FishReport = {
  readonly facilityCode: string;
  readonly facilityName: string;
  /** Master School ID, e.g. "571" for Breakfast Point Academy. */
  readonly msid: string;
  readonly buildings: readonly FishBuilding[];
  readonly rooms: readonly FishRoom[];
};

const COVER_ALTERNATION = FLOOR_COVERINGS.join("|");

/** Tail anchor: floor cover, year, condition, and the three trailing codes. */
const ROW_TAIL = new RegExp(
  `\\b(${COVER_ALTERNATION})\\s+(\\d{4})\\s+(SATISFACTORY|UNSATISFACTORY|POOR|GOOD)\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)`,
  "g",
);

/** Building header, which appears before that building's rows. */
const BUILDING_HEADER = /BUILDING:\s*(\d+)\s*-\s*([A-Za-z/ ]+)/g;

/** Per-building total line. */
const PERMANENT_TOTAL = /Permanent\s+([\d,]+)\s+(\d+)/g;

const ROOM_NUMBER = /^\d{2,5}[A-Z]?$/;

/**
 * Column captions, repeated at every page break. They are removed before row
 * parsing because a caption immediately preceding a row is otherwise absorbed
 * into that row's block and the row is lost.
 *
 * Three variants occur, because page breaks fall mid-caption:
 * "ROOM NET SQ FT DESIGN CODE DESCRIPTION STU STA ..."
 * "DESIGN CODE DESCRIPTION STU STA ..."
 * "CODE DESCRIPTION STU STA ..."
 */
const COLUMN_CAPTION = new RegExp(
  "(?:ROOM\\s+)?(?:NET\\s+SQ\\s+FT\\s+)?(?:(?:DE)?SIGN\\s+CODE|CODE)\\s+DESCRIPTION" +
    "\\s+STU\\s+STA\\s+FLR\\s+LOC\\s+FLOOR\\s+COVER\\s+YEAR\\s+CONST\\s+CONDITION" +
    "\\s+BLDG\\s+PAR\\s+FAC",
  "g",
);

/**
 * Strip the repeated column captions.
 *
 * Exported because the tests must assert that a caption does not become a row:
 * that is the failure mode which silently dropped 26 rows when this parser was
 * first written.
 */
export function stripColumnCaptions(text: string): string {
  return text.replace(COLUMN_CAPTION, " ").replace(/\s+/g, " ");
}

/** A FISH design code is one to three digits. Most are three, but `10` and `61`
 *  occur in the Breakfast Point report, and a three-digit-only rule dropped 87
 *  rows. */
const DESIGN_CODE = /^\d{1,3}$/;

/** Candidate start of a room row: room, net area, design code, then the first
 *  character of an uppercase description. */
const ROW_START = /\b\d{2,5}[A-Z]?\s+\d{1,6}\s+\d{1,3}\s+[A-Z]/g;

/**
 * Trim a block to just its row.
 *
 * Each page is preceded by a facility preamble ("DISTRICT: 3 BAY COUNTY SCHOOL
 * DISTRICT FACILITY: 51-A BREAKFAST POINT SCHOOL BUILDING: 1 - ..."), which is
 * absorbed into the block that follows it. The row is the **last** row-shaped
 * triple in the block, so the block is sliced from there. 26 rows were lost
 * before this was handled.
 */
export function trimToRow(block: string): string {
  let last = -1;
  for (const match of block.matchAll(ROW_START)) {
    if (match.index !== undefined) last = match.index;
  }
  return last < 0 ? block : block.slice(last);
}

function toInt(digits: string): number {
  return Number.parseInt(digits.replace(/,/g, ""), 10);
}

/**
 * Parse one FISH report.
 *
 * `text` must be the whole document with pages concatenated in order, because
 * buildings and their totals are separated by page breaks that the extractor
 * normalizes away.
 */
export function parseFish(text: string): FishReport {
  const cleaned = stripColumnCaptions(text);
  const facilityCode = /FACILITY:\s*([0-9A-Z-]+)/.exec(cleaned)?.[1] ?? "";
  const msid = /MSID\s+Name\s+Status\s+(\d+)/.exec(cleaned)?.[1] ?? "";
  const facilityName =
    /FACILITY:\s*[0-9A-Z-]+\s+([A-Z][A-Z ]+?)\s+Primary Use/i.exec(cleaned)?.[1] ??
    /FACILITY:\s*[0-9A-Z-]+\s+([A-Z][A-Z ]+)/.exec(cleaned)?.[1] ??
    "";

  // Building headers, with their positions, so each row can be attributed to the
  // building it appears under.
  const headers = [...cleaned.matchAll(BUILDING_HEADER)]
    .filter((m) => m[1] !== undefined && m[2] !== undefined)
    .map((m) => ({
      index: m.index ?? 0,
      id: m[1] ?? "",
      name: (m[2] ?? "").trim(),
    }))
    // A header is only a real one if no other header shares its position and it
    // is not the repeated column caption.
    .filter((h) => !h.name.startsWith("ROOM NET SQ FT"));

  const permanentTotals = [...cleaned.matchAll(PERMANENT_TOTAL)].map((m) => ({
    index: m.index ?? 0,
    sqFt: toInt(m[1] ?? "0"),
    stations: toInt(m[2] ?? "0"),
  }));

  const rooms: FishRoom[] = [];
  const tails = [...cleaned.matchAll(ROW_TAIL)];
  let previousEnd = 0;

  for (const tail of tails) {
    const rawBlock = cleaned.slice(previousEnd, tail.index ?? previousEnd).trim();
    previousEnd = (tail.index ?? 0) + tail[0].length;
    const block = trimToRow(rawBlock);

    const tokens = block.split(/\s+/);
    const room = tokens[0];
    if (room === undefined || !ROOM_NUMBER.test(room)) continue;

    const netSqFt = Number.parseInt(tokens[1] ?? "", 10);
    if (!Number.isFinite(netSqFt) || netSqFt < 0 || netSqFt > 100_000) continue;

    const designCode = tokens[2] ?? "";
    if (!DESIGN_CODE.test(designCode)) continue;

    // Tokens between the design code and the trailing STU/STA pair are the
    // description. Rows end with `<stu> <sta>`, so drop the last two.
    const middle = tokens.slice(3);
    if (middle.length < 3) continue;
    const description = middle.slice(0, -2).join(" ");
    const studentStations = Number.parseInt(middle[middle.length - 2] ?? "0", 10);
    const staffStations = Number.parseInt(middle[middle.length - 1] ?? "0", 10);
    if (description.trim() === "") continue;

    const cover = tail[1] as FloorCovering;
    const yearConstructed = Number.parseInt(tail[2] ?? "0", 10);
    const condition = tail[3] ?? "";

    // Attribute to the last header before this row.
    let building = "";
    for (const header of headers) {
      if (header.index < (tail.index ?? 0)) building = header.id;
      else break;
    }

    rooms.push({
      room,
      netSqFt,
      designCode,
      description,
      studentStations: Number.isFinite(studentStations) ? studentStations : 0,
      staffStations: Number.isFinite(staffStations) ? staffStations : 0,
      floorCover: cover,
      yearConstructed,
      condition,
      building,
    });
  }

  // Pair each building header with the next "Permanent" total, which is the
  // building's summary. Order is preserved by position.
  const buildings: FishBuilding[] = [];
  const seen = new Set<string>();
  for (const header of headers) {
    if (seen.has(header.id)) continue;
    seen.add(header.id);
    const total = permanentTotals.find((entry) => entry.index > header.index);
    buildings.push({
      id: header.id,
      name: header.name,
      permanentSqFt: total === undefined ? null : total.sqFt,
      permanentStudentStations: total === undefined ? null : total.stations,
    });
  }

  return { facilityCode, facilityName: facilityName.trim(), msid, buildings, rooms };
}

/** Net square footage by floor covering. */
export function floorCoveringTotals(
  rooms: readonly FishRoom[],
): ReadonlyMap<FloorCovering, number> {
  const totals = new Map<FloorCovering, number>();
  for (const room of rooms) {
    totals.set(room.floorCover, (totals.get(room.floorCover) ?? 0) + room.netSqFt);
  }
  return totals;
}

/** Sum of parsed room areas. */
export function parsedRoomArea(rooms: readonly FishRoom[]): number {
  return rooms.reduce((sum, room) => sum + room.netSqFt, 0);
}

/** Sum of the report's own per-building "Permanent" totals. */
export function permanentTotalArea(report: FishReport): number {
  return report.buildings.reduce((sum, b) => sum + (b.permanentSqFt ?? 0), 0);
}

/** Rooms whose function matches a pattern, for task-surface counts. */
export function roomsMatching(
  rooms: readonly FishRoom[],
  pattern: RegExp,
): readonly FishRoom[] {
  return rooms.filter((room) => pattern.test(room.description));
}

/**
 * The reconciliation between the two published areas for one campus.
 *
 * Not a judgement: it reports both figures, the difference, and the ratio, and
 * names what is unknown. The instrument will not infer which figure is "right"
 * because no fetched document says which rooms the bid area excludes.
 */
export type AreaComparison = {
  readonly pricingSheetSqFt: number;
  readonly fishNetSqFt: number;
  readonly fishPermanentTotalSqFt: number;
  readonly difference: number;
  readonly ratio: number;
  readonly verdict: "AGREE_WITHIN_ONE_PERCENT" | "DISAGREE";
};

export function compareArea(
  pricingSheetSqFt: number,
  report: FishReport,
): AreaComparison {
  const parsed = parsedRoomArea(report.rooms);
  const permanent = permanentTotalArea(report);
  const fishNetSqFt = permanent > 0 ? permanent : parsed;
  const difference = fishNetSqFt - pricingSheetSqFt;
  const ratio = pricingSheetSqFt === 0 ? 0 : fishNetSqFt / pricingSheetSqFt;
  const withinOnePercent =
    pricingSheetSqFt > 0 &&
    Math.abs(difference) <= Math.max(1, pricingSheetSqFt * 0.01);
  return {
    pricingSheetSqFt,
    fishNetSqFt,
    fishPermanentTotalSqFt: permanent,
    difference,
    ratio,
    verdict: withinOnePercent ? "AGREE_WITHIN_ONE_PERCENT" : "DISAGREE",
  };
}

/** The pricing-sheet row for a FISH report, matched on MSID. */
export function siteForReport(
  sites: readonly Site[],
  report: FishReport,
): Site | undefined {
  return sites.find((site) => site.costCenter === report.msid);
}

/**
 * Space that a cleaning contract would not normally cover at daily frequency.
 *
 * This list exists so the reconciliation attempt is explicit and bounded rather
 * than open-ended. Each category is a room function the FISH inventory names;
 * excluding them is a defensible first pass, not a claim that they are never
 * cleaned.
 */
export const NON_DAILY_CATEGORIES: readonly {
  readonly label: string;
  readonly pattern: RegExp;
}[] = [
  { label: "covered walkway", pattern: /COVERED WALKWAY/ },
  { label: "mechanical", pattern: /MECHANICAL/ },
  { label: "storage", pattern: /STORAGE/ },
  { label: "covered play area", pattern: /COVERED PLAY/ },
];

export type ReconciliationStep = {
  readonly label: string;
  readonly excludedSqFt: number;
  readonly remainingSqFt: number;
};

export type Reconciliation = {
  readonly grossNetSqFt: number;
  readonly steps: readonly ReconciliationStep[];
  readonly residualSqFt: number;
  readonly residualRatio: number;
  readonly closesGap: boolean;
  /** What would settle the question, since arithmetic alone does not. */
  readonly unresolvedBecause: string;
};

/**
 * Attempt to reconcile the FISH area against the bid area by excluding space a
 * cleaning contract would not normally service.
 *
 * The exclusions are applied cumulatively and every intermediate figure is
 * reported, so a reader can see exactly where the attempt lands. If the
 * remaining area still exceeds the bid area, that is recorded as unresolved:
 * the instrument does **not** search for further exclusions until the two
 * numbers meet, because that is fitting, not auditing.
 */
export function reconcile(
  bidSqFt: number,
  report: FishReport,
): Reconciliation {
  const gross = parsedRoomArea(report.rooms);
  const steps: ReconciliationStep[] = [];
  let remaining = gross;
  for (const category of NON_DAILY_CATEGORIES) {
    const excluded = report.rooms
      .filter((room) => category.pattern.test(room.description))
      .reduce((sum, room) => sum + room.netSqFt, 0);
    remaining -= excluded;
    steps.push({ label: category.label, excludedSqFt: excluded, remainingSqFt: remaining });
  }
  const residual = remaining - bidSqFt;
  const ratio = bidSqFt === 0 ? 0 : remaining / bidSqFt;
  return {
    grossNetSqFt: gross,
    steps,
    residualSqFt: residual,
    residualRatio: ratio,
    closesGap: Math.abs(residual) <= Math.max(1, bidSqFt * 0.01),
    unresolvedBecause:
      "No fetched document states what the bid area measures. The bid area is " +
      "described in RFP 19-10 §14.1.2 only as \"the most recent and up to date " +
      "information available to BDS\", and §12.2.2 says it is accurate \"to the " +
      "best knowledge of BDS\" and \"for contract and bidding purposes only\". " +
      "Settling this needs either the executed contract's scope schedule or a " +
      "district statement of which rooms the bid area excludes.",
  };
}
