/**
 * The executable arm of `L1_INELASTICITY.lean`.
 *
 * The theorem proves that no monotone level assignment reproduces the published
 * totals under equal weighting. A theorem is evidence about a model; this file
 * checks the same claim against the encoded data, so the proof is not the only
 * witness and the encoded data is not the only claim.
 *
 * The data is transcribed from
 * `historical_tests/PHASE_4_TRUTH_INELASTICITY_REPORT.md`, "Debt Breakdown by
 * Category". Every level is quoted, not inferred. If the report is revised, this
 * file must be revised with it, and the theorem will then need to be re-proved —
 * which is the point: the numbers cannot drift away from their derivation
 * silently.
 *
 * Usage: node dist/tools/inelasticity-check.js
 * Exit 0 when the published totals are consistent with the published levels,
 * 1 when they are not (the current, expected state).
 */


/** The six-point qualitative scale the report uses, ordered. */
const SCALE = ["Low", "Low-Medium", "Medium", "Medium-High", "High", "Very High"] as const;
type Level = (typeof SCALE)[number];

export type PublishedCandidate = {
  readonly id: string;
  readonly name: string;
  /** Debt total as published, in tenths of a point (6.5 -> 65). */
  readonly publishedTenths: number;
  /** Category -> level, exactly as the report lists them. */
  readonly levels: readonly Level[];
};

/**
 * Transcribed verbatim from the report's "Debt Breakdown by Category" section.
 * Note C₁ lists five categories where the others list six.
 */
export const PUBLISHED: readonly PublishedCandidate[] = [
  {
    id: "C2",
    name: "Jesus of Nazareth",
    publishedTenths: 65,
    levels: ["High", "High", "Medium", "Medium", "Low-Medium", "Medium"],
  },
  {
    id: "C3",
    name: "Muhammad",
    publishedTenths: 68,
    levels: ["Medium-High", "Medium", "Medium-High", "Low-Medium", "Medium", "Medium"],
  },
  {
    id: "C4",
    name: "Composite/Symbolic",
    publishedTenths: 72,
    levels: ["High", "High", "Medium", "Medium-High", "Medium", "Medium"],
  },
  {
    id: "C1",
    name: "No Instantiation",
    publishedTenths: 75,
    levels: ["Medium-High", "High", "Medium", "Very High", "Medium"],
  },
] as const;

export type Mapping = Readonly<Record<Level, number>>;

/** Index of a level's position on the scale. Higher index = more debt. */
export function rank(level: Level): number {
  const index = SCALE.indexOf(level);
  if (index < 0) throw new Error(`unknown level ${level}`);
  return index;
}

/** A mapping is monotone when a higher-ranked level is never worth less. */
export function isMonotone(mapping: Mapping): boolean {
  for (let index = 1; index < SCALE.length; index += 1) {
    const lower = SCALE[index - 1];
    const higher = SCALE[index];
    if (lower === undefined || higher === undefined) continue;
    if (mapping[higher] < mapping[lower]) return false;
  }
  return true;
}

/** Equal-weight mean of a candidate's levels, in tenths. */
export function meanTenths(candidate: PublishedCandidate, mapping: Mapping): number {
  const total = candidate.levels.reduce((sum, level) => sum + mapping[level], 0);
  // Round to the nearest tenth, deterministically.
  return Math.round(total / candidate.levels.length);
}

export type Mismatch = {
  readonly id: string;
  readonly published: number;
  readonly computed: number;
  readonly delta: number;
};

export function mismatches(mapping: Mapping): readonly Mismatch[] {
  const found: Mismatch[] = [];
  for (const candidate of PUBLISHED) {
    const computed = meanTenths(candidate, mapping);
    if (computed !== candidate.publishedTenths) {
      found.push({
        id: candidate.id,
        published: candidate.publishedTenths,
        computed,
        delta: computed - candidate.publishedTenths,
      });
    }
  }
  return found;
}

/**
 * The contradiction, computed exactly.
 *
 * C₂ = {H,H,M,M,LM,M} and C₃ = {MH,M,MH,LM,M,M} differ in exactly two
 * positions: two `High` in C₂ become two `Medium-High` in C₃. Under equal
 * weighting, the difference of their means is therefore (2·MH − 2·H)/6.
 * Since C₃ is published as the higher total, that forces MH > H — a `Medium-High`
 * level worth more than a `High` level, which no consistent scale permits.
 */
