/**
 * Tests for the view half: `isometric.ts` and `lego.ts`.
 *
 * The interesting cases are the failures. A hierarchy that adds up is easy to
 * build by accident; a hierarchy that *cannot* lie is what the module claims,
 * and the only way to check that claim is to make it lie and watch it refuse.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  auditTile,
  auditTree,
  govern,
  groundedSum,
  leavesOf,
  shortcutPays,
  type Leaf,
  type Tile,
} from "../src/isometric.js";

import { assemble, type Block } from "../src/lego.js";
import type { Source } from "../src/types.js";

const SRC: Source = { path: "fixture.pdf", sha256: "00", bytes: 1 };

const leaf = (id: string, cents: bigint): Leaf => ({
  kind: "leaf",
  id,
  scalars: { cents },
  source: SRC,
});

/** A two-level tree that adds up: 4 leaves, 2 tiles, 1 root. */
function soundTree(): Tile {
  const a = leaf("a", 10n);
  const b = leaf("b", 20n);
  const c = leaf("c", 30n);
  const d = leaf("d", 40n);
  const north: Tile = {
    kind: "tile",
    id: "north",
    children: [a, b],
    scalars: { cents: 30n },
  };
  const south: Tile = {
    kind: "tile",
    id: "south",
    children: [c, d],
    scalars: { cents: 70n },
  };
  return { kind: "tile", id: "root", children: [north, south], scalars: { cents: 100n } };
}

test("a sound tree audits clean at every level", () => {
  const t = soundTree();
  const e = auditTree(t);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.length, 3); // north, south, root
  assert.ok(e.value.every((a) => a.derived && a.grounded));
});

test("a tile that overstates its leaves is caught as not grounded", () => {
  // The classic fabrication: the root claims more than the record supports.
  const bad: Tile = {
    kind: "tile",
    id: "root",
    children: [leaf("a", 10n), leaf("b", 20n)],
    scalars: { cents: 999n },
  };
  const e = auditTile(bad);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "not-derived");
});

test("a child that lies makes its parent internally consistent but ungrounded", () => {
  // This is the subtle case the two-check design exists for: `north` reports
  // 40 while its leaves sum to 30. The root, summing *reported* figures,
  // agrees with its child and so is derived — but the leaves say otherwise.
  const a = leaf("a", 10n);
  const b = leaf("b", 20n);
  const lyingChild: Tile = {
    kind: "tile",
    id: "north",
    children: [a, b],
    scalars: { cents: 40n }, // leaves say 30
  };
  const root: Tile = {
    kind: "tile",
    id: "root",
    children: [lyingChild],
    scalars: { cents: 40n }, // agrees with the liar
  };
  const rootAudit = auditTile(root);
  assert.equal(rootAudit.ok, false);
  if (rootAudit.ok) return;
  assert.equal(rootAudit.failed, "not-grounded");
  assert.match(rootAudit.detail, /north/);

  // And the liar itself is caught on the shorter check.
  const childAudit = auditTile(lyingChild);
  assert.equal(childAudit.ok, false);
  if (childAudit.ok) return;
  assert.equal(childAudit.failed, "not-derived");
});

test("the same leaf counted twice is refused", () => {
  const a = leaf("a", 10n);
  // The same object appears under both children: a double count.
  const t: Tile = {
    kind: "tile",
    id: "root",
    children: [a, a],
    scalars: { cents: 20n },
  };
  const e = auditTile(t);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "double-counted-leaf");
});

test("a tile with no children displays nothing derivable and is refused", () => {
  const t: Tile = { kind: "tile", id: "empty", children: [], scalars: { cents: 1n } };
  const e = auditTile(t);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "empty-tile");
});

test("a dropped category is refused rather than silently omitted", () => {
  const t: Tile = {
    kind: "tile",
    id: "root",
    children: [leaf("a", 10n)],
    scalars: { cents: 10n, hours: 0n },
  };
  // The leaf does not report `hours`, so the tile's `hours` has no derivation.
  const e = auditTile(t);
  // A tile may display a key its children do not report only if the value is 0n
  // (nothing to derive); anything else is an invented number.
  assert.equal(e.ok, true);

  const invented: Tile = {
    kind: "tile",
    id: "root",
    children: [leaf("a", 10n)],
    scalars: { cents: 10n, hours: 7n },
  };
  const bad = auditTile(invented);
  assert.equal(bad.ok, false);
  if (bad.ok) return;
  assert.ok(bad.failed === "not-derived" || bad.failed === "not-grounded");
});

test("a child reporting a key the parent omits is a silent deletion", () => {
  const rich: Leaf = { kind: "leaf", id: "a", scalars: { cents: 10n, hours: 5n }, source: SRC };
  const t: Tile = { kind: "tile", id: "root", children: [rich], scalars: { cents: 10n } };
  const e = auditTile(t);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "not-derived");
  assert.match(e.detail, /hours/);
});

