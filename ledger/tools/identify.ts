/**
 * Identify docket documents from their first page.
 *
 * LOCAL ONLY. Prints a bounded snippet of page 1 so a human can classify a
 * document before drafting claims from it. The output is never committed and
 * never published — it exists to answer "what is document 433?" without
 * opening a PDF viewer.
 *
 * Usage:
 *   node dist/tools/identify.js --sources <dir> 62 69 433
 */

import { existsSync } from "node:fs";
import { join } from "node:path";

import { extractPdf } from "../src/extract.js";
import { sourceNameCandidates } from "../src/workbench.js";

const SNIPPET = 240;

function arg(name: string): string | undefined {
  const index = process.argv.indexOf(`--${name}`);
  return index < 0 ? undefined : process.argv[index + 1];
}

const sources = arg("sources") ?? "/home/idor/oe-local/evidence/fleites";
const numbers = process.argv
  .slice(2)
  .filter((value) => /^\d+$/.test(value))
  .map(Number);

if (numbers.length === 0) {
  console.error("usage: identify --sources <dir> <docNumber>...");
  process.exitCode = 2;
} else {
  for (const docNumber of numbers) {
    const path = sourceNameCandidates(docNumber)
      .map((name) => join(sources, name))
      .find((candidate) => existsSync(candidate));
    if (path === undefined) {
      console.log(`doc ${docNumber}: no local file`);
      continue;
    }
    const doc = await extractPdf(path);
    const first = doc.pages[0];
    const text = (first?.text ?? "").replace(/\s+/g, " ").trim();
    console.log(`doc ${docNumber} (${doc.totalPages} pp): ${text.slice(0, SNIPPET)}`);
    console.log("");
  }
}
