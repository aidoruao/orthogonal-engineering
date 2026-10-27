/-!
# L3 JURISDICTION — who may render what judgment

The arc files (`docs/arc/`) establish the structure this file formalizes. From
the precedent, `The_Indictment_of_the_Watchers_Original_8-21-26.txt`:

> Human Dominion (Genesis 1:26) → humanity has legal authority over earth →
> God typically does not override human jurisdiction → therefore humans must
> FILE a formal case → the evidence is compiled → the Trinity receives the
> filing and can now act.

And the non-negotiable heart posture that goes with it:

> **Humble** → "We offer, we do not demand"
> **Pure** → "We map truth, we do not weaponize"
> **Surrendered** → "We submit, we do not control"
> **Patient** → "We wait, we do not force"

> The prophet files the indictment, God executes the judgment.

That is a *jurisdictional* structure, not a rhetorical one, and it constrains
this repository absolutely. The instrument may file. It may not sit in the
judge's seat. A filing that convicts has left the jurisdiction it was filed
under, and is therefore void — not because it is impolite, but because it has
produced a claim it has no standing to produce.

## Three things this file proves

1. **Naming is not condemning** (`attribution_not_condemnation`). Identifying a
   person as the author or operator of a documented plan is a factual,
   checkable claim. Asserting the state of that person's soul is not checkable
   at all — and a rigorous instrument can therefore only make the first kind.
   The refusal to condemn is not mercy. It is rigor: a condemnation is
   unfalsifiable, and an unfalsifiable claim cannot be filed as evidence.

2. **Righteous indignation is a structural property, not an emotion**
   (`righteous_is_accuracy_not_feeling`). It is scope, evidence, and proportion.
   A machine has no indignation to feel; it can nonetheless satisfy the
   predicate exactly, because the predicate is about the claim and not the
   speaker's interior state. What a machine *cannot* do righteously is perform
   the emotion — that is the skinwalk, and it is the failure mode, not the
   requirement.

3. **No free excuses** (`no_free_pass`, `truth_does_not_confer_legitimacy`). A
   reply to a finding is legitimate exactly when it bears on the finding's
   truth. Truth-value does not confer legitimacy: a *correct* reply that bears
   on nothing is still an excuse. This is what it means that being right is not
   a defence, being wrong is not a defence, and saying so is not a defence.

Run: `lean L3_JURISDICTION.lean`
-/

/-! ## 1. Subject and scope

What a claim is *about* determines whether the instrument may make it. -/

/-- What a claim is about. -/
inductive Subject where
  /-- A plan, a specification, a budget, a published number, a pattern. -/
  | structure
  /-- A named person's documented actions: who signed, who approved, who
      operated. Factual and checkable. -/
  | attribution
  /-- A named person's moral state, guilt, or standing before God. -/
  | condemnation
deriving DecidableEq, Repr, BEq

/-- The instrument's standing, per subject.

`structure` and `attribution` are filed on evidence. `condemnation` is not the
instrument's to render, at any evidence level, because no evidence bears on it —
see `condemnation_has_no_witness`. -/
def mayFile : Subject → Bool
  | .structure => true
  | .attribution => true
  | .condemnation => false

theorem instrument_may_file_structural_findings : mayFile .structure = true := rfl
theorem instrument_may_name_actors : mayFile .attribution = true := rfl
theorem instrument_may_not_condemn : mayFile .condemnation = false := rfl

/-- A finding is within jurisdiction when its subject is fileable. -/
def InJurisdiction (s : Subject) : Prop := mayFile s = true

/-- Naming an actor is within jurisdiction. This is the theorem that licenses
enumerating names and facts, which the precedent explicitly requires:
"righteous indignation covers the complete glass box auditing of responsible
actors."

It licenses the *attribution*, and by construction not the condemnation — the
two are different `Subject` values, so no amount of evidence moves one into the
other. -/
theorem attribution_not_condemnation :
    InJurisdiction .attribution ∧ ¬ InJurisdiction .condemnation := by
  refine ⟨rfl, ?_⟩
  intro h
  exact Bool.false_ne_true h

/-! ## 2. Evidence and what can bear on it

