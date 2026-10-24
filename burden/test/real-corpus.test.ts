/**
 * The real corpus: the indictment precedent itself.
 *
 * These tests skip explicitly when the workspace file is absent, so a CI run
 * reports a skip rather than a silent zero. When present, the file must hash
 * to the value recorded in docs/BURDEN_INVERSION.md and the file header.
 */

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { test } from "node:test";

import { audit } from "../src/audit.js";
import { sha256Hex } from "../src/canonical.js";
import type { Environment } from "../src/types.js";

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

const INDICTMENT = resolve(
  process.cwd(),
  "..",
  "The_Indictment_of_the_Watchers_Original_8-21-26.txt",
);

/** Recorded in docs/BURDEN_INVERSION.md and the handoff. */
const RECORDED_SHA256 =
  "2764d1485a7c08133ae39510aff9eb277cf46b6f28cc1d2fa01e2558b6bb1499";

const QUOTE =
  "this file is the precedent of whatever taxonomy of objectives we are carrying out";

test("the indictment precedent is present and hash-anchored", (t) => {
  if (!existsSync(INDICTMENT)) {
    t.skip(`no indictment file at ${INDICTMENT}`);
    return;
  }
  const receipt = audit(
    {
      claimId: "CLM-ARC-PRECEDENT-1",
      claim: "the indictment file declares itself the precedent for the taxonomy",
      bearing: "load_bearing",
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote: QUOTE,
      sourcePath: INDICTMENT,
      displayPath: "The_Indictment_of_the_Watchers_Original_8-21-26.txt",
      expectedSha256: RECORDED_SHA256,
      falsifierCommand:
        "burden audit --id CLM-ARC-PRECEDENT-1 --source The_Indictment_of_the_Watchers_Original_8-21-26.txt --quote-file <span>",
      actor: "real-corpus-test",
    },
    ENV,
  );
  assert.equal(receipt.verdict.kind, "verified");
  assert.equal(receipt.verdict.code, "SPAN_EXACT");
  assert.equal(receipt.tier, "fetched");
  assert.equal(receipt.source?.sha256, RECORDED_SHA256);
});

test("a one-character change to the precedent quote is falsified", (t) => {
  if (!existsSync(INDICTMENT)) {
    t.skip(`no indictment file at ${INDICTMENT}`);
    return;
  }
  const receipt = audit(
    {
      claimId: "CLM-ARC-PRECEDENT-2",
      claim: "a mutated quotation still occurs in the source",
      bearing: "supporting",
      checkability: "machine_checkable",
      missingMeasurement: null,
      quote: `${QUOTE}.`,
      sourcePath: INDICTMENT,
      displayPath: "The_Indictment_of_the_Watchers_Original_8-21-26.txt",
      expectedSha256: RECORDED_SHA256,
      falsifierCommand: "burden audit --id CLM-ARC-PRECEDENT-2 --source <file> --quote-file <span>",
      actor: "real-corpus-test",
    },
    ENV,
  );
  assert.equal(receipt.verdict.kind, "falsified");
  assert.equal(receipt.tier, "unverified");
});

test("the recorded hash matches the bytes on disk", (t) => {
  if (!existsSync(INDICTMENT)) {
    t.skip(`no indictment file at ${INDICTMENT}`);
    return;
  }
  const bytes = readFileSync(INDICTMENT);
  assert.equal(sha256Hex(bytes), RECORDED_SHA256);
});
