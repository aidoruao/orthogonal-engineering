#!/usr/bin/env python3
"""
Userspace — Standard library and application framework

The standard library is the lingua franca of the commonwealth.
It provides the interface between applications and the kernel.

Biblical: Genesis 11:1 — "Now the whole world had one language and a
  common speech."
  The standard library is the common speech of Kingdom OS programs.
"""

from . import stdlib
from . import app_framework

__all__ = ["stdlib", "app_framework"]
