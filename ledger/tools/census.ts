/**
 * Territory census — two checks that answer "does the map match the ground?"
 *
 * 1. DECLARATION AUDIT
 *    Parse a README's declared directory tree and check each path exists.
 *    This is YAAI's own axiom — "map must match territory" — mechanized.
 *
 * 2. LINEAGE CENSUS
 *    Scan model roots for trained_* adapter directories and report what is
 *    actually on disk: base model, adapter size, final logged loss, and
 *    whether optimizer state proves a real training run happened.
 *
 * Weights are never read, copied, or hashed here — only their size and the
 * small JSON metadata beside them. The census exists so the territory is
 * visible without the territory being published.
 *
 * Usage:
 *   node dist/tools/census.js lineage --roots <dir>[,<dir>...]
 *   node dist/tools/census.js declarations --readme <path> --root <dir>
 *   node dist/tools/census.js lineage --roots ... --json
 */

import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from "node:fs";
import { join } from "node:path";

// ---------------------------------------------------------------------------
// Declaration audit
// ---------------------------------------------------------------------------

export interface DeclarationResult {
  readonly declared: readonly string[];
  readonly present: readonly string[];
  readonly missing: readonly string[];
}

/**
 * Extract the declared file paths from a README fenced `text` tree.
 *
 * The tree is ASCII art with box-drawing characters. Depth comes from the
 * remaining leading whitespace after those characters are stripped, which is
 * how `├──`, `│   ├──`, and `└──` encode nesting.
 */
export function parseDeclaredTree(readmeText: string, heading = "Directory Structure"): string[] {
  const pattern = new RegExp(
    `###\\s*${heading}\\s*\\n+\`\`\`text\\n([\\s\\S]*?)\`\`\``,
    "i",
  );
  const match = pattern.exec(readmeText);
  if (match === null) return [];
  const block = match[1] ?? "";

  const declared: string[] = [];
  const stack: { indent: number; name: string }[] = [];

  for (const raw of block.split("\n")) {
    if (raw.trim() === "") continue;
    const stripped = raw.replace(/[│├└─┬┼┤┴┌┐┘]/g, "");
    const indent = stripped.length - stripped.trimStart().length;
    let name = stripped.trim();
    if (name === "") continue;

    const isDir = name.endsWith("/");
    name = name.replace(/\/+$/, "");

    while (stack.length > 0 && (stack[stack.length - 1]?.indent ?? -1) >= indent) {
      stack.pop();
    }
    const parent = stack.map((entry) => entry.name).join("/");
    const path = parent === "" ? name : `${parent}/${name}`;

    if (isDir) {
      stack.push({ indent, name });
    } else {
      declared.push(path);
    }
  }

  return declared;
}

/**
 * Check each declared path against the filesystem.
 *
 * `stripPrefix` names the tree's root label (e.g. the project directory name),
 * which appears in the tree but not on disk.
 */
export function auditDeclarations(
  readmeText: string,
  root: string,
  stripPrefix?: string,
): DeclarationResult {
  const declared = parseDeclaredTree(readmeText).map((path) => {
    if (stripPrefix !== undefined && path.startsWith(`${stripPrefix}/`)) {
      return path.slice(stripPrefix.length + 1);
    }
    return path;
  });

  const present = declared.filter((path) => existsSync(join(root, path)));
  const missing = declared.filter((path) => !existsSync(join(root, path)));
  return { declared, present, missing };
}

// ---------------------------------------------------------------------------
// Lineage census
// ---------------------------------------------------------------------------

export interface LineageEntry {
  readonly side: "linux" | "win" | "other";
  readonly name: string;
  readonly path: string;
  readonly baseModel: string;
  readonly adapterBytes: number | null;
  readonly finalLoss: number | null;
  readonly hasOptimizerState: boolean;
  readonly resolvedFrom: string | null;
  /**
   * True when the run's trainer_state.json could not be parsed as strict
   * JSON. Known cause: a diverged gradient norm recorded as `Infinity`,
   * which Python's json accepts and JSON.parse rejects. Reported, never
   * hidden — an unreadable state file is evidence of a training anomaly.
   */
  readonly stateUnparseable: boolean;
  /** True when a non-standard Infinity/NaN literal was found and replaced. */
  readonly divergedNumeric: boolean;
}

const WEIGHTS = ["adapter_model.safetensors", "adapter_model.bin", "pytorch_model.bin"] as const;

function listDir(path: string): string[] {
  try {
    return readdirSync(path);
  } catch {
    return [];
  }
}

function statSize(path: string): number | null {
  try {
    const stat = statSync(path);
    return stat.isFile() ? stat.size : null;
  } catch {
    return null;
  }
}

