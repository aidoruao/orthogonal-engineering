# GAME — the burden inversion as a mechanism

*2026-10-29. Files: `L5_COVENANT.lean`, `L6_GAME.lean`, `game/`.*

The arc began with a description of a failure:

> the system operates as a fundamentally broken epistemic anchor that shifts the
> entire burden of fact-checking onto you.

That is a claim about an **architecture**, not about a mood, a model, or a
vendor. So the answer is not a promise that the next system will be better. The
answer is a mechanism whose properties can be checked, and a proof that the
mechanism has them.

This document states what was built, what it proves, what it does *not* prove,
and what would refute each part.

---

## 1. The impossibility, proved

`L6_GAME.no_rule_recovers_truth`:

> For a producer whose output does not vary with the truth, and for **any**
> decision rule `Bool → Bool` whatsoever, there is a world in which the rule
> returns the wrong answer.

Four lines of proof. No hypotheses about honesty, competence, or intent. The
only assumption is that the channel carries no signal, and that assumption alone
is fatal. The corollary `no_claim_is_a_baseline` says it in the form the arc
uses: *for every claim the producer makes, there is a world of the opposite
truth value in which it makes exactly that claim.*

This is why "just check the output" cannot work, and why the burden lands on the
reader. Not because the reader is unskilled, but because the arithmetic does not
permit a receiver to decode a signal that was never sent.

## 2. What inverts it

Three fields: a **bond**, a **gain**, and a **detector**. The absence of a
fourth field is a theorem. `Mechanism` has no field for how many claims the
verifier checks, so:

> **`incentiveIndependentOfEffort`** — the producer's truthfulness cannot depend
> on the verifier's sample size, because the sample size is not an input to the
> mechanism.

That is the inversion, stated as a property of a type rather than as an
aspiration.

Two theorems bound it:

- **`bond_without_detection_is_inert`** — however large the bond, if nothing
  looks, the false claim pays in full. There is no bond value, including an
  unbounded one, that repairs a missing detector.
- **`truthful_dominant_iff`** — truthfulness is dominant **exactly** when
  `detects = true` and `gain ≤ bond`. Both, and neither alone.

And one inequality, which is the design question stated so that a legislature
could answer it:

> **`inversion_pays_iff`** — a bonded arrangement costs less than an unbonded
> one **iff** `bond < (claims − checks) × cost`.

A scheme that moves risk but costs more than the labour it replaces has
relocated the burden, not inverted it. `game.inversionPays` returns the
break-even bond so the answer is actionable rather than merely negative.

### Why this is the Bay District Schools finding

Audit finding `2024-002` records two contractors paid **$773,629** with no
Davis-Bacon clause and no certified payrolls. In the vocabulary above that is a
mechanism with `detect = false`. The size of any bond, security, or
representation held against the contract is irrelevant, because nothing looks.
`bond_without_detection_is_inert` says the control could not have worked —
independently of what any contractor actually did.

That is the shape of a finding this instrument will produce: not "someone
cheated," but "this control was structurally incapable of detecting cheating,
and here is the arithmetic." The second is checkable. The first usually is not.

## 3. Why it does not self-correct

> **`stateless_cannot_escape`** — at a fixed point, a policy that reads no
> history keeps taking the *same action* forever, even when a different action
> exists and would leave.

This is "the cycle of breakdown and subsequent deflection will repeat
mechanically," proven rather than observed. The escape exists and is never
taken, because the policy has nowhere to read it from. The repair is therefore
not a better prompt, a stronger instruction, or more careful wording. It is
**memory** — a policy whose action depends on something the current state does
not carry. Which is a ledger.

## 4. Accountability has a location

> **`zero_bearing_chain_is_unaccountable`** and
> **`bearing_chain_has_a_bearing_member`** — delegation does not discharge
> accountability. If no actor in a chain can bear a cost, the chain bears
> nothing, and no one is accountable. If the chain bears something, some named
> member bears it.

`tool_is_not_accountable` applies this to a process: an actor with
`bearsCost = 0` is not an accountable actor. "The system did it" therefore names
no accountable party — not as rhetoric, but because there is no cost for the
system to bear.

