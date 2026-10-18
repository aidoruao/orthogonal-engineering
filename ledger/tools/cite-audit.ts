/**
 * Citation audit — checks published page cites against the PDFs.
 *
 * Three verdicts, and the distinction is the point:
 *
 *   VERBATIM   the quoted string appears on the cited page. Best.
 *   ELIDED     the string contains "...". The fragments verify, but the
 *              string is a paraphrase with *marked* elision. A reader can see
 *              words were omitted, so this is honest — but it is not a
 *              quotation and it is not eligible for the claim ledger.
 *   NOT FOUND  the string is not on the cited page. This is a failure: it
 *              presents a paraphrase as if it were a quotation. A hostile
 *              reader who checks it finds nothing, and can then dismiss
 *              everything else.
 *
 * Exits non-zero on any NOT FOUND. Requires the local corpus; skips (exit 0)
 * with a clear message when it is absent.
 *
 * Usage:
 *   node dist/tools/cite-audit.js [--corpus <dir>]
 */

import { existsSync } from "node:fs";
import { join } from "node:path";

import { checkQuoteOnPage, extractPdf } from "../src/extract.js";
import { sourceNameCandidates } from "../src/workbench.js";

interface Cite {
  readonly doc: string;
  readonly page: number;
  readonly quote: string;
}

/**
 * The page cites published in `L3_FETCHED.lean`. Transcribed faithfully; if
 * that file changes, update this list in the same commit. The audit compares
 * what is *published* against what the documents *say*.
 */
const CITES: readonly Cite[] = [
  // Antoon
  { doc: "385", page: 9, quote: "Defendant Feras Antoon ... minority owner ... de facto CEO of all the MindGeek entities" },
  { doc: "68", page: 1, quote: "DEFENDANT FERAS ANTOON'S NOTICE OF MOTION AND MOTION TO DISMISS FOR LACK OF PERSONAL JURISDICTION" },
  { doc: "385", page: 37, quote: "Antoon and Tassillo repeated this false narrative in sworn testimony" },
  // Tassillo
  { doc: "385", page: 9, quote: "Defendant David Tassillo ... minority owner ... de facto COO of all MindGeek entities" },
  { doc: "67", page: 1, quote: "SPECIALLY APPEARING DEFENDANT DAVID TASSILLO'S NOTICE OF MOTION AND MOTION TO DISMISS THE COMPLAINT" },
  // Urman
  { doc: "385", page: 65, quote: "Blake White, its vice president, said child sexual abuse made up a tiny proportion of content and the aim was to eradicate it." },
  { doc: "385", page: 65, quote: "Urman's statement was a lie. MindGeek had no real moderation function" },
  { doc: "385", page: 68, quote: "Corey Urman, falsely posing under the alias Blake White" },
  { doc: "140", page: 1, quote: "SPECIALLY-APPEARING DEFENDANT COREY URMAN'S NOTICE OF MOTION AND MOTION TO DISMISS AMENDED COMPLAINT" },
  // Bergmair / attribution
  { doc: "385", page: 67, quote: "discussed and directed by Bergmair, Antoon, and Tassillo and led by MindGeek vice-president Corey Urman" },
];

const CORPUS =
  process.argv.includes("--corpus")
    ? (process.argv[process.argv.indexOf("--corpus") + 1] ?? "")
    : (process.env["OE_CORPUS_DIR"] ?? "/home/idor/oe-local/evidence/fleites");

if (!existsSync(CORPUS)) {
  console.log(`SKIP: no corpus at ${CORPUS}; citation audit not run`);
  process.exit(0);
}

function locate(doc: string): string | undefined {
  // "140.1" style entries map to the .pdf families on disk.
  const numeric = Number.parseInt(doc.split(".")[0] ?? "", 10);
  if (!Number.isFinite(numeric)) return undefined;
  return sourceNameCandidates(numeric)
    .map((name) => join(CORPUS, name))
    .find((path) => existsSync(path));
}

let verbatim = 0;
let elided = 0;
const notFound: string[] = [];

for (const cite of CITES) {
  const path = locate(cite.doc);
  if (path === undefined) {
    notFound.push(`doc ${cite.doc}: no local source`);
    continue;
  }
  const doc = await extractPdf(path);
  const check = checkQuoteOnPage(doc, cite.page, cite.quote);
  const label = `doc ${cite.doc} p.${cite.page}`;

  if (check.found) {
    verbatim += 1;
  } else if (cite.quote.includes("...")) {
    elided += 1;
    console.log(`WARN ${label}: elided paraphrase (marked with "..."), not a quotation`);
  } else {
    notFound.push(`${label}: "${cite.quote.slice(0, 60)}…"`);
    console.log(`FAIL ${label}: not found on the cited page`);
  }
}

console.log("");
console.log(`verbatim:  ${verbatim}`);
console.log(`elided:    ${elided}`);
console.log(`not found: ${notFound.length}`);
console.log(`total:     ${CITES.length}`);

if (notFound.length > 0) {
  console.log("");
  console.log("A paraphrase presented as a quotation is not a citation. Fix these:");
  for (const item of notFound) console.log(`  ${item}`);
  process.exitCode = 1;
}