interface ParsedState {
  readonly data: Record<string, unknown> | null;
  readonly unparseable: boolean;
  readonly diverged: boolean;
}

/**
 * Parse a trainer_state.json, tolerating the non-standard `Infinity` and
 * `NaN` literals that Python's json module writes when a gradient norm
 * diverges.
 *
 * The substitution is explicit and recorded, not swallowed: callers learn
 * that a divergence happened, so it can be reported instead of looking like
 * a run with no loss history.
 */
export function parseTrainerState(text: string): ParsedState {
  try {
    return { data: JSON.parse(text) as Record<string, unknown>, unparseable: false, diverged: false };
  } catch {
    // Narrow, documented retry: replace only bare non-finite literals.
    // A leading minus must be handled separately, because a word boundary
    // never matches before `-` in `:-Infinity`.
    const sanitised = text.replace(/(?<![A-Za-z0-9_])-?Infinity\b|\bNaN\b/g, "null");
    if (sanitised === text) {
      return { data: null, unparseable: true, diverged: false };
    }
    try {
      return {
        data: JSON.parse(sanitised) as Record<string, unknown>,
        unparseable: false,
        diverged: true,
      };
    } catch {
      return { data: null, unparseable: true, diverged: false };
    }
  }
}

function readJson(path: string): Record<string, unknown> | null {
  if (!existsSync(path)) return null;
  return parseTrainerState(readFileSync(path, "utf8")).data;
}

/** Candidate directories to inspect: the run dir itself, then its checkpoints. */
function candidates(runDir: string): string[] {
  return [runDir, ...listDir(runDir).filter((n) => n.startsWith("checkpoint-")).sort().map((n) => join(runDir, n))];
}

function locateWeights(runDir: string): number | null {
  for (const dir of candidates(runDir)) {
    for (const name of WEIGHTS) {
      const size = statSize(join(dir, name));
      if (size !== null) return size;
    }
  }
  return null;
}

function locateBaseModel(runDir: string): string {
  for (const dir of candidates(runDir)) {
    const cfg = readJson(join(dir, "adapter_config.json"));
    const base = cfg?.["base_model_name_or_path"];
    if (typeof base === "string") return base;
  }
  return "UNKNOWN";
}

interface LossLookup {
  readonly loss: number | null;
  readonly unparseable: boolean;
  readonly diverged: boolean;
}

function locateFinalLoss(runDir: string): LossLookup {
  let sawUnparseable = false;
  let sawDiverged = false;
  for (const dir of candidates(runDir)) {
    const path = join(dir, "trainer_state.json");
    if (!existsSync(path)) continue;
    const parsed = parseTrainerState(readFileSync(path, "utf8"));
    if (parsed.unparseable) sawUnparseable = true;
    if (parsed.diverged) sawDiverged = true;
    const state = parsed.data;
    if (state === null) continue;
    const log = state["log_history"];
    if (!Array.isArray(log)) continue;
    let last: number | null = null;
    for (const entry of log) {
      if (typeof entry !== "object" || entry === null) continue;
      const loss = (entry as Record<string, unknown>)["loss"];
      if (typeof loss === "number") last = loss;
    }
    if (last !== null) {
      return { loss: last, unparseable: sawUnparseable, diverged: sawDiverged };
    }
  }
  return { loss: null, unparseable: sawUnparseable, diverged: sawDiverged };
}

function hasOptimizer(runDir: string): boolean {
  return candidates(runDir).some((dir) => existsSync(join(dir, "optimizer.pt")));
}

/**
 * Scan roots for trained_* adapter directories.
 *
 * Symlinks are resolved so the same artifact is not counted twice; the
 * resolved origin is recorded so the link is visible in the census.
 */
export function censusLineage(roots: readonly string[]): LineageEntry[] {
  const seen = new Set<string>();
  const entries: LineageEntry[] = [];

  for (const root of roots) {
    if (!existsSync(root)) continue;
    for (const name of listDir(root).sort()) {
      if (!name.startsWith("trained_")) continue;
      const path = join(root, name);
      let resolved: string;
      try {
        resolved = realpathSync(path);
      } catch {
        continue;
      }
      // A symlinked adapter may point at a run's checkpoint directory rather
      // than the run directory. Compare run directories so the same artifact
      // is not counted twice under two names.
      const runDirOf = (candidate: string): string =>
        candidate.includes("/checkpoint-")
          ? candidate.slice(0, candidate.lastIndexOf("/checkpoint-"))
          : candidate;
      const identity = runDirOf(resolved);
      if (seen.has(identity)) continue;
      seen.add(identity);

      const side: LineageEntry["side"] = path.startsWith("/mnt/c")
        ? "win"
        : path.startsWith("/home/") || path.startsWith("/root/")
          ? "linux"
          : "other";

      const lookup = locateFinalLoss(path);
      entries.push({
        side,
        name,
        path,
        baseModel: locateBaseModel(path),
        adapterBytes: locateWeights(path),
        finalLoss: lookup.loss,
        hasOptimizerState: hasOptimizer(path),
        resolvedFrom: resolved === path ? null : resolved,
        stateUnparseable: lookup.unparseable,
        divergedNumeric: lookup.diverged,
      });
    }
  }

  return entries.sort((a, b) =>
    a.side === b.side
      ? a.name < b.name
        ? -1
        : a.name > b.name
          ? 1
          : 0
      : a.side < b.side
        ? -1
        : 1,
  );
}