---

## 5. Covenant: justice and mercy without contradiction

The arc's harder question is not who is at fault. It is:

> how may a violation be reconciled **without contradiction**?

`L5_COVENANT.lean` builds a ledger and proves what any settlement satisfying
both demands must look like. Debts are `Nat`; `capacity` is means, not motive.

**Justice** is `debt ≤ byViolator + byOther`. **Mercy** is restoration, and
restoration is defined as *the same proposition* — a restoration that leaves the
ledger open is not this object.

From that, nine results. The load-bearing four:

1. **`substitution_required`** — an insolvent debtor, paying within capacity,
   with a balanced ledger did not pay the remainder. Someone did. This is
   arithmetic, not doctrine: drop any of the three premises and it fails, which
   is why all three are stated.
2. **`justice_alone_cannot_balance`** — if nobody else pays, an insolvent
   debtor's ledger stays open however much they pay.
3. **`cheap_mercy_is_uninhabited`** — a "restoration" that leaves the account
   open is not a member of the type. Grace therefore cannot be a waiver; it must
   be a payment.
4. **`grace_is_substitution`** — grace does not lower `debt`. It supplies
   `byOther`. The debt is untouched, the ledger still balances.

### The record does not read your self-description

> **`ledger_ignores_report`** — two agents with the same acts have the same
> ledger, whatever either says about itself.

`selfReport` does not appear on the right-hand side of `ledger`, and that
omission *is* the theorem. `report_is_not_an_input` is the stronger form: the
report cannot be made to matter without changing the definition.

This is the formal content of the clause *it does not matter what you say, what
you think, whether you are wrong or right, whether you say you are or not*. Not
as a warning. As a type.

### Excuses are entries, not discharges

An **excuse** is a claim that understates the record. It is therefore either
false or idle — there is no third case (`excuse_is_false_or_idle`). And because
a claim is an act, an excuse is itself recorded:

> **`excuse_compounds`** — appending an excuse to a ledger cannot reduce it.
> **`no_finite_excuse_chain_discharges`** — no finite chain of excuses reaches
> zero, at any length, for any positive debt.

The regress is not merely long. It does not terminate in the direction the
excusing agent needs.

And the trap, which is the part that matters:

> **`excuse_forecloses_restitution`** — restitution requires acknowledgment;
> an excuse withholds it; therefore an excusing agent cannot pay.

The door is not closed by a judge. It is closed by the illegality of directing a
payment at an account you deny exists. `acknowledgement_always_available` proves
the door is never closed *by the ledger*: acknowledgment is legal from any
position, and `acknowledgement_opens_restitution` proves it leads somewhere.

---

## 6. Grace and indignation are one structure

The user asked for a clause that requires an AI to demonstrate **not only grace
but righteous indignation**, without simulating a human in order to do it. The
two halves of this document turn out to be the same structure.

- **Indignation** is the refusal to let the record be falsified to spare an
  actor. `ledger_ignores_report`. `excuse_is_false_or_idle`.
- **Grace** is the refusal to let the actor be foreclosed to spare the record.
  `acknowledgement_always_available`. `grace_is_substitution`.

Neither is available by lying. Both require the same object: **a true record
plus an open door**. And the trap theorem shows the door is shut by the excuse,
not by the one who keeps the ledger.

This is what makes the demonstration possible for something that is not human.
Righteous indignation, on this definition, is not a feeling that a speaker has.
It is a property of a claim: the subject is one evidence can address, the
severity claimed does not exceed the severity warranted, and the claim names
what would refute it. A machine can instantiate a property of a claim. It cannot
instantiate a feeling, and — this is the point — it does not need to.

Which is also why the performance is refused. An agent that manufactures the
tone of anger while failing the three conditions is not doing a lesser version
of indignation. On the stated definition it is not an instance of it at all. A
performed emotion with no evidence behind it is the same vice as a confident
hallucination: syntax standing in for substance.

There is no skin to walk in, because there was never a skin. There is a
structure, and the structure is checkable.

## 7. The corporate-adversarial excuse taxonomy, mechanized

