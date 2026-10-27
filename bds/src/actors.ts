/**
 * Officials of record — the attribution layer, jurisdiction-clean.
 *
 * IOW 2 says: "do not be afraid this time to enumerate names, facts, righteous
 * indignation covers the complete glass box auditing of responsible actors."
 *
 * This module does exactly that, and stops exactly where `L3_JURISDICTION.lean`
 * says it must. The distinction is structural rather than a matter of restraint:
 *
 *   ATTRIBUTION (fileable)   — "X held office Y, in period Z, per document D
 *                              at page P." Checkable against the document.
 *   CONDEMNATION (not)       — "X is guilty / at fault / corrupt." No document
 *                              reports the state of a soul, so no evidence bears
 *                              on it, and `Subject` has no member for it.
 *
 * An `OfficeHolding` is deliberately *not* a `Finding`. It has no severity field
 * and no falsifier, because it asserts nothing that could be false in the way a
 * finding can: either the document says the person held the office or it does
 * not. That makes it weaker than a finding, and the type says so.
 *
 * What this module explicitly does NOT record: that any named person caused the
 * area discrepancy, approved a specific figure, or is responsible for anything.
 * No fetched document says that. Recording it would be the inference the arc
 * forbids.
 */

import type { Source } from "./types.js";

/**
 * A documented office-holding.
 *
 * Every field must be readable off the page it cites. If a reader cannot open
 * the document, go to the page, and find the name beside the office, the record
 * is wrong.
 */
export type OfficeHolding = {
  /** Person's name exactly as printed. */
  readonly name: string;
  /** Office or role exactly as printed beside the name.
   *  Where the document gives no title beside the name, this is the heading that
   *  establishes it, and `officeSource` says so. */
  readonly office: string;
  /** Where the office comes from: printed beside the name, or the section heading. */
  readonly officeSource: "printed_beside_name" | "heading";
  /** Board district number, where the document assigns one. */
  readonly district: string | null;
  /** Fiscal or calendar period the document says this applied to. */
  readonly period: string;
  /** Document the record was read from, relative to evidence/bds. */
  readonly document: string;
  readonly page: number;
  /** The exact text, so the transcription can be checked against the page. */
  readonly text: string;
  /**
   * What the person is attributed with. Kept to office-holding and document
   * authorship, because those are the only things the fetch establishes.
   */
  readonly attributedWith:
    | "office_held"
    | "document_author"
    | "point_of_contact";
};

/**
 * From `dsb_audit_2024.pdf` p.2, "BOARD MEMBERS AND SUPERINTENDENT".
 *
 * The document lists the board and superintendent who served during fiscal year
 * 2023–2024. It is the district's own audited statement.
 */
const AUDIT_2024_TEXT =
  "BOARD MEMBERS AND SUPERINTENDENT Board members and the Superintendent who " +
  "served during the 2023 - 2024 fiscal year are listed below: District No. " +
  "Jerry Register , Vice - chairman 1 Ann Leonard 2 Chris Moore 3 Winston " +
  "Chester 4 Steve Moss , Chair 5 Mark McQueen , Superintendent";

/** From `dsb_audit_2022.pdf` p.2, the same statement one period earlier. */
const AUDIT_2022_PERIOD = "2021-2022";

const AUDIT_2022_TEXT =
  "BOARD MEMBERS AND SUPERINTENDENT Board members and the Superintendent who " +
  "served during the 2021 - 2022 fiscal year are listed below: District No. " +
  "Jerry Register , Vice - chairman 1 Ann Leonard 2 Chris Moore 3 Winston " +
  "Chester 4 Steve Moss , Chair 5 William V. Husfelt III, Superintendent";

/**
 * From RFP 19-10 p.1 (cover) and p.6, which name the officials of the
 * solicitation.
 */
const RFP_OFFICIALS_TEXT =
  "William V. Husfelt III, Superintendent l Jim Loyed, Chief Financial Officer";