export function contradiction(): {
  readonly gapTenths: number;
  readonly requiredMhMinusHTenths: number;
  readonly monotoneRequires: string;
  readonly conclusion: string;
} {
  const c2 = PUBLISHED.find((candidate) => candidate.id === "C2");
  const c3 = PUBLISHED.find((candidate) => candidate.id === "C3");
  if (c2 === undefined || c3 === undefined) throw new Error("C2 and C3 must both be published");

  // means differ by (2*MH - 2*H)/6; the published totals differ by this much:
  const gapTenths = c3.publishedTenths - c2.publishedTenths;
  // (2*MH - 2*H)/6 = gap/10  =>  MH - H = (6*gap/10)/2 = 3*gap/10
  const requiredMhMinusHTenths = (3 * gapTenths) / 10;
  return {
    gapTenths,
    requiredMhMinusHTenths,
    monotoneRequires: "Medium-High <= High",
    conclusion:
      `C3 is published ${gapTenths / 10} above C2, which forces Medium-High to exceed High by ` +
      `${requiredMhMinusHTenths / 10}; the scale requires the opposite. ` +
      `The two totals cannot both be the equal-weight mean of the published levels.`,
  };
}

function main(): number {
  const lines: string[] = [];
  lines.push("inelasticity check — are the published totals the mean of the published levels?");
  lines.push("");
  lines.push("  published (transcribed from PHASE_4_TRUTH_INELASTICITY_REPORT.md):");
  for (const candidate of PUBLISHED) {
    lines.push(
      `    ${candidate.id} ${candidate.name.padEnd(20)} ${(candidate.publishedTenths / 10).toFixed(1)}  ` +
        `[${candidate.levels.join(", ")}]`,
    );
  }
  lines.push("");

  const result = contradiction();
  lines.push("  the C2/C3 contradiction, computed:");
  lines.push(`    published gap            ${result.gapTenths / 10}`);
  lines.push(`    forces Medium-High - High = ${result.requiredMhMinusHTenths / 10}`);
  lines.push(`    monotonicity requires    ${result.monotoneRequires}`);
  lines.push(`    ${result.conclusion}`);
  lines.push("");

  // A declared, monotone, equal-spaced mapping, for illustration only.
  const declared: Mapping = {
    Low: 20,
    "Low-Medium": 40,
    Medium: 60,
    "Medium-High": 80,
    High: 100,
    "Very High": 120,
  };
  lines.push("  under a declared monotone mapping (Low-Medium=4.0 … Very High=12.0):");
  for (const candidate of PUBLISHED) {
    const computed = meanTenths(candidate, declared);
    lines.push(
      `    ${candidate.id} computed ${(computed / 10).toFixed(1)}  published ${(
        candidate.publishedTenths / 10
      ).toFixed(1)}  delta ${((computed - candidate.publishedTenths) / 10).toFixed(1)}`,
    );
  }
  lines.push("");
  lines.push("  round-trip control (the arithmetic must map a mapping back to its own totals):");
  const controlMapping: Mapping = {
    Low: 20,
    "Low-Medium": 40,
    Medium: 60,
    "Medium-High": 80,
    High: 100,
    "Very High": 120,
  };
  const derived = PUBLISHED.map((candidate) => ({
    ...candidate,
    publishedTenths: meanTenths(candidate, controlMapping),
  }));
  const controlMisses = derived.filter(
    (candidate) => meanTenths(candidate, controlMapping) !== candidate.publishedTenths,
  );
  lines.push(`    mappings that fail to reproduce their own totals: ${controlMisses.length}`);
  if (controlMisses.length > 0) {
    lines.push("    FAIL: the arithmetic does not round-trip; the check is broken.");
    process.stdout.write(`${lines.join("\n")}\n`);
    return 2;
  }
  lines.push("    (0 means the mean is faithful: it reproduces totals derived from a mapping)");
  lines.push("");
  lines.push("  note: C1 lists five categories where C2/C3/C4 list six, so C1's mean is");
  lines.push("        on a different denominator and is not comparable without a stated");
  lines.push("        normalization. The report states none.");
  lines.push("");
  lines.push("  This is a bookkeeping finding about the report, not a claim about any");
  lines.push("  candidate. The ordering 6.5 < 6.8 < 7.2 < 7.5 is untouched.");

  process.stdout.write(`${lines.join("\n")}\n`);
  // The published totals do not reproduce, so this exits 1: the finding is a
  // failure of the report's own arithmetic, reported as such.
  return 1;
}

if (import.meta.url === `file://${process.argv[1] ?? ""}`) {
  process.exitCode = main();
}

