/**
 * No hidden state. The environment a verdict was produced in is part of the
 * verdict, because a check is only meaningful in the environment that ran it.
 *
 * The one catch below is not silent: a missing Lean toolchain is recorded as
 * the literal string "absent", which appears in the receipt and in calibration.
 */

import { execFileSync } from "node:child_process";

import type { Environment } from "./types.js";

function leanVersion(): string {
  try {
    const output = execFileSync("lean", ["--version"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return output.trim();
  } catch {
    return "absent";
  }
}

export function captureEnvironment(): Environment {
  return {
    node: process.version,
    lean: leanVersion(),
    platform: `${process.platform}-${process.arch}`,
  };
}
