/**
 * The append-only verdict ledger.
 *
 * Each line is one entry: a receipt plus the hash of the entry before it. The
 * chain is the calibration substrate — a statistic recomputed from a chain
 * that cannot be quietly rewritten is a different kind of number than one
 * recomputed from memory.
 *
 * Appending to a broken ledger is refused. Repairing history is not a feature.
 */

import { appendFileSync, existsSync, readFileSync } from "node:fs";

import { canonicalJson, sha256Hex } from "./canonical.js";
import { SHA256_PATTERN, type Receipt } from "./types.js";
import { validateReceipt } from "./validate.js";

/** The hash before the first entry. 64 zeros, not a special case. */
export const GENESIS = "0".repeat(64);

export type LedgerEntry = {
  readonly seq: number;
  readonly recordedAtUtc: string;
  readonly prev: string;
  readonly receipt: Receipt;
  readonly entrySha256: string;
};

export type LedgerFailure = {
  readonly line: number;
  readonly code: string;
  readonly detail: string;
};

export type LedgerRead = {
  readonly entries: readonly LedgerEntry[];
  readonly failures: readonly LedgerFailure[];
};

/** The hash commits to the sequence number, the time, the predecessor, and
 *  the receipt — so reordering, backdating, and swapping are all detectable. */
export function computeEntrySha256(
  seq: number,
  recordedAtUtc: string,
  prev: string,
  receipt: Receipt,
): string {
  return sha256Hex(canonicalJson({ seq, recordedAtUtc, prev, receipt }));
}

function isRecord(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseEntry(
  raw: unknown,
  line: number,
  expectedSeq: number,
  expectedPrev: string,
): { readonly entry: LedgerEntry | null; readonly failure: LedgerFailure | null } {
  const fail = (code: string, detail: string): { entry: null; failure: LedgerFailure } => ({
    entry: null,
    failure: { line, code, detail },
  });

  if (!isRecord(raw)) return fail("LEDGER_ENTRY_NOT_OBJECT", "entry is not a JSON object");

  const seq = raw["seq"];
  if (typeof seq !== "number" || !Number.isInteger(seq) || seq !== expectedSeq) {
    return fail("LEDGER_SEQ_GAP", `expected seq ${expectedSeq}`);
  }

  const recordedAtUtc = raw["recordedAtUtc"];
  if (typeof recordedAtUtc !== "string" || Number.isNaN(Date.parse(recordedAtUtc))) {
    return fail("LEDGER_BAD_TIMESTAMP", "recordedAtUtc is not a parseable timestamp");
  }

  const prev = raw["prev"];
  if (typeof prev !== "string" || !SHA256_PATTERN.test(prev)) {
    return fail("LEDGER_BAD_PREV", "prev is not a SHA-256");
  }
  if (prev !== expectedPrev) {
    return fail("LEDGER_BROKEN_CHAIN", `prev does not match the previous entry hash`);
  }

  const entrySha256 = raw["entrySha256"];
  if (typeof entrySha256 !== "string" || !SHA256_PATTERN.test(entrySha256)) {
    return fail("LEDGER_BAD_HASH", "entrySha256 is not a SHA-256");
  }

  const admitted = validateReceipt(raw["receipt"]);
  if (!admitted.ok) {
    const first = admitted.violations[0];
    return fail(
      "LEDGER_BAD_RECEIPT",
      first === undefined
        ? "receipt rejected"
        : `${first.code} at ${first.path || "<root>"}: ${first.message}`,
    );
  }

  const recomputed = computeEntrySha256(seq, recordedAtUtc, prev, admitted.receipt);
  if (recomputed !== entrySha256) {
    return fail("LEDGER_HASH_MISMATCH", "entrySha256 does not commit to the entry contents");
  }

  return {
    entry: { seq, recordedAtUtc, prev, receipt: admitted.receipt, entrySha256 },
    failure: null,
  };
}

/**
 * Read and verify a ledger. A missing file is an empty ledger, not an error:
 * the first append creates it. Malformed lines are reported with their line
 * number and never skipped.
 */
export function readLedger(path: string): LedgerRead {
  if (!existsSync(path)) return { entries: [], failures: [] };

  const text = readFileSync(path, "utf8");
  const lines = text.split("\n");
  const entries: LedgerEntry[] = [];
  const failures: LedgerFailure[] = [];
  let prev = GENESIS;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line === undefined) continue;
    if (line.trim() === "") {
      // The newline that ends the file is not an entry. Any other blank line
      // is an anomaly and is reported, never stepped over.
      if (index === lines.length - 1) continue;
      failures.push({
        line: index + 1,
        code: "LEDGER_BLANK_LINE",
        detail: "interior blank line",
      });
      continue;
    }

    let parsed: unknown;
    try {
      const candidate: unknown = JSON.parse(line);
      parsed = candidate;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      failures.push({
        line: index + 1,
        code: "LEDGER_UNPARSEABLE",
        detail: message,
      });
      continue;
    }

    const result = parseEntry(parsed, index + 1, entries.length, prev);
    if (result.entry === null) {
      if (result.failure !== null) failures.push(result.failure);
      continue;
    }
    entries.push(result.entry);
    prev = result.entry.entrySha256;
  }

  return { entries, failures };
}

export type LedgerWriteResult =
  | { readonly ok: true; readonly entry: LedgerEntry }
  | { readonly ok: false; readonly failures: readonly LedgerFailure[] };

/** Append one receipt, refusing if the existing chain does not verify. */
export function appendReceipt(
  path: string,
  receipt: Receipt,
  recordedAtUtc: string,
): LedgerWriteResult {
  const existing = readLedger(path);
  if (existing.failures.length > 0) {
    return { ok: false, failures: existing.failures };
  }
  const last = existing.entries.at(-1);
  const seq = existing.entries.length;
  const prev = last === undefined ? GENESIS : last.entrySha256;
  const entrySha256 = computeEntrySha256(seq, recordedAtUtc, prev, receipt);
  const entry: LedgerEntry = { seq, recordedAtUtc, prev, receipt, entrySha256 };
  appendFileSync(path, `${canonicalJson(entry)}\n`, "utf8");
  return { ok: true, entry };
}

/**
 * Verify the chain. `expectedHead` anchors the last entry hash, which is the
 * only way to detect truncation of the tail: a hash chain alone proves
 * internal consistency, not that nothing was removed from the end.
 */
export function verifyLedger(
  path: string,
  expectedHead: string | null = null,
): {
  readonly ok: boolean;
  readonly entries: number;
  readonly failures: readonly LedgerFailure[];
} {
  const read = readLedger(path);
  const failures: LedgerFailure[] = [...read.failures];
  if (expectedHead !== null) {
    const last = read.entries.at(-1);
    if (last === undefined) {
      failures.push({
        line: 0,
        code: "LEDGER_HEAD_MISMATCH",
        detail: `a head of ${expectedHead} was expected but the ledger is empty`,
      });
    } else if (last.entrySha256 !== expectedHead) {
      failures.push({
        line: 0,
        code: "LEDGER_HEAD_MISMATCH",
        detail: `last entry hash ${last.entrySha256} does not match the expected head ${expectedHead}`,
      });
    }
  }
  return {
    ok: failures.length === 0,
    entries: read.entries.length,
    failures,
  };
}
