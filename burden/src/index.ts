export {
  BEARINGS,
  CHECKABILITIES,
  CLAIM_ID_PATTERN,
  MAX_QUOTE_CHARS,
  MAX_SOURCE_BYTES,
  SCHEMA_ID,
  SHA256_PATTERN,
  SUPPORTED_TIERS,
  TIERS,
  TIER_RANK,
  UNSUPPORTED_TIERS,
  VERDICTS,
  VIOLATION_CODES,
  mayUpgrade,
  sortViolations,
} from "./types.js";
export type {
  Bearing,
  Checkability,
  DerivationStep,
  Environment,
  Falsifier,
  Holder,
  Owner,
  Receipt,
  SourceRef,
  Tier,
  ValidationResult,
  Verdict,
  VerdictRecord,
  Violation,
  ViolationCode,
} from "./types.js";

export { canonicalJson, sha256Hex, utcNow } from "./canonical.js";
export type { Json } from "./canonical.js";

export { captureEnvironment } from "./environment.js";

export {
  contractJson,
  describeContract,
  renderViolations,
  validateReceipt,
} from "./validate.js";
export type { CodeSpec, FieldSpec } from "./validate.js";

export {
  GENESIS,
  appendReceipt,
  computeEntrySha256,
  readLedger,
  verifyLedger,
} from "./ledger.js";
export type { LedgerEntry, LedgerFailure, LedgerRead, LedgerWriteResult } from "./ledger.js";

export { admitOrThrow, audit, composeReceipt, locateSpan, stripLineGutters } from "./audit.js";
export type { AuditInput, SpanFinding } from "./audit.js";

export { investigate } from "./investigate.js";
export type { InvestigateInput, Investigation } from "./investigate.js";

export { calibrate, renderCalibration } from "./calibrate.js";
export type { Calibration, TierStat } from "./calibrate.js";

export { RULES, explain, renderHits, scan, selfTest } from "./scan.js";
export type { Hit, ScanRule, SelfTestResult, Spiral } from "./scan.js";
