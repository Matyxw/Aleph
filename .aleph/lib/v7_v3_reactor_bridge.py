#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.aleph/lib/v7_v3_reactor_bridge.py
Puente Soberano V7: Demostrador Formal Z3 SSA Real + Fusión de los 3 Reactores V3.
Conecta scripts/formal_verification_z3.py, scripts/neural_code_graph.py,
scripts/aleph_speculative_engine.py y scripts/aleph_diff_engine.py + Rust C-ABI Myers SIMD
con el núcleo v5_aeos_kernel.py, aleph_omega_facade.py y aleph_mcp_server.py.
"""

from __future__ import annotations

import ast
import ctypes
from dataclasses import asdict, dataclass, field
import difflib
import hashlib
import json
from pathlib import Path
import sys
import textwrap
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

try:
    import z3
except ImportError:
    z3 = None

ALEPH_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = ALEPH_ROOT / "lib"
SCRIPTS_DIR = ALEPH_ROOT / "scripts"
V4_DIR = ALEPH_ROOT / "v4_engine"

for _p in (str(ALEPH_ROOT), str(LIB_DIR), str(SCRIPTS_DIR), str(V4_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from scripts.formal_verification_z3 import FormalVerifier
except ImportError:
    FormalVerifier = None
try:
    from scripts.neural_code_graph import NeuralCodeGraphPipeline
except ImportError:
    NeuralCodeGraphPipeline = None
try:
    from scripts.aleph_speculative_engine import SpeculativeRaceEngine
except ImportError:
    SpeculativeRaceEngine = None
try:
    from scripts.aleph_diff_engine import AlephPrecisionDiffEngine
except ImportError:
    AlephPrecisionDiffEngine = None


