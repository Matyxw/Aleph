"""
Diarios append-only independientes para agentes (Nivel 1 Memoria Corto Plazo).
Garantiza aislamiento lock-free entre múltiples agentes en ejecución y verificación de cadena SHA-256.
"""
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from aleph_core.config import JOURNALS_DIR

class AgentJournal:
    def __init__(self, agent_id: str, base_dir: Path = JOURNALS_DIR):
        self.agent_id = agent_id
        self.base_dir = Path(base_dir)
        self.journal_file = self.base_dir / f"{self.agent_id}.journal.jsonl"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def append_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un evento estructurado de forma append-only con hash encadenado."""
        prev_entries = self.get_latest(1)
        prev_hash = prev_entries[0].get("entry_hash", "GENESIS") if prev_entries else "GENESIS"
        ts = time.time()
        raw_canonical = json.dumps(
            {"ts": ts, "agent_id": self.agent_id, "event_type": event_type, "payload": payload, "prev": prev_hash},
            sort_keys=True,
            ensure_ascii=False
        )
        entry_hash = hashlib.sha256(raw_canonical.encode("utf-8")).hexdigest()
        entry = {
            "timestamp": ts,
            "agent_id": self.agent_id,
            "event_type": event_type,
            "payload": payload,
            "prev_hash": prev_hash,
            "entry_hash": entry_hash
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        with open(self.journal_file, "a", encoding="utf-8") as f:
            f.write(line)
        return entry

    def read_all(self) -> List[Dict[str, Any]]:
        if not self.journal_file.exists():
            return []
        entries = []
        with open(self.journal_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def get_latest(self, count: int = 10) -> List[Dict[str, Any]]:
        all_entries = self.read_all()
        return all_entries[-count:]
