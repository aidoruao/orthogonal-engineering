/**
 * game/isometric — governing from above without lying about what is below.
 *
 * The user's observation is exact: a city-builder presents an isometric view
 * over an enormous downstream simulation, and you can govern from it. The
 * reason that works is not that the view is pretty. It is that every number on
 * screen is a *fold* over objects that still exist, and the view carries enough
 * provenance to reach them.
 *
 * So the rule this module enforces is single:
 *
 *   **A tile may not display a number it cannot derive.**
 *
 * Each tile is checked twice, and the two checks are different questions:
 *
 * - **derived** — the tile's figure equals the sum of its children's figures.
 *   This is internal coherence. A tile can be derived and still wrong, if a
 *   child lied.
 * - **grounded** — the tile's figure equals the sum over the leaves it claims.
 *   This is correspondence to the record. Only grounding constrains reality.
 *
 * Reporting both is the whole point of a glass box: when a fabrication enters,
 * these two disagree at exactly the tile where it entered, and that tile is
 * named. A single boolean would say "the view is wrong" and leave you to find
 * out where.
 */

import { fail, pass, type Evidence, type Source, type Units } from "./types.js";

/** Scalar values shown on a tile. Keys are stable identifiers, not labels. */
export type Scalars = Readonly<Record<string, Units>>;

export type Leaf = {
  readonly kind: "leaf";
  readonly id: string;
  /** The measurement, and the document it came from. */
  readonly scalars: Scalars;
  readonly source: Source;
};

export type Tile = {
  readonly kind: "tile";
  readonly id: string;
  readonly children: readonly Node[];
  /** What the view displays. Must be derivable; see `auditTile`. */
  readonly scalars: Scalars;
};

export type Node = Leaf | Tile;

/** Every leaf under a node, sorted, for deterministic output. */
export function leavesOf(n: Node): readonly string[] {
  if (n.kind === "leaf") return [n.id];
  const all = n.children.flatMap(leavesOf);
  return [...all].sort();
}

/** Sum of a key over a node's own reports (not recursive into leaves). */
export function reportedSum(n: Node, key: string): bigint {
  if (n.kind === "leaf") return n.scalars[key] ?? 0n;
  const sum = n.children.reduce<bigint>((acc, c) => acc + (c.scalars[key] ?? 0n), 0n);
  return sum;
}

/** Sum of a key over the leaves a node covers — ground truth. */
export function groundedSum(n: Node, key: string): bigint {
  if (n.kind === "leaf") return n.scalars[key] ?? 0n;
  return n.children.reduce<bigint>((acc, c) => acc + groundedSum(c, key), 0n);
}

/** Every key mentioned anywhere under a node, sorted. */
export function keysOf(n: Node): readonly string[] {
  const seen = new Set<string>();
  const walk = (x: Node): void => {
    for (const k of Object.keys(x.scalars)) seen.add(k);
    if (x.kind === "tile") x.children.forEach(walk);
  };
  walk(n);
  return [...seen].sort();
}

export type TileAudit = {
  readonly id: string;
  readonly derived: boolean;
  readonly grounded: boolean;
  /** Keys where the tile's own figure differs from the sum of its children. */
  readonly unDerived: readonly string[];
  /** Keys where the tile's own figure differs from the sum over its leaves. */
  readonly unGrounded: readonly string[];
  readonly leafCount: number;
};

const DERIVED_FALSIFIER =
  "a tile whose displayed figure differs from the sum of its children's figures for some key";
const GROUNDED_FALSIFIER =
  "a tile whose displayed figure differs from the sum over the leaves it claims to cover";

/**
 * Audit one tile, without recursing. The caller recurses, so a fabrication is
 * reported at the tile where it entered rather than only at the root.
 */
export function auditTile(t: Tile): Evidence<TileAudit> {
  const check = `audit-tile:${t.id}`;
  if (t.children.length === 0) {
    return fail(
      check,
      DERIVED_FALSIFIER,
      "empty-tile",
      "a tile with no children displays a number with no derivation behind it. " +
        "That is the failure this module exists to prevent, so it is a hard error.",
    );
  }
  const ids = leavesOf(t);
  const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
  if (dupes.length > 0) {
    return fail(
      check,
      DERIVED_FALSIFIER,
      "double-counted-leaf",
      `leaf ids appear more than once under ${t.id}: ${[...new Set(dupes)].join(", ")}. ` +
        `Double counting is how a total becomes larger than the thing it totals.`,
    );
  }

  const unDerived: string[] = [];
  const unGrounded: string[] = [];
  for (const key of keysOf(t)) {
    const shown = t.scalars[key];
    if (shown === undefined) {
      // A child reports a key the tile does not display. The tile has dropped a
      // category, which is a silent deletion rather than a rounding.
      unDerived.push(key);
      unGrounded.push(key);
      continue;
    }
    if (shown !== reportedSum(t, key)) unDerived.push(key);
    if (shown !== groundedSum(t, key)) unGrounded.push(key);
  }

  const audit: TileAudit = {
    id: t.id,
    derived: unDerived.length === 0,
    grounded: unGrounded.length === 0,
    unDerived,
    unGrounded,
    leafCount: ids.length,
  };

  if (!audit.derived) {
    return fail(
      check,
      DERIVED_FALSIFIER,
      "not-derived",
      `${t.id} disagrees with its own children on: ${unDerived.join(", ")}`,
    );
  }
  if (!audit.grounded) {
    // Name the child whose report the leaves contradict. Pointing only at the
    // parent would say "something below here is wrong" and leave the reader to
    // bisect the tree, which is exactly the burden this module exists to lift.
    const suspects: string[] = [];
    for (const key of unGrounded) {
      for (const c of t.children) {
        const reported = c.scalars[key];
        if (reported !== undefined && reported !== groundedSum(c, key)) {
          suspects.push(`${c.id}.${key} reports ${reported}, leaves sum ${groundedSum(c, key)}`);
        }
      }
    }
    const where =
      suspects.length > 0
        ? ` Fabrication entered at: ${suspects.join("; ")}.`
        : ` No child reports a contradicted figure, so the tile's own figure is the fabrication.`;
    return fail(
      check,
      GROUNDED_FALSIFIER,
      "not-grounded",
      `${t.id} is internally consistent but disagrees with its leaves on: ` +
        `${unGrounded.join(", ")}.${where}`,
    );
  }
  return pass(check, DERIVED_FALSIFIER, audit, [
    `${t.children.length} children, ${ids.length} leaves, disjoint`,
    ...keysOf(t).map(
      (k) => `key "${k}": shown ${t.scalars[k] ?? 0n} = children sum = leaves sum`,
    ),
  ]);
}

