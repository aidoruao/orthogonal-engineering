/**
 * Selection ledger — the instrument that makes Option A honest.
 *
 * Option A drafts claims locally and publishes only some of them. That is
 * only honest if the *selection itself* is published: every candidate must
 * receive exactly one disposition, and every rejection must carry a reason.
 * Selective disclosure is a form of lying even when every published quote is
 * accurate, so the discarded set is part of the record.
 *
 * What is published: claim ID, disposition, and a machine-readable reason
 * code. What stays local: the quote text, the source name, anything that
 * could identify a third party.
 *
 * The structural invariant —
 *
 *     every candidate has exactly one disposition, and no candidate is dropped
 *
 * — is proved in Lean (`L1_SELECTION.lean`) as well as checked here.
 */

/** Why a candidate was not accepted. Codes are stable; never freeform prose. */
export type RejectCode =
  | "quote_not_found"
  | "source_hash_mismatch"
  | "source_not_in_manifest"
  | "wrong_page"
  | "editorial_not_evidential"
  | "duplicate"
  | "insufficient_corroboration"
  | "structure_invalid"
  | "out_of_scope";

/** Why a candidate was deliberately held back rather than rejected on merit. */
export type WithholdCode =
  | "third_party_identity"
  | "sealed_material"
  | "legal_review_pending"
  | "user_declined";

export type Disposition =
  | { readonly kind: "accepted" }
  | { readonly kind: "rejected"; readonly code: RejectCode }
  | { readonly kind: "withheld"; readonly code: WithholdCode };

export const REJECT_CODES: readonly RejectCode[] = [
  "quote_not_found",
  "source_hash_mismatch",
  "source_not_in_manifest",
  "wrong_page",
  "editorial_not_evidential",
  "duplicate",
  "insufficient_corroboration",
  "structure_invalid",
  "out_of_scope",
] as const;

export const WITHHOLD_CODES: readonly WithholdCode[] = [
  "third_party_identity",
  "sealed_material",
  "legal_review_pending",
  "user_declined",
] as const;

/** A candidate as it appears in the published selection ledger. */
export interface SelectionEntry {
  readonly claimId: string;
  readonly disposition: Disposition;
}

/** The published ledger: one entry per candidate, sorted by claim ID. */
export interface SelectionLedger {
  readonly entries: readonly SelectionEntry[];
}

export function isAccepted(d: Disposition): boolean {
  return d.kind === "accepted";
}

export function isRejected(d: Disposition): boolean {
  return d.kind === "rejected";
}

export function isWithheld(d: Disposition): boolean {
  return d.kind === "withheld";
}

export interface SelectionViolation {
  readonly code:
    | "duplicate_candidate"
    | "missing_disposition"
    | "orphan_disposition"
    | "empty_reason"
    | "unknown_reason_code"
    | "not_sorted";
  readonly claimId: string;
  readonly message: string;
}

export interface SelectionReport {
  readonly total: number;
  readonly accepted: number;
  readonly rejected: number;
  readonly withheld: number;
  readonly byCode: ReadonlyMap<string, number>;
  readonly violations: readonly SelectionViolation[];
}

function isKnownDisposition(d: Disposition): boolean {
  switch (d.kind) {
    case "accepted":
      return true;
    case "rejected":
      return (REJECT_CODES as readonly string[]).includes(d.code);
    case "withheld":
      return (WITHHOLD_CODES as readonly string[]).includes(d.code);
    default:
      return false;
  }
}

/**
 * Audit a selection: is every candidate accounted for exactly once, does every
 * non-acceptance carry a valid reason, and is the ledger sorted?
 *
 * `candidateIds` is the full set of candidates that were drafted. Any candidate
 * absent from `entries` is a silent drop — the exact failure this exists to
 * catch.
 */
