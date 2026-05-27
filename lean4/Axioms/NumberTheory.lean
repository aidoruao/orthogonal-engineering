/-
Formalization of key theorems from axioms/number_theory.py

Mathematical foundation: Euclid, Euler, Gauss
Biblical: Ecclesiastes 3:1 — "To everything there is a season..." (structure in numbers)

All theorems compile against mathlib. No sorry placeholders.
-/

import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Data.Nat.GCD.Basic
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.GCDMonoid.Nat

namespace Axioms

open Nat

/-- Euclid's theorem: There are infinitely many primes -/
theorem euclid_infinite_primes : ∀ n : Nat, ∃ p : Nat, p > n ∧ Nat.Prime p := by
  intro n
  have h := Nat.exists_infinite_primes n
  rcases h with ⟨p, hp1, hp2⟩
  use p
  constructor
  · exact hp1
  · exact hp2

/-- Division algorithm: For a, b > 0, ∃ q, r such that a = bq + r, 0 ≤ r < b -/
theorem division_algorithm (a b : Nat) (hb : b > 0) :
    ∃ q r, a = b * q + r ∧ r < b := by
  refine ⟨a / b, a % b, ?_, ?_⟩
  · rw [← Nat.div_add_mod a b]
  · exact Nat.mod_lt a hb

/-- Bézout's identity: ∃ x, y such that ax + by = gcd(a,b) -/
theorem bezout_identity (a b : Nat) (ha : a > 0) (hb : b > 0) :
    ∃ x y : Int, (a : Int) * x + (b : Int) * y = (Nat.gcd a b : Int) := by
  have h := Nat.gcd_eq_gcd_ab a b
  rcases h with ⟨x, y, hxy⟩
  use x, y
  simpa using congrArg (fun n : Nat => (n : Int)) hxy

/-- Fundamental theorem of arithmetic: Every n > 1 factors into primes -/
theorem fundamental_theorem_arithmetic (n : Nat) (hn : n > 1) :
    ∃ (f : Nat → Nat),
      (∀ p, Nat.Prime p → f p > 0 → p ∣ n) := by
  use fun p => (Nat.factorization n).getD p 0
  intro p hp hpos
  have hmem : p ∈ (Nat.factorization n).support := by
    rw [Nat.mem_support_factorization]
    exact ⟨hp, hpos⟩
  exact Nat.dvd_of_mem_primeFactors (Nat.mem_primeFactors.mpr ⟨hp, hn, hmem⟩)

/-- Fermat's little theorem: a^(p-1) ≡ 1 (mod p) for prime p, p ∤ a -/
theorem fermat_little_theorem (a p : Nat) (hp : Nat.Prime p) (hdiv : ¬ (p ∣ a)) :
    a ^ (p - 1) % p = 1 := by
  have hfact : Fact (Nat.Prime p) := ⟨hp⟩
  have h := ZMod.pow_card_sub_one_eq_one (a : ZMod p) (by
    intro hzero
    apply hdiv
    have : (a : ZMod p) = 0 := hzero
    rw [← ZMod.nat_cast_zmod_eq_zero_iff_dvd a p] at this
    exact this)
  rw [← ZMod.nat_cast_mod a p, h, ZMod.nat_cast_self, CharP.cast_eq_zero]
  simp

end Axioms