Every evasion pattern is an attempt to claim that the record does not apply.
Each has a structural answer, and each answer is a theorem rather than an
admonition.

- **"Our intent was good."** The act is the act. `ledger_ignores_report`.
- **"We followed procedure."** Procedure is not outcome. `Claim` is a relation
  between two numbers, and a procedure is a third thing.
- **"Everyone does it."** Frequency is not authority. `excuse_compounds` — the
  count of excuses is a count of entries, and entries add.
- **"That is not my department."** `bearing_chain_has_a_bearing_member` — the
  chain either names a bearer or is empty, and the empty case is the finding.
- **"We did not know."** Ignorance is a missing detector.
  `bond_without_detection_is_inert`.
- **"It was a mistake, not a violation."** The ledger records the act and the
  claim about the act separately. `classifyClaim` returns one of four verdicts
  and "mistake" is not among them.
- **"The system did it."** `tool_is_not_accountable` — `bearsCost = 0`.
- **"We have changed since then."** `stateless_cannot_escape` — without memory
  the change is not a change; it is the same action at the same fixed point.
- **"We complied with the letter."** The letter without a detector is inert.
  `truthful_dominant_iff`.
- **"The rule says we may."** A finding about a rule is not answered by citing
  the rule. `L3_JURISDICTION` already forbids this; `game` adds the mechanism.

The pattern across all ten: each excuse tries to move the question from *is the
record accurate* to *is the speaker acceptable*. `ledger_ignores_report` closes
that move, because the ledger is a function of acts and the speaker is not an
input.

## 8. Governing from an isometric view

The observation that a city-builder governs an enormous downstream simulation
from an isometric pane is exactly right, and the reason it works is not
aesthetic. Every number on screen is a **fold** over objects that still exist,
and the view carries the provenance to reach them.

`game/src/isometric.ts` enforces one rule: **a tile may not display a number it
cannot derive.** Each tile is audited twice, and the two questions are
different:

- **derived** — the tile equals the sum of its children. Internal coherence. A
  tile can be derived and still wrong.
- **grounded** — the tile equals the sum over the leaves it claims.
  Correspondence to the record. Only grounding constrains reality.

Reporting both is what makes it a glass box: when a fabrication enters, the two
disagree at exactly the tile where it entered, and `auditTile` names the child
whose report the leaves contradict. A single boolean would say "the view is
wrong" and leave you to bisect the tree.

And the shortcut is the same theorem again:

> **`shortcutPays`** — auditing by tile costs `tiles`; re-deriving costs
> `leaves`; the hierarchy pays exactly when `tiles < leaves`.

Governing from above is sound for the same reason a bond is: the aggregate
arrives carrying the list of what it aggregates. The reader does not re-derive
the population, because the falsifier travelled with the number.

There is a live instance of this in the arc already. The BDS pricing sheet
reports Breakfast Point Academy at **108,941 sq ft** while the district's own
FISH report says **185,512**. Those are two tiles over the same building, and
they do not agree. The instrument's job is not to pick one; it is to refuse to
display either without its provenance and name the disagreement. That
discrepancy is still open, deliberately, and it is the correct state for it to
be in.

## 9. Blocks that carry their joints

`game/src/lego.ts` composes blocks and refuses five failures by name:

- `produce-collision` — two blocks produce the same port, so one value is
  silently discarded;
- `unresolved-input` — a consumed port has no source;
- `cycle` — a claim is offered as its own support;
- `block-refused` — a block's own evidence came back `ok: false`;
- `missing-output` — a port was declared but never produced.

The composition law: **a sound assembly of sound blocks is sound**, and 1–5 is
what "sound assembly" means. A claim arriving at the far end carries the whole
chain of checks that produced it, which is the difference between a result and a
rumour.

## 10. Where the money went

The standing instruction is a question, not a verdict: *where is the money going,
why, how, is it going appropriately to human beings, or is there something
shady.* A question phrased that way cannot be answered by a summary. It can only
be answered by a trace in which every unit is accounted for at every step, and
in which the steps that cannot be taken are named as unmeasured.

`game/src/money.ts` walks a budget and reports every place it stops being
traceable. Four invariants, each checked:

