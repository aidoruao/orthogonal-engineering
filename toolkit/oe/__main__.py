"""
Orthogonal Engineering Toolkit - Command Line Interface Entry Point

This module allows the toolkit package to be executed directly:
    python -m toolkit.oe [command]

Implements G11-01: Unified CLI exists (/toolkit/oe/cli.py)
"""

import sys


def main():
    """Main entry point for package execution."""
    from .cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
