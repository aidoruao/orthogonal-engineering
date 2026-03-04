"""
Wrapper test for F_PLATFORM_005.
"""
# @falsification_id: F_PLATFORM_005

from test_falsification import run_f005_struct_pack_little_endian


def test_f_platform_005():
    run_f005_struct_pack_little_endian()
