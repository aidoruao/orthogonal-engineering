/**
 * Tests for the corpus custody check, using synthetic files in a temp dir.
 * No corpus is required and nothing real is read.
 */

import { strict as assert } from "node:assert";
import { createHash } from "node:crypto";
import { mkdirSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, describe, it } from "node:test";

import { isClean, verifyCorpus } from "../src/corpus.js";

function sha(data: string): string {
  return createHash("sha256").update(data).digest("hex");
}

const root = mkdtempSync(join(tmpdir(), "oe-corpus-"));
after(() => {
  rmSync(root, { recursive: true, force: true });
});

interface Fixture {
  readonly dir: string;
  readonly manifest: string;
}

function fixture(name: string, files: Record<string, string>, manifestLines: string): Fixture {
  const dir = join(root, name);
  mkdirSync(dir, { recursive: true });
  for (const [filename, content] of Object.entries(files)) {
    writeFileSync(join(dir, filename), content);
  }
  const manifest = join(dir, "MANIFEST.sha256");
  writeFileSync(manifest, manifestLines);
  return { dir, manifest };
}

describe("verifyCorpus", () => {
  it("reports a clean corpus", () => {
    const f = fixture(
      "clean",
      { "a.pdf": "alpha", "b.pdf": "beta" },
      `${sha("alpha")}  a.pdf\n${sha("beta")}  b.pdf\n`,
    );
    const report = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.equal(report.committed, 2);
    assert.equal(report.matched, 2);
    assert.equal(isClean(report), true);
  });

  it("reports a mismatched file", () => {
    const f = fixture(
      "mismatch",
      { "a.pdf": "tampered" },
      `${sha("original")}  a.pdf\n`,
    );
    const report = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.equal(report.matched, 0);
    assert.equal(report.mismatched.length, 1);
    assert.equal(report.mismatched[0]?.name, "a.pdf");
    assert.equal(isClean(report), false);
  });

  it("reports a missing file", () => {
    const f = fixture("missing", {}, `${sha("gone")}  gone.pdf\n`);
    const report = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.deepEqual(report.missing, ["gone.pdf"]);
    assert.equal(isClean(report), false);
  });

  it("reports an unlisted file", () => {
    const f = fixture(
      "unlisted",
      { "a.pdf": "alpha", "extra.pdf": "surprise" },
      `${sha("alpha")}  a.pdf\n`,
    );
    const report = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.deepEqual(report.unlisted, ["extra.pdf"]);
    assert.equal(isClean(report), false);
  });

  it("reports a malformed manifest line", () => {
    const f = fixture("malformed", { "a.pdf": "alpha" }, `not-a-hash  a.pdf\n`);
    const report = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.equal(report.malformed.length, 1);
    assert.equal(isClean(report), false);
  });

  it("sorts its outputs deterministically", () => {
    const f = fixture(
      "sorted",
      { "z.pdf": "z", "a.pdf": "a", "m.pdf": "m" },
      "",
    );
    const first = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    const second = verifyCorpus(f.manifest, f.dir, ["MANIFEST.sha256"]);
    assert.deepEqual(first.unlisted, second.unlisted);
    assert.deepEqual(first.unlisted, ["a.pdf", "m.pdf", "z.pdf"]);
  });
});
