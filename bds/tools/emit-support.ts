/**
 * Re-exports for the jurisdiction emitter.
 *
 * The emitter must read the *built* gate, and it must not carry its own copy of
 * the severity weights — a copy could drift from the one the gate uses, and the
 * whole point of the generated table is that it records what the real gate did.
 */

export { SEVERITY_WEIGHT, admissible } from "../src/types.js";
export type { Severity } from "../src/types.js";

/** The evidence tier union, re-exported under a name the emitter can use. */
export type Evidence2 =
  | "unmeasured"
  | "located_blocked"
  | "corroborated"
  | "fetched"
  | "retired";
