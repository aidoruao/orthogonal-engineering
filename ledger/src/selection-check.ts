/**
 * Selection ledger check — runs anywhere, including CI.
 *
 * Two published files:
 *   candidates.jsonl  one claim ID per line — everything that was drafted
 *   selection.jsonl   one disposition per line — what happened to each
 *
 * Claim IDs are publishable; the quote text and source names are not. That is
 * the whole point: a reader can see that nothing vanished, without seeing
 * anything that belongs in L0.
 *
 * Usage:
 *   node dist/src/selection-check.js --candidates <path> --ledger <path>
 *
 * Exit codes: 0 partition holds, 1 a violation, 2 usage or I/O error.
 */

import { readFileSync } from "node:fs";

import { auditSelection, partitionHolds, parseLedger } from "./selection.js";

export function parseCandidateIds(text: string): { ids: string[]; malformed: string[] } {
  const ids: string[] = [];
  const malformed: string[] = [];
  text.split(/\r?\n/).forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed === "") return;
    let parsed: unknown;
    try {
      parsed = JSON.parse(trimmed) as unknown;
    } catch {
      // Allow a bare ID per line as well as {"claimId": "..."}.
      if (/^[A-Z0-9][A-Z0-9-]{2,63}$/.test(trimmed)) {
        ids.push(trimmed);
      } else {
        malformed.push(`line ${index + 1}: not a claim ID`);
      }
      return;
    }
    if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
      const id = (parsed as Record<string, unknown>)["claimId"];
      if (typeof id === "string" && id.trim() !== "") {
        ids.push(id);
        return;
      }
    }
    malformed.push(`line ${index + 1}: object without a claimId`);
  });
  return { ids, malformed };
}

function parseArgs(argv: readonly string[]): { candidates: string; ledger: string } {
  let candidates: string | undefined;
  let ledger: string | undefined;
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--candidates") {
      candidates = argv[i + 1];
      i += 1;
    } else if (arg === "--ledger") {
      ledger = argv[i + 1];
      i += 1;
    }
  }
  if (candidates === undefined || ledger === undefined) {
    throw new Error("usage: selection-check --candidates <path> --ledger <path>");
  }
  return { candidates, ledger };
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("selection-check.js");

if (invokedDirectly) {
  try {
    const args = parseArgs(process.argv.slice(2));

    const candidatesText = readFileSync(args.candidates, "utf8");
    const { ids, malformed: badCandidates } = parseCandidateIds(candidatesText);
    if (badCandidates.length > 0) {
      console.error("FAIL: candidates file has malformed lines:");
      for (const line of badCandidates) console.error(`  ${line}`);
      process.exitCode = 1;
    } else {
      const ledgerText = readFileSync(args.ledger, "utf8");
      const { ledger, malformed } = parseLedger(ledgerText);
      if (malformed.length > 0) {
        console.error("FAIL: ledger has malformed lines:");
        for (const line of malformed) console.error(`  ${line}`);
        process.exitCode = 1;
      } else {
        const report = auditSelection(ids, ledger);
        console.log(`candidates: ${ids.length}`);
        console.log(`accepted:   ${report.accepted}`);
        console.log(`rejected:   ${report.rejected}`);
        console.log(`withheld:   ${report.withheld}`);
        console.log(`total:      ${report.total}`);
        for (const [code, count] of [...report.byCode.entries()].sort()) {
          console.log(`  ${code}: ${count}`);
        }
        if (!partitionHolds(report)) {
          console.error("FAIL: the selection does not account for every candidate:");
          for (const violation of report.violations) {
            console.error(`  ${violation.code} ${violation.claimId}: ${violation.message}`);
          }
          process.exitCode = 1;
        } else {
          console.log("OK: every candidate has exactly one disposition");
        }
      }
    }
  } catch (error) {
    console.error(`fatal: ${String(error)}`);
    process.exitCode = 2;
  }
}
