"""Overrides the abandoned PyPI ``pathlib==1.0.1`` backport that ``mega.py`` pins.

That backport's source does ``from collections import Sequence``, which was removed
in Python 3.10 (``Sequence`` now lives in ``collections.abc``). Once pip installs it,
it shadows the real stdlib ``pathlib`` module for the entire process and crashes on
the very first ``import pathlib`` anywhere — including the platform's own runtime
bootstrap, before application code even runs.

This local package satisfies mega.py's exact ``pathlib==1.0.1`` pin (so pip's
resolver is happy) while loading and delegating to the genuine stdlib module instead
of shipping the broken Python-2-era source.
"""

import sys
import sysconfig
from importlib.machinery import PathFinder
from importlib.util import module_from_spec

_stdlib_dir = sysconfig.get_path("stdlib")
_spec = PathFinder.find_spec("pathlib", path=[_stdlib_dir])
if _spec is None:  # pragma: no cover - would mean a broken interpreter install
    raise ImportError("could not locate the real stdlib pathlib module")

_real = module_from_spec(_spec)
sys.modules[__name__] = _real
_spec.loader.exec_module(_real)
