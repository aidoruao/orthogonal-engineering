#!/usr/bin/env node
/**
 * game — command line.
 *
 * Every subcommand prints the evidence object it received, including the
 * falsifier. Exit code is 0 when the checked proposition holds and 1 when it
 * does not; there is no third state, and no subcommand exits 0 on an
 * inapplicable check.
 *
 * Usage:
 *   node dist/src/cli.js incentive --bond N --gain N --detects
 *   node dist/src/cli.js settle    --debt N --capacity N --violator N --other N
 *   node dist/src/cli.js claim     --recorded N --stated N
 *   node dist/src/cli.js inversion --claims N --checks N --cost N --bond N
 *   node dist/src/cli.js grace     --debt N --capacity N --violator N --supplied N
 */

import { render, type Evidence } from "../src/types.js";
import {
  bondIsInert,
  incentiveCompatible,
  inversionPays,
  type Mechanism,
} from "../src/incentive.js";
import { applyGrace, classifyClaim, settle, type Settlement } from "../src/covenant.js";
import { BDS_FINDING_LINES, traceFindings } from "../src/audit-trace.js";

type Args = ReadonlyMap<string, string>;

function parse(argv: readonly string[]): { cmd: string; flags: Args } {
  const cmd = argv[0] ?? "";
  const flags = new Map<string, string>();
  for (let i = 1; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === undefined || !key.startsWith("--")) continue;
    const value = argv[i + 1];
    if (value === undefined || value.startsWith("--")) {
      flags.set(key.slice(2), "true");
    } else {
      flags.set(key.slice(2), value);
      i += 1;
    }
  }
  return { cmd, flags };
}

function need(flags: Args, key: string): bigint {
  const raw = flags.get(key);
  if (raw === undefined) {
    throw new Error(`missing --${key}`);
  }
  if (!/^-?\d+$/.test(raw)) {
    throw new Error(`--${key} must be an integer, got "${raw}"`);
  }
  return BigInt(raw);
}

function needInt(flags: Args, key: string): number {
  const v = need(flags, key);
  if (v > BigInt(Number.MAX_SAFE_INTEGER) || v < BigInt(Number.MIN_SAFE_INTEGER)) {
    throw new Error(`--${key} out of safe range: ${v}`);
  }
  return Number(v);
}

function emit<T>(e: Evidence<T>): number {
  process.stdout.write(`${render(e)}\n`);
  return e.ok ? 0 : 1;
}

function main(argv: readonly string[]): number {
  const { cmd, flags } = parse(argv);
  switch (cmd) {
    case "incentive": {
      const m: Mechanism = {
        bond: need(flags, "bond"),
        gain: need(flags, "gain"),
        detects: flags.get("detects") === "true" || flags.has("detects"),
      };
      const c = incentiveCompatible(m);
      if (!c.ok && c.failed === "no-detector") {
        // Report both refusals: the mechanism is not compatible, and the bond
        // is not the thing that would have fixed it.
        const inert = bondIsInert(m);
        process.stdout.write(`${render(c)}\n${render(inert)}\n`);
        return 1;
      }
      return emit(c);
    }
    case "settle": {
      const s: Settlement = {
        account: { debt: need(flags, "debt"), capacity: need(flags, "capacity") },
        byViolator: need(flags, "violator"),
        byOther: need(flags, "other"),
      };
      return emit(settle(s));
    }
    case "claim": {
      return emit(
        classifyClaim({ recorded: need(flags, "recorded"), stated: need(flags, "stated") }),
      );
    }
    case "inversion": {
      return emit(
        inversionPays(
          needInt(flags, "claims"),
          needInt(flags, "checks"),
          need(flags, "cost"),
          need(flags, "bond"),
        ),
      );
    }
    case "grace": {
      const base: Settlement = {
        account: { debt: need(flags, "debt"), capacity: need(flags, "capacity") },
        byViolator: need(flags, "violator"),
        byOther: 0n,
      };
      return emit(applyGrace({ base, supplied: need(flags, "supplied") }));
    }
    case "money": {
      // Reads the BDS findings as compiled from the audited statements. This is
      // not a synthetic fixture: every figure is quoted from `findings.ts`, which
      // quotes the audit at the cited page.
      const t = traceFindings(BDS_FINDING_LINES);
      if (!t.ok) return emit(t);
      const lines = t.value.lines.map((l) => {
        const head = `  ${l.id}  ${l.status}`;
        const gaps = l.gaps.map((g) => `      absent ${g.field}: ${g.why}`);
        const finds = l.findings.map(
          (f) => `      FINDING ${f.kind} ${f.amount}: ${f.detail}`,
        );
        const need = l.wouldMeasure.map((m) => `      would measure: ${m}`);
        return [head, ...gaps, ...finds, ...need].join("\n");
      });
      process.stdout.write(
        [
          render(t),
          "",
          `stated total: ${t.value.statedTotal}`,
          `measured ${t.value.measuredCount} / unmeasured ${t.value.unmeasuredCount} ` +
            `/ findings ${t.value.findingCount}`,
          `closed: ${t.value.closed}`,
          "",
          ...lines,
        ].join("\n") + "\n",
      );
      // Exit 0 when the trace ran. A trace that finds holes is a successful
      // trace; the holes are its result, not its failure. Exit 1 is reserved
      // for a trace that could not be performed at all.
      return 0;
    }
    default: {
      process.stderr.write(
        `unknown subcommand "${cmd}". Expected: incentive | settle | claim | inversion | grace | money\n`,
      );
      return 2;
    }
  }
}

try {
  process.exitCode = main(process.argv.slice(2));
} catch (err: unknown) {
  const msg = err instanceof Error ? err.message : String(err);
  process.stderr.write(`error: ${msg}\n`);
  process.exitCode = 2;
}
