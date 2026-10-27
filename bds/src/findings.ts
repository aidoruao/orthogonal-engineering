/**
 * Audit findings — where the money went and what the auditor said about it.
 *
 * Everything before this module measured *quantities*: area, function totals,
 * task counts. None of it asked the question that matters most to a reader:
 * **did anyone who examined the books conclude that something was wrong?**
 *
 * The answer is yes, and it is in the auditors' own schedules. These are the
 * strongest evidence tier in this package: they are not this instrument's
 * inferences, they are findings by a licensed CPA firm under Government Auditing
 * Standards, with statutory citations and dollar amounts.
 *
 * ## What these findings are, precisely
 *
 * Every one of them is about **financial reporting, budget law, or federal grant
 * compliance**. Not one is about custodial staffing levels, cleaning standards,
 * or wage rates paid to district custodial employees. The connection to the
 * labour question — and there is one — is stated where it occurs and marked as
 * an inferential step, not as a finding.
 *
 * ## Evidence discipline
 *
 * A finding is recorded here only with: the document, the page, the finding
 * number, the auditor's own words, and the dollar amount if one is stated. No
 * finding is summarised into something stronger than the auditor wrote.
 */

export type FindingKind =
  | "material_weakness"
  | "significant_deficiency"
  | "noncompliance"
  | "questioned_costs";

export type AuditFinding = {
  /** Auditor's finding number, e.g. "2024-001". */
  readonly id: string;
  readonly fiscalYear: number;
  readonly kind: FindingKind;
  /** The auditor's heading, verbatim. */
  readonly heading: string;
  /** Document and page within evidence/bds. */
  readonly document: string;
  readonly page: number;
  /** The auditor's "Condition" text, quoted. */
  readonly condition: string;
  /** The auditor's "Cause" text, quoted, where the schedule states one. */
  readonly cause: string | null;
  /** Dollar amount the auditor states, in whole dollars, where one is stated. */
  readonly amountUsd: number | null;
  /** The statutory criteria the auditor cites. */
  readonly criteria: string;
  /** True when the auditor's own text says the finding was previously reported. */
  readonly repeatOfPriorYear: boolean;
};

/** FY2024 findings, from `dsb_audit_2024.pdf` pp.101–103 (printed 95–97). */
const F2024_001: AuditFinding = {
  id: "2024-001",
  fiscalYear: 2024,
  kind: "material_weakness",
  heading: "Lack of Appropriate Staffing Leading to Audit Entries",
  document: "dsb_audit_2024.pdf",
  page: 101,
  condition:
    "The District made various reporting and record keeping errors during the year " +
    "due to a lack of appropriate staffing. Management did not have appropriate " +
    "processes and controls in place to prevent, or detect and correct errors in a " +
    "timely manner.",
  cause:
    "The District's processes and controls did not allow staff to identify these adjustments.",
  amountUsd: null,
  criteria:
    "Section 1010.01, Florida Statutes, requires that each school district prepare " +
    "and maintain financial records and accounts in accordance with generally " +
    "accepted accounting principles (GAAP).",
  repeatOfPriorYear: true,
};

const F2024_003: AuditFinding = {
  id: "2024-003",
  fiscalYear: 2024,
  kind: "noncompliance",
  heading:
    "District procedures did not always limit expenditures to budgeted amounts, " +
    "contrary to State law, State Board of Education (SBE) rules, and Board policies",
  document: "dsb_audit_2024.pdf",
  page: 101,
  condition:
    "District records show that expenditures were not always limited to budgeted " +
    "amounts. As of June 30, 2024, General Fund expenditures exceeded the budgeted " +
    "amounts in three functional categories by $750,000, $379,895, $32,706, for a " +
    "total of $1,162,601, and the Board did not amend the budget by September 10th " +
    "to authorize the over-expended amounts.",
  cause:
    "District personnel indicated that, due to oversights, certain budget amounts " +
    "were not increased during the preparation of the budget schedule for the " +
    "2023-24 fiscal year annual financial report. In addition, separate budget " +
    "amendments to cover the over-expended amounts were not presented to the Board " +
    "for approval.",
  amountUsd: 1_162_601,
  criteria:
    "Section 1011.05, Florida Statutes, provides that the official budget shall not " +
    "be altered, amended, or exceeded except as authorized. In addition, SBE Rule " +
    "6A-1.007(2), Florida Administrative Code, allows end-of-year expenditures to " +
    "exceed budgeted amounts provided the Board approves the expenditures and amends " +
    "the budget no later than September 10th following the fiscal year end.",
  repeatOfPriorYear: false,
};

