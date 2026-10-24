/**
 * The audit engine and the autonomous investigator.
 *
 * The load-bearing test is the mutation: one character changed must turn a
 * verified span into a falsified one. A checker that cannot fail on a single
 * character is not checking anything.
 */

import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { audit, locateSpan, stripLineGutters } from "../src/audit.js";
import { canonicalJson, sha256Hex } from "../src/canonical.js";
import { investigate } from "../src/investigate.js";
import type { AuditInput } from "../src/audit.js";
import type { InvestigateInput } from "../src/investigate.js";
import type { Environment, Receipt } from "../src/types.js";

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

const SOURCE_TEXT = [
  "0001 The Watchers have no defense against a truth they cannot refute.",
  "0002 A quotation that crosses a line-number gutter is not one span.",
  "",
  "A line that is present.",
  "An intervening line.",
  "Another line that is present.",
].join("\n");

function tempDir(): string {
  return mkdtempSync(join(tmpdir(), "burden-test-"));
}

/** Guarded disposal: only a burden test directory may be removed. */
function dispose(dir: string): void {
  if (!dir.startsWith(tmpdir()) || !dir.includes("burden-test-")) {
    throw new Error(`refusing to remove ${dir}`);
  }
  rmSync(dir, { recursive: true, force: true });
}

function withSource(): { readonly dir: string; readonly path: string } {
  const dir = tempDir();
  const path = join(dir, "source.txt");
  writeFileSync(path, SOURCE_TEXT, "utf8");
  return { dir, path };
}

function input(path: string, overrides: Partial<AuditInput> = {}): AuditInput {
  return {
    claimId: "CLM-AUDIT-1",
    claim: "the span occurs verbatim in the named source",
    bearing: "supporting",
    checkability: "machine_checkable",
    missingMeasurement: null,
    quote: "The Watchers have no defense against a truth they cannot refute.",
    sourcePath: path,
    displayPath: "source.txt",
    expectedSha256: null,
    falsifierCommand: "burden audit --id CLM-AUDIT-1 --source source.txt --quote '<span>'",
    actor: "audit-test",
    ...overrides,
  };
}

function code(receipt: Receipt): string {
  return receipt.verdict.code;
}

test("an exact contiguous span is verified at fetched tier", () => {
  const { dir, path } = withSource();
  try {
    const receipt = audit(input(path), ENV);
    assert.equal(receipt.verdict.kind, "verified");
    assert.equal(code(receipt), "SPAN_EXACT");
    assert.equal(receipt.tier, "fetched");
    assert.equal(receipt.source?.sha256, sha256Hex(SOURCE_TEXT));
    assert.equal(receipt.source?.bytes, Buffer.byteLength(SOURCE_TEXT));
    assert.ok(receipt.derivation.some((step) => step.check === "span_exact" && step.ok));
  } finally {
    dispose(dir);
  }
});

test("one changed character falsifies the claim", () => {
  const { dir, path } = withSource();
  try {
    const receipt = audit(
      input(path, {
        quote: "The Watchers have no defense against a truth they cannot refute!",
      }),
      ENV,
    );
    assert.equal(receipt.verdict.kind, "falsified");
    assert.equal(code(receipt), "SPAN_NOT_FOUND");
    assert.equal(receipt.tier, "unverified");
  } finally {
    dispose(dir);
  }
});

test("a span that crosses a line-number gutter is falsified and disclosed", () => {
  const { dir, path } = withSource();
  try {
    const receipt = audit(
      input(path, {
        quote:
          "The Watchers have no defense against a truth they cannot refute.\nA quotation that crosses a line-number gutter is not one span.",
      }),
      ENV,
    );
    assert.equal(receipt.verdict.kind, "falsified");
    assert.equal(code(receipt), "SPAN_GUTTER_ARTIFACT");
    const diagnosis = receipt.derivation.find((step) => step.check === "gutter_diagnosis");
    assert.ok(diagnosis !== undefined);
    assert.ok(diagnosis.detail.includes("disclosed, not stripped"));
  } finally {
    dispose(dir);
  }
});

test("lines that occur separately do not make a span", () => {
  const { dir, path } = withSource();
  try {
    const receipt = audit(
      input(path, {
        quote: "A line that is present.\nAnother line that is present.",
      }),
      ENV,
    );
    assert.equal(receipt.verdict.kind, "falsified");
    assert.equal(code(receipt), "SPAN_NONCONTIGUOUS");
  } finally {
    dispose(dir);
  }
});

test("a named source with the wrong hash is falsified before the span is read", () => {
  const { dir, path } = withSource();
  try {
    const receipt = audit(input(path, { expectedSha256: "b".repeat(64) }), ENV);
    assert.equal(receipt.verdict.kind, "falsified");
    assert.equal(code(receipt), "SOURCE_HASH_MISMATCH");
    assert.equal(receipt.tier, "unverified");
  } finally {
    dispose(dir);
  }
});

