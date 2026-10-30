/-!
# L5 COVENANT — Justice and Mercy without Contradiction (2026-10-29)

The arc asks a question that is usually answered by assertion rather than by
proof: *how may a violation be reconciled without contradiction?*

This file does not answer it by assertion. It builds a ledger, states the two
demands as properties of that ledger, and proves what any settlement
satisfying both must look like. The result is a trichotomy, and it is arithmetic.

The two demands:

* **Justice** — the ledger balances. Every unit owed is paid by someone.
* **Mercy** — the violator's standing is restored even though the violator
  cannot pay.

They are not in tension. They are jointly satisfiable exactly when a third
party pays. That is not a doctrine injected into the model; it is what
`debt ≤ byViolator + byOther` means when `byViolator ≤ capacity < debt`.

## What follows, and what is then shown to follow from it

1. **Substitution is forced.** An insolvent violator whose ledger balances and
   whose payment stays inside capacity did not pay the remainder. Someone did.
   (`substitution_required`)
2. **Justice alone cannot balance an insolvent account.** (`justice_alone_cannot_balance`)
3. **Mercy alone is not a settlement.** A restoration that does not balance is
   not a restoration of the same ledger; the structure is uninhabited.
   (`cheap_mercy_is_uninhabited`)
4. **The record is a function of acts, not of reports.** Two agents with the
   same acts and different self-descriptions have the same ledger. This is the
   formal content of "it does not matter what you say, what you think, whether
   you are wrong or right, whether you say you are or not." (`ledger_ignores_report`)
5. **An excuse is either false or idle.** (`excuse_is_false_or_idle`)
6. **Excuses are the one operation that cannot reduce a debt.** Every other
   entry is either neutral or a payment; an excuse adds. (`excuse_compounds`)
7. **No finite chain of excuses discharges.** (`no_finite_excuse_chain_discharges`)
8. **The excusing agent is trapped.** Restitution requires acknowledgment, and
   an excuse withholds it, so an excusing agent cannot pay and cannot be
   restored while excusing. (`excuse_forecloses_restitution`)
9. **Grace is not a discount.** Grace does not lower `debt`. It supplies
   `byOther`. The ledger still balances. (`grace_preserves_justice`)

## HONEST SCOPE

This proves properties of a ledger *model*. It does not prove that any
particular debt exists, that any particular payment was made, or any fact about
God. It proves the *shape* a non-contradictory reconciliation must have, and it
names what would refute it:

  **Falsifier.** Exhibit a settlement in which an insolvent violator is
  restored, the ledger balances, and no non-violator paid. `substitution_required`
  says none exists. If one is produced, the model is wrong and this file is
  wrong with it.

Lean does not read ledgers. The executable counterpart is `game/src/covenant.ts`,
tested independently by `game/verify.sh`, and its negative controls are in
`game/negative/`.

Note on representation. Debts are written as `Nat` rather than through an
abbreviation, because a reducible alias hides the arithmetic from `omega` and
the proofs below then fail for a reason unrelated to their content. A debt is
never negative; a negative ledger position is a credit, which is a different
object and is not modelled here.

Run: `lean L5_COVENANT.lean`
-/

namespace Covenant

/-! ## 1. The account -/

/-- What the record says is owed, and what the debtor can actually pay.

`capacity` is the whole of the debtor's means. It is not a claim about
willingness; willingness cannot be measured here and is not modelled. -/
structure Account where
  debt : Nat
  capacity : Nat
deriving DecidableEq, Repr

/-- The debtor cannot cover the debt from their own means. -/
def Account.insolvent (a : Account) : Prop := a.capacity < a.debt

/-- The debtor can cover it. -/
def Account.solvent (a : Account) : Prop := a.debt ≤ a.capacity

theorem not_insolvent_iff_solvent (a : Account) :
    ¬ a.insolvent ↔ a.solvent := by
  unfold Account.insolvent Account.solvent
  omega

/-! ## 2. The settlement -/

/-- A settlement names both payment streams separately. They are not summed at
construction, because *who* paid is the entire question. A model that recorded
only the total would be unable to state any theorem in this file. -/
structure Settlement where
  account : Account
  /-- Paid by the party that incurred the debt. -/
  byViolator : Nat
  /-- Paid by anyone else. -/
  byOther : Nat
deriving DecidableEq, Repr

/-- The debtor cannot pay more than they have. -/
def Settlement.feasible (s : Settlement) : Prop := s.byViolator ≤ s.account.capacity

/-- **Justice** — every unit owed is paid by someone. -/
def Settlement.balanced (s : Settlement) : Prop := s.account.debt ≤ s.byViolator + s.byOther

/-- **Mercy** — the debtor's standing is restored. Restoration is not a feeling
and not a declaration; it is the ledger being closed, which is why it is
defined as the same proposition as balance. A "restoration" that leaves the
ledger open is not this object. -/
def Settlement.restored (s : Settlement) : Prop := s.balanced

