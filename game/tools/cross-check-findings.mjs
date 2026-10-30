#!/usr/bin/env node
/**
 * Cross-check: game's transcription of the BDS findings against bds's.
 *
 * ## Why this exists
 *
 * `game/src/audit-trace.ts` and `bds/src/findings.ts` both record the same six
 * audit findings: id, document, page, and dollar amount. Two transcriptions of
 * one document is the right number — a single transcription is a lead, not a
 * premise — but only if something compares them.
 *
 * Nothing did. On the first run of this check, **five of six page citations in
 * `audit-trace.ts` were wrong**: I had written sequential guesses (pp. 88, 89,
 * 90 for the FY2022 findings) instead of reading the pages out of `findings.ts`,
 * which had them from the fetched PDF (pp. 123, 124, 126). The ids, documents,
 * and amounts all agreed; only the citations had been invented, which is the
 * hardest kind of error to notice because everything around it is right.
 *
 * A citation that was guessed is a false source commitment. This gate exists so
 * that no such guess survives a commit again.
 *
 * ## What it compares, and what it cannot
 *
 * It compares `bds/src/findings.ts` (parsed as text) against
 * `game/dist/src/audit-trace.js` (compiled output). Both derive from the same
 * fetched PDFs, so this is a consistency check between two independent
 * transcriptions — **not** a check against the PDF itself. Only re-reading the
 * PDF can do that, and the hashes in `evidence/bds/MANIFEST.sha256` are what
 * make the re-read meaningful.
 *
 * Exit 0 when they agree, 1 on any disagreement, 2 if either side cannot be read.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");

/** Parse the `id`, `document`, `page`, `amountUsd` of each finding in findings.ts. */
function parseBds() {
  const src = readFileSync(join(root, "bds", "src", "findings.ts"), "utf8");
  const out = new Map();
  // Each finding literal begins with `id: "NNNN-NNN",` and the four fields we
  // care about follow within the same object. Splitting on the id pattern keeps
  // this robust against field reordering and added fields.
  const parts = src.split(/\n\s*id:\s*"/).slice(1);
  for (const part of parts) {
    const id = part.slice(0, part.indexOf('"'));
    if (!/^\d{4}-\d{3}$/.test(id)) continue;
    const doc = part.match(/document:\s*"([^"]+)"/);
    const page = part.match(/page:\s*(\d+)/);
    const amount = part.match(/amountUsd:\s*([0-9_]+|null)/);
    if (!doc || !page || !amount) continue;
    const raw = amount[1];
    out.set(id, {
      document: doc[1],
      page: Number(page[1]),
      amount: raw === "null" ? null : BigInt(raw.replaceAll("_", "")),
    });
  }
  return out;
}

async function parseGame() {
  const mod = await import(join(root, "game", "dist", "src", "audit-trace.js"));
  const out = new Map();
  for (const line of mod.BDS_FINDING_LINES) {
    out.set(line.id, {
      document: line.document,
      page: line.page,
      amount: line.stated.kind === "known" ? line.stated.value : null,
      role: line.role,
    });
  }
  return out;
}

const problems = [];

let bds;
try {
  bds = parseBds();
} catch (err) {
  console.error(`FAIL: cannot read bds/src/findings.ts: ${err.message}`);
  process.exit(2);
}
if (bds.size === 0) {
  console.error("FAIL: parsed zero findings from bds/src/findings.ts — the parser is stale");
  process.exit(2);
}

let game;
try {
  game = await parseGame();
} catch (err) {
  console.error(`FAIL: cannot read game/dist/src/audit-trace.js: ${err.message}`);
  console.error("      Run the build (gate 2) before this gate.");
  process.exit(2);
}

for (const id of bds.keys()) {
  if (!game.has(id)) problems.push(`${id}: present in bds, missing from game`);
}
for (const id of game.keys()) {
  if (!bds.has(id)) problems.push(`${id}: present in game, missing from bds`);
}

for (const [id, b] of bds) {
  const g = game.get(id);
  if (g === undefined) continue;
  if (g.document !== b.document) {
    problems.push(`${id}: document "${g.document}" != "${b.document}"`);
  }
  if (g.page !== b.page) {
    problems.push(`${id}: page ${g.page} != ${b.page}  <-- a guessed citation`);
  }
  if (g.amount !== b.amount) {
    problems.push(`${id}: amount ${g.amount} != ${b.amount}`);
  }
}

/**
 * The amount role is game's own addition and bds has no counterpart, so it is
 * checked against the auditor's `kind` rather than against a number. A
 * questioned cost must never be classed as an excess over budget: that
 * conflation is the defect this package was already repaired for once.
 */
const ROLE_FOR_KIND = {
  noncompliance_excess: "excess_over_budget",
};

const src = readFileSync(join(root, "bds", "src", "findings.ts"), "utf8");
for (const part of src.split(/\n\s*id:\s*"/).slice(1)) {
  const id = part.slice(0, part.indexOf('"'));
  if (!/^\d{4}-\d{3}$/.test(id)) continue;
  const g = game.get(id);
  if (g === undefined) continue;
  if (g.role === "excess_over_budget" && !/exceeded budgeted amounts|exceed.*budget/i.test(part)) {
    problems.push(
      `${id}: game classes this as excess_over_budget but the bds text does not state a budget excess`,
    );
  }
}

if (problems.length > 0) {
  console.error(`FAIL: the two transcriptions disagree (${problems.length} problem(s)):`);
  for (const p of problems) console.error(`      ${p}`);
  console.error("");
  console.error("      bds/src/findings.ts is the authority: it was transcribed from the");
  console.error("      fetched PDF at the page it cites. Fix game/src/audit-trace.ts.");
  process.exit(1);
}

console.log(
  `      ${bds.size} findings agree across both transcriptions ` +
    `(id, document, page, amount, role)`,
);
void ROLE_FOR_KIND;
