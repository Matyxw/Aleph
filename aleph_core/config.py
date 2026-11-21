"""
aleph_core/config.py
Configuración central y constantes del motor El Aleph (v33.0.0 Sovereign Core).
Aísla los artefactos mutables de tiempo de ejecución (SQLite WAL y bitácoras JSONL) en un directorio
temporal configurable (`ALEPH_DATA_DIR`) para nunca contaminar el árbol de código fuente con archivos `.db`.
"""
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PACKAGE_DATA_DIR = BASE_DIR / "data"
DATA_DIR = Path(
    os.environ.get("ALEPH_DATA_DIR", str(Path(tempfile.gettempdir()) / "aleph_sovereign_runtime"))
).resolve()
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

# Cost Routing & Gemini 4 Asymmetric Profiles (SparkOS / REG-002)
LOCAL_DETERMINISTIC_ENGINE = "local-ast-cas/python-z3"
GEMINI4_HYDROGEN_MODEL = "gemini-4-hydrogen"
GEMINI4_NEON_MODEL = "gemini-4-neon"
GEMINI4_ARGON_MODEL = "gemini-4-argon"
BASELINE_MODEL = GEMINI4_ARGON_MODEL
BASELINE_MARGINAL_COST_USD = 0.00
ANTI_HYPE_MIN_SCORE = 65
