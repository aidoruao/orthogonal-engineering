/**
 * Tests for `money.ts`.
 *
 * The pattern is the same as elsewhere: every invariant is exercised once where
 * it holds and once where it is refuted and the refusal is correct. The
 * interesting cases are the two the standing question turns on — an overrun
 * with no board action, and a residual nobody owns.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  labourShare,
  ratio,
  traceMoney,
  type BudgetLine,
  type MoneyFindingKind,
} from "../src/money.js";

const within = { kind: "within_budget" } as const;

const line = (
  code: string,
  allocated: bigint,
  spent: bigint,
  extra: Partial<BudgetLine> = {},
): BudgetLine => ({ code, label: `line ${code}`, allocated, spent, authority: within, ...extra });

function kinds(lines: readonly BudgetLine[]): readonly MoneyFindingKind[] {
  const e = traceMoney(lines);
  assert.equal(e.ok, true);
  if (!e.ok) return [];
  return e.value.findings.map((f) => f.kind);
}

test("a clean budget closes", () => {
  const e = traceMoney([
    line("5100", 1_000n, 900n, { residualOwner: "general fund carryover" }),
    line("5200", 500n, 500n),
  ]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.closed, true);
  assert.equal(e.value.totalAllocated, 1_500n);
  assert.equal(e.value.totalSpent, 1_400n);
  assert.equal(e.value.totalResidual, 100n);
});

test("conservation holds across the whole budget", () => {
  const e = traceMoney([
    line("a", 100n, 40n, { residualOwner: "x" }),
    line("b", 200n, 250n, { authority: { kind: "amended", reference: "min 2024-11", recordedOn: "2024-05-14" } }),
  ]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(
    e.value.totalAllocated,
    e.value.totalSpent + e.value.totalResidual,
  );
});

test("an overrun with no board action is a finding, and its size is named", () => {
  const e = traceMoney([line("3300", 1_000n, 1_150n)]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.closed, false);
  const f = e.value.findings.find((x) => x.kind === "overrun_without_authority");
  assert.ok(f);
  assert.equal(f?.amount, 150n);
  assert.match(f?.detail ?? "", /150 above/);
  // The falsifier must be a document someone could go and fetch.
  assert.match(f?.falsifier ?? "", /board minute|amendment|resolution/);
});

test("an overrun with a recorded amendment is not a finding", () => {
  assert.deepEqual(
    kinds([
      line("3300", 1_000n, 1_150n, {
        authority: { kind: "amended", reference: "min 2024-11 p.4", recordedOn: "2024-05-14" },
      }),
    ]),
    [],
  );
});

test("an amendment with an empty reference is not an authority", () => {
  assert.deepEqual(
    kinds([
      line("3300", 1_000n, 1_150n, {
        authority: { kind: "amended", reference: "   ", recordedOn: "2024-05-14" },
      }),
    ]),
    ["authority_not_recorded"],
  );
});

test("an unowned residual is a finding — this is where money stops being traceable", () => {
  const e = traceMoney([line("4400", 1_000n, 800n)]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  const f = e.value.findings.find((x) => x.kind === "residual_unowned");
  assert.ok(f);
  assert.equal(f?.amount, 200n);
});

test("an owned residual is not a finding", () => {
  assert.deepEqual(kinds([line("4400", 1_000n, 800n, { residualOwner: "fund balance" })]), []);
});

test("an exact spend leaves no residual and needs no owner", () => {
  assert.deepEqual(kinds([line("5100", 700n, 700n)]), []);
});

test("a duplicate object code is refused — one of the two would be dropped", () => {
  const e = traceMoney([line("5100", 1n, 1n), line("5100", 2n, 2n)]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "duplicate-code");
});

test("a negative appropriation is refused as an input", () => {
  const e = traceMoney([line("5100", -5n, 0n)]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "negative_line");
});

test("a trace with findings is still a successful trace", () => {
  // The distinction matters: the instrument worked. The account has holes.
  const e = traceMoney([line("3300", 100n, 200n)]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.closed, false);
  assert.ok(e.value.findings.length > 0);
});

/* --------------------------------------------------------------- ratios */

test("a ratio with no denominator is unmeasured, not zero and not one", () => {
  const r = ratio(0n, 0n);
  assert.equal(r.kind, "unmeasured");
  if (r.kind !== "unmeasured") return;
  assert.match(r.why, /not 0%/);
});

test("a ratio is exact integer basis points", () => {
  const r = ratio(1n, 3n);
  assert.equal(r.kind, "measured");
  if (r.kind !== "measured") return;
  assert.equal(r.value, 3333n); // 33.33%, truncated exactly, never 0.333...
});

test("labour share answers the question the record can answer", () => {
  const e = labourShare(750n, 1_000n);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.kind, "measured");
  if (e.value.kind !== "measured") return;
  assert.equal(e.value.value, 7500n);
});

test("labour share refuses when there is no expenditure to divide by", () => {
  const e = labourShare(0n, 0n);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "unmeasured");
});

test("parts exceeding the whole is refused, and neither figure is used", () => {
  const e = labourShare(1_200n, 1_000n);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "labour-exceeds-total");
});
