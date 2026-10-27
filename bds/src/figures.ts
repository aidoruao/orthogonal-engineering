/**
 * Figures read out of the district's own audited financial statements.
 *
 * Every entry here carries the page it was read from and the exact text it was
 * read from, so a reader can open the same page of the same document and check
 * the transcription. Nothing in this file is estimated, interpolated, or
 * "approximately" anything: a number either appears on a page or it is absent.
 *
 * SCOPE WARNING, and it is the reason this file exists rather than a hardcoded
 * constant: `Plant operations` is a *function* total. It includes salaries,
 * benefits, utilities, supplies, and purchased services. It is not custodial
 * wage spend, and using it as though it were is an overstatement of available
 * labor. `maxAffordableMinutes` therefore treats any share of it as an upper
 * bound, and the report says so on every line where it is used.
 */

export type AuditedFigure = {
  /** Stable identifier. */
  readonly id: string;
  /** What the figure is, in the audit's own terminology. */
  readonly label: string;
  /** Fiscal year the figure reports. */
  readonly fiscalYear: number;
  /** Whole US dollars. */
  readonly amountUsd: number;
  /** Document the figure was read from, relative to evidence/bds. */
  readonly document: string;
  /** Page number within that document. */
  readonly page: number;
  /** The exact text, so the transcription can be checked against the page. */
  readonly text: string;
};

/**
 * Read from `dsb_audit_2024.pdf` page 14 (printed page "- 10 -"), "Statement of
 * Activities", function/program expenses column for the year ended June 30.
 */
export const FIGURES: readonly AuditedFigure[] = [
  {
    id: "plant-ops-fy2024",
    label: "Plant operations",
    fiscalYear: 2024,
    amountUsd: 21729416,
    document: "dsb_audit_2024.pdf",
    page: 14,
    text: "Plant operations 21,729,416 20,451,916 - - 21,729,416 20,451,916",
  },
  {
    id: "plant-ops-fy2023",
    label: "Plant operations",
    fiscalYear: 2023,
    amountUsd: 20451916,
    document: "dsb_audit_2024.pdf",
    page: 14,
    text: "Plant operations 21,729,416 20,451,916 - - 21,729,416 20,451,916",
  },
  {
    id: "maintenance-fy2024",
    label: "Maintenance services",
    fiscalYear: 2024,
    amountUsd: 6687135,
    document: "dsb_audit_2024.pdf",
    page: 14,
    text: "Maintenance services 6,687,135 5,769,630 - - 6,687,135 5,769,630",
  },
  {
    id: "maintenance-fy2023",
    label: "Maintenance services",
    fiscalYear: 2023,
    amountUsd: 5769630,
    document: "dsb_audit_2024.pdf",
    page: 14,
    text: "Maintenance services 6,687,135 5,769,630 - - 6,687,135 5,769,630",
  },
  {
    id: "plant-ops-fy2022",
    label: "Plant operations",
    fiscalYear: 2022,
    amountUsd: 18144339,
    document: "dsb_audit_2022.pdf",
    page: 14,
    text: "Plant operations 18,144,339 18,546,921 - - 18,144,339 18,546,921",
  },
  {
    id: "maintenance-fy2022",
    label: "Maintenance services",
    fiscalYear: 2022,
    amountUsd: 5259828,
    document: "dsb_audit_2022.pdf",
    page: 14,
    text: "Maintenance services 5,259,828 5,368,010 - - 5,259,828 5,368,010",
  },
] as const;

/** Look up one figure, or undefined. Never invents a default. */
export function figure(id: string): AuditedFigure | undefined {
  return FIGURES.find((entry) => entry.id === id);
}

/** The figures the report uses for the break-even bound. */
export const PLANT_OPS_FY2024_ID = "plant-ops-fy2024";
export const MAINTENANCE_FY2024_ID = "maintenance-fy2024";

/**
 * What the district's own document says about its scope, read from RFP 19-10
 * page 5. This is the sentence that bounds every claim in this instrument: the
 * cleaning specification covers *contract* cleaning at seven of forty
 * facilities, not the whole district's custodial operation.
 */
export const SCOPE_STATEMENT = {
  page: 5,
  text:
    "Currently , ONLY ( 7 ) seven of the (40) forty BDS schools, administra  tive and support facilities are utiliz  ing contract cleaning services a s listed herein",
  note:
    "The specification governs contract cleaning at seven sites. A finding about " +
    "these seven says nothing about the other thirty-three, and nothing about " +
    "in-house custodial staffing anywhere.",
} as const;