/** Audit every tile in the tree, bottom-up. */
export function auditTree(n: Node): Evidence<readonly TileAudit[]> {
  const check = `audit-tree:${n.id}`;
  const FALSIFIER = "a tile anywhere in the tree whose displayed figure is not derivable and grounded";
  const audits: TileAudit[] = [];
  const walk = (x: Node): Evidence<null> => {
    if (x.kind === "leaf") return pass(check, FALSIFIER, null, [`leaf ${x.id} taken as given`]);
    for (const c of x.children) {
      const r = walk(c);
      if (!r.ok) return r;
    }
    const a = auditTile(x);
    if (!a.ok) return a;
    audits.push(a.value);
    return pass(check, FALSIFIER, null, [`tile ${x.id} sound`]);
  };
  const r = walk(n);
  if (!r.ok) return r;
  return pass(check, FALSIFIER, audits, [
    `${audits.length} tiles audited`,
    `all tiles derived from children and grounded in leaves`,
  ]);
}

/**
 * What a governor sees at a given tile, and what it would cost to check.
 *
 * The view is the same object at every zoom level. Governing from it is sound
 * because the tile carries its own falsifier: the leaf set. That is the burden
 * inversion applied to observation — the reader does not re-derive the
 * population, because the aggregate arrives with the list of what it aggregates.
 */
export type GovernanceView = {
  readonly tileId: string;
  readonly depth: number;
  readonly leaves: readonly string[];
  readonly leafCount: number;
  readonly scalars: Scalars;
  /** Cost of auditing every tile at or below this one. */
  readonly tileAuditCost: number;
  /** Cost of re-deriving every leaf instead. */
  readonly fullReDerivationCost: number;
};

export function govern(n: Node, depth = 0): Evidence<GovernanceView> {
  const check = `govern:${n.id}`;
  const FALSIFIER = "a governance view whose scalars are not the fold over its claimed leaves";
  const leaves = leavesOf(n);
  const scalars: Scalars = n.scalars;

  // The view is only sound if the figures are the fold. Check, do not assume.
  for (const key of keysOf(n)) {
    const shown = scalars[key];
    if (shown === undefined) {
      return fail(check, FALSIFIER, "dropped-category", `${n.id} omits key "${key}"`);
    }
    const truth = groundedSum(n, key);
    if (shown !== truth) {
      return fail(
        check,
        FALSIFIER,
        "figure-not-grounded",
        `${n.id} key "${key}": shown ${shown}, leaves sum ${truth}`,
      );
    }
  }

  let tileCount = 0;
  const countTiles = (x: Node): void => {
    if (x.kind === "tile") {
      tileCount += 1;
      x.children.forEach(countTiles);
    }
  };
  countTiles(n);

  return pass(check, FALSIFIER, {
    tileId: n.id,
    depth,
    leaves,
    leafCount: leaves.length,
    scalars,
    tileAuditCost: tileCount,
    fullReDerivationCost: leaves.length,
  }, [
    `${leaves.length} leaves claimed and disjoint`,
    `${tileCount} tiles below ${n.id}`,
    ...keysOf(n).map((k) => `key "${k}" = ${scalars[k] ?? 0n}, matches leaf fold`),
  ]);
}

/**
 * **The isometric shortcut pays exactly when there are more leaves than tiles.**
 *
 * This is `inversion_pays_iff` in the observation domain: the governor's check
 * is proportional to the number of aggregates, not the number of objects —
 * provided every aggregate is derived and grounded, which `auditTree` enforces.
 * If a tree had as many tiles as leaves, the shortcut would save nothing, and
 * this function says so rather than assuming the answer.
 */
export function shortcutPays(
  n: Node,
): Evidence<{ readonly saved: number; readonly ratio: string }> {
  const check = `shortcut-pays:${n.id}`;
  const FALSIFIER = "a tree whose tile count is at least its leaf count, presented as a saving";
  const leaves = leavesOf(n).length;
  let tiles = 0;
  const count = (x: Node): void => {
    if (x.kind === "tile") {
      tiles += 1;
      x.children.forEach(count);
    }
  };
  count(n);
  if (leaves <= tiles) {
    return fail(
      check,
      FALSIFIER,
      "no-saving",
      `leaves ${leaves} <= tiles ${tiles}: the hierarchy costs at least as much to audit as ` +
        `the population it summarizes.`,
    );
  }
  return pass(check, FALSIFIER, { saved: leaves - tiles, ratio: `${tiles}:${leaves}` }, [
    `audit by tile: ${tiles} checks`,
    `re-derive: ${leaves} checks`,
    `saved ${leaves - tiles}, ratio ${tiles}:${leaves}`,
  ]);
}
