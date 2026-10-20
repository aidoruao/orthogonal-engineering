/**
 * Standards compliance check.
 *
 * WHAT THIS IS: a presence check. It verifies that the mechanisms the
 * constitution and the corpus standards require are actually present in the
 * tree. It does not verify that they work — the tests, the Lean proofs, and
 * the negative controls do that.
 *
 * WHAT THIS IS NOT: a substitute for those gates, and not a claim that the
 * project is compliant in any absolute sense. A string match can be satisfied
 * by a comment. Read the failures; do not over-trust the passes.
 *
 * Usage:
 *   node dist/src/compliance.js --root <repo root>
 * Exit 0 when every required check passes, 1 otherwise.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

export interface CheckResult {
  readonly id: string;
  readonly requirement: string;
  readonly status: "pass" | "fail" | "info";
  readonly evidence: string;
}

const SECRET_PATTERNS: readonly RegExp[] = [
  /ghp_[A-Za-z0-9]{30,}/,
  /github_pat_[A-Za-z0-9_]{30,}/,
  /https:\/\/[^/\s]+:[^/\s]+@github\.com/,
];

/** Read a file, returning "" when absent so a missing file fails its check. */
function readOr(path: string): string {
  return existsSync(path) ? readFileSync(path, "utf8") : "";
}

