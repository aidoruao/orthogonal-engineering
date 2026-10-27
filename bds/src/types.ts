/**
 * bds — core types.
 *
 * The evidence discipline is the same one `burden/` enforces, applied to a
 * different subject: a claim about a school district's published plan is worth
 * exactly what its source commitment is worth, and nothing more.
 *
 * The one addition here is `Severity`, imported in spirit from
 * `L3_JURISDICTION.lean`: a finding declares the severity it claims and the
 * severity its evidence warrants, and the instrument refuses to publish a
 * finding where the first exceeds the second. Indignation that outruns the
 * facts is vengeance wearing the same clothes.
 */

/** A fetched primary document, committed to by hash. */
export type Source = {
  /** Path as reported to the reader. */
  readonly path: string;
  /** SHA-256 of the exact bytes examined, lowercase hex. */
  readonly sha256: string;
  readonly bytes: number;
  /** Page numbers within the document that were actually read. */
  readonly pages: readonly number[];
};

/** How well a claim is evidenced. Ordered by strength; see `mayUpgrade`. */
export type Tier =
  | "unmeasured"
  | "located_blocked"
  | "corroborated"
  | "fetched"
  | "retired";

export const TIERS: readonly Tier[] = [
  "unmeasured",
  "located_blocked",
  "corroborated",
  "fetched",
  "retired",
] as const;

/** A site listed in the district's own published square-footage table. */
export type Site = {
  /** Cost centre number as printed, e.g. "0571". */
  readonly costCenter: string;
  /** Site name exactly as printed. */
  readonly name: string;
  /** Square footage as printed. */
  readonly squareFeet: number;
  /** Which page of the source this row was read from. */
  readonly page: number;
};

/** A required task, from the specification's frequency sections. */
export type SpecTask = {
  /** Stable identifier, e.g. "13.4.1.floor.dust-mop". */
  readonly id: string;
  /** Section reference in the source, e.g. "13.4.1". */
  readonly section: string;
  /** The source's own words for the task. */
  readonly description: string;
  /** Minimum performances per year, as the specification states it. */
  readonly frequencyPerYear: number;
};

/** Frequency words the specification uses, and the minimum they denote. */
export type FrequencyBasis = {
  readonly label: string;
  readonly section: string;
  readonly perYear: number;
  /** The source clause that fixes the number, quoted. */
  readonly quote: string;
};

/**
 * A demand result.
 *
 * `unmeasured` is a first-class outcome, not an error. If the paid minutes are
 * not available from a fetched primary, the instrument cannot say whether the
 * plan is feasible, and it says so instead of guessing.
 */
export type Feasibility =
  | {
      readonly kind: "unmeasured";
      readonly code: "NO_PAID_HOURS" | "NO_TASK_TIMES" | "NO_AREA";
      readonly detail: string;
    }
  | {
      readonly kind: "feasible";
      readonly demandedMinutes: number;
      readonly paidMinutes: number;
      readonly headroomMinutes: number;
    }
  | {
      readonly kind: "infeasible";
      readonly demandedMinutes: number;
      readonly paidMinutes: number;
      readonly shortfallMinutes: number;
    };

/** Severity, mirroring `Severity` in `L3_JURISDICTION.lean`. */
export type Severity = "critical" | "major" | "minor" | "none";

export const SEVERITY_WEIGHT: Readonly<Record<Severity, number>> = {
  critical: 3,
  major: 2,
  minor: 1,
  none: 0,
};

/** What a finding is about. Mirrors `Subject` in `L3_JURISDICTION.lean`. */
export type Subject = "structure" | "attribution";

/**
 * A finding.
 *
 * There is no `condemnation` subject. That is not an oversight and not a
 * politeness: `L3_JURISDICTION.lean` proves no evidence bears on one, so an
 * instrument that files only what evidence supports cannot reach one. The type
 * cannot express it either.
 */
export type Finding = {
  readonly id: string;
  readonly subject: Subject;
  readonly claim: string;
  readonly severity: Severity;
  /** The severity the attached evidence actually warrants. */
  readonly warrantedSeverity: Severity;
  readonly evidence: Tier;
  readonly source: Source | null;
  /** What would refute this finding. Non-empty, always. */
  readonly falsifier: string;
  readonly detail: string;
};

export type ViolationCode =
  | "severity_exceeds_warrant"
  | "no_falsifier"
  | "fetched_requires_source"
  | "unsupported_severity"
  | "empty_claim";

export type Violation = {
  readonly code: ViolationCode;
  readonly path: string;
  readonly message: string;
};

/**
 * The jurisdiction gate, in code.
 *
 * A finding is admissible only if it is proportionate, falsifiable, and sourced
 * in proportion to the severity it claims. This is the runtime twin of
 * `Righteous` in `L3_JURISDICTION.lean`; `TS_JURISDICTION.lean` proves the two
 * agree pair by pair, so they cannot drift.
 */
export function admissible(finding: Finding): readonly Violation[] {
  const violations: Violation[] = [];

  if (finding.claim.trim() === "") {
    violations.push({
      code: "empty_claim",
      path: "claim",
      message: "a finding must state the proposition it asserts",
    });
  }

  if (finding.falsifier.trim() === "") {
    violations.push({
      code: "no_falsifier",
      path: "falsifier",
      message:
        "a finding that names nothing that would refute it is not a finding; it is an assertion",
    });
  }

  if (
    SEVERITY_WEIGHT[finding.severity] > SEVERITY_WEIGHT[finding.warrantedSeverity]
  ) {
    violations.push({
      code: "severity_exceeds_warrant",
      path: "severity",
      message: `claims ${finding.severity} where the evidence warrants only ${finding.warrantedSeverity}`,
    });
  }

  if (
    (finding.severity === "critical" || finding.severity === "major") &&
    finding.evidence !== "fetched" &&
    finding.evidence !== "corroborated"
  ) {
    violations.push({
      code: "unsupported_severity",
      path: "evidence",
      message: `a ${finding.severity} finding may not rest on ${finding.evidence} evidence`,
    });
  }

  if (finding.evidence === "fetched" && finding.source === null) {
    violations.push({
      code: "fetched_requires_source",
      path: "source",
      message: "a fetched finding must name the document and its hash",
    });
  }

  return violations;
}

/** Stable ordering for deterministic output. */
export function sortViolations(violations: readonly Violation[]): Violation[] {
  return [...violations].sort((a, b) => {
    if (a.path !== b.path) return a.path < b.path ? -1 : 1;
    if (a.code !== b.code) return a.code < b.code ? -1 : 1;
    return 0;
  });
}