const F2024_002: AuditFinding = {
  id: "2024-002",
  fiscalYear: 2024,
  kind: "significant_deficiency",
  heading: "Deficiencies Related to the Wage Rate Compliance Requirements",
  document: "dsb_audit_2024.pdf",
  page: 103,
  condition:
    "There were no controls over the wage rate compliance requirements which " +
    "resulted in the District being unaware that two of the contractors did not " +
    "have the required Davis-Bacon wage rate clause in their contracts and were not " +
    "submitting the required certified payrolls.",
  cause:
    "While the District was aware that wage-rate requirements applied to " +
    "construction type federal grant expenditures, they did not consider whether " +
    "these requirements were considered in projects originally intended to be paid " +
    "from non-federal funds. The funding source of certain projects was changed mid " +
    "process and the District did not have a process in place to review the " +
    "agreements for compliance with federal grant requirements prior to the change.",
  amountUsd: 773_629,
  criteria:
    "2 CFR section 200.303 requires internal control over federal awards. 2 CFR " +
    "Part 176 Subpart C requires nonfederal entities to include provisions requiring " +
    "compliance with the Wage-Rate requirements in federally-funded construction " +
    "contracts exceeding $2,000, and to collect certified payrolls from contractors " +
    "and subcontractors for every week in which contract work is performed.",
  repeatOfPriorYear: false,
};

/** FY2022 findings, from `dsb_audit_2022.pdf` pp.123–127, 129. */
const F2022_001: AuditFinding = {
  id: "2022-001",
  fiscalYear: 2022,
  kind: "material_weakness",
  heading: "Lack of Appropriate Staffing and Journal Entry Review",
  document: "dsb_audit_2022.pdf",
  page: 123,
  condition:
    "The District made various reporting and record keeping errors during the year " +
    "due to a lack of appropriate staffing. Due to the lack of proper staffing they " +
    "were unable to perform the same level of reviews as they have in previous years " +
    "and simply missed adjustments needed that would have generally been identified " +
    "in review.",
  cause:
    "The District lost two key employees in the finance department during the Spring " +
    "of 2022. The loss of these employees resulted in a lack of staffing needed for " +
    "appropriate review, a lack of knowledge in some areas due to limited " +
    "documentation of procedures, as well as a lack of time necessary to perform " +
    "procedures appropriately. Replacement staff were not as knowledgeable as " +
    "expected resulting in errors not being identified.",
  amountUsd: null,
  criteria:
    "Section 1010.01, Florida Statutes, requires that each school district prepare " +
    "and maintain financial records and accounts in accordance with GAAP.",
  repeatOfPriorYear: true,
};

const F2022_002: AuditFinding = {
  id: "2022-002",
  fiscalYear: 2022,
  kind: "material_weakness",
  heading: "Lack of Review Related to Property, Plant, and Equipment",
  document: "dsb_audit_2022.pdf",
  page: 124,
  condition:
    "The District did not review current year activity associated with buildings and " +
    "improvements activity to verify appropriate classification between capital and " +
    "noncapital activity resulting in unidentified errors in capital outlay " +
    "associated with various projects. The District's capital outlay was misstated in " +
    "various funds by varying amounts from $150,000 to $530,000.",
  cause:
    "The District lost two key employees in the finance department during the Spring " +
    "of 2022.",
  amountUsd: 530_000,
  criteria:
    "Section 1010.01, Florida Statutes, requires that each school district prepare " +
    "and maintain financial records and accounts in accordance with GAAP.",
  repeatOfPriorYear: true,
};