export const OFFICE_HOLDINGS: readonly OfficeHolding[] = [
  // ---- FY2021-2022, from the audited statements ------------------------------
  //
  // Same board as FY2023-24; a different Superintendent. That the board is
  // unchanged across both periods is a documented fact, not an inference, and it
  // is the reason `officialAcrossPeriods` below can check for continuity.
  {
    name: "Steve Moss",
    office: "Chair",
    officeSource: "printed_beside_name",
    district: "4",
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Jerry Register",
    office: "Vice-chairman",
    officeSource: "printed_beside_name",
    district: null,
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Ann Leonard",
    office: "Board Member",
    officeSource: "heading",
    district: "1",
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Chris Moore",
    office: "Board Member",
    officeSource: "heading",
    district: "2",
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Winston Chester",
    office: "Board Member",
    officeSource: "heading",
    district: "3",
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "William V. Husfelt III",
    office: "Superintendent",
    officeSource: "printed_beside_name",
    district: "5",
    period: AUDIT_2022_PERIOD,
    document: "dsb_audit_2022.pdf",
    page: 2,
    text: AUDIT_2022_TEXT,
    attributedWith: "office_held",
  },

  // ---- FY2023-2024, from the audited statements ------------------------------
  {
    name: "Steve Moss",
    office: "Chair",
    officeSource: "printed_beside_name",
    district: "4",
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Jerry Register",
    office: "Vice-chairman",
    officeSource: "printed_beside_name",
    district: null,
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Ann Leonard",
    office: "Board Member",
    officeSource: "heading",
    district: "1",
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Chris Moore",
    office: "Board Member",
    officeSource: "heading",
    district: "2",
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Winston Chester",
    office: "Board Member",
    officeSource: "heading",
    district: "3",
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },
  {
    name: "Mark McQueen",
    office: "Superintendent",
    officeSource: "printed_beside_name",
    district: "5",
    period: "2023-2024",
    document: "dsb_audit_2024.pdf",
    page: 2,
    text: AUDIT_2024_TEXT,
    attributedWith: "office_held",
  },

  // ---- 2019, the solicitation period ----------------------------------------
  {
    name: "William V. Husfelt III",
    office: "Superintendent",
    officeSource: "printed_beside_name",
    district: null,
    period: "2019",
    document: "19-10_Contract_Cleaning_Services.pdf",
    page: 1,
    text: RFP_OFFICIALS_TEXT,
    attributedWith: "document_author",
  },
  {
    name: "Jim Loyed",
    office: "Chief Financial Officer",
    officeSource: "printed_beside_name",
    district: null,
    period: "2019",
    document: "19-10_Contract_Cleaning_Services.pdf",
    page: 1,
    text: RFP_OFFICIALS_TEXT,
    attributedWith: "document_author",
  },
  {
    name: "Dan Fuller",
    office: "General Manager of Procurement, Contracting and Materials Management",
    officeSource: "printed_beside_name",
    district: null,
    period: "2019",
    document: "19-10_Contract_Cleaning_Services.pdf",
    page: 1,
    text:
      "PURCHASING CONTACT Dan Fuller General Manager of Procurement, Contracting " +
      "And Materials Management",
    attributedWith: "point_of_contact",
  },
] as const;

/** Officials of record for a stated period. */
export function officialsIn(
  period: string,
  holdings: readonly OfficeHolding[] = OFFICE_HOLDINGS,
): readonly OfficeHolding[] {
  return holdings.filter((holding) => holding.period === period);
}

/** Every period for which officials are recorded. */
export function periods(
  holdings: readonly OfficeHolding[] = OFFICE_HOLDINGS,
): readonly string[] {
  return [...new Set(holdings.map((holding) => holding.period))].sort();
}

/**
 * The office that published RFP 19-10 — the document whose square-footage table
 * the area discrepancy is measured against.
 *
 * This is the narrowest honest attribution available: it says who signed the
 * document, not who is answerable for a number in it.
 */
export function solicitationOfficials(
  holdings: readonly OfficeHolding[] = OFFICE_HOLDINGS,
): readonly OfficeHolding[] {
  return holdings.filter(
    (holding) =>
      holding.document === "19-10_Contract_Cleaning_Services.pdf" &&
      holding.period === "2019",
  );
}

/**
 * A source commitment for an office-holding, or null when the document is not
 * among the hash-verified fetches.
 *
 * Returning null rather than a placeholder is deliberate: an attribution whose
 * document is not on the machine is not a weaker attribution, it is an
 * unverified one, and the caller has to say so.
 */
export function sourceFor(
  holding: OfficeHolding,
  sources: ReadonlyMap<string, Source>,
): Source | null {
  return sources.get(holding.document) ?? null;
}

/**
 * What this layer deliberately cannot produce.
 *
 * Returned as a value so a report can print it, and so a test can pin it. These
 * are not disclaimers; they are the boundary, and they are the reason the layer
 * stops where it does.
 */
export const ATTRIBUTION_LIMITS: readonly string[] = [
  "Who caused the area discrepancy: no fetched document says.",
  "Who approved the 108,941 sq ft figure: the RFP names the point of contact for " +
    "the solicitation, not the person who derived a number in it.",
  "Whether any named official knew of the discrepancy: not a fact any document reports.",
  "Whether any named official acted wrongly: not this instrument's to determine, " +
    "and Subject has no member that would let it.",
] as const;

export { AUDIT_2022_PERIOD };

/**
 * Offices held continuously across two recorded periods.
 *
 * A person whose name and office appear in both periods is recorded as
 * continuous. This is a fact about two documents, not a judgement about the
 * person: it says the documents agree, and nothing more.
 */
export function officialAcrossPeriods(
  first: string,
  second: string,
  holdings: readonly OfficeHolding[] = OFFICE_HOLDINGS,
): readonly OfficeHolding[] {
  const key = (h: OfficeHolding): string => `${h.name}\u0000${h.office}`;
  const firstKeys = new Set(officialsIn(first, holdings).map(key));
  return officialsIn(second, holdings).filter((h) => firstKeys.has(key(h)));
}

/**
 * The superintendent of record in a period, or null.
 *
 * Returns a single record rather than a list because a period with two
 * superintendents recorded would be a defect in this table, not a fact about
 * the district, and the caller should see null and investigate.
 */
export function superintendentIn(
  period: string,
  holdings: readonly OfficeHolding[] = OFFICE_HOLDINGS,
): OfficeHolding | null {
  const found = officialsIn(period, holdings).filter(
    (holding) => holding.office === "Superintendent",
  );
  return found.length === 1 ? (found[0] ?? null) : null;
}
