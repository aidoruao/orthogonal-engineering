/**
 * Canonical serialization and hashing.
 *
 * Determinism is a requirement, not a nicety: generated evidence must be
 * byte-identical across runs. That means sorted keys, no whitespace, no
 * locale-dependent ordering, no non-finite numbers, and an explicit refusal
 * of anything that JSON cannot represent.
 */

import { createHash } from "node:crypto";

export type Json =
  | string
  | number
  | boolean
  | null
  | readonly Json[]
  | { readonly [key: string]: Json };

function isJsonArray(value: Json): value is readonly Json[] {
  return Array.isArray(value);
}

function isJsonObject(value: Json): value is { readonly [key: string]: Json } {
  return typeof value === "object" && value !== null && !isJsonArray(value);
}

function render(value: Json): string {
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new Error(`canonicalJson: non-finite number ${String(value)}`);
    }
    return JSON.stringify(value);
  }
  if (isJsonArray(value)) {
    return `[${value.map(render).join(",")}]`;
  }
  if (isJsonObject(value)) {
    const entries = Object.entries(value).sort(([a], [b]) =>
      a < b ? -1 : a > b ? 1 : 0,
    );
    return `{${entries.map(([key, child]) => `${JSON.stringify(key)}:${render(child)}`).join(",")}}`;
  }
  // Unreachable for well-typed input; loud rather than silent.
  throw new Error("canonicalJson: value is not representable as JSON");
}

/** Sorted-key, whitespace-free JSON. Throws on non-JSON input. */
export function canonicalJson(value: Json): string {
  return render(value);
}

/** SHA-256 of a string (UTF-8) or raw bytes, lowercase hex. */
export function sha256Hex(input: string | Uint8Array): string {
  return createHash("sha256").update(input).digest("hex");
}

/** UTC ISO-8601 with milliseconds — the only timestamp format we emit. */
export function utcNow(): string {
  return new Date().toISOString();
}
