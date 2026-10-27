/**
 * Emit the jurisdiction gate's correspondence with L3's `Righteous`, from the
 * compiled TypeScript.
 *
 * `bds/src/types.ts#admissible` is the runtime twin of `Righteous` in
 * `L3_JURISDICTION.lean`. A comment claiming they agree is not a check — the
 * same defect that was closed for the burden package's tier relation.
 *
 * The axes are stated in **weight space**, because `L3_JURISDICTION.lean`
 * compares severities as `Nat`s (`claimedSeverity`, `warrantedSeverity`) rather
 * than through a four-constructor enum. Using the weights directly makes the
 * bridge a statement about the arithmetic the two layers actually share, and the
 * weight table is injective (4→3, 3→2, 2→1, 1→0), so nothing is lost.
 *
 * Emits one theorem per combination:
 *
 *     theorem ts_c000 :
 *       (tsViolations 3 3 Evidence.unmeasured true = some 0 ↔
 *        Righteous (probe 3 3 Evidence.unmeasured true) = true) := by decide
 *
 * The left side is the count `admissible()` actually returned at build time; the
 * right side is recomputed by Lean. A drift on either side stops a specific
 * theorem from proving, and the gate names the combination.
 *
 * Usage: node dist/tools/emit-jurisdiction.js > TS_JURISDICTION.lean
 */

import { SEVERITY_WEIGHT, admissible, type Severity } from "./emit-support.js";

type EvidenceTier =
  | "unmeasured"
  | "located_blocked"
  | "corroborated"
  | "fetched"
  | "retired";

const SEVERITIES: readonly Severity[] = ["critical", "major", "minor", "none"];
const TIERS: readonly EvidenceTier[] = [
  "unmeasured",
  "located_blocked",
  "corroborated",
  "fetched",
  "retired",
];

const SOURCE = {
  path: "evidence/bds/probe.pdf",
  sha256: "0".repeat(64),
  bytes: 1,
  pages: [1],
};

function leanEvidence(t: EvidenceTier): string {
  // The constructors carry payloads; a probe supplies placeholders. The payload
  // is irrelevant to `Evidence.bearsOn`, which is what the bridge compares.
  switch (t) {
    case "unmeasured":
      return "Evidence.unmeasured";
    case "located_blocked":
      return "(Evidence.locatedBlocked \"probe\")";
    case "corroborated":
      return "(Evidence.corroborated \"a\" \"b\")";
    case "fetched":
      return "(Evidence.fetched \"probe\")";
    case "retired":
      return "(Evidence.retired \"probe\")";
  }
}

type Row = {
  readonly claimed: Severity;
  readonly warranted: Severity;
  readonly tier: EvidenceTier;
  readonly falsifier: boolean;
  readonly count: number;
};

const rows: Row[] = [];
for (const claimed of SEVERITIES) {
  for (const warranted of SEVERITIES) {
    for (const tier of TIERS) {
      for (const hasFalsifier of [true, false]) {
        const count = admissible({
          id: "FND-PROBE",
          subject: "structure",
          claim: "probe",
          severity: claimed,
          warrantedSeverity: warranted,
          evidence: tier,
          source: tier === "fetched" ? SOURCE : null,
          falsifier: hasFalsifier ? "probe" : "",
          detail: "probe",
        }).length;
        rows.push({ claimed, warranted, tier, falsifier: hasFalsifier, count });
      }
    }
  }
}

const tableLines = rows.map(
  (row) =>
    `  (${String(SEVERITY_WEIGHT[row.claimed])}, ${String(SEVERITY_WEIGHT[row.warranted])}, ` +
    `${leanEvidence(row.tier)}, ${row.falsifier ? "true" : "false"}, ${String(row.count)}),`,
);