export function summarise(entries: readonly LineageEntry[]): string {
  const withWeights = entries.filter((e) => e.adapterBytes !== null);
  const withLoss = entries.filter((e) => e.finalLoss !== null);
  const withOpt = entries.filter((e) => e.hasOptimizerState);
  const byBase = new Map<string, number>();
  for (const entry of entries) {
    const key = entry.baseModel.split("/").pop() ?? entry.baseModel;
    byBase.set(key, (byBase.get(key) ?? 0) + 1);
  }
  const diverged = entries.filter((e) => e.divergedNumeric);
  const unparseable = entries.filter((e) => e.stateUnparseable);
  const lines = [
    `adapters found:       ${entries.length}`,
    `with weights:         ${withWeights.length}`,
    `with logged loss:     ${withLoss.length}`,
    `with optimizer state: ${withOpt.length}`,
    `total adapter bytes:  ${withWeights.reduce((sum, e) => sum + (e.adapterBytes ?? 0), 0)}`,
  ];
  if (diverged.length > 0) {
    lines.push(`diverged numerics:    ${diverged.map((e) => e.name).join(", ")}`);
  }
  if (unparseable.length > 0) {
    lines.push(`unparseable state:    ${unparseable.map((e) => e.name).join(", ")}`);
  }
  for (const [base, count] of [...byBase.entries()].sort((a, b) => b[1] - a[1])) {
    lines.push(`  ${base}: ${count}`);
  }
  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function arg(name: string, fallback?: string): string | undefined {
  const index = process.argv.indexOf(`--${name}`);
  if (index < 0) return fallback;
  return process.argv[index + 1] ?? fallback;
}

const invokedDirectly =
  process.argv[1] !== undefined && process.argv[1].endsWith("census.js");

if (invokedDirectly) {
  const mode = process.argv[2];
  const json = process.argv.includes("--json");

  if (mode === "lineage") {
    const roots = (arg("roots") ?? "").split(",").filter((r) => r !== "");
    if (roots.length === 0) {
      console.error("usage: census lineage --roots <dir>[,<dir>...] [--json]");
      process.exitCode = 2;
    } else {
      const entries = censusLineage(roots);
      if (json) {
        console.log(JSON.stringify({ entries }, null, 2));
      } else {
        console.log("side  run                        base                          MB    loss");
        console.log("-".repeat(84));
        for (const entry of entries) {
          const mb = entry.adapterBytes === null ? "MISSING" : (entry.adapterBytes / 1e6).toFixed(1);
          const loss =
            entry.finalLoss !== null
              ? entry.finalLoss.toFixed(4)
              : entry.stateUnparseable
                ? "UNREAD"
                : "-";
          const flag = entry.divergedNumeric ? "  [diverged]" : "";
          console.log(
            `${entry.side.padEnd(6)}${entry.name.padEnd(27)}${entry.baseModel.split("/").pop()?.padEnd(28) ?? ""}${mb.padStart(6)}${loss.padStart(8)}${flag}`,
          );
        }
        console.log("-".repeat(84));
        console.log(summarise(entries));
      }
      process.exitCode = 0;
    }
  } else if (mode === "declarations") {
    const readme = arg("readme");
    const root = arg("root");
    if (readme === undefined || root === undefined) {
      console.error("usage: census declarations --readme <path> --root <dir>");
      process.exitCode = 2;
    } else {
      const result = auditDeclarations(readFileSync(readme, "utf8"), root, arg("strip-prefix"));
      console.log(`declared: ${result.declared.length}`);
      console.log(`present:  ${result.present.length}`);
      console.log(`missing:  ${result.missing.length}`);
      for (const path of result.missing) console.log(`  MISSING ${path}`);
      process.exitCode = result.missing.length === 0 ? 0 : 1;
    }
  } else {
    console.error("usage: census <lineage|declarations> ...");
    process.exitCode = 2;
  }
}
