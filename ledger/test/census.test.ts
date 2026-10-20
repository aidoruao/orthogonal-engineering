/**
 * Territory-census tests.
 *
 * Three things are under test:
 *   1. Parsing a README's declared tree correctly (nesting, box drawing).
 *   2. Reporting divergence between declared and actual files.
 *   3. Tolerating Python-written `Infinity` in trainer_state.json while
 *      *recording* that it happened, rather than reporting a silent blank.
 */

import { strict as assert } from "node:assert";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, describe, it } from "node:test";

import {
  auditDeclarations,
  censusLineage,
  parseDeclaredTree,
  parseTrainerState,
  summarise,
} from "../tools/census.js";

const root = mkdtempSync(join(tmpdir(), "oe-census-"));
after(() => {
  rmSync(root, { recursive: true, force: true });
});

const README = `# Thing

### Directory Structure

\`\`\`text
Thing/
├── axioms/
│   ├── one.md
│   └── two.md
├── implementation/
│   └── tests/
│       └── test_one.py
└── README.md
\`\`\`

## Next
`;

describe("parseDeclaredTree", () => {
  it("reconstructs nested paths", () => {
    const declared = parseDeclaredTree(README);
    assert.deepEqual(declared, [
      "Thing/axioms/one.md",
      "Thing/axioms/two.md",
      "Thing/implementation/tests/test_one.py",
      "Thing/README.md",
    ]);
  });

  it("returns an empty list when there is no tree block", () => {
    assert.deepEqual(parseDeclaredTree("# No tree here"), []);
  });

  it("ignores blank lines inside the block", () => {
    const text = "### Directory Structure\n\n```text\na/\n  b.md\n\n  c.md\n```\n";
    assert.deepEqual(parseDeclaredTree(text), ["a/b.md", "a/c.md"]);
  });
});

describe("auditDeclarations", () => {
  it("reports every declared path as missing in an empty repo", () => {
    const empty = join(root, "empty");
    mkdirSync(empty, { recursive: true });
    writeFileSync(join(empty, "README.md"), README);
    const result = auditDeclarations(README, empty, "Thing");
    assert.equal(result.declared.length, 4);
    assert.equal(result.present.length, 1, "only README.md exists");
    assert.equal(result.missing.length, 3);
  });

  it("reports no divergence when the tree is real", () => {
    const full = join(root, "full");
    mkdirSync(join(full, "axioms"), { recursive: true });
    mkdirSync(join(full, "implementation", "tests"), { recursive: true });
    writeFileSync(join(full, "axioms", "one.md"), "");
    writeFileSync(join(full, "axioms", "two.md"), "");
    writeFileSync(join(full, "implementation", "tests", "test_one.py"), "");
    writeFileSync(join(full, "README.md"), "");
    const result = auditDeclarations(README, full, "Thing");
    assert.equal(result.missing.length, 0);
    assert.equal(result.present.length, 4);
  });
});

describe("parseTrainerState", () => {
  it("parses strict JSON", () => {
    const result = parseTrainerState('{"log_history":[{"loss":0.5}],"global_step":10}');
    assert.equal(result.unparseable, false);
    assert.equal(result.diverged, false);
    assert.equal((result.data?.["global_step"] as number), 10);
  });

  it("tolerates Infinity and records the divergence", () => {
    const text = '{"log_history":[{"loss":0.5,"grad_norm":Infinity}]}';
    const result = parseTrainerState(text);
    assert.equal(result.unparseable, false);
    assert.equal(result.diverged, true, "the divergence must be reported, not hidden");
    assert.ok(result.data !== null);
  });

  it("tolerates NaN and -Infinity", () => {
    assert.equal(parseTrainerState('{"a":NaN}').diverged, true);
    assert.equal(parseTrainerState('{"a":-Infinity}').diverged, true);
  });

  it("reports genuinely broken JSON as unparseable", () => {
    const result = parseTrainerState("{not json at all");
    assert.equal(result.unparseable, true);
    assert.equal(result.data, null);
    assert.equal(result.diverged, false);
  });

  it("does not silently accept a truncated object", () => {
    assert.equal(parseTrainerState('{"log_history":[').unparseable, true);
  });
});

describe("censusLineage", () => {
  function makeRun(base: string, name: string, loss: number | "infinity" | null): void {
    const runDir = join(base, name, "checkpoint-9000");
    mkdirSync(runDir, { recursive: true });
    writeFileSync(join(runDir, "adapter_model.safetensors"), Buffer.alloc(1024));
    writeFileSync(
      join(runDir, "adapter_config.json"),
      JSON.stringify({ base_model_name_or_path: "Qwen/Qwen2.5-1.5B" }),
    );
    writeFileSync(join(runDir, "optimizer.pt"), Buffer.alloc(16));
    if (loss === "infinity") {
      writeFileSync(
        join(runDir, "trainer_state.json"),
        '{"log_history":[{"loss":0.25,"grad_norm":Infinity}]}',
      );
    } else if (loss !== null) {
      writeFileSync(
        join(runDir, "trainer_state.json"),
        JSON.stringify({ log_history: [{ loss }] }),
      );
    }
  }

  it("finds adapters and reports their metadata", () => {
    const base = join(root, "lineage");
    mkdirSync(base, { recursive: true });
    makeRun(base, "trained_a", 0.1);
    makeRun(base, "trained_b", 0.2);

    const entries = censusLineage([base]);
    assert.equal(entries.length, 2);
    assert.equal(entries[0]?.baseModel, "Qwen/Qwen2.5-1.5B");
    assert.equal(entries[0]?.adapterBytes, 1024);
    assert.equal(entries[0]?.hasOptimizerState, true);
    const losses = entries.map((e) => e.finalLoss).sort();
    assert.deepEqual(losses, [0.1, 0.2]);
  });

  it("marks a diverged run without dropping its loss", () => {
    const base = join(root, "diverged");
    mkdirSync(base, { recursive: true });
    makeRun(base, "trained_c", "infinity");
    const entries = censusLineage([base]);
    assert.equal(entries.length, 1);
    assert.equal(entries[0]?.divergedNumeric, true);
    assert.equal(entries[0]?.finalLoss, 0.25);
  });

  it("reports a run with no weights distinctly", () => {
    const base = join(root, "empty-run");
    mkdirSync(join(base, "trained_d"), { recursive: true });
    const entries = censusLineage([base]);
    assert.equal(entries.length, 1);
    assert.equal(entries[0]?.adapterBytes, null);
  });

  it("is deterministic across runs", () => {
    const base = join(root, "lineage");
    assert.deepEqual(censusLineage([base]), censusLineage([base]));
  });

  it("summarises counts without claiming anything it did not measure", () => {
    const base = join(root, "lineage");
    const entries = censusLineage([base]);
    const text = summarise(entries);
    assert.match(text, /adapters found:\s+2/);
    assert.match(text, /Qwen2\.5-1\.5B: 2/);
  });
});