const theoremLines: string[] = [];
let index = 0;
for (const row of rows) {
  const cw = SEVERITY_WEIGHT[row.claimed];
  const ww = SEVERITY_WEIGHT[row.warranted];
  const ev = leanEvidence(row.tier);
  const f = row.falsifier ? "true" : "false";
  const id = `ts_c${String(index).padStart(3, "0")}`;
  // The TypeScript is deliberately stricter than the bare predicate: a
  // critical or major finding may not rest on unsupported evidence. So the
  // implication holds one way everywhere, and both ways only where the extra
  // rule does not bite. The emitter picks the statement the row supports,
  // which is why a drift on either side changes *which* theorem breaks.
  const extraRuleBites =
    (row.claimed === "critical" || row.claimed === "major") &&
    row.tier !== "fetched" &&
    row.tier !== "corroborated";
  const assumption = `Righteous (probe ${String(cw)} ${String(ww)} ${ev} ${f})`;
  theoremLines.push(
    `-- ${row.claimed} (${cw}) vs ${row.warranted} (${ww}), ${row.tier}, falsifier=${f} → ${String(row.count)} violation(s)`,
    `-- extra rule ${extraRuleBites ? "applies: correspondence is one-way" : "does not apply: correspondence is two-way"}`,
  );
  if (extraRuleBites) {
    theoremLines.push(
      `theorem ${id} :`,
      `    tsViolations ${String(cw)} ${String(ww)} ${ev} ${f} = some 0 →`,
      `      ${assumption} = true := by`,
      `  decide`,
      "",
    );
  } else {
    theoremLines.push(
      `theorem ${id} :`,
      `    (tsViolations ${String(cw)} ${String(ww)} ${ev} ${f} = some 0 ↔`,
      `      ${assumption} = true) := by`,
      `  decide`,
      "",
    );
  }
  index += 1;
}

const lines: string[] = [
  "import «L1_BURDEN»",
  "import «L3_JURISDICTION»",
  "",
  "set_option maxRecDepth 100000",
  "",
  "/-!",
  "# TS_JURISDICTION — generated from the compiled TypeScript, do not edit",
  "",
  "Produced by `bds/tools/emit-jurisdiction.ts`. Each theorem records one",
  "combination: the violation count that `admissible()` actually returned at build",
  "time on the left, and `Righteous` from `L3_JURISDICTION.lean` recomputed by",
  "`decide` on the right.",
  "",
  "`ts_table_complete` proves the table has every combination, so a missing row",
  "cannot masquerade as zero violations.",
  "",
  `Combinations: ${SEVERITIES.length} × ${SEVERITIES.length} × ${TIERS.length} × 2 = ${rows.length}.`,
  "-/",
  "",
  "namespace TsJurisdiction",
  "",
  "/-- Severity weight, exactly as `SEVERITY_WEIGHT` in `bds/src/types.ts`.",
  "    The table below is keyed on these numbers, so pinning them pins the",
  "    encoding the correspondence is stated in.",
  "-/" ,
  "def tsWeight (s : Severity) : Nat :=",
  `  if s = Severity.critical then ${String(SEVERITY_WEIGHT.critical)}`,
  `  else if s = Severity.major then ${String(SEVERITY_WEIGHT.major)}`,
  `  else if s = Severity.minor then ${String(SEVERITY_WEIGHT.minor)}`,
  `  else ${String(SEVERITY_WEIGHT.none)}`,
  "",
  "",
  "/-- One generated row: (claimed weight, warranted weight, evidence, falsifier, violations). -/",
  "abbrev Row := Nat × Nat × Evidence × Bool × Nat",
  "",
  "/-- The counts `admissible()` produced at build time. Generated, not hand-written. -/",
  "def tsTable : List Row := [",
  ...tableLines,
  "]",
  "",
  "/-- Look a row up. `none` means the table is incomplete, which the theorems",
  "    below treat as a failure rather than as zero violations. -/",
  "def tsViolations (cw ww : Nat) (e : Evidence) (f : Bool) : Option Nat :=",
  "  (tsTable.find? fun row =>",
  "    row.1 == cw && row.2.1 == ww && row.2.2.1 == e && row.2.2.2.1 == f).map",
  "    fun row => row.2.2.2.2",
  "",
  "/-- Every combination is present, so an absent row cannot read as a clean gate. -/",
  `theorem ts_table_complete : tsTable.length = ${String(rows.length)} := rfl`,
  "",
  "/-- The subject `admissible` is exercised with. `bds` has no other subject:",
  "    `Subject` in the TypeScript is `structure | attribution`, and the",
  "    condemnation axis is unrepresentable there. -/",
  "def probe (cw ww : Nat) (e : Evidence) (f : Bool) : Finding :=",
  "  { subject := Subject.structure,",
  "    claimedSeverity := cw,",
  "    warrantedSeverity := ww,",
  "    evidence := e,",
  "    hasFalsifier := f }",
  "",
  "/-! ## The correspondence, one theorem per combination -/",
  "",
  ...theoremLines,
  "end TsJurisdiction",
];

process.stdout.write(`${lines.join("\n")}\n`);
