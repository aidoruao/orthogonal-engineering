---
tags: [src, domains, d-judicial-review, readme]
register: technical
---

# D_JUDICIAL_REVIEW: Judicial Review

**Layer:** 1 (Constitutional)  
**CardinalStrength:** INACCESSIBLE  
**Authority:** Marbury v. Madison (1803)

## Description

Domain implementing Marbury v. Madison judicial review: courts can invalidate
unconstitutional statutes. Ensures review by independent situs (not the enacting
branch).

## Invariants

1. **Any Statute Challengeable**: Any statute can be challenged for constitutional
compliance.

2. **Independent Situs Required**: Review must be by independent judiciary,
not the branch that enacted the law.

3. **Invalidation Power**: Courts can invalidate unconstitutional statutes.

4. **Standing Doctrine**: Challenges must have valid grounds.

## Key Classes

- `JudicialReview`: Judicial review of constitutional compliance
- `ConstitutionalChallenge`: A challenge to a statute's constitutionality
- `SitusIndependence`: Independence of the reviewing court
- `ReviewOutcome`: Outcome of judicial review

## Usage

```python
from src.domains.d_judicial_review import (
    JudicialReview,
    ChallengeGround,
)

review = JudicialReview()

# File constitutional challenge
challenge = review.file_challenge(
    challenge_id="CH-001",
    statute_name="Contested Act",
    enacting_branch="legislative",
    grounds=[ChallengeGround.FIRST_AMENDMENT],
)

# Assign independent court
review.assign_independent_situs("CH-001", "Federal District Court")

# Conduct review
outcome = review.conduct_review(
    challenge_id="CH-001",
    statute_unconstitutional=True,
    reasoning="Violates First Amendment",
)
```

## Biblical Inspiration

Deuteronomy 17:8-9 — "If cases come before your courts that are too difficult
for you to judge... go to the place the LORD your God will choose. Go to the
Levitical priests and to the judge who is in office at that time."

Judicial review by independent authorities has ancient roots—disputes must be
resolved by those not party to the dispute.

## Falsification Tests

- `F_JUDICIAL_001`: Verify any statute can be challenged
- `F_JUDICIAL_002`: Verify review requires independent situs
- `F_JUDICIAL_003`: Verify independent situs accepts review
- `F_JUDUDICIAL_004`: Verify unconstitutional statutes are invalidated
- `F_JUDICIAL_005`: Verify judicial review availability
- `F_JUDICIAL_006`: Verify situs independence scoring
