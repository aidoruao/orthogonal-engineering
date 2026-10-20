/-!
# L1 DECAY — Verification Decays (2026-10-19)

A passing check is not a property of code. It is a claim indexed by the
environment it was made in — toolchain version, lockfile, OS, network. When the
environment moves, the claim does not become false. It becomes **unknown**.

This file proves the structure of that, and the consequence for any project that
wants to stay healthy: you can pin the environment, or you can re-verify
continuously, and there is no third option.

## The model

- An **environment** is a natural-number version. Any real fingerprint (node
  version, compiler version, lockfile hash) is collapsed to an index; only
  equality matters here.
- A **verification** is `(version, passed)` — a check run at one version.
- A **status** is three-valued: `verified`, `failed`, `unknown`.
- A **schedule** is the list of verifications actually performed.

## What is proved

1. **`stale_is_unknown`** — a verification at another version, whether it
   passed or failed, yields `unknown` for the current version. Staleness is not
   evidence either way. This is the theorem that stops "it passed last month"
   from being used as either proof or refutation.
2. **`pinned_one_verification_suffices`** — if the environment never moves from
   the verified version, a single verification covers every point.
3. **`pinned_environment_is_stable`** — with a constant environment, the status
   computed from one passing verification is `verified` everywhere.
4. **`adversary_finds_a_gap`** — for **any finite schedule** over an unbounded
   version sequence, there exists a version the schedule never touched. No
   finite amount of verification covers unbounded drift.
5. **`finite_schedule_cannot_cover_all`** — the same statement in coverage form.

## What is NOT proved, and must not be implied

- Nothing here measures how fast an environment drifts. `Nat` versions are an
  abstraction; the real drift rate is an empirical question per project.
- Nothing here says a passing verification is *correct* — only that it was
  performed and passed in a known environment. Correctness is the gate's own
  burden, discharged by the negative controls.
- Nothing here is about people, motive, or intention.

The engineering reading is the whole point:

> **Pin what you can. Verify what you cannot pin. Know which is which.**
> A stale pass is not a lie; treating it as current is.

Run: `lean L1_DECAY.lean`
-/

/-! ## 1. Environments, verifications, status -/

/-- An environment version. Equality is all that matters. -/
abbrev Version : Type := Nat

/-- One check, run at one environment version. -/
structure Verification where
  version : Version
  passed : Bool
deriving DecidableEq

/-- Three-valued status. `unknown` is a distinct outcome, not a soft `failed`. -/
inductive Status where
  | verified
  | failed
  | unknown
deriving DecidableEq

/-- Status of an environment, given the verifications actually performed.
    Only a verification *at that exact version* is consulted. -/
def statusOf (vs : List Verification) (env : Version) : Status :=
  match vs.find? (fun v => v.version = env) with
  | some v => if v.passed then .verified else .failed
  | none => .unknown

/-! ## 2. The central theorem: stale is unknown -/

/-- A list containing only verifications from other versions reports `unknown`.
    This is the statement that staleness is neither confirmation nor refutation. -/
theorem stale_is_unknown (vs : List Verification) (env : Version)
    (h : ∀ v ∈ vs, v.version ≠ env) : statusOf vs env = .unknown := by
  unfold statusOf
  have hnone : vs.find? (fun v => v.version = env) = none := by
    apply List.find?_eq_none.mpr
    intro v hv
    have hne := h v hv
    simp [hne]
  rw [hnone]

