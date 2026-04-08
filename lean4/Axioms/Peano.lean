/-
Formalization of the Peano axioms from axioms/peano.py

Mathematical foundation: Giuseppe Peano (1889)
Biblical: Genesis 1:1 — "In the beginning..." (the primordial foundation)
-/

namespace Axioms

/-- P1: 0 is a natural number (built into Lean's Nat) -/
def zero : Nat := 0

/-- P2: Every natural number has a successor -/
def successor (n : Nat) : Nat := Nat.succ n

/-- P3: 0 is not the successor of any natural number -/
theorem zero_not_succ : ∀ n : Nat, Nat.succ n ≠ 0 := by
  intro n h
  exact absurd h (Nat.succ_ne_zero n)

/-- P4: Successor is injective -/
theorem succ_injective : ∀ m n : Nat, Nat.succ m = Nat.succ n → m = n := by
  intro m n h
  exact Nat.succ.inj h

/-- P5: Mathematical induction principle -/
theorem induction_principle {P : Nat → Prop}
    (base : P 0)
    (step : ∀ n, P n → P (Nat.succ n))
    : ∀ n, P n := by
  intro n
  induction n with
  | zero => exact base
  | succ n ih => exact step n ih

/-- Addition is defined recursively -/
def peanoAdd (m n : Nat) : Nat :=
  match n with
  | 0 => m
  | Nat.succ n' => Nat.succ (peanoAdd m n')

/-- Multiplication is defined recursively -/
def peanoMul (m n : Nat) : Nat :=
  match n with
  | 0 => 0
  | Nat.succ n' => peanoAdd m (peanoMul m n')

/-- Addition is associative -/
theorem add_assoc : ∀ a b c : Nat, peanoAdd (peanoAdd a b) c = peanoAdd a (peanoAdd b c) := by
  intro a b c
  induction c with
  | zero => rfl
  | succ c ih => simp [peanoAdd, ih]

/-- Addition is commutative -/
theorem add_comm : ∀ a b : Nat, peanoAdd a b = peanoAdd b a := by
  intro a b
  induction b with
  | zero => simp [peanoAdd]
  | succ b ih => simp [peanoAdd, ih]

/-- Multiplication distributes over addition -/
theorem mul_dist_add : ∀ a b c : Nat,
    peanoMul a (peanoAdd b c) = peanoAdd (peanoMul a b) (peanoMul a c) := by
  intro a b c
  induction c with
  | zero => simp [peanoAdd, peanoMul]
  | succ c ih => 
    simp [peanoAdd, peanoMul, ih]
    rw [add_assoc]

end Axioms
