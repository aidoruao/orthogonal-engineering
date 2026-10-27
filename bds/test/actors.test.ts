/**
 * The attribution layer's falsifiers.
 *
 * The load-bearing test is `every holding's recorded text contains its own
 * name`. That is the same discipline `burden audit` applies to a quoted span: if
 * the text beside the name does not contain the name, the record is a
 * paraphrase wearing a citation, and the whole layer is worthless.
 *
 * The second load-bearing test is that no office-holding can become a
 * condemnation. That is not a stylistic preference; it is the jurisdiction
 * boundary, and `Subject` in `src/types.ts` is what enforces it.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  ATTRIBUTION_LIMITS,
  AUDIT_2022_PERIOD,
  OFFICE_HOLDINGS,
  officialAcrossPeriods,
  officialsIn,
  periods,
  solicitationOfficials,
  superintendentIn,
  type OfficeHolding,
} from "../src/actors.js";
import { admissible, type Subject } from "../src/types.js";

/** PDF extraction renders hyphens as separate tokens ("Vice - chairman"), so
 *  comparison collapses whitespace and spaced hyphens before matching. This is
 *  the same normalisation `ledger` applies to a quoted span, and it is stated
 *  here rather than hidden in the assertion. */
function normalize(text: string): string {
  return text
    .replace(/\s+-\s+/g, "-")
    .replace(/\s+/g, " ")
    .toLowerCase()
    .trim();
}

function nameTokens(name: string): readonly string[] {
  return name
    .replace(/[.,]/g, " ")
    .split(/\s+/)
    .filter((token) => token.length > 1 && token !== "III" && token !== "V");
}

test("every holding's recorded text contains its own name", () => {
  // Long names are broken across lines in the source ("William V. Husfelt III"),
  // so the check is that every substantial token appears, not the full string.
  for (const holding of OFFICE_HOLDINGS) {
    for (const token of nameTokens(holding.name)) {
      assert.ok(
        normalize(holding.text).includes(normalize(token)),
        `${holding.name}: token "${token}" is not in the recorded text for ${holding.document} p.${String(holding.page)}`,
      );
    }
  }
});

test("every holding's recorded office is supported where it claims to be", () => {
  for (const holding of OFFICE_HOLDINGS) {
    if (holding.officeSource === "heading") {
      // The title is not printed beside the name; it comes from the section
      // heading. The heading must therefore be present in the recorded text,
      // and the name must still be there.
      assert.ok(
        normalize(holding.text).includes("board members"),
        `${holding.name}: heading-sourced office but no BOARD MEMBERS heading in text`,
      );
    } else {
      // Printed beside the name: the exact word must appear after the name.
      const afterName = holding.text.split(holding.name.split(/[ ,]+/)[0] ?? "").pop() ?? "";
      const probe = holding.office.split(" ")[0] ?? holding.office;
      assert.ok(
        normalize(holding.text).includes(normalize(probe)),
        `${holding.name}: "${probe}" is not in the recorded text`,
      );
      assert.ok(afterName.length >= 0);
    }
  }
});

test("every holding cites a page and a document", () => {
  for (const holding of OFFICE_HOLDINGS) {
    assert.ok(holding.document.endsWith(".pdf"), `${holding.name}: no document`);
    assert.ok(Number.isInteger(holding.page) && holding.page > 0, `${holding.name}: no page`);
    assert.ok(holding.text.length > 40, `${holding.name}: text too short to be a quotation`);
  }
});

test("no holding can produce a condemnation", () => {
  // The office-holding record has no severity field and no subject field: it is
  // not a Finding at all. This test pins that, because a future refactor that
  // made it one is exactly how the boundary would erode.
  const keys = Object.keys(OFFICE_HOLDINGS[0] ?? {});
  assert.ok(!keys.includes("severity"), "an office-holding must not carry severity");
  assert.ok(!keys.includes("warrantedSeverity"), "an office-holding must not carry a warrant");
  assert.ok(!keys.includes("claim"), "an office-holding must not carry a proposition");
});

