/**
 * Freshness tests.
 *
 * The comparison is pure, so every case is deterministic and needs no
 * toolchain. The one property that matters most: a mismatch is STALE, never
 * FAILED. If staleness ever becomes a failure, operators disable the check.
 */

import { strict as assert } from "node:assert";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import {
  compareFingerprint,
  computeFingerprint,
  parseVersion,
  readRecorded,
  serializeFingerprint,
  type Fingerprint,
} from "../src/freshness.js";

const root = mkdtempSync(join(tmpdir(), "oe-fresh-"));
after(() => {
  rmSync(root, { recursive: true, force: true });
});

function fp(overrides: Partial<Fingerprint> = {}): Fingerprint {
  return {
    node: "22.23.1",
    typescript: "5.9.3",
    lean: "4.35.0",
    lockfile: "a".repeat(64),
    ...overrides,
  };
}

describe("parseVersion", () => {
  it("extracts a semver from tool output", () => {
    assert.equal(parseVersion("Version 5.9.3"), "5.9.3");
    assert.equal(parseVersion("v22.23.1"), "22.23.1");
    assert.equal(parseVersion("Lean (version 4.35.0, x86_64)"), "4.35.0");
  });

  it("returns null for absent or unversioned output", () => {
    assert.equal(parseVersion(null), null);
    assert.equal(parseVersion("no version here"), null);
  });
});

describe("compareFingerprint", () => {
  it("reports absent when nothing was recorded", () => {
    const verdict = compareFingerprint(null, fp());
    assert.equal(verdict.status, "absent");
  });

  it("reports verified when every dimension matches", () => {
    const verdict = compareFingerprint(fp(), fp());
    assert.equal(verdict.status, "verified");
  });

  it("reports stale, never failed, when node moves", () => {
    const verdict = compareFingerprint(fp(), fp({ node: "24.0.0" }));
    assert.equal(verdict.status, "stale");
    if (verdict.status !== "stale") return;
    assert.equal(verdict.differences.length, 1);
    assert.match(verdict.differences[0] ?? "", /node/);
    assert.match(verdict.differences[0] ?? "", /22\.23\.1/);
    assert.match(verdict.differences[0] ?? "", /24\.0\.0/);
  });

  it("reports stale when only the lockfile moves", () => {
    const verdict = compareFingerprint(fp(), fp({ lockfile: "b".repeat(64) }));
    assert.equal(verdict.status, "stale");
  });

  it("reports every dimension that moved, not just the first", () => {
    const verdict = compareFingerprint(
      fp(),
      fp({ node: "24.0.0", lean: "4.36.0", lockfile: "c".repeat(64) }),
    );
    assert.equal(verdict.status, "stale");
    if (verdict.status !== "stale") return;
    assert.equal(verdict.differences.length, 3);
  });

  it("is deterministic", () => {
    const first = compareFingerprint(fp(), fp({ lean: "4.36.0" }));
    const second = compareFingerprint(fp(), fp({ lean: "4.36.0" }));
    assert.deepEqual(first, second);
  });

  it("treats a tool appearing or disappearing as stale", () => {
    const absentToPresent = compareFingerprint(fp({ lean: "absent" }), fp());
    assert.equal(absentToPresent.status, "stale");
    const presentToAbsent = compareFingerprint(fp(), fp({ lean: "absent" }));
    assert.equal(presentToAbsent.status, "stale");
  });
});

describe("serialization", () => {
  it("round-trips through a file", () => {
    const path = join(root, "fp.json");
    writeFileSync(path, serializeFingerprint(fp()));
    const loaded = readRecorded(path);
    assert.deepEqual(loaded, fp());
  });

  it("writes a fixed key order with a trailing newline", () => {
    const text = serializeFingerprint(fp());
    assert.ok(text.endsWith("\n"));
    const keys = [...text.matchAll(/^  "(\w+)":/gm)].map((m) => m[1]);
    assert.deepEqual(keys, ["node", "typescript", "lean", "lockfile"]);
  });

  it("returns null for a missing file", () => {
    assert.equal(readRecorded(join(root, "nope.json")), null);
  });

  it("returns null for malformed JSON rather than guessing", () => {
    const path = join(root, "bad.json");
    writeFileSync(path, "{not json");
    assert.equal(readRecorded(path), null);
  });

  it("returns null when a required dimension is missing", () => {
    const path = join(root, "partial.json");
    writeFileSync(path, JSON.stringify({ node: "22.0.0" }));
    assert.equal(readRecorded(path), null);
  });
});

describe("computeFingerprint", () => {
  it("produces well-formed values for every dimension", () => {
    const current = computeFingerprint(root);
    assert.match(current.node, /^\d+\.\d+\.\d+$/);
    // The compiler may be present or absent depending on install state; both
    // are valid and both must be recorded honestly.
    assert.ok(current.typescript === "absent" || /^\d+\.\d+\.\d+$/.test(current.typescript));
    assert.ok(current.lean === "absent" || /^\d+\.\d+\.\d+$/.test(current.lean));
    assert.ok(current.lockfile === "absent" || /^[0-9a-f]{64}$/.test(current.lockfile));
  });

  it("is stable across two calls in one environment", () => {
    assert.deepEqual(computeFingerprint(root), computeFingerprint(root));
  });

  it("does not depend on the caller's working directory", () => {
    // Regression: `npx tsc` resolves relative to cwd, so a fingerprint taken
    // from the repo root measured TypeScript as "absent" while the same
    // environment measured "5.9.3" from the ledger. Every check then reported
    // STALE. The fingerprint must be a property of the environment, not of the
    // directory the tool happened to be invoked from.
    mkdirSync(join(root, "ledger"), { recursive: true });
    const cli = fileURLToPath(new URL("../src/freshness.js", import.meta.url));
    const fromLedger = execFileSync(process.execPath, [cli, "--root", root], {
      encoding: "utf8",
      cwd: join(root, "ledger"),
    });
    const fromRoot = execFileSync(process.execPath, [cli, "--root", root], {
      encoding: "utf8",
      cwd: root,
    });
    assert.equal(fromLedger, fromRoot);
  });
});