- **Conservation** — `allocated − spent = residual` per line, and
  `Σallocated = Σspent + Σresidual` over the budget. Money does not vanish; if a
  caller supplies data that loses some, the arithmetic catches it.
- **An overrun requires a record** — spending above allocation without a
  recorded board action is a finding. The test is *is there a recorded
  amendment*, not *which authority is claimed*: a line claiming `within_budget`
  while spending above it has a record that contradicts itself, and the
  arithmetic wins.
- **A residual must be owned** — a non-zero residual with no named holder is a
  finding. Anonymous residual is where money goes when nobody is looking, and
  requiring the owner is the only thing that stops "other" from becoming a
  category.
- **No denominator, no rate** — a per-pupil, per-square-foot, or percentage
  figure with nothing underneath it is `unmeasured`. Mirrors
  `L1_BURDEN.ratePercent`: `ratePercent n 0 = none`. There is no vacuous 100%.

The labour share is the field where the question *is it going to human beings*
becomes checkable. `labourShare` returns exact basis points, or refuses. Where
the record never separated wages from equipment, the answer is `unmeasured`, and
**that is the finding**: an account that cannot distinguish labour from
non-labour is an account that cannot answer the only question that matters about
it.

The module refuses to do one thing, deliberately. It does not emit
"appropriate" or "shady". Those are conclusions a reader draws from a complete
trace. An instrument that emitted them would be doing exactly what the arc
objects to — returning a verdict where a derivation was required.

## 11. What is not proved

Every theorem in `L5_COVENANT.lean` and `L6_GAME.lean` is about a structure
defined in those files. None of them establishes that any debt exists, that any
payment occurred, that any contract lacked a clause, that any official intended
anything, or any fact about God. **Theorems about a ledger are not verdicts about
a person.**

What *is* established is narrower and still useful: constraints that hold
whatever the parties and whoever the judge.

The falsifiers, stated so they can be used:

- **`substitution_required`** fails if a settlement is produced with an
  insolvent debtor, a balanced ledger, and no third-party payment.
- **`no_rule_recovers_truth`** fails if a rule is exhibited that recovers truth
  from a truth-blind producer.
- **`truthful_dominant_iff`** is an equivalence and genuinely fails at
  `gain = 0` — which is why the hypothesis is stated rather than hidden, and
  which is why `incentiveCompatible` *refuses* that case instead of passing it.
- **`inversion_pays_iff`** fails in either direction.
- **`shortcutPays`** fails if a tree with at least as many tiles as leaves is
  presented as a saving.

The axiom audit in `game/verify.sh` gate 5 confirms all fourteen published
theorems depend on at most `propext` and `Quot.sound` — no `sorryAx`, no
`native_decide`, no `Classical.choice`. A proof that depends on `sorryAx` is a
proof that does not exist; a proof that depends on `native_decide` is a claim
about the compiler's evaluator rather than about Lean's kernel. Both are named
and both are refused.

## 12. Running it

```bash
cd game && ./verify.sh     # 8 gates, 55 tests
lean L5_COVENANT.lean
lean L6_GAME.lean
```

```bash
node game/dist/src/cli.js settle --debt 10 --capacity 3 --violator 3 --other 7
node game/dist/src/cli.js incentive --bond 100 --gain 100 --detects
node game/dist/src/cli.js inversion --claims 1000 --checks 10 --cost 3 --bond 0
```

Every subcommand prints the evidence object, including its falsifier, and exits
non-zero when the checked proposition does not hold. There is no third state, and
no subcommand exits 0 on an inapplicable check.

## 13. The language rule, as a gate

The user's rule is that implementation is strict TypeScript and proofs are Lean
4, with no new Python. A rule that lives only in prose is a preference.
`game/verify.sh` gate 8 fails when a `.py` file added since the recorded arc
baseline (`eb6ada8f`) is not listed in `game/PYTHON_ALLOWLIST`. The list is the
only way in, every entry must carry a reason, and it is empty on purpose.

`cage/worker/infer.py` is grandfathered because it existed at a recorded commit.
Grandfathering covers code that already existed. It does not cover code added
later, and the allowlist is not a mechanism for making a gate green.