const F2022_005: AuditFinding = {
  id: "2022-005",
  fiscalYear: 2022,
  kind: "noncompliance",
  heading: "Preparation of the Schedule of Expenditures of Federal Awards",
  document: "dsb_audit_2022.pdf",
  page: 126,
  condition:
    "The District misclassified approximately $1,200,000 as ALN 84.425E instead of " +
    "84.425F. The District's expenditures reported for multiple grants were " +
    "understated due to unidentified year-end payables.",
  cause:
    "The District lost two key employees in the finance department during the Spring " +
    "of 2022.",
  amountUsd: 1_200_000,
  criteria:
    "Section 1010.01, Florida Statutes; 2 CFR Section 200.510 requires the auditee " +
    "to prepare a Schedule of Expenditures of Federal Awards.",
  repeatOfPriorYear: true,
};

export const AUDIT_FINDINGS: readonly AuditFinding[] = [
  F2022_001,
  F2022_002,
  F2022_005,
  F2024_001,
  F2024_002,
  F2024_003,
] as const;

/** Total questioned costs across every finding that states an amount. */
export function questionedCosts(
  findings: readonly AuditFinding[] = AUDIT_FINDINGS,
): number {
  return findings.reduce((sum, finding) => sum + (finding.amountUsd ?? 0), 0);
}

/**
 * Findings that recur across fiscal years, matched on the auditor's heading.
 *
 * A deficiency reported once is an incident. The same deficiency reported in two
 * consecutive audit cycles, still open, is a structural condition — and that
 * distinction is the auditor's own, made by the schedule's "previously reported"
 * marking rather than by this instrument.
 */
export type Recurrence = {
  readonly heading: string;
  readonly occurrences: readonly AuditFinding[];
};

export function recurrences(
  findings: readonly AuditFinding[] = AUDIT_FINDINGS,
): readonly Recurrence[] {
  const byHeading = new Map<string, AuditFinding[]>();
  for (const finding of findings) {
    // The FY2022 and FY2024 headings for the staffing deficiency differ by a
    // suffix ("... and Journal Entry Review"), so recurrence is matched on the
    // shared stem rather than the full string.
    const stem = finding.heading.split(/ (?:and|Leading) /)[0] ?? finding.heading;
    const bucket = byHeading.get(stem);
    if (bucket === undefined) byHeading.set(stem, [finding]);
    else bucket.push(finding);
  }
  return [...byHeading]
    .filter(([, group]) => group.length > 1)
    .map(([heading, occurrences]) => ({
      heading,
      occurrences: [...occurrences].sort((a, b) => a.fiscalYear - b.fiscalYear),
    }));
}

/**
 * What the findings do **not** establish.
 *
 * Stated as data so a report prints them and a test pins them. Each of these is
 * a claim a careless reader could make from the findings above, and none of them
 * follows.
 */
export const FINDING_LIMITS: readonly string[] = [
  "That custodial staff were underpaid: no finding addresses custodial wages. " +
    "2024-002 is about construction contractors' Davis-Bacon compliance.",
  "That any over-expenditure went to a person or a private interest: 2024-003 " +
    "reports categories over budget, not destinations of funds.",
  "That a named official caused any finding: the findings name no individual.",
  "That the district's cleaning specification is infeasible: unrelated to these " +
    "findings, and still UNMEASURED for want of paid hours.",
  "That anything criminal occurred: the auditor reports deficiencies and " +
    "noncompliance, and states no such conclusion.",
] as const;