test("a missing source is a finding, not a crash", () => {
  const { dir } = withSource();
  try {
    const receipt = audit(input(join(dir, "absent.txt")), ENV);
    assert.equal(receipt.verdict.kind, "falsified");
    assert.equal(code(receipt), "SOURCE_MISSING");
  } finally {
    dispose(dir);
  }
});

test("an empty or oversized span is rejected before any read", () => {
  const { dir, path } = withSource();
  try {
    assert.equal(code(audit(input(path, { quote: "   " }), ENV)), "QUOTE_EMPTY");
    assert.equal(
      code(audit(input(path, { quote: "x".repeat(2001) }), ENV)),
      "QUOTE_TOO_LONG",
    );
  } finally {
    dispose(dir);
  }
});

test("the same inputs produce byte-identical receipts", () => {
  const { dir, path } = withSource();
  try {
    const first = audit(input(path), ENV);
    const second = audit(input(path), ENV);
    assert.equal(canonicalJson(first), canonicalJson(second));
  } finally {
    dispose(dir);
  }
});

test("line gutters are stripped for diagnosis only", () => {
  const stripped = stripLineGutters("0001 first\n0002 second\nplain third");
  assert.equal(stripped.removed, 2);
  assert.equal(stripped.normalized, "first\nsecond\nplain third");
});

test("locateSpan reports 1-based line numbers", () => {
  const finding = locateSpan(SOURCE_TEXT, "A line that is present.");
  assert.equal(finding.kind, "exact");
  if (finding.kind === "exact") {
    assert.equal(finding.lineStart, 4);
    assert.equal(finding.lineEnd, 4);
  }
});

function investigationInput(
  root: string,
  overrides: Partial<InvestigateInput> = {},
): InvestigateInput {
  return {
    claimId: "CLM-INVESTIGATE-1",
    claim: "the span occurs in the corpus",
    bearing: "supporting",
    checkability: "machine_checkable",
    missingMeasurement: null,
    quote: "A line that is present.",
    root,
    extensions: [".txt"],
    maxFiles: 50,
    expectedSha256: null,
    falsifierCommand: "burden investigate --id CLM-INVESTIGATE-1 --corpus <root> --quote '<span>'",
    actor: "investigate-test",
    ...overrides,
  };
}

test("investigate finds the source without being told which file", () => {
  const dir = tempDir();
  try {
    mkdirSync(join(dir, "a"));
    mkdirSync(join(dir, "b"));
    writeFileSync(join(dir, "b", "noise.txt"), "nothing here\n", "utf8");
    writeFileSync(join(dir, "a", "target.txt"), SOURCE_TEXT, "utf8");

    const result = investigate(investigationInput(dir), ENV);
    assert.equal(result.receipt.verdict.kind, "verified");
    assert.equal(result.receipt.source?.path, "a/target.txt");
    assert.deepEqual(result.matches, ["a/target.txt"]);
    assert.ok(result.scanned >= 2);
  } finally {
    dispose(dir);
  }
});

test("investigate refuses to guess between two matching sources", () => {
  const dir = tempDir();
  try {
    writeFileSync(join(dir, "one.txt"), SOURCE_TEXT, "utf8");
    writeFileSync(join(dir, "two.txt"), SOURCE_TEXT, "utf8");

    const result = investigate(investigationInput(dir), ENV);
    assert.equal(result.receipt.verdict.kind, "falsified");
    assert.equal(result.receipt.verdict.code, "AMBIGUOUS_SOURCE");
    assert.equal(result.matches.length, 2);
  } finally {
    dispose(dir);
  }
});

test("investigate reports an absent span across the whole corpus", () => {
  const dir = tempDir();
  try {
    writeFileSync(join(dir, "one.txt"), "nothing here\n", "utf8");
    const result = investigate(
      investigationInput(dir, { quote: "A line that is not present." }),
      ENV,
    );
    assert.equal(result.receipt.verdict.kind, "falsified");
    assert.equal(result.receipt.verdict.code, "SPAN_NOT_FOUND_IN_CORPUS");
    assert.equal(result.scanned, 1);
  } finally {
    dispose(dir);
  }
});

test("investigate traversal is deterministic", () => {
  const dir = tempDir();
  try {
    mkdirSync(join(dir, "z"));
    mkdirSync(join(dir, "a"));
    writeFileSync(join(dir, "z", "one.txt"), "nothing\n", "utf8");
    writeFileSync(join(dir, "a", "two.txt"), "nothing\n", "utf8");
    const first = investigate(investigationInput(dir, { quote: "absent" }), ENV);
    const second = investigate(investigationInput(dir, { quote: "absent" }), ENV);
    assert.equal(canonicalJson(first.receipt), canonicalJson(second.receipt));
  } finally {
    dispose(dir);
  }
});

test("an empty span is rejected before the corpus is walked", () => {
  const dir = tempDir();
  try {
    writeFileSync(join(dir, "one.txt"), "anything at all\n", "utf8");
    const result = investigate(investigationInput(dir, { quote: "   " }), ENV);
    assert.equal(result.receipt.verdict.code, "QUOTE_EMPTY");
    assert.equal(result.scanned, 0);
    assert.equal(result.matches.length, 0);
  } finally {
    dispose(dir);
  }
});
