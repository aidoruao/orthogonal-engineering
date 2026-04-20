---
tags: [src, domains, d-voting-rights, readme]
register: technical
---

# D_VOTING_RIGHTS: Voting & Elections

**Layer:** 1 (Constitutional)  
**CardinalStrength:** INACCESSIBLE  
**Authority:** 15th, 19th, 24th, 26th Amendments

## Description

Domain implementing constitutional voting rights: 15th Amendment (race),
19th Amendment (sex), 24th Amendment (poll taxes), 26th Amendment (age 18+).
Ensures vote is recorded as cast and verifiable.

## Invariants

1. **15th Amendment**: Right to vote shall not be denied on account of race.

2. **19th Amendment**: Right to vote shall not be denied on account of sex.

3. **24th Amendment**: Poll taxes are prohibited in federal elections.

4. **26th Amendment**: Citizens 18+ have right to vote.

5. **Vote Verification**: Vote is recorded as cast and verifiable via hash
commitment.

## Key Classes

- `VotingRightsChecker`: Voting rights compliance checker
- `Voter`: A voter with constitutional protections
- `Ballot`: A ballot with verifiable hash commitment
- `VoteVerification`: Vote verification record

## Usage

```python
from src.domains.d_voting_rights import VotingRightsChecker

checker = VotingRightsChecker()

# Register voter
voter = checker.register_voter(
    voter_id="V001",
    age=25,
    is_citizen=True,
)

# Check eligibility
result = checker.check_voting_eligibility("V001")

# Cast ballot
ballot = checker.cast_ballot(
    voter_id="V001",
    selections={"President": "Candidate A"},
)

# Verify vote
verification = checker.verify_vote(
    ballot_id=ballot.ballot_id,
    expected_selections={"President": "Candidate A"},
)
```

## Biblical Inspiration

Deuteronomy 1:13 — "Choose some wise, understanding and respected men from each
of your tribes, and I will set them over you."

Democratic participation in choosing leaders reflects the biblical principle
of representative governance with consent of the governed.

## Falsification Tests

- `F_VOTING_001`: Verify 15th Amendment (no racial discrimination)
- `F_VOTING_002`: Verify 19th Amendment (no sex discrimination)
- `F_VOTING_003`: Verify 26th Amendment (age 18+)
- `F_VOTING_004`: Verify under-18 cannot vote
- `F_VOTING_005`: Verify non-citizen cannot vote
- `F_VOTING_006`: Verify vote recording and verification
- `F_VOTING_007`: Verify 24th Amendment (no poll tax)