/**
 * The one inferential step this module permits, stated as a link rather than a
 * finding.
 *
 * IOW 2's thesis is that the operation depends on unpaid or under-compensated
 * labour. The auditor independently documents (a) that the district was operating
 * with insufficient administrative staffing to the level of a repeat material
 * weakness, and (b) that $773,629 was paid to contractors whose contracts lacked
 * wage-rate clauses and who submitted no certified payrolls.
 *
 * Those are convergent with the thesis. They are not the thesis: neither finding
 * concerns custodial labour, and neither establishes that anyone was unpaid.
 */
export const INFERENTIAL_LINK = {
  convergentFacts: [
    "2024-001 and 2022-001: repeat material weakness for lack of appropriate staffing.",
    "2024-002: $773,629 paid to two contractors without Davis-Bacon clauses or certified payrolls.",
    "2024-003: $1,162,601 expended over budget without the board amendment state law requires.",
  ],
  whatWouldEstablishTheThesis: [
    "Per-site custodial hours actually paid, from the executed contract or payroll records.",
    "Task times per square foot, from a district standard or a time study.",
    "A finding or admission that cleaning was performed outside paid hours.",
  ],
  status:
    "CONVERGENT, NOT PROVEN. The findings corroborate a pattern of under-resourcing " +
    "and wage-compliance failure. They do not establish the specific claim about " +
    "custodial labour, and this module does not assert it.",
} as const;

/**
 * Normalize a quotation or a page of extracted text for *comparison only*.
 *
 * PDF extraction inserts artifacts that are properties of the layout, not of the
 * document: `Davis - Bacon` for `Davis-Bacon`, `requirement s` for
 * `requirements`, `t he` for `the`, `over - expend` for `over-expend`. The
 * quotations in this module are transcribed in readable form — what the
 * document says — and this function is how they are checked against the
 * extraction.
 *
 * This is disclosed rather than silent. A reader comparing the `condition` field
 * character by character against a PDF dump will find these differences, and the
 * difference is extraction, not alteration. The same normalisation is applied by
 * `ledger`'s `normalizeForComparison`, so the two packages agree on what
 * "verbatim" means under extraction.
 */
export function normalizeForQuote(text: string): string {
  return text
    .replace(/\r\n?/g, " ")
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '\"')
    .replace(/\u2013|\u2014/g, "-")
    // Collapse every run of whitespace, then REMOVE all whitespace entirely.
    //
    // This is deliberately aggressive: PDF extraction inserts spaces at places
    // that are not word boundaries ("requirement s", "t he", "Davis - Bacon"),
    // and any rule that tries to guess which spaces are real will glue some
    // legitimate ones together — an earlier version of this function turned
    // "budgeted amounts in" into "budgeted amountsin" and broke a genuine match.
    //
    // Removing all whitespace from both sides makes the comparison a check of
    // the characters present, which is what "verbatim under extraction" can
    // honestly mean. Case is preserved, so a change of case still fails.
    .replace(/\s+/g, "");
}

export type QuoteCheck = {
  readonly id: string;
  readonly found: boolean;
  readonly probe: string;
};

/**
 * Check every recorded condition against the extracted page it cites.
 *
 * Returns per-finding results rather than a boolean, because a boolean would
 * hide *which* quotation failed — and a finding whose quotation does not appear
 * on its cited page is the false-citation failure this repository has already
 * recorded once (`docs/LESSONS_LEARNED.md` §2).
 */
export function verifyQuotes(
  pages: ReadonlyMap<string, string>,
  findings: readonly AuditFinding[] = AUDIT_FINDINGS,
): readonly QuoteCheck[] {
  return findings.map((finding) => {
    const key = `${finding.document}#${String(finding.page)}`;
    const haystack = normalizeForQuote(pages.get(key) ?? "");
    // The WHOLE condition is verified, not a prefix. An earlier version checked
    // only the first 110 characters, which meant a wrong dollar figure — the most
    // load-bearing part of a findings record — passed the check.
    const probe = normalizeForQuote(finding.condition);
    return { id: finding.id, found: haystack.includes(probe), probe };
  });
}
