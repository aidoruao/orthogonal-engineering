/**
 * Selection ledger tests.
 *
 * The rule under test: every candidate gets exactly one disposition, and every
 * non-acceptance carries a reason. A candidate that vanishes is the failure
 * mode this instrument exists to catch.
 */

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import {
  auditSelection,
  isAccepted,
  isRejected,
  isWithheld,
  parseLedger,
  partitionHolds,
  serializeLedger,
  type Disposition,
  type SelectionLedger,
} from "../src/selection.js";

function accepted(): Disposition {
  return { kind: "accepted" };
}
function rejected(code: "quote_not_found" | "duplicate" | "out_of_scope"): Disposition {
  return { kind: "rejected", code };
}
function withheld(code: "third_party_identity" | "user_declined"): Disposition {
  return { kind: "withheld", code };
}

describe("auditSelection — the clean case", () => {
  it("accepts a complete, sorted selection", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: accepted() },
        { claimId: "CLM-B", disposition: rejected("quote_not_found") },
        { claimId: "CLM-C", disposition: withheld("third_party_identity") },
      ],
    };
    const report = auditSelection(["CLM-A", "CLM-B", "CLM-C"], ledger);
    assert.equal(report.violations.length, 0);
    assert.equal(report.accepted, 1);
    assert.equal(report.rejected, 1);
    assert.equal(report.withheld, 1);
    assert.equal(report.total, 3);
    assert.equal(partitionHolds(report), true);
  });

  it("counts by reason code", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: rejected("quote_not_found") },
        { claimId: "CLM-B", disposition: rejected("quote_not_found") },
        { claimId: "CLM-C", disposition: rejected("duplicate") },
      ],
    };
    const report = auditSelection(["CLM-A", "CLM-B", "CLM-C"], ledger);
    assert.equal(report.byCode.get("quote_not_found"), 2);
    assert.equal(report.byCode.get("duplicate"), 1);
  });

  it("accepts an empty selection when there were no candidates", () => {
    const report = auditSelection([], { entries: [] });
    assert.equal(report.total, 0);
    assert.equal(partitionHolds(report), true);
  });
});

describe("auditSelection — the silent drop", () => {
  it("flags a candidate with no disposition", () => {
    const ledger: SelectionLedger = {
      entries: [{ claimId: "CLM-A", disposition: accepted() }],
    };
    const report = auditSelection(["CLM-A", "CLM-B"], ledger);
    assert.equal(report.violations.length, 1);
    assert.equal(report.violations[0]?.code, "missing_disposition");
    assert.equal(report.violations[0]?.claimId, "CLM-B");
    assert.equal(partitionHolds(report), false);
  });

  it("flags every dropped candidate, not just the first", () => {
    const report = auditSelection(["CLM-A", "CLM-B", "CLM-C"], { entries: [] });
    assert.equal(report.violations.length, 3);
    assert.deepEqual(
      report.violations.map((v) => v.claimId),
      ["CLM-A", "CLM-B", "CLM-C"],
    );
  });

  it("flags a disposition for a candidate that was never drafted", () => {
    const ledger: SelectionLedger = {
      entries: [{ claimId: "CLM-GHOST", disposition: accepted() }],
    };
    const report = auditSelection(["CLM-A"], ledger);
    const codes = report.violations.map((v) => v.code);
    assert.ok(codes.includes("orphan_disposition"));
    assert.ok(codes.includes("missing_disposition"));
  });
});

describe("auditSelection — reasons and codes", () => {
  it("flags a rejection with an empty reason", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: { kind: "rejected", code: "" as never } },
      ],
    };
    const report = auditSelection(["CLM-A"], ledger);
    assert.equal(report.violations[0]?.code, "empty_reason");
  });

  it("flags a rejection with a whitespace-only reason", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: { kind: "rejected", code: "   " as never } },
      ],
    };
    const report = auditSelection(["CLM-A"], ledger);
    assert.equal(report.violations[0]?.code, "empty_reason");
  });

  it("flags an unknown reason code", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: { kind: "rejected", code: "felt_wrong" as never } },
      ],
    };
    const report = auditSelection(["CLM-A"], ledger);
    assert.equal(report.violations[0]?.code, "unknown_reason_code");
  });

  it("does not require a reason for an accepted claim", () => {
    const report = auditSelection(["CLM-A"], {
      entries: [{ claimId: "CLM-A", disposition: accepted() }],
    });
    assert.equal(report.violations.length, 0);
  });
});

