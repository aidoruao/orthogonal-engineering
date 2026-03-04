"""
Wrapper test for F_PLATFORM_002.
"""
# @falsification_id: F_PLATFORM_002

from test_falsification import run_f002_int64_arithmetic_vectors


def test_f_platform_002():
    run_f002_int64_arithmetic_vectors()
