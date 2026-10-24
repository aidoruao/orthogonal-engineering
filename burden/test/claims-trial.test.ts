/**
 * The claims trial: the tool against the ledger's own published claims.
 *
 * This is the only test in the package that can contradict work already
 * published. It runs the 17 claims in `ledger/drafts/verified.jsonl` against the
 * L0 corpus and requires every one to be reproducible.
 *
 * Then it does the harder thing: it mutates real claims and requires the audit
 * to catch each mutation. A verifier that agrees with everything proves
 * nothing, and its first trial is exactly when to doubt it. Three mutants:
 *
 *   wrong page              -> QUOTE_NOT_ON_CITED_PAGE
 *   one character changed   -> QUOTE_NOT_ON_CITED_PAGE
 *   source not committed    -> SOURCE_NOT_IN_MANIFEST
 *
 * The mutations are asserted to have actually changed the line before the
 * audit runs, because a `sed` that silently matches nothing would otherwise
 * produce a passing "mutation" test that mutates nothing.
 *
 * Skips explicitly when the L0 corpus is absent, so a CI run reports a skip
 * rather than a silent zero.
 */

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { test } from "node:test";

import { auditClaim, loadExtractor, parseClaim, parseManifest } from "../src/claims.js";
import type { ClaimInput } from "../src/claims.js";
import type { Environment, Receipt } from "../src/types.js";

const HOME = resolve(process.cwd(), "..");
const CORPUS = resolve(HOME, "evidence", "fleites");
const MANIFEST = resolve(CORPUS, "FLEITES_MANIFEST.sha256");
const CLAIMS = resolve(HOME, "ledger", "drafts", "verified.jsonl");
const EXTRACTOR = resolve(HOME, "ledger", "dist", "src", "extract.js");

const ENV: Environment = {
  node: "v22.0.0",
  lean: "Lean (test)",
  platform: "linux-test",
};

function corpusPresent(): boolean {
  return (
    existsSync(MANIFEST) && existsSync(CLAIMS) && existsSync(EXTRACTOR) && existsSync(CORPUS)
  );
}

function readClaims(): readonly ClaimInput[] {
  const lines = readFileSync(CLAIMS, "utf8").split("\n");
  const claims: ClaimInput[] = [];
  for (const line of lines) {
    if (line.trim() === "") continue;
    const parsed = parseClaim(line);
    assert.equal(parsed.error, null, `claim line failed to parse: ${parsed.error ?? ""}`);
    if (parsed.claim !== null) claims.push(parsed.claim);
  }
  return claims;
}

async function auditAll(claims: readonly ClaimInput[]): Promise<readonly Receipt[]> {
  const loaded = await loadExtractor(EXTRACTOR);
  assert.notEqual(loaded.extractor, null, `extractor missing: ${loaded.error ?? ""}`);
  if (loaded.extractor === null) return [];
  const manifest = parseManifest(readFileSync(MANIFEST, "utf8"));
  const receipts: Receipt[] = [];
  for (const claim of claims) {
    receipts.push(
      await auditClaim(
        {
          claim,
          corpusDir: CORPUS,
          corpusLabel: "../evidence/fleites",
          manifest,
          bearing: "supporting",
          actor: "claims-trial",
          instrument: "burden",
        },
        ENV,
        loaded.extractor,
      ),
    );
  }
  return receipts;
}

test("manifests parse into hash -> file maps", () => {
  const map = parseManifest(
    [
      `${"a".repeat(64)}  first.pdf`,
      `${"b".repeat(64)} *second.pdf`,
      "# a comment",
      "not a manifest line",
      "",
    ].join("\n"),
  );
  assert.equal(map.size, 2);
  assert.equal(map.get("a".repeat(64)), "first.pdf");
  assert.equal(map.get("b".repeat(64)), "second.pdf");
});

test("a malformed claim line is an error, not a silent skip", () => {
  assert.notEqual(parseClaim("{not json").error, null);
  assert.notEqual(parseClaim('{"claimId":"X"}').error, null);
  const ok = parseClaim(
    JSON.stringify({
      claimId: "CLM-T-1",
      docket: "2:21-cv-04920",
      documentNumber: 1,
      page: 1,
      quote: "a span",
      sourceSha256: "a".repeat(64),
      nature: "allegation",
    }),
  );
  assert.equal(ok.error, null);
  assert.equal(ok.claim?.claimId, "CLM-T-1");
});

test("every published claim is reproducible against the corpus", async (t) => {
  if (!corpusPresent()) {
    t.skip("L0 corpus, claims file, or ledger extractor is absent on this machine");
    return;
  }
  const claims = readClaims();
  assert.ok(claims.length > 0, "no claims to audit");

  const receipts = await auditAll(claims);
  const failures = receipts.filter((receipt) => receipt.verdict.kind !== "verified");
  assert.deepEqual(
    failures.map((receipt) => `${receipt.claimId}: ${receipt.verdict.code}`),
    [],
    "the audit could not reproduce published claims",
  );
  assert.equal(receipts.length, claims.length);
});

test("the audit catches a wrong page citation", async (t) => {
  if (!corpusPresent()) {
    t.skip("L0 corpus absent on this machine");
    return;
  }
  const original = readClaims()[0];
  assert.ok(original !== undefined);
  const mutated: ClaimInput = { ...original, page: original.page + 1 };

  const receipts = await auditAll([mutated]);
  const receipt = receipts[0];
  assert.ok(receipt !== undefined);
  assert.equal(receipt.verdict.kind, "falsified");
  assert.equal(receipt.verdict.code, "QUOTE_NOT_ON_CITED_PAGE");
});

test("the audit catches a single changed character", async (t) => {
  if (!corpusPresent()) {
    t.skip("L0 corpus absent on this machine");
    return;
  }
  const original = readClaims()[0];
  assert.ok(original !== undefined);

  // Mutate one interior character of the quote, and assert the mutation landed.
  const at = Math.floor(original.quote.length / 2);
  const character = original.quote[at];
  assert.ok(character !== undefined);
  const replacement = character === "e" ? "x" : "e";
  const mutatedQuote = `${original.quote.slice(0, at)}${replacement}${original.quote.slice(at + 1)}`;
  assert.notEqual(mutatedQuote, original.quote, "the mutation did not change the quote");

  const receipts = await auditAll([{ ...original, quote: mutatedQuote }]);
  const receipt = receipts[0];
  assert.ok(receipt !== undefined);
  assert.equal(receipt.verdict.kind, "falsified");
  assert.equal(receipt.verdict.code, "QUOTE_NOT_ON_CITED_PAGE");
});

test("an uncommitted source is unmeasured, never a pass and never a false failure", async (t) => {
  if (!corpusPresent()) {
    t.skip("L0 corpus absent on this machine");
    return;
  }
  const original = readClaims()[0];
  assert.ok(original !== undefined);
  const mutated: ClaimInput = { ...original, sourceSha256: "f".repeat(64) };

  const receipts = await auditAll([mutated]);
  const receipt = receipts[0];
  assert.ok(receipt !== undefined);
  assert.equal(receipt.verdict.kind, "unmeasured");
  assert.equal(receipt.verdict.code, "SOURCE_NOT_IN_MANIFEST");
  // And it must not enter the calibration denominator.
  assert.ok(receipt.missingMeasurement !== null);
});