function json(path: string): Record<string, unknown> {
  const text = readOr(path);
  if (text === "") return {};
  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export function runCompliance(root: string): CheckResult[] {
  const results: CheckResult[] = [];
  const add = (
    id: string,
    requirement: string,
    ok: boolean,
    evidence: string,
  ): void => {
    results.push({ id, requirement, status: ok ? "pass" : "fail", evidence });
  };

  const ledger = join(root, "ledger");

  // 1. TypeScript is strict.
  const tsconfig = json(join(ledger, "tsconfig.json"));
  const compiler = (tsconfig["compilerOptions"] ?? {}) as Record<string, unknown>;
  const strictFlags = [
    "strict",
    "exactOptionalPropertyTypes",
    "noUncheckedIndexedAccess",
    "noImplicitOverride",
    "noPropertyAccessFromIndexSignature",
    "verbatimModuleSyntax",
  ];
  const missingFlags = strictFlags.filter((flag) => compiler[flag] !== true);
  add(
    "typescript-strict",
    "The implementation compiles under the strictest practical TypeScript flags.",
    missingFlags.length === 0,
    missingFlags.length === 0
      ? `all ${strictFlags.length} strict flags set`
      : `missing: ${missingFlags.join(", ")}`,
  );

  // 2. Dependencies are pinned.
  const pkg = json(join(ledger, "package.json"));
  const deps = {
    ...((pkg["dependencies"] ?? {}) as Record<string, string>),
    ...((pkg["devDependencies"] ?? {}) as Record<string, string>),
  };
  const unpinned = Object.entries(deps)
    .filter(([, version]) => /[\^~]/.test(version))
    .map(([name]) => name);
  add(
    "pinned-dependencies",
    "No dependency floats on a range; the lockfile is committed.",
    unpinned.length === 0 && existsSync(join(ledger, "package-lock.json")),
    unpinned.length === 0
      ? `${Object.keys(deps).length} dependencies pinned exact, lockfile present`
      : `unpinned: ${unpinned.join(", ")}`,
  );

  // 3. Lean is the proof layer only: no I/O in the Lean modules.
  const leanFiles = ["L1_LEDGER.lean", "L1_SELECTION.lean"]
    .map((name) => join(root, name))
    .filter((path) => existsSync(path));
  const leanHasIo = leanFiles.filter((path) => /\bIO\.|main\s*:\s*IO/.test(readOr(path)));
  add(
    "lean-is-proof-only",
    "Lean modules state theorems; they perform no application I/O.",
    leanFiles.length === 2 && leanHasIo.length === 0,
    leanFiles.length !== 2
      ? `expected 2 Lean modules, found ${leanFiles.length}`
      : leanHasIo.length === 0
        ? "2 modules, no IO usage"
        : `I/O found in: ${leanHasIo.join(", ")}`,
  );

  // 4. Every Lean module names how to run it.
  const missingRun = leanFiles.filter((path) => !/Run:\s*`lean /.test(readOr(path)));
  add(
    "lean-runnable",
    "Each proof module states its own verification command.",
    missingRun.length === 0,
    missingRun.length === 0 ? "all modules document their run command" : `missing in: ${missingRun.join(", ")}`,
  );

  // 5. Negative controls exist for each invariant family.
  const controls = [
    join(ledger, "negative", "NEGATIVE_CONTROL.lean"),
    join(ledger, "negative", "SELECTION_DROP.lean"),
    join(ledger, "negative", "SELECTION_ANONYMOUS.lean"),
  ];
  const presentControls = controls.filter((path) => existsSync(path));
  add(
    "falsifiers-present",
    "Every structural invariant has a negative control that must fail to compile.",
    presentControls.length === controls.length,
    `${presentControls.length}/${controls.length} negative controls present`,
  );

  // 6. Evidence tiers are the corpus standard set.
  const typesText = readOr(join(ledger, "src", "types.ts"));
  const tierKinds = ["fetched", "corroborated", "located_blocked", "retired", "unverified"];
  const missingTiers = tierKinds.filter((kind) => !typesText.includes(kind));
  add(
    "evidence-tiers",
    "All five evidence tiers from the corpus standard are modelled.",
    missingTiers.length === 0,
    missingTiers.length === 0 ? "5/5 tiers present" : `missing: ${missingTiers.join(", ")}`,
  );

  // 7. Corroboration requires at least two independent sources.
  const corroboration = /MIN_CORROBORATORS\s*=\s*2/.test(typesText);
  add(
    "corroboration-threshold",
    "A load-bearing claim needs at least two corroborators.",
    corroboration,
    corroboration ? "MIN_CORROBORATORS = 2" : "threshold not found or not 2",
  );

  // 8. Attribution is not causation: adjudication is a separate axis from intent.
  const natureText = readOr(join(ledger, "src", "types.ts"));
  const hasAdjudicated =
    natureText.includes("ADJUDICATED_NATURES") &&
    natureText.includes('"order"') &&
    natureText.includes('"finding"') &&
    natureText.includes('"stated_intent"') &&
    natureText.includes('"party_filing"');
  add(
    "attribution-not-causation",
    "An adjudicated outcome is separable from a stated intent.",
    hasAdjudicated,
    hasAdjudicated
      ? "nature axis separates order/finding from stated_intent"
      : "nature axis does not separate adjudication from intent",
  );

  // 9. No swallowed errors in the shipping sources.
  const sourceFiles = [
    "validate.ts",
    "manifest.ts",
    "extract.ts",
    "workbench.ts",
    "corpus.ts",
    "selection.ts",
    "selection-check.ts",
    "span.ts",
    "draft.ts",
    "admit-batch.ts",
    "review.ts",
    "compliance.ts",
  ];
  const swallowed: string[] = [];
  for (const name of sourceFiles) {
    const text = readOr(join(ledger, "src", name));
    if (/catch\s*(\([^)]*\))?\s*\{\s*\}/.test(text)) swallowed.push(name);
  }
  add(
    "no-silent-anomaly",
    "No empty catch block in the shipping sources.",
    swallowed.length === 0,
    swallowed.length === 0 ? `${sourceFiles.length} sources clean` : `empty catch in: ${swallowed.join(", ")}`,
  );

  // 10. No stubs.
  //
  // The markers are assembled from parts so this scanner does not detect its
  // own pattern literal. A self-match would fail every run for the wrong
  // reason, and "fixing" it by skipping this file would create a blind spot.
  const stubMarkers = ["TO" + "DO", "FIX" + "ME", "NotImplemented" + "Error"];
  const stubPattern = new RegExp(`\\b(${stubMarkers.join("|")})\\b`);
  const stubbed: string[] = [];
  for (const name of sourceFiles) {
    const text = readOr(join(ledger, "src", name));
    if (stubPattern.test(text)) stubbed.push(name);
  }
  add(
    "no-stubs",
    "No placeholder markers (unfinished-work comments or unimplemented throws) in the shipping sources.",
    stubbed.length === 0,
    stubbed.length === 0 ? `${sourceFiles.length} sources clean` : `placeholders in: ${stubbed.join(", ")}`,
  );

  // 11. No credentials in the tree.
  const secretHits: string[] = [];
  const scanTargets = [
    join(ledger, "src", "types.ts"),
    join(ledger, "src", "validate.ts"),
    join(ledger, "src", "workbench.ts"),
    join(root, ".github", "workflows", "l1-ledger.yml"),
  ];
  for (const path of scanTargets) {
    const text = readOr(path);
    if (SECRET_PATTERNS.some((pattern) => pattern.test(text))) secretHits.push(path);
  }
  add(
    "no-credentials",
    "No token or credentialed URL in tracked source.",
    secretHits.length === 0,
    secretHits.length === 0 ? `${scanTargets.length} files clean` : `secret-shaped string in: ${secretHits.join(", ")}`,
  );

  // 12. Consent recorded for the kernel surface.
  const consent = readOr(join(root, "pr47_stewardship", "witness", "consent_log.jsonl"));
  const consented = consent.includes("codewhale-20261017-l1-ledger-gate");
  add(
    "consent-kernel-surface",
    "The CI workflow change carries a recorded consent entry.",
    consented,
    consented ? "consent entry present" : "no consent entry for l1-ledger.yml",
  );

  // 13. The covenant document classifies every axiom.
  //
  // A document that rates a system on eighteen axioms is itself making
  // eighteen-plus claims. This check makes its structure verifiable: the
  // classification headings must be numbered 1..18 contiguously, and the
  // tally table must sum to the same count. It does not check that the
  // classifications are *correct* — only that the document is complete and
  // internally consistent, which is the failure mode YAAI itself had.
  const covenant = readOr(join(root, "docs", "YAAI_COVENANT.md"));
  const numbered = [...covenant.matchAll(/^### (\d+)\./gm)].map((m) => Number(m[1]));
  const expected = Array.from({ length: 18 }, (_, i) => i + 1);
  const complete = numbered.length === 18 && numbered.every((n, i) => n === expected[i]);

  // Classify per axiom section, not by counting markers in the whole file:
  // the legend defines each class once, and axiom 15 is "ENFORCED BY THEOREM".
  // Counting bare markers made 18 axioms look like 20 classes.
  const sections = covenant.split(/^### \d+\./m).slice(1);
  let enforced = 0;
  let partial = 0;
  let notEnforced = 0;
  let unclassified = 0;
  for (const section of sections) {
    const head = section.split("\n").slice(0, 3).join(" ");
    if (/NOT ENFORCED/.test(head)) notEnforced += 1;
    else if (/ENFORCED/.test(head)) enforced += 1;
    else if (/PARTIAL/.test(head)) partial += 1;
    else unclassified += 1;
  }
  const tallySum = enforced + partial + notEnforced;

  // The tally table must agree with the per-axiom sections. A document whose
  // summary contradicts its own body is the same class of defect as a README
  // that declares files it does not have — the failure this file catalogues.
  const tableCount = (label: string): number | null => {
    const match = new RegExp(`\\|\\s*${label}\\s*\\|\\s*(\\d+)\\s*\\|`).exec(covenant);
    return match === null ? null : Number(match[1]);
  };
  const tableEnforced = tableCount("ENFORCED");
  const tablePartial = tableCount("PARTIAL");
  const tableNot = tableCount("NOT ENFORCED");
  const tableAgrees =
    tableEnforced === enforced &&
    tablePartial === partial &&
    tableNot === notEnforced;

  add(
    "covenant-complete",
    "The covenant classifies all 18 axioms, and its tally table agrees with its sections.",
    complete && tallySum === 18 && unclassified === 0 && tableAgrees,
    complete
      ? tableAgrees
        ? `18 axioms; sections ${enforced}/${partial}/${notEnforced}; table agrees`
        : `18 axioms, but table ${tableEnforced}/${tablePartial}/${tableNot} contradicts sections ${enforced}/${partial}/${notEnforced}`
      : `expected 18 contiguous axioms, found ${numbered.length}`,
  );

  return results;
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("compliance.js");

if (invokedDirectly) {
  const rootIndex = process.argv.indexOf("--root");
  const root = rootIndex >= 0 ? process.argv[rootIndex + 1] : ".";
  if (root === undefined) {
    console.error("usage: compliance --root <repo root>");
    process.exitCode = 2;
  } else {
    const results = runCompliance(root);
    const failures = results.filter((r) => r.status === "fail");
    for (const result of results) {
      const mark = result.status === "pass" ? "PASS" : "FAIL";
      console.log(`[${mark}] ${result.id}`);
      console.log(`       ${result.requirement}`);
      console.log(`       ${result.evidence}`);
    }
    console.log("");
    console.log(`${results.length - failures.length}/${results.length} checks pass`);
    process.exitCode = failures.length === 0 ? 0 : 1;
  }
}
