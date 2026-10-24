/**
 * The append-only ledger: the chain is the calibration substrate, so a
 * rewrite must be detectable and an append to a broken chain must be refused.
 */

import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { admitOrThrow } from "../src/audit.js";
import { canonicalJson } from "../src/canonical.js";
import { GENESIS, appendReceipt, readLedger, verifyLedger } from "../src/ledger.js";
import type {
  Bearing,
  Environment,
  Receipt,
  Tier,
  Verdict,
} from "../src/types.js";

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

const AT = "2026-10-24T09:00:00.000Z";

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "burden-test-"));
}

function dispose(dir: string): void {
  if (!dir.startsWith(tmpdir()) || !dir.includes("burden-test-")) {
    throw new Error(`refusing to remove ${dir}`);
  }
  rmSync(dir, { recursive: true, force: true });
}

function makeReceipt(args: {
  readonly claimId: string;
  readonly tier: Tier;
  readonly kind: Verdict;
  readonly bearing: Bearing;
  readonly code: string;
}): Receipt {
  return admitOrThrow({
    schema: "burden.receipt/1",
    claimId: args.claimId,
    claim: "a ledger test claim",
    bearing: args.bearing,
    checkability: "machine_checkable",
    missingMeasurement: null,
    tier: args.tier,
    source: {
      path: "fixtures/source.txt",
      sha256: "a".repeat(64),
      bytes: 10,
    },
    derivation: [{ check: "span_exact", ok: true, detail: "found at line 1" }],
    falsifier: {
      command: "burden audit --claim <id>",
      refutes: "the span is absent",
    },
    owner: { actor: "ledger-test", tool: "burden/test", environment: ENV },
    verdict: { kind: args.kind, code: args.code, detail: "recorded by a test" },
  });
}

test("three appends produce a verifiable chain", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    const first = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-1",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    assert.equal(first.ok, true);
    if (!first.ok) return;
    assert.equal(first.entry.seq, 0);
    assert.equal(first.entry.prev, GENESIS);

    const second = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-2",
        tier: "unverified",
        kind: "falsified",
        bearing: "supporting",
        code: "SPAN_NOT_FOUND",
      }),
      AT,
    );
    assert.equal(second.ok, true);
    if (!second.ok) return;
    assert.equal(second.entry.seq, 1);
    assert.equal(second.entry.prev, first.entry.entrySha256);

    const third = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-3",
        tier: "unverified",
        kind: "unmeasured",
        bearing: "load_bearing",
        code: "NOT_RUN",
      }),
      AT,
    );
    assert.equal(third.ok, true);

    const verified = verifyLedger(path);
    assert.equal(verified.ok, true);
    assert.equal(verified.entries, 3);
  } finally {
    dispose(dir);
  }
});

test("editing a receipt breaks the chain", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-1",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    const text = readFileSync(path, "utf8");
    writeFileSync(path, text.replace('"bytes":10', '"bytes":11'), "utf8");

    const verified = verifyLedger(path);
    assert.equal(verified.ok, false);
    assert.ok(
      verified.failures.some((failure) => failure.code === "LEDGER_HASH_MISMATCH"),
    );
  } finally {
    dispose(dir);
  }
});

test("an unparseable line is reported, never skipped", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    writeFileSync(path, "this is not json\n", "utf8");
    const read = readLedger(path);
    assert.equal(read.entries.length, 0);
    assert.equal(read.failures.length, 1);
    assert.equal(read.failures[0]?.code, "LEDGER_UNPARSEABLE");
  } finally {
    dispose(dir);
  }
});

test("appending to a broken ledger is refused", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    writeFileSync(path, "this is not json\n", "utf8");
    const result = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-9",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    assert.equal(result.ok, false);
    assert.equal(readFileSync(path, "utf8"), "this is not json\n");
  } finally {
    dispose(dir);
  }
});

test("each line is canonical JSON with sorted keys", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    const written = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-1",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    assert.equal(written.ok, true);
    if (!written.ok) return;
    const line = readFileSync(path, "utf8").trim();
    assert.ok(line.startsWith('{"entrySha256":'));
    assert.equal(line, canonicalJson(written.entry));
  } finally {
    dispose(dir);
  }
});

test("an expected head anchors the tail against truncation", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-1",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    const second = appendReceipt(
      path,
      makeReceipt({
        claimId: "CLM-LEDGER-2",
        tier: "fetched",
        kind: "verified",
        bearing: "supporting",
        code: "SPAN_EXACT",
      }),
      AT,
    );
    assert.equal(second.ok, true);
    if (!second.ok) return;

    assert.equal(verifyLedger(path, second.entry.entrySha256).ok, true);
    const wrong = verifyLedger(path, "c".repeat(64));
    assert.equal(wrong.ok, false);
    assert.ok(
      wrong.failures.some((failure) => failure.code === "LEDGER_HEAD_MISMATCH"),
    );
  } finally {
    dispose(dir);
  }
});

test("an interior blank line is reported, never stepped over", () => {
  const dir = tempDir();
  try {
    const path = join(dir, "receipts.jsonl");
    writeFileSync(path, "\n", "utf8");
    const read = readLedger(path);
    assert.ok(read.failures.some((failure) => failure.code === "LEDGER_BLANK_LINE"));
  } finally {
    dispose(dir);
  }
});
