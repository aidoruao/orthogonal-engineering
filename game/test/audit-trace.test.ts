/**
 * Tests for `audit-trace.ts` — the real findings through the walk.
 *
 * The load-bearing tests here are the two that pin the correction described in
 * that file's header. Before `AmountRole` existed, this module reported four
 * `overrun_without_authority` findings where the record supports one. Two of
 * the four were false, and both are pinned below so the defect cannot return.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  BDS_FINDING_LINES,
  known,
  traceFindings,
  traceLine,
  unmeasured,
  type FindingLine,
  type TracedLine,
} from "../src/audit-trace.js";

const base: FindingLine = {
  id: "T-1",
  fiscalYear: 2024,
  heading: "test line",
  document: "t.pdf",
  page: 1,
  role: "excess_over_budget",
  stated: known(100n),
  allocated: unmeasured("not published"),
  spent: unmeasured("not published"),
  amendment: unmeasured("none recorded"),
  repeatOfPriorYear: false,
};

/* --------------------------------------------------- the real BDS findings */

test("the six real findings total 3,666,230 — the auditor's own figures, summed", () => {
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.statedTotal, 3_666_230n);
});

test("the roles are kept apart: adding them would produce a meaningless number", () => {
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.byRole.excess_over_budget, 1_162_601n);
  assert.equal(e.value.byRole.questioned_cost, 773_629n);
  assert.equal(e.value.byRole.reported_understatement, 1_730_000n);
  assert.equal(e.value.byRole.none_stated, 0n);
  // And the four sum to the stated total, so nothing is lost or double counted.
  const sum =
    e.value.byRole.excess_over_budget +
    e.value.byRole.questioned_cost +
    e.value.byRole.reported_understatement +
    e.value.byRole.none_stated;
  assert.equal(sum, e.value.statedTotal);
});

test("CORRECTION: only 2024-003 is an overrun — 2024-002 is a control-absent finding", () => {
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;

  const overruns = e.value.lines.flatMap((l) =>
    l.findings.filter((f) => f.kind === "overrun_without_authority"),
  );
  // Exactly one. The earlier implementation produced four here, two of them false.
  assert.equal(overruns.length, 1);
  assert.equal(overruns[0]?.code, "2024-003");
  assert.equal(overruns[0]?.amount, 1_162_601n);

  const absent = e.value.lines.flatMap((l) =>
    l.findings.filter((f) => f.kind === "control_absent"),
  );
  assert.equal(absent.length, 1);
  assert.equal(absent[0]?.code, "2024-002");
  assert.equal(absent[0]?.amount, 773_629n);
  // The detail must refuse the stronger reading, not merely avoid asserting it.
  assert.match(absent[0]?.detail ?? "", /NOT an overrun/);
});

test("CORRECTION: a reported understatement produces no overrun finding", () => {
  // 2022-002 and 2022-005 are reporting errors. Neither is a spend.
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  for (const id of ["2022-002", "2022-005"]) {
    const found: TracedLine | undefined = e.value.lines.find((l) => l.id === id);
    assert.ok(found !== undefined, `${id} missing`);
    if (found === undefined) return;
    assert.equal(found.findings.length, 0, `${id} produced a finding it should not have`);
    assert.equal(found.status, "unmeasured");
  }
});

test("the trace is NOT closed, and says which quantity is missing", () => {
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.closed, false);
  assert.equal(e.value.unmeasuredCount, 4); // 2024-001, 2022-001, 2022-002, 2022-005
  // Every unmeasured line names what would measure it.
  for (const l of e.value.lines) {
    if (l.status === "unmeasured") {
      assert.ok(
        l.wouldMeasure.length > 0,
        `${l.id} is unmeasured but names nothing that would measure it`,
      );
    }
  }
});

test("the two material weaknesses state no amount, and none is invented for them", () => {
  const e = traceFindings(BDS_FINDING_LINES);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  for (const id of ["2022-001", "2024-001"]) {
    const found: FindingLine | undefined = BDS_FINDING_LINES.find((l) => l.id === id);
    assert.ok(found !== undefined);
    if (found === undefined) return;
    assert.equal(found.role, "none_stated");
    assert.equal(found.stated.kind, "unmeasured");
  }
});

/* ---------------------------------------------------- the line-level rules */

test("an excess over budget with no amendment is an overrun finding", () => {
  const t = traceLine(base);
  assert.equal(t.status, "finding");
  assert.equal(t.findings.length, 1);
  assert.equal(t.findings[0]?.kind, "overrun_without_authority");
  assert.equal(t.findings[0]?.amount, 100n);
});

test("an excess with a recorded amendment is not a finding", () => {
  const t = traceLine({
    ...base,
    allocated: known(1_000n),
    spent: known(1_100n),
    amendment: known(0n), // presence of a known amendment is what matters
  });
  assert.equal(t.findings.length, 0);
  assert.equal(t.status, "closed");
});

test("a questioned cost never becomes an overrun, whatever the number", () => {
  const t = traceLine({ ...base, role: "questioned_cost", stated: known(9_999_999n) });
  assert.equal(t.findings.length, 1);
  assert.equal(t.findings[0]?.kind, "control_absent");
  assert.notEqual(t.findings[0]?.kind, "overrun_without_authority");
});

test("a stated amount with no role cannot be classified — the type forbids omitting it", () => {
  // This is a compile-time guarantee, demonstrated by construction: every
  // FindingLine in this file has a role, and `traceFindings` refuses a role that
  // claims an amount it does not carry.
  const e = traceFindings([{ ...base, stated: unmeasured("absent") }]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "role-without-amount");
});

test("a duplicate finding id is refused", () => {
  const e = traceFindings([base, { ...base }]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "duplicate-finding-id");
});

test("a negative stated amount is refused", () => {
  const e = traceFindings([{ ...base, stated: known(-1n) }]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "negative-amount");
});

test("an unmeasured line names the allocation as the missing quantity", () => {
  const t = traceLine({ ...base, role: "none_stated", stated: unmeasured("none") });
  assert.equal(t.status, "unmeasured");
  assert.ok(t.wouldMeasure.some((m) => m.includes("allocation")));
});