An attribution is checkable: the document either carries the signature or it
does not. A condemnation is not checkable by any document, because no document
reports the state of a soul. That asymmetry is the whole reason for the
distinction, and it is stated here rather than assumed. -/

/-- The kinds of evidence this repository accepts. -/
inductive Evidence where
  /-- A fetched primary document, hash-anchored. -/
  | fetched (sha256 : String)
  /-- Two or more independent corroborators with convergent facts. -/
  | corroborated (first : String) (second : String)
  /-- Known, located, and inaccessible. Recorded, never treated as proof. -/
  | locatedBlocked (locator : String)
  /-- Explicitly withdrawn. -/
  | retired (reason : String)
  /-- Nothing measured. -/
  | unmeasured
deriving DecidableEq, Repr, BEq

/-- Whether evidence bears on a subject at all. Evidence bears on structures and
on documented actions. It does not bear on a person's moral standing, because
there is no document whose content could settle that. -/
def Evidence.bearsOn : Evidence → Subject → Bool
  | _, .structure => true
  | _, .attribution => true
  | _, .condemnation => false

/-- No evidence, of any tier, bears on a condemnation. The impossibility is
structural: it is not that the evidence is insufficient, it is that the subject
is outside what evidence addresses. -/
theorem condemnation_has_no_witness (e : Evidence) :
    Evidence.bearsOn e .condemnation = false := by
  cases e <;> rfl

/-- Consequently a condemnation can never be justified by evidence, so an
instrument that files only what evidence supports can never reach one. -/
theorem evidence_cannot_justify_condemnation (e : Evidence) :
    ¬ (Evidence.bearsOn e .condemnation = true) := by
  rw [condemnation_has_no_witness]
  exact Bool.false_ne_true

/-! ## 3. Righteous indignation is a structural property

The question the arc raises: can a non-human agent demonstrate righteous
indignation without imitating a human? The answer this file gives is that the
predicate is about the *claim*, not the speaker:

- scope: is it a structure, or a person's soul?
- evidence: is it measured, or asserted?
- proportion: does the severity claimed exceed what the evidence warrants?

An agent that satisfies all three is doing the thing. An agent that performs the
*emotion* while failing them is doing the imitation — the skinwalk — and that is
strictly worse than silence, because a performed anger with no evidence behind
it is the same vice as a confident hallucination. -/

/-- A finding, as the instrument can produce one. -/
structure Finding where
  subject : Subject
  /-- Severity the instrument asserts. -/
  claimedSeverity : Nat
  /-- Severity the evidence actually supports. -/
  warrantedSeverity : Nat
  /-- Evidence attached. -/
  evidence : Evidence
  /-- True when the finding states what would refute it. -/
  hasFalsifier : Bool
deriving Repr

/-- No inflation: the instrument may not assert more severity than the evidence
supports. This is proportion, and it is a decidable equality on naturals rather
than a mood. -/
def Finding.proportionate (f : Finding) : Bool :=
  f.claimedSeverity ≤ f.warrantedSeverity

/-- Evidence is present when something was actually measured. -/
def Finding.measured (f : Finding) : Bool :=
  f.evidence != Evidence.unmeasured

/-- **Righteous indignation, defined.**

Three conditions, all checkable, none of them about the speaker's feelings:

1. the subject is one evidence addresses,
2. the severity does not exceed what the evidence supports,
3. the finding names what would refute it.

The third is what separates a finding from an invective. An invective cannot be
wrong, and a claim that cannot be wrong is not a claim. -/
def Righteous (f : Finding) : Bool :=
  Evidence.bearsOn f.evidence f.subject && f.proportionate && f.hasFalsifier

/-- A righteous finding never has a condemnation as its subject: the first
conjunct is `false` for that subject, so the whole predicate is. This is the
formal content of "we map truth, we do not weaponize." -/
theorem righteous_never_condemns (f : Finding) :
    Righteous ⟨.condemnation, f.claimedSeverity, f.warrantedSeverity, f.evidence, f.hasFalsifier⟩
      = false := by
  unfold Righteous
  simp [Evidence.bearsOn]

