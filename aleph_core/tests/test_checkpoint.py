"""
aleph_core/tests/test_checkpoint.py
"""
import unittest
import tempfile
from pathlib import Path
from aleph_core.engine import AlephEngine
from aleph_core.state.store import StateStore, SessionCheckpoint

class TestCheckpointingV22(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_chk.db"
        self.engine = AlephEngine(engine_id="test_engine_chk", db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_checkpoint_save_and_restore_cycle(self):
        session_id = "sess_demo_101"
        mem_data = {
            "phase": "PHASE_4_VERIFY",
            "active_contract": "safe_divide",
            "verified_claims": ["c_1", "c_2"],
            "intermediate_tokens": 14500
        }
        summary = "Fase 4 completada: safe_divide verificado formalmente en 1.4ms con Z3."

        # 1. Guardar checkpoint
        chk = self.engine.save_session_checkpoint(
            session_id=session_id,
            step_number=4,
            working_memory=mem_data,
            compact_summary=summary,
            domain_category="Código"
        )
        self.assertIsNotNone(chk.checkpoint_id)
        self.assertEqual(chk.step_number, 4)

        # 2. Restaurar checkpoint
        restored = self.engine.resume_session_checkpoint(session_id=session_id)
        self.assertIsNotNone(restored)
        self.assertEqual(restored["step_number"], 4)
        self.assertEqual(restored["compact_summary"], summary)
        self.assertEqual(restored["working_memory"], mem_data)
        self.assertIn("REG-001", restored["active_rules"])

if __name__ == "__main__":
    unittest.main()