/-- A single stale verification that **passed** still reports `unknown`. -/
theorem stale_pass_is_unknown (v : Verification) (env : Version)
    (hne : v.version ≠ env) (_hpass : v.passed = true) :
    statusOf [v] env = .unknown := by
  apply stale_is_unknown
  intro w hw
  have hw' : w = v := by simpa using hw
  rw [hw']
  exact hne

/-- A single stale verification that **failed** also reports `unknown`.
    Together with `stale_pass_is_unknown`: staleness carries no information. -/
theorem stale_fail_is_unknown (v : Verification) (env : Version)
    (hne : v.version ≠ env) (_hfail : v.passed = false) :
    statusOf [v] env = .unknown := by
  apply stale_is_unknown
  intro w hw
  have hw' : w = v := by simpa using hw
  rw [hw']
  exact hne

/-! ## 3. Pinning -/

/-- Coverage: every version in `versions` has a matching verification. -/
def covers (vs : List Verification) (versions : List Version) : Prop :=
  ∀ e ∈ versions, ∃ v ∈ vs, v.version = e

/-- **`pinned_one_verification_suffices`.** If every version the project will
    ever occupy equals the verified version, one verification covers them all.
    This is why pinning works: it collapses the schedule to a single point. -/
theorem pinned_one_verification_suffices (v : Verification) (versions : List Version)
    (hpinned : ∀ e ∈ versions, e = v.version) : covers [v] versions := by
  intro e he
  exact ⟨v, by simp, (hpinned e he).symm⟩

/-- With a pinned environment, a single passing verification reports `verified`
    at every version in the sequence. -/
theorem pinned_environment_is_stable (v : Verification) (versions : List Version)
    (hpass : v.passed = true) (hpinned : ∀ e ∈ versions, e = v.version) :
    ∀ e ∈ versions, statusOf [v] e = .verified := by
  intro e he
  have heq : v.version = e := (hpinned e he).symm
  unfold statusOf
  simp [heq, hpass]

/-! ## 4. Drift cannot be outrun by any finite schedule -/

/-- The largest version appearing in a schedule (0 when empty). -/
def maxVersion (vs : List Verification) : Version :=
  vs.foldr (fun v acc => max v.version acc) 0

/-- Every scheduled version is at most `maxVersion`. -/
theorem le_maxVersion (vs : List Verification) (v : Verification) (hv : v ∈ vs) :
    v.version ≤ maxVersion vs := by
  induction vs with
  | nil => simp at hv
  | cons head tail ih =>
    rcases List.mem_cons.mp hv with hhead | hmem
    · rw [hhead]
      show head.version ≤ List.foldr (fun v acc => max v.version acc) 0 (head :: tail)
      simp only [List.foldr]
      exact Nat.le_max_left _ _
    · have hmem' := ih hmem
      show v.version ≤ List.foldr (fun v acc => max v.version acc) 0 (head :: tail)
      simp only [List.foldr]
      exact Nat.le_trans hmem' (Nat.le_max_right _ _)

/-- **`adversary_finds_a_gap`.** For any finite schedule, there is an
    environment version it never verified. The environment has more versions
    than the schedule has entries, and no finite schedule can cover them all.

    This is the game-theoretic core: an auditee that drifts has an unbeatable
    move against any finite auditor. The only counter is to stop the drift
    (pin), or to keep the schedule growing with the drift (re-verify). -/
theorem adversary_finds_a_gap (vs : List Verification) :
    ∃ env : Version, ∀ v ∈ vs, v.version ≠ env := by
  refine ⟨maxVersion vs + 1, ?_⟩
  intro v hv hcontra
  have hle : v.version ≤ maxVersion vs := le_maxVersion vs v hv
  rw [hcontra] at hle
  exact Nat.not_succ_le_self (maxVersion vs) hle

/-- The gap is reported as unknown, not as failure. Awareness of the gap is
    itself the honest outcome. -/
theorem gap_is_unknown (vs : List Verification) :
    ∃ env : Version, statusOf vs env = .unknown := by
  obtain ⟨env, hfresh⟩ := adversary_finds_a_gap vs
  exact ⟨env, stale_is_unknown vs env hfresh⟩

/-- **`finite_schedule_cannot_cover_all`.** No finite schedule covers every
    version. Stated in coverage form, so it can be cited next to
    `pinned_one_verification_suffices` as the two halves of the choice. -/
theorem finite_schedule_cannot_cover_all (vs : List Verification) :
    ¬ covers vs (List.range (maxVersion vs + 2)) := by
  intro hcov
  have hfresh : ∀ v ∈ vs, v.version ≠ maxVersion vs + 1 := by
    intro v hv hcontra
    have hle : v.version ≤ maxVersion vs := le_maxVersion vs v hv
    rw [hcontra] at hle
    exact Nat.not_succ_le_self (maxVersion vs) hle
  have hmem : maxVersion vs + 1 ∈ List.range (maxVersion vs + 2) := by
    simp
  obtain ⟨v, hv, hver⟩ := hcov (maxVersion vs + 1) hmem
  exact hfresh v hv hver

/-! ## 5. A worked instance

Synthetic. Three verifications; the environment reaches a fourth version.

    v₁ = (0, passed), v₂ = (1, passed), v₃ = (2, failed)

Version 0 and 1 are verified, version 2 is failed, version 3 — never touched —
is unknown. It is not failed. Nothing was learned about it. -/

def schedule : List Verification :=
  [⟨0, true⟩, ⟨1, true⟩, ⟨2, false⟩]

theorem v0_verified : statusOf schedule 0 = .verified := by decide
theorem v1_verified : statusOf schedule 1 = .verified := by decide
theorem v2_failed : statusOf schedule 2 = .failed := by decide

/-- Version 3 was never checked, and the spec says `unknown` — not `failed`. -/
theorem v3_unknown : statusOf schedule 3 = .unknown := by decide

/-- The same three verifications say nothing about version 3, in either
    direction: a pass elsewhere is not a pass here, and a failure elsewhere is
    not a failure here. -/
theorem v3_not_inferred : statusOf schedule 3 ≠ .verified ∧ statusOf schedule 3 ≠ .failed := by
  decide

/-!
## What this file establishes

1. `stale_is_unknown`, `stale_pass_is_unknown`, `stale_fail_is_unknown` —
   staleness is a third outcome, not a weak yes or a weak no.
2. `pinned_one_verification_suffices`, `pinned_environment_is_stable` — the
   case for pinning, proved rather than asserted.
3. `adversary_finds_a_gap`, `gap_is_unknown`, `finite_schedule_cannot_cover_all`
   — the case against relying on a finite schedule over unbounded drift.
4. `v3_unknown` / `v3_not_inferred` — the worked instance.

The practical consequences, each already reflected in the ledger:

- Record the environment a verification was made in. `ledger/VERIFIED_ENVIRONMENT.json`
  does this; `freshness.ts` compares it.
- When the environment differs, report **STALE**, never **FAILED**.
- Nightly CI exists because drift is unbounded and a finite schedule cannot
  cover it. **Only re-verification keeps a claim current.**
- `node_modules` under version control is a 93 MB pinned environment that is
  never verified. That is the worst of both.

A stale pass is not a lie. Treating it as current is.
-/
