/**
 * Audit findings — the strongest evidence tier in this package.
 *
 * These are a licensed firm's conclusions under Government Auditing Standards,
 * so two things must hold and both are tested here:
 *
 *   1. Every quotation must actually appear on the page it cites, modulo PDF
 *      extraction artifacts. A finding whose quote does not appear is the
 *      false-citation failure already recorded in `docs/LESSONS_LEARNED.md`.
 *   2. Nothing may be derived from the findings that the auditor did not say.
 *      `FINDING_LIMITS` is pinned so a future edit cannot quietly drop it.
 */

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

import {
  AUDIT_FINDINGS,
  FINDING_LIMITS,
  INFERENTIAL_LINK,
  normalizeForQuote,
  questionedCosts,
  recurrences,
  verifyQuotes,
} from "../src/findings.js";

test("every finding cites a document, a page, and statutory criteria", () => {
  for (const finding of AUDIT_FINDINGS) {
    assert.ok(finding.document.endsWith(".pdf"), `${finding.id}: no document`);
    assert.ok(Number.isInteger(finding.page) && finding.page > 0, `${finding.id}: no page`);
    assert.ok(finding.criteria.length > 40, `${finding.id}: criteria too short`);
    assert.ok(finding.condition.length > 80, `${finding.id}: condition too short`);
    assert.ok(/^\d{4}-\d{3}$/.test(finding.id), `${finding.id}: malformed finding number`);
  }
});

test("the amounts stated are the auditor's, and they sum to the reported total", () => {
  const stated = AUDIT_FINDINGS.filter((f) => f.amountUsd !== null);
  assert.equal(stated.length, 4);
  // 530,000 + 1,200,000 + 773,629 + 1,162,601
  assert.equal(questionedCosts(), 530_000 + 1_200_000 + 773_629 + 1_162_601);
});

test("the wage-rate finding carries the auditor's questioned cost", () => {
  const wage = AUDIT_FINDINGS.find((f) => f.id === "2024-002");
  assert.ok(wage !== undefined);
  assert.equal(wage.amountUsd, 773_629);
  assert.equal(wage.kind, "significant_deficiency");
  // The condition must be about contracts and payrolls, because that is what the
  // auditor found; a summary that dropped either would overstate or understate it.
  assert.ok(wage.condition.includes("Davis-Bacon"));
  assert.ok(wage.condition.includes("certified payrolls"));
});

test("the staffing deficiency is recorded as recurring across both audits", () => {
  const recurring = recurrences();
  assert.equal(recurring.length, 1);
  const staffing = recurring[0];
  assert.ok(staffing !== undefined);
  assert.deepEqual(
    staffing.occurrences.map((o) => o.id),
    ["2022-001", "2024-001"],
  );
  for (const occurrence of staffing.occurrences) {
    assert.equal(occurrence.kind, "material_weakness");
    assert.equal(occurrence.repeatOfPriorYear, true);
  }
});

test("both audits are represented, so neither was dropped", () => {
  const years = [...new Set(AUDIT_FINDINGS.map((f) => f.fiscalYear))].sort();
  assert.deepEqual(years, [2022, 2024]);
  assert.equal(AUDIT_FINDINGS.filter((f) => f.fiscalYear === 2022).length, 3);
  assert.equal(AUDIT_FINDINGS.filter((f) => f.fiscalYear === 2024).length, 3);
});

test("the limits name the claims a careless reader would make", () => {
  assert.ok(FINDING_LIMITS.length >= 4);
  const joined = FINDING_LIMITS.join(" ");
  // The single most important one: the findings do not establish custodial underpayment.
  assert.ok(/custodial/i.test(joined));
  assert.ok(/criminal|no such conclusion/i.test(joined));
});

test("the inferential link is labelled convergent, not proven", () => {
  assert.ok(INFERENTIAL_LINK.status.startsWith("CONVERGENT, NOT PROVEN"));
  assert.equal(INFERENTIAL_LINK.convergentFacts.length, 3);
  assert.ok(INFERENTIAL_LINK.whatWouldEstablishTheThesis.length >= 3);
  // It must say what is still missing, and the missing thing must be hours.
  assert.ok(INFERENTIAL_LINK.whatWouldEstablishTheThesis.join(" ").toLowerCase().includes("hours"));
});

test("normalisation strips extraction artifacts but preserves case", () => {
  assert.equal(normalizeForQuote("requirement s"), "requirements");
  assert.equal(normalizeForQuote("Davis - Bacon"), "Davis-Bacon");
  assert.equal(normalizeForQuote("t he District"), "theDistrict");
  // Case is preserved, so a case change would still fail a quote check.
  assert.notEqual(normalizeForQuote("the District"), normalizeForQuote("the district"));
});

const PAGES = join(process.cwd(), "..", "evidence", "bds");

test("real corpus: every recorded quotation appears on its cited page", async (t) => {
  const blobs = new Map<string, string>();
  for (const name of ["dsb_audit_2022.pdf", "dsb_audit_2024.pdf"]) {
    const path = join(PAGES, name.replace(/\.pdf$/, ".txt"));
    if (!existsSync(path)) {
      t.skip(`no extracted text at ${path}`);
      return;
    }
    // The extract is page-marked by `ledger`'s extractor: "=== PAGE n ===".
    const text = readFileSync(path, "utf8");
    const parts = text.split(/^=== PAGE (\d+) ===$/m);
    for (let i = 1; i < parts.length; i += 2) {
      const pageNo = Number.parseInt(parts[i] ?? "", 10);
      const body = parts[i + 1] ?? "";
      blobs.set(`${name}#${String(pageNo)}`, body);
    }
  }
  const checks = verifyQuotes(blobs);
  for (const check of checks) {
    assert.ok(check.found, `${check.id}: quotation not found on its cited page`);
  }
});