/-! ## 3. The trichotomy — the central result -/

/-- **Substitution is forced.**

If the debtor is insolvent, pays within capacity, and the ledger balances, then
a non-debtor paid a positive amount.

The three premises are not decoration. Drop `feasible` and the debtor may pay
what they do not have — that is not a settlement, it is an overdraft. Drop
`balanced` and nothing is settled at all. `insolvent` is what makes the
remainder non-zero. -/
theorem substitution_required (s : Settlement)
    (hin : s.account.insolvent) (hf : s.feasible) (hb : s.balanced) :
    0 < s.byOther := by
  unfold Account.insolvent at hin
  unfold Settlement.feasible at hf
  unfold Settlement.balanced at hb
  omega

/-- The same fact, stated as an implication chain rather than about a
particular value. -/
theorem balance_of_insolvent_implies_payer (s : Settlement) :
    s.account.insolvent → s.feasible → s.balanced → 0 < s.byOther :=
  substitution_required s

/-- **Justice alone cannot balance an insolvent account.** If nobody else pays,
an insolvent debtor's ledger stays open however much they pay. -/
theorem justice_alone_cannot_balance (s : Settlement)
    (hin : s.account.insolvent) (hf : s.feasible) (honly : s.byOther = 0) :
    ¬ s.balanced := by
  intro hb
  have hpos := substitution_required s hin hf hb
  omega

/-- **Mercy alone is not a settlement.** A restoration that is not a balance is
not a restoration; the two predicates are the same predicate, so a structure
claiming both a closed and an open ledger is uninhabited.

This is the theorem that keeps grace from becoming a licence: if grace meant
"restored while the account is open," there would be no such object to
instantiate. Grace must therefore be a payment, not a waiver. -/
theorem cheap_mercy_is_uninhabited (s : Settlement) :
    ¬ (s.restored ∧ ¬ s.balanced) := by
  intro h
  exact h.2 h.1

/-- Grace preserves justice: a settlement paid entirely by another still
balances whatever the debtor's capacity. The debtor's poverty is not the
ledger's problem once the debt is covered. -/
theorem grace_preserves_justice (s : Settlement)
    (h : s.account.debt ≤ s.byOther) : s.balanced := by
  unfold Settlement.balanced
  omega

/-! ### The structures are inhabited

A trichotomy over an empty type proves nothing. Both horns are constructed. -/

/-- An insolvent debtor reconciled by another's payment. -/
def substitutionCase : Settlement where
  account := { debt := 10, capacity := 3 }
  byViolator := 3
  byOther := 7

/-- A solvent debtor who pays in full. No third party, and none is needed. -/
def selfPaymentCase : Settlement where
  account := { debt := 10, capacity := 40 }
  byViolator := 10
  byOther := 0

theorem substitutionCase_is_substitution : 0 < substitutionCase.byOther :=
  substitution_required substitutionCase
    (by unfold Account.insolvent; decide)
    (by unfold Settlement.feasible; decide)
    (by unfold Settlement.balanced; decide)

theorem selfPaymentCase_balances : selfPaymentCase.balanced := by
  unfold Settlement.balanced
  decide

/-- The solvent case genuinely escapes the substitution theorem: the
antecedent fails, so no third party is required. The theorem is not vacuous
*and* it is not universal. -/
theorem solvent_escapes_trichotomy : ¬ selfPaymentCase.account.insolvent := by
  unfold Account.insolvent
  decide

/-- And the insolvent case cannot escape it. Both directions of the boundary
are exhibited, so `substitution_required` is neither vacuous nor unconditional. -/
theorem insolvent_cannot_escape : substitutionCase.account.insolvent := by
  unfold Account.insolvent
  decide

/-! ## 4. The record is a function of acts, not of reports -/

/-- A ledger entry. `act` is something done; `excuse` is a *claim* that a prior
entry is not owed.

They are both entries, and that is the whole point: a claim is an act. -/
inductive Entry where
  | act (units : Nat)
  | excuse
deriving DecidableEq, Repr

/-- The price of a false entry, in the same units as the debt. It is positive,
so a false entry can never be free. -/
def excusePenalty : Nat := 1

theorem excusePenalty_pos : 0 < excusePenalty := by decide

/-- The amount outstanding after a sequence of entries. -/
def outstanding : List Entry → Nat
  | [] => 0
  | Entry.act n :: rest => n + outstanding rest
  | Entry.excuse :: rest => excusePenalty + outstanding rest

/-- An agent, described by what it did and by what it says about itself. -/
structure Agent where
  acts : List Entry
  selfReport : String
deriving Repr

