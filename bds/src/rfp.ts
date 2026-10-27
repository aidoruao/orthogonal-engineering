/**
 * Parse the district's own published specification.
 *
 * The source is RFP #19-10, "Contract Cleaning Services", Bay District Schools,
 * 71 pages. Two things are extracted and nothing is inferred:
 *
 *   1. The square-footage table, which the district publishes for bidding. It
 *      appears twice — page 58 (Exhibit B) and page 60 (Exhibit C) — so the
 *      parser reads both and cross-checks them against each other. Agreement is
 *      corroboration *within a single primary*; disagreement is a finding in
 *      its own right, and is reported rather than resolved.
 *
 *   2. The stated minimum frequencies, from Section 13. The specification gives
 *      them as words ("each service day", "once per week", "twice per year no
 *      less than six months apart"), and those words have minimum annual counts.
 *      The basis for each number is carried alongside it, quoted from the
 *      document, so a reader can check the arithmetic against the prose.
 *
 * What the parser deliberately does NOT extract: minutes per square foot. The
 * district's specification does not state task times, and a tool that invented
 * them would be manufacturing the very number its conclusion rests on. Those
 * figures are supplied separately, with their own provenance, or the demand
 * calculation reports `NO_TASK_TIMES`.
 */

import type { FrequencyBasis, Site, SpecTask } from "./types.js";

