"""
aleph_core/state/checkpoint.py
Sistema de Checkpointing Jerárquico y Compresión Contextual Estructural (Nivel 6).
Permite pausar, persistir, compactar y reanudar sesiones agénticas en SQLite WAL
garantizando tolerancia a fallos, recuperación tras compactación de contexto y cero pérdida de claims.
"""
import json
import time
import uuid
import zlib
import base64
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from aleph_core.state.store import SessionCheckpoint

class CheckpointManager:
    def __init__(self, store: Any):
        self.store = store
        self._init_checkpoint_table()

    def _init_checkpoint_table(self):
        if hasattr(self.store, "create_session_checkpoint"):
            return
        with self.store._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    parent_checkpoint_id TEXT,
                    active_rule_ids TEXT NOT NULL,
                    compact_summary TEXT NOT NULL,
                    working_memory_json TEXT NOT NULL,
                    compressed_state_blob TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
            """)
            conn.commit()

    def create_checkpoint(
        self,
        session_id: str,
        step_number: int,
        working_memory: Dict[str, Any],
        compact_summary: str,
        active_rule_ids: List[str],
        parent_checkpoint_id: Optional[str] = None
    ) -> SessionCheckpoint:
        if hasattr(self.store, "create_session_checkpoint"):
            return self.store.create_session_checkpoint(
                session_id=session_id,
                step_number=step_number,
                working_memory=working_memory,
                compact_summary=compact_summary,
                active_rule_ids=active_rule_ids,
                parent_checkpoint_id=parent_checkpoint_id,
            )
        cid = f"chk_{uuid.uuid4().hex[:12]}"
        mem_str = json.dumps(working_memory, ensure_ascii=False)
        compressed = base64.b64encode(zlib.compress(mem_str.encode("utf-8"))).decode("ascii")

        chk = SessionCheckpoint(
            checkpoint_id=cid,
            session_id=session_id,
            step_number=step_number,
            parent_checkpoint_id=parent_checkpoint_id,
            active_rule_ids=active_rule_ids,
            compact_summary=compact_summary,
            working_memory_json=mem_str,
            compressed_state_blob=compressed,
            created_at=time.time()
        )

        with self.store._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO session_checkpoints
                (checkpoint_id, session_id, step_number, parent_checkpoint_id, active_rule_ids, compact_summary, working_memory_json, compressed_state_blob, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chk.checkpoint_id, chk.session_id, chk.step_number, chk.parent_checkpoint_id,
                json.dumps(chk.active_rule_ids), chk.compact_summary, chk.working_memory_json,
                chk.compressed_state_blob, chk.created_at
            ))
            conn.commit()
        return chk

    def load_latest_checkpoint(self, session_id: str) -> Optional[SessionCheckpoint]:
        if hasattr(self.store, "load_latest_session_checkpoint"):
            return self.store.load_latest_session_checkpoint(session_id)
        with self.store._connection() as conn:
            row = conn.execute("""
                SELECT * FROM session_checkpoints
                WHERE session_id = ?
                ORDER BY step_number DESC, created_at DESC
                LIMIT 1
            """, (session_id,)).fetchone()
            if not row:
                return None
            return SessionCheckpoint(
                checkpoint_id=row["checkpoint_id"],
                session_id=row["session_id"],
                step_number=row["step_number"],
                parent_checkpoint_id=row["parent_checkpoint_id"],
                active_rule_ids=json.loads(row["active_rule_ids"]),
                compact_summary=row["compact_summary"],
                working_memory_json=row["working_memory_json"],
                compressed_state_blob=row["compressed_state_blob"],
                created_at=row["created_at"]
            )

    @staticmethod
    def restore_memory(checkpoint: SessionCheckpoint) -> Dict[str, Any]:
        from aleph_core.state.store import StateStore
        return StateStore.restore_checkpoint_memory(checkpoint)