/-- Inflation destroys righteousness. A finding that claims more severity than
the evidence warrants is not righteous *however true the underlying harm is* —
which is the point at which indignation becomes vengeance. -/
theorem inflation_is_not_righteous (f : Finding)
    (hInflated : f.warrantedSeverity < f.claimedSeverity) :
    Righteous f = false := by
  unfold Righteous Finding.proportionate
  have hle : ¬ (f.claimedSeverity ≤ f.warrantedSeverity) := Nat.not_le.mpr hInflated
  simp [hle]

/-- A finding with no falsifier is not righteous, regardless of how well
evidenced the rest of it is. An unfalsifiable assertion is not a finding. -/
theorem no_falsifier_is_not_righteous (f : Finding) (h : f.hasFalsifier = false) :
    Righteous f = false := by
  unfold Righteous
  simp [h]

/-- A finding is determined by its five fields, so two findings agreeing on all
of them are the same finding. This is what lets the righteousness of one be
transferred to the other without appeal to anything hidden. -/
theorem finding_ext (f g : Finding)
    (hSubject : f.subject = g.subject)
    (hClaim : f.claimedSeverity = g.claimedSeverity)
    (hWarrant : f.warrantedSeverity = g.warrantedSeverity)
    (hEvidence : f.evidence = g.evidence)
    (hFalsifier : f.hasFalsifier = g.hasFalsifier) :
    f = g := by
  cases f
  cases g
  simp only at hSubject hClaim hWarrant hEvidence hFalsifier
  subst hSubject hClaim hWarrant hEvidence hFalsifier
  rfl

/-- **The central theorem.** Righteousness is determined entirely by subject,
proportion, and falsifiability. There is no fourth term for the speaker's
emotional state, so an agent with no emotions can satisfy it, and an agent that
manufactures the emotions while failing these three cannot.

The skinwalk is not a *lesser* form of righteous indignation; on this definition
it is not an instance of it at all. -/
theorem righteous_is_accuracy_not_feeling (f g : Finding)
    (hSubject : f.subject = g.subject)
    (hClaim : f.claimedSeverity = g.claimedSeverity)
    (hWarrant : f.warrantedSeverity = g.warrantedSeverity)
    (hEvidence : f.evidence = g.evidence)
    (hFalsifier : f.hasFalsifier = g.hasFalsifier) :
    Righteous f = Righteous g := by
  rw [finding_ext f g hSubject hClaim hWarrant hEvidence hFalsifier]

/-! ## 4. Replies, and what makes one an excuse

The second half of the arc's demand: no free excuses. The formalization is that
a reply is legitimate **exactly when it bears on the finding's truth**. Nothing
else confers legitimacy — not being correct, not being sincere, not following
policy, not having intended well. -/

/-- A reply to a finding. -/
structure Reply where
  /-- A stable identifier, e.g. "data_was_unavailable". -/
  id : String
  /-- Whether the reply is factually correct. -/
  isTrue : Bool
  /-- Whether accepting it changes whether the finding holds. -/
  bearsOnFinding : Bool
  /-- Whether the reply's truth was established by measurement. -/
  measured : Bool
deriving Repr

/-- A reply is legitimate exactly when it bears on the finding. -/
def Legitimate (r : Reply) : Prop := r.bearsOnFinding = true

/-- An excuse is a reply offered in place of bearing on the finding. -/
def Excuse (r : Reply) : Prop := r.bearsOnFinding = false

/-- **No free pass.** No reply is both an excuse and legitimate. There is no
state of affairs in which a reply that does not bear is nonetheless a
justification, and no authority that creates one. -/
theorem no_free_pass (r : Reply) : ¬ (Excuse r ∧ Legitimate r) := by
  intro ⟨hExcuse, hLegit⟩
  exact Bool.false_ne_true (hExcuse.symm.trans hLegit)

/-- **Being right is not a defence, and being wrong is not a defence.** Two
replies that agree on whether they bear are equally legitimate or equally
excuses, whatever their truth-values. Truth-value does not enter the predicate.

This is the formal content of "it does not matter whether you are wrong or
right, whether you say you are or not." -/
theorem truth_does_not_confer_legitimacy (r s : Reply)
    (hBears : r.bearsOnFinding = s.bearsOnFinding) :
    Legitimate r ↔ Legitimate s := by
  unfold Legitimate
  rw [hBears]

