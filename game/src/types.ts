/**
 * game — core types.
 *
 * One rule governs this package and it is the rule the whole arc is about:
 *
 *   **An invariant-bearing function returns evidence, never a bare boolean.**
 *
 * A `boolean` is a claim with no content. `true` does not say what was checked,
 * against what, on what input, or what would have made it false. A caller that
 * receives `false` learns nothing it can act on, and a caller that receives
 * `true` learns nothing it can cite. Both are exactly the failure the arc
 * documents: a confident verdict with no derivation attached.
 *
 * `Evidence<T>` is therefore a discriminated union that carries the check's
 * name and the falsifier in *both* branches. The falsifier is not decoration.
 * A check that cannot state what would refute it is not a check; it is a
 * comment that costs CPU.
 *
 * Money and debt are `bigint`, in whole cents where the subject is currency
 * and in whole units where the subject is a ledger. Floating point is not used
 * anywhere in this package, because `0.1 + 0.2 !== 0.3` is the smallest
 * possible instance of a number that does not mean what it says.
 */

/** Money and debts are exact integers. Never `number`. */
export type Units = bigint;

/**
 * The result of a check.
 *
 * - `check` names what was tested, so a failure is locatable.
 * - `falsifier` states what would refute the invariant, in both branches, so
 *   the claim is bounded before it is made.
 * - the failure branch carries `failed` (a stable machine-readable code) and
 *   `detail` (the numbers that disagreed), so no failure is ever silent and
 *   none requires a debugger to interpret.
 */
export type Evidence<T> =
  | {
      readonly ok: true;
      readonly check: string;
      readonly falsifier: string;
      readonly value: T;
      /** The steps actually performed, in order. Empty is a defect. */
      readonly derivation: readonly string[];
    }
  | {
      readonly ok: false;
      readonly check: string;
      readonly falsifier: string;
      readonly failed: string;
      readonly detail: string;
    };

/** A passed check, carrying the work that was done to pass it. */
export function pass<T>(
  check: string,
  falsifier: string,
  value: T,
  derivation: readonly string[],
): Evidence<T> {
  if (derivation.length === 0) {
    throw new Error(
      `pass("${check}") with an empty derivation: a check records the steps it performed, ` +
        `or it is not a check.`,
    );
  }
  return { ok: true, check, falsifier, value, derivation };
}

/** A failed check. The detail is required, not optional. */
export function fail<T>(
  check: string,
  falsifier: string,
  failed: string,
  detail: string,
): Evidence<T> {
  return { ok: false, check, falsifier, failed, detail };
}

/** Unwrap or throw, for call sites that cannot continue past a failure. */
export function expect<T>(e: Evidence<T>, context: string): T {
  if (!e.ok) {
    throw new Error(`${context}: ${e.check} failed (${e.failed}): ${e.detail}`);
  }
  return e.value;
}

/** Render evidence for a human. Used by the CLI and by test failure output. */
export function render(e: Evidence<unknown>): string {
  if (e.ok) {
    const steps = e.derivation.map((s) => `    - ${s}`).join("\n");
    return `PASS ${e.check}\n  falsified if: ${e.falsifier}\n${steps}`;
  }
  return `FAIL ${e.check}\n  code: ${e.failed}\n  detail: ${e.detail}\n  falsified if: ${e.falsifier}`;
}

/**
 * A source commitment. Same discipline as `burden/` and `bds/`: a claim about
 * bytes is worth what its hash is worth.
 */
export type Source = {
  readonly path: string;
  readonly sha256: string;
  readonly bytes: number;
};

/**
 * A named falsifier attached to a published figure. Every number this package
 * emits is accompanied by one, because a number without one is unfalsifiable
 * and therefore not a measurement.
 */
export type FalsifiedBy = {
  readonly figure: string;
  readonly wouldRefute: string;
  readonly measurement: string;
};
