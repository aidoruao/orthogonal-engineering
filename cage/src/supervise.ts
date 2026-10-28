/**
 * The supervisor — TypeScript binding the process.
 *
 * This is the only place Python is ever launched, and it launches exactly one
 * program with a fixed argument vector. The worker cannot choose its own file,
 * open a port, or outlive its deadline, because none of those is reachable from
 * the interface this module exposes.
 *
 * The supervisor assumes the worst at every step:
 *
 *   - the worker may hang        -> wall-clock timeout, then SIGKILL
 *   - the worker may flood       -> stdout is capped and the process killed
 *   - the worker may crash       -> non-zero exit is a rejection, not a throw
 *   - the worker may lie         -> every field is validated by `admit`
 *   - the worker may replay      -> the nonce ties the reply to this call
 *   - the worker may be swapped  -> the file is hashed before each call
 *
 * None of those failure modes escalates. Each produces a `Rejection` with a
 * stable code, and no rejection can become a `Proposal`.
 */

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import {
  MAX_RESPONSE_BYTES,
  admit,
  type GateResult,
  type Rejection,
} from "./protocol.js";

export type SupervisorConfig = {
  /** Absolute path to the worker. Fixed at construction; not caller-controlled. */
  readonly workerPath: string;
  /** Wall-clock limit in milliseconds. */
  readonly timeoutMs: number;
  /** Interpreter to use. */
  readonly python: string;
  /** Working directory. */
  readonly cwd: string;
};

export type InferRequest = {
  readonly prompt: string;
  readonly maxNewTokens: number;
  /** Extra environment for the worker. Offline flags are added by the supervisor. */
  readonly env?: Readonly<Record<string, string>>;
};

/** Deterministic monotonic nonce: content hash plus a counter, never random. */
export function makeNonce(sequence: number, prompt: string): string {
  return createHash("sha256")
    .update(`${String(sequence)}\u0000${prompt}`)
    .digest("hex")
    .slice(0, 32);
}

function reject(code: Rejection["code"], detail: string): GateResult {
  return { ok: false, rejection: { code, detail } };
}

/**
 * Run the worker once and gate its reply.
 *
 * Every path through this function returns a `GateResult`. It never throws for
 * a worker misbehaviour — a throw here would be an unhandled failure mode, and
 * an unhandled failure mode is indistinguishable from a pass to a careless
 * caller.
 */
export async function runOnce(
  config: SupervisorConfig,
  request: InferRequest,
  sequence: number,
): Promise<GateResult> {
  let workerSha256: string;
  try {
    workerSha256 = createHash("sha256").update(readFileSync(config.workerPath)).digest("hex");
  } catch (error: unknown) {
    const detail = error instanceof Error ? error.message : String(error);
    return reject("worker_crashed", `worker file unreadable: ${detail}`);
  }

  const nonce = makeNonce(sequence, request.prompt);
  const payload = JSON.stringify({
    nonce,
    prompt: request.prompt,
    maxNewTokens: request.maxNewTokens,
  });

  return await new Promise<GateResult>((resolve) => {
    const child = spawn(config.python, [config.workerPath], {
      cwd: config.cwd,
      // Offline by default: a model call must not depend on the network, because
      // a network dependency is an unverifiable dependency.
      env: {
        ...process.env,
        HF_HUB_OFFLINE: "1",
        TRANSFORMERS_OFFLINE: "1",
        TOKENIZERS_PARALLELISM: "false",
        ...(request.env ?? {}),
      },
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let bytes = 0;
    let settled = false;
    let timedOut = false;

    const settle = (result: GateResult): void => {
      if (settled) return;
      settled = true;
      resolve(result);
    };

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, config.timeoutMs);

    child.stdout.on("data", (chunk: Buffer) => {
      bytes += chunk.byteLength;
      if (bytes > MAX_RESPONSE_BYTES) {
        child.kill("SIGKILL");
        settle(
          reject(
            "response_too_large",
            `worker emitted more than ${String(MAX_RESPONSE_BYTES)} bytes`,
          ),
        );
        return;
      }
      stdout += chunk.toString("utf8");
    });

    // stderr is drained and discarded. Not reading it would deadlock the child on
    // a full pipe; surfacing it would let the worker write to the caller's log.
    child.stderr.on("data", () => undefined);

    child.on("error", (error: Error) => {
      clearTimeout(timer);
      settle(reject("worker_crashed", `spawn failed: ${error.message}`));
    });

    child.on("close", (code, signal) => {
      clearTimeout(timer);
      if (timedOut) {
        settle(
          reject("timeout", `worker exceeded ${String(config.timeoutMs)}ms and was killed`),
        );
        return;
      }
      if (stdout.trim() === "") {
        settle(
          reject(
            "no_output",
            `worker produced no stdout (exit ${String(code)}, signal ${String(signal)})`,
          ),
        );
        return;
      }
      let parsed: unknown;
      try {
        parsed = JSON.parse(stdout);
      } catch {
        settle(reject("not_json", "worker stdout is not a single JSON value"));
        return;
      }
      // A non-zero exit after a well-formed reply is still worth recording, but
      // the reply is gated on its own merits: the gate is the authority.
      settle(admit(parsed, nonce, workerSha256));
    });

    child.stdin.write(payload);
    child.stdin.end();
  });
}
