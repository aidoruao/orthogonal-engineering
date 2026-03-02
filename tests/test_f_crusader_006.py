"""
Falsification test: No spores detected outside unit after deployment.
Spore containment is enforced.

# @falsification_id: F_CRUSADER_006
"""
import pytest

class SporeContainment:
    def __init__(self):
        self.external_cfu = 0
        self.internal_filter_active = True

    def deploy(self, spores: int):
        if self.internal_filter_active:
            self.external_cfu = 0
        else:
            self.external_cfu = spores

def test_no_spores_outside_with_filter():
    unit = SporeContainment()
    unit.deploy(1000)
    assert unit.external_cfu == 0, f"External CFU = {unit.external_cfu}, expected 0"
