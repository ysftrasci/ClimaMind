#!/usr/bin/env python3
"""Launch Clima Mind (no PYTHONPATH setup required)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
_src_str = str(_SRC)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

from climamind.app import main

if __name__ == "__main__":
    main()
