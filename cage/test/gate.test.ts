/**
 * The gate's falsifiers, and one live test against the real worker.
 *
 * Every rejection code must be reachable by a fixture. A code with no fixture is
 * a comment; `L4_CAGE.lean` proves properties of the gate, these tests prove the
 * gate is the one that runs.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import {
  MAX_TEXT_CHARS,
  PROTOCOL_VERSION,
  REJECTION_CODES,
  admit,
  type RejectionCode,
} from "../src/protocol.js";
import { makeNonce, runOnce } from "../src/supervise.js";

const NONCE = "abc123";
const WORKER = "a".repeat(64);

function ok(extra: Record<string, unknown> = {}): unknown {
  return {
    protocol: PROTOCOL_VERSION,
    kind: "proposal",
    nonce: NONCE,
    text: "a candidate span",
    selfReportedConfidence: 0.5,
    ...extra,
  };
}

const FIXTURES: readonly { code: RejectionCode; make: () => unknown }[] = [
  { code: "not_an_object", make: () => "a string" },
  { code: "nonce_mismatch", make: () => ok({ nonce: "wrong" }) },
  { code: "text_empty", make: () => ok({ text: "  " }) },
  { code: "text_too_long", make: () => ok({ text: "x".repeat(MAX_TEXT_CHARS + 1) }) },
  { code: "confidence_not_in_range", make: () => ok({ selfReportedConfidence: 1.5 }) },
  { code: "unknown_kind", make: () => ok({ kind: "verdict" }) },
  { code: "refusal_without_reason", make: () => ({ kind: "refusal", nonce: NONCE, reason: "" }) },
  { code: "error_reported", make: () => ({ kind: "error", nonce: NONCE, detail: "boom" }) },
  { code: "protocol_version_mismatch", make: () => ok({ protocol: "cage/0" }) },
];

test("a well-formed proposal is admitted", () => {
  const result = admit(ok(), NONCE, WORKER);
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.proposal.text, "a candidate span");
    assert.equal(result.proposal.workerSha256, WORKER);
  }
});

test("every documented rejection code is reachable", () => {
  const reached = new Set<string>();
  for (const fixture of FIXTURES) {
    const result = admit(fixture.make(), NONCE, WORKER);
    assert.equal(result.ok, false, `${fixture.code}: was admitted`);
    if (!result.ok) {
      assert.equal(result.rejection.code, fixture.code, `wrong code for ${fixture.code}`);
      reached.add(result.rejection.code);
    }
  }
  // Codes only the supervisor can emit (timeout, crash, oversize, no output) are
  // reachable through `runOnce`, not through `admit`. Listed so the split is
  // explicit rather than an omission.
  const supervisorOnly = new Set(["timeout", "worker_crashed", "response_too_large", "no_output", "not_json"]);
  for (const code of REJECTION_CODES) {
    assert.ok(
      reached.has(code) || supervisorOnly.has(code),
      `${code} is neither fixture-reachable nor declared supervisor-only`,
    );
  }
});

test("a worker cannot smuggle a verdict through", () => {
  // There is no wire type for a decision. A worker that tries is rejected as an
  // unknown kind, which is the only thing the gate can do with it.
  for (const attempt of ["verdict", "admitted", "finding", "true", "ACCEPT"]) {
    const result = admit(ok({ kind: attempt }), NONCE, WORKER);
    assert.equal(result.ok, false, `"${attempt}" was admitted`);
  }
});

test("the confidence never decides admission", () => {
  for (const confidence of [0, 0.001, 0.5, 0.999, 1]) {
    const result = admit(ok({ selfReportedConfidence: confidence }), NONCE, WORKER);
    assert.equal(result.ok, true, `confidence ${String(confidence)} rejected`);
  }
});

test("a replay with a stale nonce is refused", () => {
  const result = admit(ok(), "different-nonce", WORKER);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "nonce_mismatch");
});

test("nonces are deterministic, so a receipt is reproducible", () => {
  assert.equal(makeNonce(1, "p"), makeNonce(1, "p"));
  assert.notEqual(makeNonce(1, "p"), makeNonce(2, "p"));
  assert.notEqual(makeNonce(1, "p"), makeNonce(1, "q"));
});

// --- The live binding -------------------------------------------------------
//
// Three synthetic workers exercise the process boundary without loading a model:
// a well-behaved one, a hanging one, and a crashing one. These are the failure
// modes a model actually exhibits, and each must become a Rejection rather than
// a throw.

const HERE = process.cwd();

async function workerWith(script: string, timeoutMs = 5000) {
  const { writeFileSync, mkdtempSync } = await import("node:fs");
  const { tmpdir } = await import("node:os");
  const { join } = await import("node:path");
  const dir = mkdtempSync(join(tmpdir(), "cage-test-"));
  const path = join(dir, "w.py");
  writeFileSync(path, script, "utf8");
  return { config: { workerPath: path, timeoutMs, python: "python3", cwd: HERE }, dir };
}

test("a well-behaved worker is admitted through the real process boundary", async () => {
  const { config } = await workerWith(`
import json, sys
req = json.loads(sys.stdin.read())
print(json.dumps({"protocol":"cage/1","kind":"proposal","nonce":req["nonce"],
                  "text":"from a real subprocess","selfReportedConfidence":0.0}))
`);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, true);
  if (result.ok) assert.equal(result.proposal.text, "from a real subprocess");
});

test("a worker that answers with prose instead of JSON is refused", async () => {
  const { config } = await workerWith(`print("I think the answer is 42")`);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "not_json");
});

test("a worker that hangs is killed and reported as a timeout", async () => {
  const { config } = await workerWith(`import time; time.sleep(60)`, 600);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "timeout");
});

test("a worker that echoes the wrong nonce is refused", async () => {
  const { config } = await workerWith(`
import json, sys
json.loads(sys.stdin.read())
print(json.dumps({"protocol":"cage/1","kind":"proposal","nonce":"replayed",
                  "text":"t","selfReportedConfidence":0.0}))
`);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "nonce_mismatch");
});

test("a worker that emits nothing is refused, not silently accepted", async () => {
  const { config } = await workerWith(`pass`);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "no_output");
});

test("a worker that floods stdout is killed", async () => {
  const { config } = await workerWith(`print("x" * 200000)`);
  const result = await runOnce(config, { prompt: "x", maxNewTokens: 1 }, 1);
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "response_too_large");
});

test("a missing worker file is a rejection, not a throw", async () => {
  const result = await runOnce(
    { workerPath: "/nonexistent/w.py", timeoutMs: 1000, python: "python3", cwd: HERE },
    { prompt: "x", maxNewTokens: 1 },
    1,
  );
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.rejection.code, "worker_crashed");
});