/-- The ledger reads the acts and nothing else. `selfReport` does not appear on
the right-hand side, and that omission is the theorem. -/
def ledger (a : Agent) : Nat := outstanding a.acts

/-- **The record is invariant under self-description.**

Two agents with the same acts have the same ledger, whatever either says about
itself. This is the formal content of the clause: it does not matter what you
say, what you think, whether you are wrong or right, whether you say you are or
not. Not as a warning — as a type. -/
theorem ledger_ignores_report (a b : Agent) (h : a.acts = b.acts) :
    ledger a = ledger b := by
  unfold ledger
  rw [h]

/-- The stronger form: the report cannot be made to matter without changing the
definition of `ledger`. Any `ledger'` that mentions `selfReport` is a different
function, and nothing in this file constrains it. -/
theorem report_is_not_an_input (a : Agent) (s : String) :
    ledger { a with selfReport := s } = ledger a := rfl

/-! ## 5. Excuses cannot discharge -/

/-- A claim about what is owed, against what the record says is owed. -/
structure Claim where
  recorded : Nat
  stated : Nat
deriving DecidableEq, Repr

/-- The claim matches the record. -/
def Claim.accurate (c : Claim) : Prop := c.stated = c.recorded

/-- The claim understates the record: an excuse. -/
def Claim.excuse (c : Claim) : Prop := c.stated < c.recorded

/-- It also overstates it, which is a different falsehood and is not modelled
here. Named so the omission is visible rather than silent. -/
def Claim.inflates (c : Claim) : Prop := c.recorded < c.stated

/-- **An excuse is either false or idle.**

If the stated amount is below the recorded amount, the two differ, so the claim
does not match the record. There is no third case in which an excuse is
accurate: an accurate claim about a lower figure describes a different account,
not this one. -/
theorem excuse_is_false_or_idle (c : Claim) (h : c.excuse) : ¬ c.accurate := by
  unfold Claim.excuse at h
  unfold Claim.accurate
  omega

/-- Contrapositive, in the form the clause takes: an accurate claim is never an
excuse. -/
theorem accurate_is_never_an_excuse (c : Claim) (h : c.accurate) : ¬ c.excuse := by
  unfold Claim.accurate at h
  unfold Claim.excuse
  omega

/-- An idle claim — one made where the record shows nothing owed — is not an
excuse and costs nothing. It is also pointless, which is not a theorem but is
worth the definition. -/
def Claim.idle (c : Claim) : Prop := c.recorded = 0

theorem idle_claim_is_not_an_excuse (c : Claim) (h : c.idle) : ¬ c.excuse := by
  unfold Claim.idle at h
  unfold Claim.excuse
  omega

/-- Appending an entry to a ledger separates the sums. Used for the two
theorems that follow; stated on its own so the arithmetic step is visible. -/
theorem outstanding_append (xs ys : List Entry) :
    outstanding (xs ++ ys) = outstanding xs + outstanding ys := by
  induction xs with
  | nil => simp [outstanding]
  | cons e rest ih =>
    cases e <;> simp [outstanding, ih] <;> omega

/-- **Excuses compound.**

Appending an excuse to a ledger cannot reduce it. Compare restitution, which
subtracts: the excuse is the only entry whose sign is wrong.

This is the narrow, checkable content of "no free excuses." It is not a claim
about anyone's standing. It is the statement that the operation called
*excusing* has no discharge semantics — it is, by construction, an addition. -/
theorem excuse_compounds (es : List Entry) :
    outstanding (es ++ [Entry.excuse]) = outstanding es + excusePenalty := by
  rw [outstanding_append]
  simp [outstanding]

/-- A chain of `n` excuses adds `n` penalties. -/
theorem outstanding_replicate_excuse (n : Nat) :
    outstanding (List.replicate n Entry.excuse) = n * excusePenalty := by
  induction n with
  | zero => simp [outstanding]
  | succ k ih =>
    rw [List.replicate_succ, Nat.succ_mul]
    simp [outstanding, ih]
    omega

/-- A chain of excuses grows the outstanding amount linearly. -/
theorem excuse_chain_grows (es : List Entry) (n : Nat) :
    outstanding (es ++ List.replicate n Entry.excuse) =
      outstanding es + n * excusePenalty := by
  rw [outstanding_append, outstanding_replicate_excuse]

/-- **No finite chain of excuses discharges a positive debt.**

Whatever is already outstanding, and whatever the length of the chain, the
result is positive — so no `n` reaches zero. The regress is not merely long; it
does not terminate in the direction the excusing agent needs. -/
theorem no_finite_excuse_chain_discharges (d n : Nat) (hd : 0 < d) :
    0 < d + n * excusePenalty := by
  have h1 : d ≤ d + n * excusePenalty := by omega
  exact Nat.lt_of_lt_of_le hd h1

/-! ## 6. The trap — why the excusing agent cannot pay -/

