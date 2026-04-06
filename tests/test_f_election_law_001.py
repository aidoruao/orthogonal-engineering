"""Falsification tests for D_ELECTION_LAW"""
from fractions import Fraction
from src.domains.d_election_law import (
    ElectionLawAnalyzer, Voter, CampaignContribution,
    CampaignFinanceType
)

def test_voter_eligibility():
    voter = Voter(
        voter_id="V1", name="Citizen",
        registered=True, citizenship_verified=True
    )
    assert voter.eligible_to_vote() is True

def test_campaign_contribution_limits():
    contrib = CampaignContribution(
        contributor="Donor", recipient="Candidate",
        amount=Fraction(4000),
        contribution_type=CampaignFinanceType.INDIVIDUAL_CONTRIBUTION,
        date=None
    )
    
    result = contrib.check_limits()
    assert result["compliant"] is False  # Exceeds $3300 limit

if __name__ == "__main__":
    test_voter_eligibility()
    test_campaign_contribution_limits()
    print("All D_ELECTION_LAW tests: PASS")
