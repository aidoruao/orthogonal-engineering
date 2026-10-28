/**
 * The cage protocol — what the Python worker is allowed to say, and nothing more.
 *
 * The model is not trusted. It is treated as a possibly-adversarial process that
 * can return anything at all: a verdict, a malformed object, a gigabyte of text,
 * a hang, a crash. Every one of those is a case the supervisor handles, and none
 * of them can reach the caller as a decision.
 *
 * The binding is three-layered, and each layer buys something different:
 *
 *   TypeScript binds the PROCESS. Spawn, protocol, timeout, output cap, schema
 *   validation, receipt. The worker cannot widen what it is allowed to say,
 *   because the supervisor only accepts one shape.
 *
 *   Lean binds the GATE. `L4_CAGE.lean` proves that no accepted proposal can be
 *   a verdict, that every rejection carries a reason, and that the admission
 *   function is total. Those are properties of the checker, not of the model.
 *
 *   Nothing binds the COMPUTATION. What the network computes inside Python is
 *   unverified and unverifiable by this design. That is why the model may only
 *   *propose*. A proposal is a candidate for someone else to check; it is never
 *   an admitted fact.
 *
 * The consequence is the whole point: a hallucination cannot become a finding,
 * because there is no wire type that carries a finding.
 */

/** Wire protocol version. Bumping this invalidates every recorded receipt. */
export const PROTOCOL_VERSION = "cage/1";

/** The only kind of message the worker may send back. */
export type WorkerMessage =
  | {
      readonly kind: "proposal";
      /** Must echo the request nonce, so a response cannot be replayed. */
      readonly nonce: string;
      /** The candidate text. Not a fact; a candidate. */
      readonly text: string;
      /** The worker's own confidence, which the gate records but never trusts. */
      readonly selfReportedConfidence: number;
    }
  | {
      readonly kind: "refusal";
      readonly nonce: string;
      readonly reason: string;
    }
  | {
      readonly kind: "error";
      readonly nonce: string;
      readonly detail: string;
    };

export type WorkerKind = WorkerMessage["kind"];

/**
 * Why a worker response was not admitted.
 *
 * Every code names a specific way the process could misbehave. A code with no
 * reachable fixture would be a comment, so `cage/test/gate.test.ts` requires
 * every one of these to be reachable.
 */
export type RejectionCode =
  | "not_json"
  | "not_an_object"
  | "unknown_kind"
  | "nonce_mismatch"
  | "text_empty"
  | "text_too_long"
  | "confidence_not_in_range"
  | "refusal_without_reason"
  | "error_reported"
  | "protocol_version_mismatch"
  | "response_too_large"
  | "timeout"
  | "worker_crashed"
  | "no_output";

export const REJECTION_CODES: readonly RejectionCode[] = [
  "not_json",
  "not_an_object",
  "unknown_kind",
  "nonce_mismatch",
  "text_empty",
  "text_too_long",
  "confidence_not_in_range",
  "refusal_without_reason",
  "error_reported",
  "protocol_version_mismatch",
  "response_too_large",
  "timeout",
  "worker_crashed",
  "no_output",
] as const;

/** The only shape that can leave the cage as accepted. */
export type Proposal = {
  readonly protocol: typeof PROTOCOL_VERSION;
  readonly nonce: string;
  readonly text: string;
  /** Recorded, never used for admission. */
  readonly selfReportedConfidence: number;
  /** Hash of the worker file that produced this, for the receipt. */
  readonly workerSha256: string;
};

export type Rejection = {
  readonly code: RejectionCode;
  readonly detail: string;
};

export type GateResult =
  | { readonly ok: true; readonly proposal: Proposal }
  | { readonly ok: false; readonly rejection: Rejection };

/** Maximum characters a proposal may carry. */
export const MAX_TEXT_CHARS = 4000;

/** Maximum bytes of worker stdout the supervisor will read. */
export const MAX_RESPONSE_BYTES = 64 * 1024;

/**
 * Admit or reject a decoded worker message.
 *
 * Pure and total: it takes the parsed value and the nonce it expects, and
 * returns exactly one outcome. `L4_CAGE.lean` proves this function's decisions
 * match its stated conditions, so the proof and the runtime cannot drift.
 */
export function admit(
  raw: unknown,
  expectedNonce: string,
  workerSha256: string,
): GateResult {
  if (typeof raw !== "object" || raw === null || Array.isArray(raw)) {
    return { ok: false, rejection: { code: "not_an_object", detail: "worker sent a non-object" } };
  }
  const record = raw as Readonly<Record<string, unknown>>;

  const version = record["protocol"];
  if (version !== undefined && version !== PROTOCOL_VERSION) {
    return {
      ok: false,
      rejection: {
        code: "protocol_version_mismatch",
        detail: `worker declared ${String(version)}, expected ${PROTOCOL_VERSION}`,
      },
    };
  }

  const nonce = record["nonce"];
  if (typeof nonce !== "string" || nonce !== expectedNonce) {
    return {
      ok: false,
      rejection: {
        code: "nonce_mismatch",
        detail: "response does not echo the request nonce, so it cannot be tied to this call",
      },
    };
  }

  const kind = record["kind"];
  if (kind === "refusal") {
    const reason = record["reason"];
    if (typeof reason !== "string" || reason.trim() === "") {
      return {
        ok: false,
        rejection: { code: "refusal_without_reason", detail: "a refusal must state why" },
      };
    }
    return { ok: false, rejection: { code: "refusal_without_reason", detail: reason } };
  }
  if (kind === "error") {
    const detail = record["detail"];
    return {
      ok: false,
      rejection: {
        code: "error_reported",
        detail: typeof detail === "string" ? detail : "worker reported an error",
      },
    };
  }
  if (kind !== "proposal") {
    return {
      ok: false,
      rejection: { code: "unknown_kind", detail: `unknown message kind "${String(kind)}"` },
    };
  }

  const text = record["text"];
  if (typeof text !== "string" || text.trim() === "") {
    return { ok: false, rejection: { code: "text_empty", detail: "proposal carries no text" } };
  }
  if (text.length > MAX_TEXT_CHARS) {
    return {
      ok: false,
      rejection: {
        code: "text_too_long",
        detail: `${String(text.length)} characters exceeds the ${String(MAX_TEXT_CHARS)} limit`,
      },
    };
  }

  const confidence = record["selfReportedConfidence"];
  if (
    typeof confidence !== "number" ||
    Number.isNaN(confidence) ||
    confidence < 0 ||
    confidence > 1
  ) {
    return {
      ok: false,
      rejection: {
        code: "confidence_not_in_range",
        detail: "self-reported confidence must be a number in [0, 1]",
      },
    };
  }

  return {
    ok: true,
    proposal: {
      protocol: PROTOCOL_VERSION,
      nonce: expectedNonce,
      text,
      selfReportedConfidence: confidence,
      workerSha256,
    },
  };
}

/** Deterministic one-line rendering of a rejection, for logs and tests. */
export function renderRejection(rejection: Rejection): string {
  return `${rejection.code}: ${rejection.detail}`;
}
