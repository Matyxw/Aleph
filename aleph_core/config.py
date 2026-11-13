"""
Configuración central y constantes del motor El Aleph (v2.0 Sovereign Core).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
JOURNALS_DIR = DATA_DIR / "journals"
DB_PATH = DATA_DIR / "aleph_state.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
JOURNALS_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros operativos y límites deterministas
DEFAULT_LEASE_TIMEOUT_SEC = 15.0
MAX_REDUCER_TOKENS = 1500
SQLITE_TIMEOUT_SEC = 10.0
Z3_SOLVER_TIMEOUT_MS = 45
PBT_MAX_EXAMPLES = 150

# Cost Routing Baseline (SparkOS / REG-002)
BASELINE_MODEL = "gemini-4-argon"
BASELINE_MARGINAL_COST_USD = 0.00
ANTI_HYPE_MIN_SCORE = 65