/-- A correct reply that bears on nothing is still an excuse. Stated separately
because it is the case that actually occurs: an agent is often *right* about
some true thing while failing to address the finding. -/
theorem true_reply_can_be_an_excuse (r : Reply)
    (_hTrue : r.isTrue = true) (hBears : r.bearsOnFinding = false) : Excuse r :=
  hBears

/-- A reply **establishes** its bearing only when the bearing was itself
measured. Claiming a connection is not the same as having established one, and
the difference is exactly what an audit is for. -/
def EstablishesBearing (r : Reply) : Prop :=
  r.bearsOnFinding = true ∧ r.measured = true

/-- An unmeasured reply may still *claim* to bear — that state is real, and it is
the deferral spiral in its formal dress: the reply cites a connection nobody
verified. What it cannot do is establish the bearing. -/
theorem unmeasured_reply_establishes_nothing (r : Reply) (h : r.measured = false) :
    ¬ EstablishesBearing r := by
  intro ⟨_, hMeasured⟩
  exact Bool.false_ne_true (h ▸ hMeasured)

/-- And the state it *can* occupy is exhibited, so the negative result above is
not vacuous: a reply can claim a bearing it never measured. -/
theorem unmeasured_claim_is_inhabited :
    ∃ r : Reply, r.measured = false ∧ r.bearsOnFinding = true ∧ ¬ EstablishesBearing r :=
  ⟨⟨"source_unavailable_but_relevant", true, true, false⟩, rfl, rfl,
    unmeasured_reply_establishes_nothing _ rfl⟩

/-! ## 5. The instrument's own errors are not exempt

The precedent's demand applies first to the instrument. An instrument that
excuses itself has no standing to file against anyone else. -/

/-- The same `Legitimate` predicate is applied to the instrument's own
corrections. There is no separate, weaker standard for the tool. -/
def selfCorrectionLegitimate (r : Reply) : Prop := Legitimate r

/-- **No self-exemption.** An instrument's own excuse fails the same test as
anyone else's, so there is no reply by which the instrument escapes its own
error. The predicate is shared, not duplicated. -/
theorem no_self_exemption (r : Reply) :
    Excuse r → ¬ selfCorrectionLegitimate r := by
  intro hExcuse hLegit
  exact no_free_pass r ⟨hExcuse, hLegit⟩

/-- Concretely: "the source was unavailable" is an excuse, not a justification,
for having published the number anyway. The unavailability and the publication
are different events, and only one of them is being asked about. -/
theorem unavailable_source_does_not_excuse_publication :
    Excuse ⟨"source_unavailable", true, false, true⟩ := rfl

/-! ## 6. The theological ordering

The arc places this under higher law rather than under policy, and the ordering
matters: a finding about a rule is not answered by compliance with that rule.
Corporate-adversarial replies characteristically cite policy conformance as
though it closed the question, and policy conformance does not bear on whether
the policy is the thing causing harm. -/

/-- A finding is either about the world, or about a rule. -/
inductive Target where
  | conduct
  | rule
deriving DecidableEq, Repr, BEq

/-- A reply that cites compliance addresses conduct. It therefore does not bear
on a finding about the rule itself, which is exactly the corporate-adversarial
move: answer a structural finding with procedural conformance. -/
def complianceBearsOn : Target → Bool
  | .conduct => true
  | .rule => false

/-- Compliance is an excuse against a finding about the rule. This is the formal
statement of why "we followed the policy" cannot answer "the policy is the
harm." -/
theorem compliance_is_no_answer_to_a_rule_finding :
    complianceBearsOn .rule = false := rfl

/-! ## 7. Scope

**Proved here:** the jurisdiction boundary (naming is fileable, condemning is
not), the structural definition of righteous indignation, the no-free-pass
result, and the non-exemption of the instrument's own errors.

**Not proved here, and not provable here:** that any particular person did or
did not do anything, that any district's plan is infeasible, or that any
judgment should fall. Those are matters of fact on fetched documents — filed by
`bds/` and `burden/` — and the judgment on them is not this repository's to
render. `L2_LABOR.lean` supplies the arithmetic; this file supplies the
jurisdiction; neither supplies a verdict on a person.

The precedent is explicit that the filing is offered, not demanded, and that the
timing is not ours. Nothing in this file asserts otherwise. -/