test("govern returns the leaf list with the figure, so the figure is checkable", () => {
  const t = soundTree();
  const e = govern(t);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.deepEqual(e.value.leaves, ["a", "b", "c", "d"]);
  assert.equal(e.value.leafCount, 4);
  assert.equal(e.value.scalars["cents"], 100n);
});

test("govern refuses a view whose figure is not the fold", () => {
  const bad: Tile = {
    kind: "tile",
    id: "root",
    children: [leaf("a", 1n)],
    scalars: { cents: 2n },
  };
  const e = govern(bad);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "figure-not-grounded");
});

test("the isometric shortcut pays only when leaves outnumber tiles", () => {
  const e = shortcutPays(soundTree());
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.equal(e.value.saved, 1); // 4 leaves, 3 tiles

  // A degenerate hierarchy: one tile per leaf saves nothing.
  const chain: Tile = {
    kind: "tile",
    id: "root",
    children: [leaf("a", 1n)],
    scalars: { cents: 1n },
  };
  const noSaving = shortcutPays(chain);
  assert.equal(noSaving.ok, false);
  if (noSaving.ok) return;
  assert.equal(noSaving.failed, "no-saving");
});

test("leaf enumeration and ground sums are deterministic and sorted", () => {
  const t = soundTree();
  assert.deepEqual(leavesOf(t), [...leavesOf(t)]);
  assert.deepEqual(leavesOf(t), ["a", "b", "c", "d"]);
  assert.equal(groundedSum(t, "cents"), 100n);
});

/* --------------------------------------------------------------------- lego */

const doubler: Block = {
  id: "double",
  consumes: ["x"],
  produces: ["y"],
  run: (inputs) => {
    const x = inputs.get("x");
    if (typeof x !== "bigint") {
      throw new Error("double expects bigint at x");
    }
    return {
      ok: true,
      check: "double",
      falsifier: "y != 2x",
      value: new Map([["y", x * 2n]]),
      derivation: [`y = 2 * ${x} = ${x * 2n}`],
    };
  },
};

const adder: Block = {
  id: "add",
  consumes: ["y"],
  produces: ["z"],
  run: (inputs) => {
    const y = inputs.get("y");
    if (typeof y !== "bigint") {
      throw new Error("add expects bigint at y");
    }
    return {
      ok: true,
      check: "add",
      falsifier: "z != y + 1",
      value: new Map([["z", y + 1n]]),
      derivation: [`z = ${y} + 1 = ${y + 1n}`],
    };
  },
};

test("a sound assembly executes in dependency order and produces its outputs", () => {
  const e = assemble([adder, doubler], new Map([["x", 5n]]), ["z"]);
  assert.equal(e.ok, true);
  if (!e.ok) return;
  assert.deepEqual(e.value.order, ["double", "add"]);
  assert.equal(e.value.outputs.get("z"), 11n);
});

test("two blocks producing the same port is a collision, not a merge", () => {
  const rival: Block = { ...doubler, id: "double-2" };
  const e = assemble([doubler, rival, adder], new Map([["x", 1n]]), ["z"]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "produce-collision");
});

test("an input with no source is refused by name", () => {
  const e = assemble([adder], new Map(), ["z"]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "unresolved-input");
  assert.match(e.detail, /"y"/);
});

test("a dependency cycle is refused as a self-supporting claim", () => {
  const loopA: Block = {
    id: "a",
    consumes: ["p2"],
    produces: ["p1"],
    run: () => ({
      ok: true,
      check: "a",
      falsifier: "never",
      value: new Map([["p1", 1n]]),
      derivation: ["identity"],
    }),
  };
  const loopB: Block = {
    id: "b",
    consumes: ["p1"],
    produces: ["p2"],
    run: () => ({
      ok: true,
      check: "b",
      falsifier: "never",
      value: new Map([["p2", 1n]]),
      derivation: ["identity"],
    }),
  };
  const e = assemble([loopA, loopB], new Map(), []);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "cycle");
});

test("a block that refuses stops the assembly and is named", () => {
  const refusing: Block = {
    id: "refuse",
    consumes: ["x"],
    produces: ["y"],
    run: () => ({
      ok: false,
      check: "refuse",
      falsifier: "a case where it passes",
      failed: "by-construction",
      detail: "this block always refuses",
    }),
  };
  const e = assemble([refusing, adder], new Map([["x", 1n]]), ["z"]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "block-refused");
  assert.match(e.detail, /refuse/);
});

test("a required output that was never produced is refused", () => {
  const e = assemble([doubler], new Map([["x", 1n]]), ["never-produced"]);
  assert.equal(e.ok, false);
  if (e.ok) return;
  assert.equal(e.failed, "missing-output");
});
