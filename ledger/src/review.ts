/**
 * Review a verified candidate set.
 *
 * Re-runs both gates independently of the admit step, then prints each record
 * with its citation and quote so a human can approve or reject it. A record
 * that fails re-verification is marked and must not be published.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { loadManifest } from "./manifest.js";
import { admit } from "./validate.js";
import { checkQuoteOnPage, extractPdf } from "./extract.js";
import { sourceNameCandidates } from "./workbench.js";
import type { ClaimRecord } from "./types.js";

const SOURCES = "/home/idor/oe-local/evidence/fleites";
const MANIFEST = join(SOURCES, "FLEITES_MANIFEST.sha256");
const INPUT = process.argv[2] ?? "drafts/verified.jsonl";

const manifest = loadManifest(MANIFEST);
const lines = readFileSync(INPUT, "utf8").split(/\r?\n/).filter((line) => line.trim() !== "");

let ok = 0;
let bad = 0;

for (const line of lines) {
  const raw = JSON.parse(line) as unknown;
  const structural = admit(raw, manifest.hashes);
  if (!structural.ok) {
    bad += 1;
    console.log(`!! ${JSON.stringify(raw).slice(0, 80)} — structural re-check FAILED`);
    continue;
  }
  const record: ClaimRecord = structural.record;

  const sourceName = sourceNameCandidates(record.documentNumber).find((name) =>
    existsSync(join(SOURCES, name)),
  );
  if (sourceName === undefined) {
    bad += 1;
    console.log(`!! ${record.claimId} — source missing`);
    continue;
  }
  const doc = await extractPdf(join(SOURCES, sourceName));
  const check = checkQuoteOnPage(doc, record.page, record.quote);
  if (!check.found) {
    bad += 1;
    console.log(`!! ${record.claimId} — quote re-check FAILED: ${check.reason ?? ""}`);
    continue;
  }

  ok += 1;
  console.log("=".repeat(78));
  console.log(`${record.claimId}   nature=${record.nature}   tier=${record.tier.kind}`);
  console.log(`docket ${record.docket}  doc ${record.documentNumber}  page ${record.page}`);
  console.log(`source ${sourceName}`);
  console.log(`sha256 ${record.sourceSha256}`);
  console.log(`quote  "${record.quote}"`);
  console.log(`chars  ${record.quote.length}`);
}

console.log("");
console.log(`re-verified: ${ok}`);
console.log(`failed:      ${bad}`);
process.exitCode = bad === 0 ? 0 : 1;