/** A row of the published square-footage table. */
const SITE_ROW =
  /(\d{1,2})\s+(\d{4})\s+([A-Za-z][A-Za-z0-9 .,'#()-]*?)\s+\$\s*X\s+([\d,]+)/g;

function toInt(digits: string): number {
  return Number.parseInt(digits.replace(/,/g, ""), 10);
}

export type ParsedSites = {
  readonly sites: readonly Site[];
  /** Rows read per page, for the cross-check report. */
  readonly byPage: ReadonlyMap<number, readonly Site[]>;
};

/**
 * Read every site row from a page's text.
 *
 * The regex is anchored on the `$ X` placeholder the district prints where the
 * bidder writes a price, because that marker is what actually distinguishes a
 * pricing-sheet row from prose that happens to contain numbers. A row that does
 * not carry it is not a pricing row.
 */
export function parseSites(pageText: string, page: number): readonly Site[] {
  const sites: Site[] = [];
  const pattern = new RegExp(SITE_ROW.source, "g");
  for (;;) {
    const match = pattern.exec(pageText);
    if (match === null) break;
    const [, , costCenter, rawName, rawArea] = match;
    if (costCenter === undefined || rawName === undefined || rawArea === undefined) {
      continue;
    }
    const squareFeet = toInt(rawArea);
    if (!Number.isFinite(squareFeet) || squareFeet <= 0) continue;
    sites.push({
      costCenter,
      name: rawName.replace(/\s+/g, " ").trim(),
      squareFeet,
      page,
    });
  }
  return sites;
}

export type CrossCheck = {
  readonly agreed: readonly Site[];
  readonly disagreed: readonly {
    readonly costCenter: string;
    readonly first: Site;
    readonly second: Site;
  }[];
  readonly onlyInFirst: readonly Site[];
  readonly onlyInSecond: readonly Site[];
  /**
   * Cost centres that appear on more than one row within a single exhibit.
   *
   * This is not an anomaly to be deduplicated away: the district genuinely
   * assigns cost centre 9100 to four separate buildings. Keying a match on the
   * cost centre alone therefore conflates them, and an earlier version of this
   * function silently dropped three of the twelve published rows because of it.
   * The multiplicity is reported so the drop cannot recur unnoticed.
   */
  readonly repeatedCostCenters: readonly {
    readonly costCenter: string;
    readonly count: number;
  }[];
};

/** Names differ between the exhibits ("Breakfast Point" / "Breakfast Point
 *  Academy"), so comparison uses the first token run, lowercased. */
function nameKey(site: Site): string {
  return site.name.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().split(" ")[0] ?? "";
}

/**
 * Compare the two published tables.
 *
 * Matching is by `(costCenter, ordinal within that cost centre)`, not by cost
 * centre alone, because cost centre 9100 covers four buildings. Rows are paired
 * in the order each exhibit prints them, which is stable within a document.
 *
 * Both exhibits are the district's own document, so this is internal
 * consistency, not independent corroboration, and the README says so. It still
 * catches a transcription error on either page, which is the failure mode that
 * matters for a parser.
 */
export function crossCheck(
  first: readonly Site[],
  second: readonly Site[],
): CrossCheck {
  const group = (sites: readonly Site[]): Map<string, Site[]> => {
    const map = new Map<string, Site[]>();
    for (const site of sites) {
      const bucket = map.get(site.costCenter);
      if (bucket === undefined) map.set(site.costCenter, [site]);
      else bucket.push(site);
    }
    return map;
  };

  const a = group(first);
  const b = group(second);
  const agreed: Site[] = [];
  const disagreed: { costCenter: string; first: Site; second: Site }[] = [];
  const onlyInFirst: Site[] = [];
  const onlyInSecond: Site[] = [];
  const repeatedCostCenters: { costCenter: string; count: number }[] = [];

  for (const [centre, rows] of a) {
    if (rows.length > 1) repeatedCostCenters.push({ costCenter: centre, count: rows.length });
  }

  for (const [centre, rowsA] of a) {
    const rowsB = b.get(centre) ?? [];
    const shared = Math.min(rowsA.length, rowsB.length);
    for (let index = 0; index < shared; index += 1) {
      const siteA = rowsA[index];
      const siteB = rowsB[index];
      if (siteA === undefined || siteB === undefined) continue;
      if (siteA.squareFeet === siteB.squareFeet) {
        agreed.push(siteA);
      } else if (nameKey(siteA) === nameKey(siteB)) {
        // Same building, different area: a genuine transcription or revision
        // difference, and worth reporting as such.
        disagreed.push({ costCenter: centre, first: siteA, second: siteB });
      } else {
        // Same cost centre, different buildings in different order. Not a
        // disagreement; report each side separately rather than pairing them.
        onlyInFirst.push(siteA);
        onlyInSecond.push(siteB);
      }
    }
    for (let index = shared; index < rowsA.length; index += 1) {
      const siteA = rowsA[index];
      if (siteA !== undefined) onlyInFirst.push(siteA);
    }
    for (let index = shared; index < rowsB.length; index += 1) {
      const siteB = rowsB[index];
      if (siteB !== undefined) onlyInSecond.push(siteB);
    }
  }
  for (const centre of b.keys()) {
    if (!a.has(centre)) {
      for (const siteB of b.get(centre) ?? []) onlyInSecond.push(siteB);
    }
  }

  const bySite = (x: Site, y: Site): number => {
    if (x.costCenter !== y.costCenter) return x.costCenter < y.costCenter ? -1 : 1;
    return x.squareFeet - y.squareFeet;
  };

  return {
    agreed: [...agreed].sort(bySite),
    disagreed,
    onlyInFirst: [...onlyInFirst].sort(bySite),
    onlyInSecond: [...onlyInSecond].sort(bySite),
    repeatedCostCenters: [...repeatedCostCenters].sort((x, y) =>
      x.costCenter < y.costCenter ? -1 : 1,
    ),
  };
}

/**
 * The frequency vocabulary of Section 13, with the minimum each word denotes
 * and the clause that fixes it.
 *
 * The specification is careful to say "at a minimum of", so these are floors,
 * not estimates. Where the source gives a period ("no less than six (6) months
 * apart") the annual count follows arithmetically and the quote is carried.
 */
export const FREQUENCY_BASIS: readonly FrequencyBasis[] = [
  {
    label: "Daily",
    section: "13.3.4",
    perYear: 180,
    quote:
      "Daily : Work to be performed each and every day of the week.",
  },
  {
    label: "Weekly",
    section: "13.4.2",
    perYear: 36,
    quote:
      "Weekly: Following services will be performed in every assigned service areas at a minimum of once per week",
  },
  {
    label: "Monthly",
    section: "13.4.3",
    perYear: 12,
    quote:
      "Monthly: Following services will be performed in every assigned service areas at a minimum of once per month",
  },
  {
    label: "Semi-Annually",
    section: "13.4.4",
    perYear: 2,
    quote:
      "Semi - Annually: Following services will be performed in every assigned service areas at a minimum of twice per year no less than six (6) months apart",
  },
  {
    label: "Annually",
    section: "13.4.5",
    perYear: 1,
    quote:
      "Annually: Following services will be performed in every assigned service areas at a minimum of once per year no less than twelve (12) months apart",
  },
] as const;

/**
 * Why `Daily` is 180 rather than 365.
 *
 * The specification scopes daily tasks to service days: "each service day when
 * school is in session and students and/or staff are present" (13.5.1, 13.6.1).
 * A Florida school year is 180 instructional days. That is a *district-external*
 * constant, and it is declared here rather than buried: if the calendar differs,
 * daily demand scales by the ratio, and every downstream number changes.
 */
export const SERVICE_DAYS_PER_YEAR = 180;
export const SERVICE_DAYS_BASIS =
  "Florida instructional year = 180 days. Not stated in RFP 19-10; declared " +
  "here as an external constant. Daily demand scales linearly with it.";

/**
 * The specification's daily/weekly/monthly task list for general assigned
 * areas (Section 13.4), transcribed clause by clause.
 *
 * Only clauses that (a) state a period and (b) describe physical work are
 * included. Clauses that assign responsibility without a task (13.4.1.11,
 * "secure any exterior doors and turn off lights") are excluded because their
 * labor content is not a cleaning task and cannot be estimated on an area
 * basis; excluding them *understates* demand, which is the safe direction for
 * this instrument.
 */
export const SPEC_TASKS: readonly SpecTask[] = [
  { id: "13.4.1.1", section: "13.4.1", description: "Empty garbage/recycling wastebaskets; replace liners daily", frequencyPerYear: 180 },
  { id: "13.4.1.2", section: "13.4.1", description: "Spot clean desk tops", frequencyPerYear: 180 },
  { id: "13.4.1.3", section: "13.4.1", description: "Clean and sanitize counters and sinks", frequencyPerYear: 180 },
  { id: "13.4.1.4", section: "13.4.1", description: "Clean all dry-erase/chalkboards", frequencyPerYear: 180 },
  { id: "13.4.1.5", section: "13.4.1", description: "Sweep and/or dust mop all composition floors", frequencyPerYear: 180 },
  { id: "13.4.1.6", section: "13.4.1", description: "Spot mop composition floors with all-purpose cleaner", frequencyPerYear: 180 },
  { id: "13.4.1.7", section: "13.4.1", description: "Vacuum all carpets", frequencyPerYear: 180 },
  { id: "13.4.1.10", section: "13.4.1", description: "Remove fingerprints from doors, frames, switches, handles, glass", frequencyPerYear: 180 },
  { id: "13.4.2.1", section: "13.4.2", description: "Low dust all horizontal surfaces to hand height", frequencyPerYear: 36 },
  { id: "13.4.2.2", section: "13.4.2", description: "Sweep, wipe and damp clean baseboards", frequencyPerYear: 36 },
  { id: "13.4.2.3", section: "13.4.2", description: "Dust and damp clean window ledges", frequencyPerYear: 36 },
  { id: "13.4.2.7", section: "13.4.2", description: "Mop all composition floors", frequencyPerYear: 36 },
  { id: "13.4.2.8", section: "13.4.2", description: "Vacuum all carpeted areas", frequencyPerYear: 36 },
  { id: "13.4.3.1", section: "13.4.3", description: "High dust above hand height with 6' ladder", frequencyPerYear: 12 },
  { id: "13.4.3.4", section: "13.4.3", description: "Dust blinds", frequencyPerYear: 12 },
  { id: "13.4.4.1", section: "13.4.4", description: "Clean student desks and chairs", frequencyPerYear: 2 },
  { id: "13.4.4.4", section: "13.4.4", description: "Clean upholstered furniture", frequencyPerYear: 2 },
  { id: "13.4.5.1", section: "13.4.5", description: "Clean all carpets and rugs", frequencyPerYear: 1 },
  { id: "13.4.5.2", section: "13.4.5", description: "Strip and refinish all floors", frequencyPerYear: 1 },
  { id: "13.5.1.4", section: "13.5.1", description: "Cafeteria: sweep entire floor and mop", frequencyPerYear: 180 },
  { id: "13.6.1.10", section: "13.6.1", description: "Restrooms: sweep floors daily", frequencyPerYear: 180 },
  { id: "13.6.1.11", section: "13.6.1", description: "Restrooms: mop floors with germicidal disinfectant daily", frequencyPerYear: 180 },
  { id: "13.6.2.5", section: "13.6.2", description: "Restrooms: detailed cleaning of all floors with germicidal disinfectant", frequencyPerYear: 36 },
  { id: "13.6.4.1", section: "13.6.4", description: "Restrooms: strip and/or refinish all floors", frequencyPerYear: 2 },
] as const;

/** Find a site by cost centre. */
export function findSite(
  sites: readonly Site[],
  costCenter: string,
): Site | undefined {
  return sites.find((site) => site.costCenter === costCenter);
}