export function auditSelection(
  candidateIds: readonly string[],
  ledger: SelectionLedger,
): SelectionReport {
  const violations: SelectionViolation[] = [];
  const byCode = new Map<string, number>();

  // Duplicate candidates make totality ambiguous.
  const seenCandidates = new Set<string>();
  for (const id of candidateIds) {
    if (seenCandidates.has(id)) {
      violations.push({
        code: "duplicate_candidate",
        claimId: id,
        message: "candidate id appears more than once in the input set",
      });
    }
    seenCandidates.add(id);
  }

  // Sorting is checked so two runs produce byte-identical output.
  for (let i = 1; i < ledger.entries.length; i += 1) {
    const previous = ledger.entries[i - 1];
    const current = ledger.entries[i];
    if (previous === undefined || current === undefined) continue;
    if (previous.claimId > current.claimId) {
      violations.push({
        code: "not_sorted",
        claimId: current.claimId,
        message: `entries must be sorted by claimId; "${current.claimId}" follows "${previous.claimId}"`,
      });
    }
  }

  const seenEntries = new Set<string>();
  for (const entry of ledger.entries) {
    if (seenEntries.has(entry.claimId)) {
      violations.push({
        code: "duplicate_candidate",
        claimId: entry.claimId,
        message: "claimId appears more than once in the selection ledger",
      });
    }
    seenEntries.add(entry.claimId);

    if (!seenCandidates.has(entry.claimId)) {
      violations.push({
        code: "orphan_disposition",
        claimId: entry.claimId,
        message: "disposition names a candidate that was never drafted",
      });
    }

    if (!isKnownDisposition(entry.disposition)) {
      violations.push({
        code: "unknown_reason_code",
        claimId: entry.claimId,
        message: `unknown reason code in disposition "${entry.disposition.kind}"`,
      });
    }

    if (entry.disposition.kind !== "accepted") {
      const code: string = entry.disposition.code;
      if (code.trim() === "") {
        violations.push({
          code: "empty_reason",
          claimId: entry.claimId,
          message: "a non-accepted candidate must carry a reason",
        });
      } else {
        byCode.set(code, (byCode.get(code) ?? 0) + 1);
      }
    }
  }

  for (const id of seenCandidates) {
    if (!seenEntries.has(id)) {
      violations.push({
        code: "missing_disposition",
        claimId: id,
        message: "candidate has no disposition; this is a silent drop",
      });
    }
  }

  const accepted = ledger.entries.filter((e) => isAccepted(e.disposition)).length;
  const rejected = ledger.entries.filter((e) => isRejected(e.disposition)).length;
  const withheld = ledger.entries.filter((e) => isWithheld(e.disposition)).length;

  return {
    total: ledger.entries.length,
    accepted,
    rejected,
    withheld,
    byCode,
    violations: [...violations].sort((a, b) => {
      if (a.claimId !== b.claimId) return a.claimId < b.claimId ? -1 : 1;
      return a.code < b.code ? -1 : a.code > b.code ? 1 : 0;
    }),
  };
}

/** The partition must account for every candidate, with no double counting. */
export function partitionHolds(report: SelectionReport): boolean {
  return (
    report.violations.length === 0 &&
    report.accepted + report.rejected + report.withheld === report.total
  );
}

/** Serialize deterministically: sorted by claimId, one JSON object per line. */
export function serializeLedger(ledger: SelectionLedger): string {
  const sorted = [...ledger.entries].sort((a, b) =>
    a.claimId < b.claimId ? -1 : a.claimId > b.claimId ? 1 : 0,
  );
  return sorted
    .map((entry) =>
      JSON.stringify(
        entry.disposition.kind === "accepted"
          ? { claimId: entry.claimId, disposition: "accepted" }
          : {
              claimId: entry.claimId,
              disposition: entry.disposition.kind,
              code: entry.disposition.code,
            },
      ),
    )
    .join("\n") + (sorted.length === 0 ? "" : "\n");
}

/** Parse a published selection ledger. Malformed lines are reported. */
export function parseLedger(
  text: string,
): { ledger: SelectionLedger; malformed: string[] } {
  const entries: SelectionEntry[] = [];
  const malformed: string[] = [];

  text.split(/\r?\n/).forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed === "") return;
    let parsed: unknown;
    try {
      parsed = JSON.parse(trimmed) as unknown;
    } catch {
      malformed.push(`line ${index + 1}: not JSON`);
      return;
    }
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      malformed.push(`line ${index + 1}: not an object`);
      return;
    }
    const record = parsed as Record<string, unknown>;
    const claimId = record["claimId"];
    const disposition = record["disposition"];
    if (typeof claimId !== "string" || claimId.trim() === "") {
      malformed.push(`line ${index + 1}: missing claimId`);
      return;
    }
    if (disposition === "accepted") {
      entries.push({ claimId, disposition: { kind: "accepted" } });
      return;
    }
    const code = record["code"];
    if (disposition === "rejected" || disposition === "withheld") {
      if (typeof code !== "string" || code.trim() === "") {
        malformed.push(`line ${index + 1}: ${disposition} without a code`);
        return;
      }
      entries.push({
        claimId,
        disposition:
          disposition === "rejected"
            ? { kind: "rejected", code: code as RejectCode }
            : { kind: "withheld", code: code as WithholdCode },
      });
      return;
    }
    malformed.push(`line ${index + 1}: unknown disposition`);
  });

  return { ledger: { entries }, malformed };
}
