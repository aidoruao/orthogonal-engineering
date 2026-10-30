/**
 * game/lego — composition, with the joints checked.
 *
 * The user's image is the right one: a set of blocks that snap together. The
 * reason a toy brick set works is not that the bricks are individually good. It
 * is that the *interface* is exact — one stud, one tube, no ambiguity — so any
 * assembly you can physically build is an assembly that holds.
 *
 * That is a type system plus a runtime witness, and this module supplies the
 * runtime half. A `Block` declares what it consumes and what it produces; an
 * `Assembly` is accepted only when:
 *
 * 1. no two blocks produce the same port — no silent shadowing;
 * 2. every consumed port is either supplied up front or produced by a block —
 *    no undefined dependency;
 * 3. the dependency graph has no cycle — no self-supporting claim;
 * 4. every block's own `run` returns evidence, and the evidence is `ok`;
 * 5. every port declared as a final output is actually produced.
 *
 * The composition law is that a sound assembly of sound blocks is sound, and
 * conditions 1–5 are exactly what "sound assembly" means. A claim that arrives
 * at the far end of an assembly carries the whole chain of checks that produced
 * it, which is the difference between a result and a rumour.
 */

import { fail, pass, type Evidence } from "./types.js";

/** The value flowing along a port. Deliberately opaque: ports are not typed by content here. */
export type PortValue = unknown;

export type Block = {
  readonly id: string;
  readonly consumes: readonly string[];
  readonly produces: readonly string[];
  readonly run: (
    inputs: ReadonlyMap<string, PortValue>,
  ) => Evidence<ReadonlyMap<string, PortValue>>;
};

export type AssemblyReport = {
  /** The order that was actually executed. */
  readonly order: readonly string[];
  /** What each block returned, for inspection. */
  readonly evidence: ReadonlyMap<string, string>;
  readonly outputs: ReadonlyMap<string, PortValue>;
};

const ASSEMBLY_FALSIFIER =
  "an assembly accepted here in which some output is not traceable to a stated input through blocks that all returned ok";

/**
 * Compose blocks and prove it.
 *
 * Failure modes are named, because "the assembly failed" is not a finding. A
 * caller that receives `produce-collision` knows a port was shadowed; a caller
 * that receives `unresolved-input` knows which port had no source.
 */
export function assemble(
  blocks: readonly Block[],
  inputs: ReadonlyMap<string, PortValue>,
  requiredOutputs: readonly string[],
): Evidence<AssemblyReport> {
  const check = "assemble";

  // 1. No two blocks may produce the same port.
  const producer = new Map<string, string>();
  for (const b of blocks) {
    for (const p of b.produces) {
      const prior = producer.get(p);
      if (prior !== undefined) {
        return fail(
          check,
          ASSEMBLY_FALSIFIER,
          "produce-collision",
          `port "${p}" is produced by both "${prior}" and "${b.id}". A shadowed output ` +
            `means one of the two values is silently discarded.`,
        );
      }
      producer.set(p, b.id);
    }
  }

  // 2. Every consumed port must have a source.
  for (const b of blocks) {
    for (const p of b.consumes) {
      if (!inputs.has(p) && !producer.has(p)) {
        return fail(
          check,
          ASSEMBLY_FALSIFIER,
          "unresolved-input",
          `block "${b.id}" consumes "${p}", which is neither supplied nor produced.`,
        );
      }
    }
  }

  // 3. Resolve an order; a cycle means the claim supports itself.
  const order: string[] = [];
  const done = new Set<string>();
  const available = new Set<string>(inputs.keys());
  const remaining = new Map(blocks.map((b) => [b.id, b] as const));
  let progress = true;
  while (remaining.size > 0 && progress) {
    progress = false;
    for (const [id, b] of [...remaining]) {
      if (b.consumes.every((p) => available.has(p))) {
        order.push(id);
        for (const p of b.produces) available.add(p);
        remaining.delete(id);
        done.add(id);
        progress = true;
      }
    }
  }
  if (remaining.size > 0) {
    return fail(
      check,
      ASSEMBLY_FALSIFIER,
      "cycle",
      `blocks could not be ordered: ${[...remaining.keys()].join(", ")}. ` +
        `A dependency cycle means some claim is offered as its own support.`,
    );
  }

  // 4. Run every block, in order, refusing the first non-ok evidence.
  const values = new Map<string, PortValue>(inputs);
  const evidenceLog = new Map<string, string>();
  for (const id of order) {
    const b = remaining.get(id) ?? blocks.find((x) => x.id === id);
    if (b === undefined) {
      return fail(check, ASSEMBLY_FALSIFIER, "lost-block", `block "${id}" vanished from the plan`);
    }
    const given = new Map<string, PortValue>();
    for (const p of b.consumes) {
      if (values.has(p)) given.set(p, values.get(p));
    }
    const out = b.run(given);
    if (!out.ok) {
      return fail(
        check,
        ASSEMBLY_FALSIFIER,
        "block-refused",
        `block "${b.id}" refused at ${out.check}: ${out.failed} — ${out.detail}`,
      );
    }
    evidenceLog.set(b.id, `${out.check}: ok (${out.derivation.length} steps)`);
    for (const [k, v] of out.value) values.set(k, v);
  }

  // 5. Every required output must exist.
  const outputs = new Map<string, PortValue>();
  for (const p of requiredOutputs) {
    if (!values.has(p)) {
      return fail(
        check,
        ASSEMBLY_FALSIFIER,
        "missing-output",
        `required output "${p}" is not present after execution. Declared is not produced.`,
      );
    }
    outputs.set(p, values.get(p));
  }

  return pass(check, ASSEMBLY_FALSIFIER, { order, evidence: evidenceLog, outputs }, [
    `${blocks.length} blocks, ${order.length} ordered without cycle`,
    `no port produced twice`,
    `every consumed port resolved`,
    ...order.map((id) => `ran ${id}`),
    `${requiredOutputs.length} required outputs present`,
  ]);
}
