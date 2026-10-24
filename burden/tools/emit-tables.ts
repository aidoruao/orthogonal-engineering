/**
 * Emit the TypeScript relations as Lean theorems, one per pair.
 *
 * This is the mechanism that stops the two languages from drifting apart.
 * `L1_BURDEN.lean` proves properties of `mayUpgrade` and `severity`; the
 * runtime enforces `mayUpgrade` and `severity` in `src/types.ts`. A comment
 * saying they are "the same relation" is not a check.
 *
 * So the TypeScript is compiled, each function is called on every pair, and the
 * result is emitted as a Lean theorem of the form
 *
 *     theorem ts_tier_p0 : mayUpgrade Tier.unverified Tier.unverified = true := by decide
 *
 * `decide` recomputes the Lean side. If TypeScript says `true` where Lean
 * computes `false`, the theorem is false and the build fails — naming the exact
 * pair. One theorem per pair means a drift is reported as a specific pair, not
 * as a vague mismatch.
 *
 * The tables are read from the built module rather than hand-written, so they
 * cannot be edited into agreement.
 *
 * Usage: node dist/tools/emit-tables.js > TS_TABLES.lean
 */

import { BEARINGS, TIERS, mayUpgrade, severity } from "../src/types.js";

function tier(name: string): string {
  switch (name) {
    case "unverified":
      return "Tier.unverified";
    case "located_blocked":
      return "Tier.locatedBlocked";
    case "corroborated":
      return "Tier.corroborated";
    case "fetched":
      return "Tier.fetched";
    case "retired":
      return "Tier.retired";
    default:
      throw new Error(`emit-tables: unknown tier "${name}"`);
  }
}

function bearing(name: string): string {
  switch (name) {
    case "load_bearing":
      return "Bearing.loadBearing";
    case "supporting":
      return "Bearing.supporting";
    case "illustrative":
      return "Bearing.illustrative";
    default:
      throw new Error(`emit-tables: unknown bearing "${name}"`);
  }
}

function sev(name: string): string {
  switch (name) {
    case "critical":
      return "Severity.critical";
    case "major":
      return "Severity.major";
    case "minor":
      return "Severity.minor";
    case "none":
      return "Severity.none";
    default:
      throw new Error(`emit-tables: unknown severity "${name}"`);
  }
}

const lines: string[] = [];
lines.push("import «L1_BURDEN»");
lines.push("");
lines.push("/-!");
lines.push("# TS_TABLES — generated from the compiled TypeScript, do not edit");
lines.push("");
lines.push("Produced by `burden/tools/emit-tables.ts`. One theorem per pair: the");
lines.push("TypeScript value is the assertion, `decide` recomputes the Lean side.");
lines.push("A disagreement fails to compile and names the pair.");
lines.push("");
lines.push(`Tier pairs: ${TIERS.length * TIERS.length}. Bearing/verdict pairs: ${BEARINGS.length * 2}.`);
lines.push("-/");

lines.push("");
lines.push("namespace TsTables");
lines.push("");
lines.push("/-! ### The tier relation, all 25 pairs -/");
lines.push("");

let index = 0;
for (const from of TIERS) {
  for (const to of TIERS) {
    const value = mayUpgrade(from, to);
    lines.push(
      `theorem ts_tier_p${String(index).padStart(2, "0")} : ` +
        `mayUpgrade ${tier(from)} ${tier(to)} = ${value ? "true" : "false"} := by decide`,
    );
    index += 1;
  }
}

lines.push("");
lines.push("/-! ### The reporting weight, all 6 bearing/verdict pairs -/");
lines.push("");

index = 0;
for (const b of BEARINGS) {
  for (const verified of [true, false]) {
    const value = severity(b, verified);
    lines.push(
      `theorem ts_sev_p${String(index).padStart(2, "0")} : ` +
        `severity ${bearing(b)} ${verified ? "true" : "false"} = ${sev(value)} := by decide`,
    );
    index += 1;
  }
}

lines.push("");
lines.push("end TsTables");

process.stdout.write(`${lines.join("\n")}\n`);
