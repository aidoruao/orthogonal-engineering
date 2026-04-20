"""Machine-readable OE enumerations (anti-patterns, hidden failures, magic numbers)."""
from .integrity import (
    check_all_entries_have_falsifies_if,
    check_all_entries_have_keys,
    check_all_keys_unique_across_files,
    check_all_keys_unique_per_file,
    load_black_box_antipatterns,
    load_hidden_failures,
    load_magic_numbers,
    run_all_invariants,
)

__all__ = [
    "check_all_entries_have_falsifies_if",
    "check_all_entries_have_keys",
    "check_all_keys_unique_across_files",
    "check_all_keys_unique_per_file",
    "load_black_box_antipatterns",
    "load_hidden_failures",
    "load_magic_numbers",
    "run_all_invariants",
]