describe("auditSelection — determinism", () => {
  it("flags an unsorted ledger", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-B", disposition: accepted() },
        { claimId: "CLM-A", disposition: accepted() },
      ],
    };
    const report = auditSelection(["CLM-A", "CLM-B"], ledger);
    assert.ok(report.violations.some((v) => v.code === "not_sorted"));
  });

  it("flags a duplicate candidate id in the input", () => {
    const report = auditSelection(["CLM-A", "CLM-A"], {
      entries: [{ claimId: "CLM-A", disposition: accepted() }],
    });
    assert.ok(report.violations.some((v) => v.code === "duplicate_candidate"));
  });

  it("flags a duplicate entry", () => {
    const report = auditSelection(["CLM-A"], {
      entries: [
        { claimId: "CLM-A", disposition: accepted() },
        { claimId: "CLM-A", disposition: rejected("duplicate") },
      ],
    });
    assert.ok(report.violations.some((v) => v.code === "duplicate_candidate"));
  });

  it("sorts violations deterministically", () => {
    const ledger: SelectionLedger = { entries: [] };
    const first = auditSelection(["CLM-B", "CLM-A"], ledger);
    const second = auditSelection(["CLM-B", "CLM-A"], ledger);
    assert.deepEqual(first.violations, second.violations);
  });
});

describe("serialization", () => {
  it("round-trips a ledger", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: accepted() },
        { claimId: "CLM-B", disposition: rejected("quote_not_found") },
        { claimId: "CLM-C", disposition: withheld("third_party_identity") },
      ],
    };
    const text = serializeLedger(ledger);
    const parsed = parseLedger(text);
    assert.equal(parsed.malformed.length, 0);
    assert.deepEqual(parsed.ledger.entries, ledger.entries);
  });

  it("writes deterministically, sorted by claimId", () => {
    const one: SelectionLedger = {
      entries: [
        { claimId: "CLM-B", disposition: accepted() },
        { claimId: "CLM-A", disposition: rejected("duplicate") },
      ],
    };
    const two: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: rejected("duplicate") },
        { claimId: "CLM-B", disposition: accepted() },
      ],
    };
    assert.equal(serializeLedger(one), serializeLedger(two));
    const lines = serializeLedger(one).trimEnd().split("\n");
    assert.match(lines[0] ?? "", /CLM-A/);
  });

  it("omits the code for accepted entries", () => {
    const text = serializeLedger({ entries: [{ claimId: "CLM-A", disposition: accepted() }] });
    assert.equal(text.trim(), '{"claimId":"CLM-A","disposition":"accepted"}');
  });

  it("reports malformed lines rather than dropping them", () => {
    const parsed = parseLedger("not json\n{\"claimId\":\"CLM-A\",\"disposition\":\"accepted\"}\n");
    assert.equal(parsed.malformed.length, 1);
    assert.equal(parsed.ledger.entries.length, 1);
  });

  it("rejects a rejected entry with no code", () => {
    const parsed = parseLedger('{"claimId":"CLM-A","disposition":"rejected"}\n');
    assert.equal(parsed.malformed.length, 1);
  });

  it("rejects an unknown disposition", () => {
    const parsed = parseLedger('{"claimId":"CLM-A","disposition":"maybe"}\n');
    assert.equal(parsed.malformed.length, 1);
  });
});

describe("disposition predicates", () => {
  it("classifies each kind exactly once", () => {
    for (const d of [accepted(), rejected("duplicate"), withheld("user_declined")]) {
      const count = [isAccepted(d), isRejected(d), isWithheld(d)].filter(Boolean).length;
      assert.equal(count, 1);
    }
  });
});

describe("cross-check with the Lean proof", () => {
  // L1_SELECTION.lean proves `example_partition` over this exact vector:
  //   candidates [CLM-A, CLM-B, CLM-C, CLM-D]
  //   accepted 1, rejected 2, withheld 1, total 4
  // If this test and the Lean theorem ever disagree, one of them is wrong.
  it("reproduces the Lean example counts", () => {
    const ledger: SelectionLedger = {
      entries: [
        { claimId: "CLM-A", disposition: accepted() },
        { claimId: "CLM-B", disposition: rejected("quote_not_found") },
        { claimId: "CLM-C", disposition: withheld("third_party_identity") },
        { claimId: "CLM-D", disposition: rejected("duplicate") },
      ],
    };
    const report = auditSelection(
      ["CLM-A", "CLM-B", "CLM-C", "CLM-D"],
      ledger,
    );
    assert.equal(report.accepted, 1);
    assert.equal(report.rejected, 2);
    assert.equal(report.withheld, 1);
    assert.equal(report.total, 4);
    assert.equal(partitionHolds(report), true);
  });
});
