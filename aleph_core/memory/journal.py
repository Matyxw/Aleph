"""
Diarios append-only independientes para agentes (Nivel 1 Memoria Corto Plazo).
Garantiza aislamiento lock-free entre múltiples agentes en ejecución y verificación de cadena SHA-256.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
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
        """Lectura O(1) amortizada desde el final del archivo mediante os.SEEK_END."""
        if count <= 0 or not self.journal_file.exists():
            return []
        chunk_size = 8192
        entries: List[Dict[str, Any]] = []
        with open(self.journal_file, "rb") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            buf = b""
            while pos > 0 and len(entries) < count:
                read_size = min(chunk_size, pos)
                pos -= read_size
                f.seek(pos, os.SEEK_SET)
                data = f.read(read_size)
                buf = data + buf
                lines = buf.splitlines()
                # Si pos > 0, lines[0] puede estar cortada a mitad de línea; conservarla en buf.
                if pos > 0 and lines:
                    buf = lines[0]
                    complete_lines = lines[1:]
                else:
                    buf = b""
                    complete_lines = lines
                parsed_chunk: List[Dict[str, Any]] = []
                for raw_line in complete_lines:
                    text_line = raw_line.decode("utf-8").strip()
                    if text_line:
                        parsed_chunk.append(json.loads(text_line))
                entries = parsed_chunk + entries
        return entries[-count:]

    def verify_chain(self) -> Tuple[bool, Optional[int], str]:
        """Verifica criptográficamente la cadena completa de hashes SHA-256 desde GENESIS."""
        if not self.journal_file.exists():
            return True, None, "Journal inexistente (cadena vacía válida)"
        expected_prev = "GENESIS"
        checked = 0
        with open(self.journal_file, "r", encoding="utf-8") as f:
            for line_num, raw in enumerate(f, start=1):
                stripped = raw.strip()
                if not stripped:
                    continue
                try:
                    entry = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    return False, line_num, f"JSON corrupto en línea {line_num}: {exc}"
                if entry.get("prev_hash") != expected_prev:
                    return False, line_num, f"Ruptura de prev_hash en línea {line_num}"
                raw_canonical = json.dumps(
                    {
                        "ts": entry.get("timestamp"),
                        "agent_id": entry.get("agent_id"),
                        "event_type": entry.get("event_type"),
                        "payload": entry.get("payload"),
                        "prev": entry.get("prev_hash"),
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                )
                recomputed = hashlib.sha256(raw_canonical.encode("utf-8")).hexdigest()
                if entry.get("entry_hash") != recomputed:
                    return False, line_num, f"Manipulación detectada en entry_hash (línea {line_num})"
                expected_prev = recomputed
                checked += 1
        return True, None, f"Cadena íntegra ({checked} eventos verificados)"
