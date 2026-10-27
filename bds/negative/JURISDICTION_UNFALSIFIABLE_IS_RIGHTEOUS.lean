import «L3_JURISDICTION»

/-! # Negative control — this file MUST fail to compile.

It asserts that a finding which names nothing that would refute it is righteous,
provided everything else about it is sound.

If Lean accepts this, `no_falsifier_is_not_righteous` is vacuous, and an
unfalsifiable assertion would count as a finding. An assertion that cannot be
wrong is not a claim, and filing one would be the exact vice the repository
exists to refuse: confident syntax with no exposure.

Expected: `decide` proves it false.

Run: `lean bds/negative/JURISDICTION_UNFALSIFIABLE_IS_RIGHTEOUS.lean; test $? -ne 0`
-/

/-- Perfectly evidenced, perfectly proportionate, and expressly unfalsifiable. -/
example :
    Righteous
      { subject := .attribution
        claimedSeverity := 1
        warrantedSeverity := 1
        evidence := .fetched "abc123"
        hasFalsifier := false } = true := by
  decide
