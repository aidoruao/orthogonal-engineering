/**
 * The operative document, which is not the original document.
 *
 * RFP 19-10 §5 states that addenda are the only official method of
 * clarification and that failure to acknowledge one "may result in rejection of
 * the bid." So an audit that reads only the base RFP is reading a superseded
 * document.
 *
 * Addendum 1 (2019-05-16) deletes Bay High School from the service list and from
 * both pricing sheets. The instrument therefore has to apply it, and the earlier
 * version of this file — which reported twelve sites straight from the base
 * RFP — was reporting a site the district had already removed.
 *
 * The addendum was obtained because it was not among the first four documents
 * fetched; its existence was known only from §5's warning that addenda exist.
 * That is the general lesson and it is why `BASE_DOCUMENT_ONLY` is a recorded
 * access gap rather than a silent assumption.
 */

import type { Site } from "./types.js";

/** A formal change to the solicitation. */
export type Amendment = {
  readonly id: string;
  /** Date printed on the memorandum. */
  readonly date: string;
  /** Document the amendment was read from, relative to evidence/bds. */
  readonly document: string;
  readonly page: number;
  /** The exact sentence that performs the deletion, quoted. */
  readonly text: string;
  /** Cost centres removed from the operative scope. */
  readonly deletes: readonly {
    readonly costCenter: string;
    readonly siteName: string;
  }[];
  /** Pages of the base RFP the amendment changes. */
  readonly affectsPages: readonly number[];
};

/**
 * RFP 19-10, Addendum No. 1, 2019-05-16.
 *
 * > Change original RFP 19-10, page 5 of 71, delete Bay High School from
 * > services. Change original RFP 19-10 Exhibit B, page 58 of 71, delete Bay
 * > High School from pricing sheet. Change original RFP 19-10 Exhibit C, page 60
 * > of 71, delete Bay High School from pricing sheet
 */
export const ADDENDUM_1: Amendment = {
  id: "RFP-19-10-ADDENDUM-1",
  date: "2019-05-16",
  document: "RFP-19-10-ADDENDUM-1-Contract-Cleaning-Services.pdf",
  page: 1,
  text:
    "Change original RFP 19 - 10, page 5 of 71, delete Bay High School from services. " +
    "Change original RFP 19 - 10 Exhibit B, page 58 of 71, delete Bay High School from " +
    "pricing sheet. Change original RFP 19 - 10 Exhibit C, page 60 of 71, delete Bay " +
    "High School from pricing sheet",
  deletes: [{ costCenter: "0061", siteName: "Bay High School" }],
  affectsPages: [5, 58, 60],
};

export const AMENDMENTS: readonly Amendment[] = [ADDENDUM_1];

export type ScopeApplication = {
  /** Sites still in scope after every amendment is applied. */
  readonly operative: readonly Site[];
  /** Sites removed by an amendment, with the amendment that removed them. */
  readonly removed: readonly { readonly site: Site; readonly by: string }[];
  /** Deletions naming a cost centre that the base document did not list. */
  readonly unresolvedDeletions: readonly {
    readonly costCenter: string;
    readonly siteName: string;
    readonly by: string;
  }[];
  /** Cost centres in the base document that no amendment mentions. */
  readonly untouched: readonly string[];
};

/**
 * Apply amendments to the base table.
 *
 * A deletion that matches nothing is reported rather than ignored: if an
 * amendment says to delete a site the table does not contain, either the parse
 * missed a row or the amendment refers to a revision this table is not, and
 * both are worth knowing.
 */
export function applyAmendments(
  base: readonly Site[],
  amendments: readonly Amendment[] = AMENDMENTS,
): ScopeApplication {
  const deleted = new Map<string, string>();
  for (const amendment of amendments) {
    for (const removal of amendment.deletes) {
      deleted.set(removal.costCenter, amendment.id);
    }
  }

  const operative: Site[] = [];
  const removed: { site: Site; by: string }[] = [];
  for (const site of base) {
    const by = deleted.get(site.costCenter);
    if (by === undefined) operative.push(site);
    else removed.push({ site, by });
  }

  const present = new Set(base.map((site) => site.costCenter));
  const unresolvedDeletions: {
    costCenter: string;
    siteName: string;
    by: string;
  }[] = [];
  for (const amendment of amendments) {
    for (const removal of amendment.deletes) {
      if (!present.has(removal.costCenter)) {
        unresolvedDeletions.push({ ...removal, by: amendment.id });
      }
    }
  }

  const bySite = (a: Site, b: Site): number =>
    a.costCenter < b.costCenter ? -1 : a.costCenter > b.costCenter ? 1 : 0;

  return {
    operative: [...operative].sort(bySite),
    removed,
    unresolvedDeletions,
    untouched: [...present].sort(),
  };
}

/** Total square footage of the operative scope. */
export function operativeSquareFeet(application: ScopeApplication): number {
  return application.operative.reduce((sum, site) => sum + site.squareFeet, 0);
}
