"""
Wrapper test for F_PLATFORM_001.
"""
# @falsification_id: F_PLATFORM_001

from test_falsification import run_f001_seed_bytes_sha256_deterministic


def test_f_platform_001():
    run_f001_seed_bytes_sha256_deterministic()