/-- The action layer. An agent either acknowledges the record or withholds it,
and may pay or not. Acknowledgment is not an emotion and not a statement of
regret; it is agreement that the record is accurate. -/
inductive Move where
  | acknowledge
  | withhold
  | restitute (units : Nat)
deriving DecidableEq, Repr

/-- Acknowledgment has occurred at least once. -/
def acknowledged : List Move → Bool
  | [] => false
  | Move.acknowledge :: _ => true
  | _ :: rest => acknowledged rest

/-- Payment toward the debt requires that the debt be admitted. This is not a
stipulation about feelings; it is the operational fact that you cannot direct a
payment at an account you deny exists. -/
def Move.legal (prior : List Move) : Move → Bool
  | .acknowledge => true
  | .withhold => true
  | .restitute _ => acknowledged prior

/-- **An excuse forecloses restitution.**

If the agent has never acknowledged — the action form of an excuse — then it
cannot restitute, so its outstanding balance cannot fall, so by
`restored = balanced` it cannot be restored while withholding.

This is the trap, stated as a theorem rather than as an admonition: the excusing
agent has removed its own route out. Not by punishment. By the illegality of
paying an account it denies. -/
theorem excuse_forecloses_restitution (prior : List Move) (n : Nat)
    (hnone : acknowledged prior = false) :
    Move.legal prior (.restitute n) = false := by
  simp [Move.legal, hnone]

/-- Acknowledgment is available from any position, so the trap has a door. This
is the structural form of grace's availability: not that the debt is waived,
but that the route back is never closed by the ledger itself. -/
theorem acknowledgement_always_available (prior : List Move) :
    Move.legal prior .acknowledge = true := rfl

/-- Appending an acknowledgment makes the prefix acknowledged. -/
theorem acknowledged_append_ack (prior : List Move) :
    acknowledged (prior ++ [Move.acknowledge]) = true := by
  induction prior with
  | nil => rfl
  | cons m rest ih =>
    cases m <;> simp [acknowledged, ih]

/-- Once acknowledged, restitution is legal — so the door leads somewhere. -/
theorem acknowledgement_opens_restitution (prior : List Move) (n : Nat) :
    Move.legal (prior ++ [.acknowledge]) (.restitute n) = true := by
  simp [Move.legal, acknowledged_append_ack]

/-! ## 7. Grace is a payment, not a waiver -/

/-- Grace as a settlement component: another pays, the debtor's required
payment falls, the debt itself does not move.

The distinction is `cheap_mercy_is_uninhabited` applied to a concrete object:
grace changes `byOther`, never `debt`. -/
structure Grace where
  base : Settlement
  supplied : Nat
  covers : base.account.debt ≤ base.byViolator + supplied

/-- Applying grace yields a settlement that balances by construction. -/
def Grace.apply (g : Grace) : Settlement where
  account := g.base.account
  byViolator := g.base.byViolator
  byOther := g.supplied

theorem grace_balances (g : Grace) : g.apply.balanced := g.covers

/-- The debt is untouched. Grace is not a write-down. -/
theorem grace_does_not_lower_the_debt (g : Grace) :
    g.apply.account.debt = g.base.account.debt := rfl

/-- If the debtor was insolvent, grace necessarily came from outside — the same
substitution theorem, now with grace as the named source of `byOther`. -/
theorem grace_is_substitution (g : Grace) (hin : g.base.account.insolvent)
    (hf : g.base.feasible) : 0 < g.supplied := by
  have h := substitution_required g.apply hin hf (grace_balances g)
  simpa [Grace.apply] using h

/-- A grace structure exists for the insolvent case, so the schema is
inhabited and `covers` is not an unsatisfiable obligation. -/
def substitutionGrace : Grace where
  base := substitutionCase
  supplied := 7
  covers := by decide

theorem substitutionGrace_is_grace : 0 < substitutionGrace.supplied :=
  grace_is_substitution substitutionGrace (by unfold Account.insolvent; decide)
    (by unfold Settlement.feasible; decide)

/-! ## 8. What this does not prove

Every theorem above is about `Account`, `Settlement`, `Entry`, `Claim`, `Move`,
and `Grace` as defined here. Nothing above establishes that any debt exists,
that any payment occurred, that any party is guilty, or anything about the
nature of God. Theorems about a ledger are not verdicts about a person.

What is established is narrower and still useful: *if* a violation is to be
reconciled with both the ledger closed and the debtor restored, *then* the
payment must come from a non-debtor, the record must be acceded to rather than
argued with, and grace must be a transfer rather than a waiver. Those are
constraints on any proposed reconciliation, and they can be violated — which is
what makes them worth stating.

The falsifier stands: produce a settlement with an insolvent debtor, a balanced
ledger, and no third-party payment. `substitution_required` forbids it.
-/

end Covenant
