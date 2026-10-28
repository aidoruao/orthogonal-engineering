---
tags: [cage, local-model, binding, trust]
register: documentation
---

# cage — binding Python with TypeScript and Lean 4

The answer to "can Python be bound by TypeScript and Lean 4" is **yes, but only
the process and the gate, never the computation.** This package is that sentence
made executable.

## The three layers

```
  TypeScript  ──binds──>  the PROCESS
      │                   spawn, timeout, byte cap, nonce, schema, hash
      ▼
  Lean 4      ──binds──>  the GATE
      │                   what may leave; what may never leave
      ▼
  Python      ──is──>     an UNTRUSTED ORACLE
                          it may propose. it may not decide.
```

## Why the model may only propose

A proposal is a candidate for someone else to check. An admitted fact is
something a deterministic checker verified. Collapsing those is the original
failure this repository exists to invert — so the wire format keeps them apart
structurally: `Proposal` has no field a verdict could travel in, and
`L4_CAGE.lean#proposal_shape` proves it.

A hallucination cannot become a finding because **there is no wire type that
carries a finding.**

## What each layer buys, and what it does not

| Layer | Guarantee | Not guaranteed |
| :--- | :--- | :--- |
| TypeScript | The worker cannot hang, flood, crash, replay, or swap its binary without producing a stable rejection code | That the worker's output is true |
| Lean 4 | Nonce required, non-empty text, reason on every rejection, confidence inert, gate total, no verdict field | Anything about Python's behaviour |
| — | — | **What the network computes.** Unverified by design. |

## Use

```bash
# The gate alone, no model needed:
npm run build && node --test dist/test/*.test.js

# The real model through the cage:
node -e "
import('./dist/src/supervise.js').then(async ({runOnce}) => {
  const r = await runOnce(
    { workerPath: process.cwd()+'/worker/infer.py', timeoutMs: 240000,
      python: '/usr/bin/python3', cwd: '..' },
    { prompt: 'your prompt', maxNewTokens: 64 }, 1);
  console.log(r.ok ? r.proposal.text : r.rejection.code);
});"
```

## Verify

```bash
./verify.sh
```

Six steps: strict typecheck; 13 gate tests including real subprocess failures
(hang, flood, crash, replay, no output); the Lean proof; no `sorry` or
`native_decide`; exactly one Python file and it states its own untrusted status;
no verdict-shaped wire field.

## The honest state of the local model

Run live on 2026-10-27, the adapter echoed the prompt instead of answering it.
The binding worked; the model did not. That is recorded in
`../docs/TRUST_ASSUMPTIONS.md` §6 rather than smoothed over, because "the cage
works" and "the model is useful" are different claims and only the first is
currently true.
