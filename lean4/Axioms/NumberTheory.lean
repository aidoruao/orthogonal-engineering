import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Data.Nat.GCD.Basic
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.GCDMonoid.Nat

namespace Axioms

open Nat

/-- Euclid's theorem: There are infinitely many primes -/
theorem euclid_infinite_primes : ∀ n : Nat, ∃ p : Nat, p > n ∧ Nat.Prime p :=
  Nat.exists_infinite_primes

/-- Division algorithm: For a, b > 0, ∃ q, r such that a = bq + r, 0 ≤ r < b -/
theorem division_algorithm (a b : Nat) (hb : b > 0) :
    ∃ q r, a = b * q + r ∧ r < b := by
  refine ⟨a / b, a % b, ?_, Nat.mod_lt a hb⟩
  rw [← Nat.div_add_mod a b]

/-- Bézout's identity: ∃ x, y such that ax + by = gcd(a,b) -/
theorem bezout_identity (a b : Nat) (ha : a > 0) (hb : b > 0) :
    ∃ x y : Int, (a : Int) * x + (b : Int) * y = (Nat.gcd a b : Int) := by
  have h := Nat.gcd_eq_gcd_ab a b
  rcases h with ⟨x, y, hxy⟩
  use x, y
  simpa using congrArg (fun n : Nat => (n : Int)) hxy

/-- Fundamental theorem of arithmetic: Every n > 1 is divisible by some prime -/
theorem fundamental_theorem_arithmetic (n : Nat) (hn : n > 1) :
    ∃ p : Nat, Nat.Prime p ∧ p ∣ n := by
  have h := Nat.exists_prime_and_dvd hn
  rcases h with ⟨p, hp, hdvd⟩
  exact ⟨p, hp, hdvd⟩

/-- Fermat's little theorem: a^(p-1) ≡ 1 (mod p) for prime p, p ∤ a -/
theorem fermat_little_theorem (a p : Nat) (hp : Nat.Prime p) (hdiv : ¬ (p ∣ a)) :
    a ^ (p - 1) % p = 1 := by
  have hp1 : 1 < p := Nat.Prime.one_lt hp
  have hfact : Fact (1 < p) := ⟨hp1⟩
  have ha : (a : ZMod p) ≠ 0 := by
    intro hzero
    apply hdiv
    rw [← ZMod.natCast_zmod_eq_zero_iff_dvd a p]
    exact hzero
  have h_eq : (a : ZMod p) ^ (p - 1) = 1 := ZMod.pow_card_sub_one_eq_one ha
  rw [← ZMod.val_natCast p (a ^ (p - 1))]
  rw [Nat.cast_pow (a : ℕ) (p - 1)]
  rw [h_eq]
  rw [ZMod.val_natCast p 1]
  exact Nat.mod_eq_of_lt hp1

end Axioms