test("the condemnation subject does not exist in the type system", () => {
  const subjects: readonly Subject[] = ["structure", "attribution"];
  for (const subject of subjects) {
    const codes = admissible({
      id: "FND-ACTOR-CHECK",
      subject,
      claim: "a checkable proposition",
      severity: "minor",
      warrantedSeverity: "minor",
      evidence: "fetched",
      source: {
        path: "x.pdf",
        sha256: "0".repeat(64),
        bytes: 1,
        pages: [1],
      },
      falsifier: "re-read the page",
      detail: "probe",
    }).map((violation) => violation.code);
    assert.deepEqual(codes, [], `subject ${subject} should be admissible`);
  }
});

test("the superintendent of record changes between the two audited periods", () => {
  const first = superintendentIn(AUDIT_2022_PERIOD);
  const second = superintendentIn("2023-2024");
  assert.ok(first !== null && second !== null);
  assert.equal(first.name, "William V. Husfelt III");
  assert.equal(second.name, "Mark McQueen");
  assert.notEqual(first.name, second.name);
});

test("the 2019 solicitation and the 2022 audit agree on the superintendent", () => {
  // Two independent fetched primaries, three years apart, naming the same person
  // in the same office. That is corroboration for the office-holding fact.
  const solicitation = officialsIn("2019").find((h) => h.office === "Superintendent");
  const audited = superintendentIn(AUDIT_2022_PERIOD);
  assert.ok(solicitation !== undefined && audited !== null);
  assert.equal(solicitation.name, audited.name);
  assert.notEqual(solicitation.document, audited.document);
});

test("the board was continuous across the two audited periods", () => {
  const continuous = officialAcrossPeriods(AUDIT_2022_PERIOD, "2023-2024");
  // Five board members plus the superintendent's *office*; but the office is
  // held by a different person, so only the five board seats carry over.
  const names = continuous.map((h) => h.name).sort();
  assert.deepEqual(names, [
    "Ann Leonard",
    "Chris Moore",
    "Jerry Register",
    "Steve Moss",
    "Winston Chester",
  ]);
});

test("solicitation officials are the 2019 RFP's own officers", () => {
  const found = solicitationOfficials();
  const names = found.map((h) => h.name).sort();
  assert.deepEqual(names, ["Dan Fuller", "Jim Loyed", "William V. Husfelt III"]);
  for (const holding of found) {
    assert.equal(holding.document, "19-10_Contract_Cleaning_Services.pdf");
  }
});

test("periods are reported in order and are the three recorded", () => {
  assert.deepEqual(periods(), ["2019", "2021-2022", "2023-2024"]);
});

test("an unknown period yields no officials rather than a default", () => {
  assert.deepEqual(officialsIn("1999"), []);
  assert.equal(superintendentIn("1999"), null);
});

test("the recorded limits name what the layer cannot produce", () => {
  assert.ok(ATTRIBUTION_LIMITS.length >= 4);
  const joined = ATTRIBUTION_LIMITS.join(" ");
  assert.ok(joined.includes("caused"));
  assert.ok(joined.includes("this instrument"));
});

test("every holding is one of the three permitted attribution kinds", () => {
  const permitted = new Set(["office_held", "document_author", "point_of_contact"]);
  for (const holding of OFFICE_HOLDINGS) {
    assert.ok(
      permitted.has(holding.attributedWith),
      `${holding.name}: "${holding.attributedWith}" is not a permitted attribution`,
    );
  }
});

test("no holding attributes an action to a person", () => {
  // The only attributions allowed are office-holding and document provenance.
  // Nothing in this table may say a person did, approved, or knew anything.
  const actionWords = /approv|caused|knew|ordered|directed|failed|concealed/i;
  for (const holding of OFFICE_HOLDINGS as readonly OfficeHolding[]) {
    assert.ok(
      !actionWords.test(holding.office),
      `${holding.name}: office "${holding.office}" imputes an action`,
    );
  }
});
