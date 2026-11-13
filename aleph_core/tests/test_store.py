import unittest
import tempfile
from pathlib import Path
from aleph_core.state.store import StateStore
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus

class TestStateStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_store.db"
        self.store = StateStore(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sqlite_wal_persistence(self):
        claim = EpistemicClaim(
            claim_id="test_c1",
            description="Persistent claim",
            payload={"key": "value"},
            status=EpistemicStatus.VERIFIED,
            proof_hash="sha256_mock_hash",
            proof_output="Test passed"
        )
        self.store.save_claim(claim)
        retrieved = self.store.get_claim("test_c1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.claim_id, "test_c1")
        self.assertEqual(retrieved.status, EpistemicStatus.VERIFIED)
        self.assertEqual(retrieved.payload, {"key": "value"})

    def test_lease_concurrency(self):
        acquired = self.store.acquire_lease("resource_A", "agent_1", timeout_sec=2.0)
        self.assertTrue(acquired)
        blocked = self.store.acquire_lease("resource_A", "agent_2", timeout_sec=2.0)
        self.assertFalse(blocked)
        released = self.store.release_lease("resource_A", "agent_1")
        self.assertTrue(released)
        now_acquired = self.store.acquire_lease("resource_A", "agent_2", timeout_sec=2.0)
        self.assertTrue(now_acquired)

    def test_atomic_file_write(self):
        target = Path(self.temp_dir.name) / "subfolder" / "atomic.txt"
        content = "CONTENIDO_ATÓMICO_VERIFICADO"
        StateStore.atomic_write_file(target, content)
        self.assertTrue(target.exists())
        with open(target, "r", encoding="utf-8") as f:
            read_content = f.read()
        self.assertEqual(read_content, content)


    def test_session_checkpoint_save_and_restore(self):
        mem = {"step": 4, "task": "compile_rust", "tokens": 12500}
        chk = self.store.create_session_checkpoint(
            session_id="sess_core_1",
            step_number=4,
            working_memory=mem,
            compact_summary="Paso 4 compilado",
            active_rule_ids=["REG-001", "REG-006"]
        )
        self.assertIsNotNone(chk.checkpoint_id)
        latest = self.store.load_latest_session_checkpoint("sess_core_1")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.step_number, 4)
        restored = StateStore.restore_checkpoint_memory(latest)
        self.assertEqual(restored, mem)


    def test_semantic_task_cache_ast_normalization(self):
        payload = {"x": 10}
        code_v1 = "def fn(a: int):\n    # Comentario 1\n    return a + 1\n"
        code_v2 = "def fn(a: int):\n\n    # Comentario diferente con otros espacios\n    return a + 1\n"
        
        # Guardar en cache con code_v1
        ck = self.store.store_semantic_cache(
            task_type="proof_task",
            input_payload=payload,
            output_payload={"verified": True},
            epistemic_status="FORMALLY_PROVEN",
            proof_hash="hash_123",
            formal_source_code=code_v1
        )
        self.assertIsNotNone(ck)

        # Consultar con code_v2 (mismo AST estructural pero comentarios y espacios distintos) -> DEBE SER CACHE HIT
        hit = self.store.query_semantic_cache(
            task_type="proof_task",
            input_payload=payload,
            formal_source_code=code_v2
        )
        self.assertIsNotNone(hit)
        self.assertEqual(hit.epistemic_status, "FORMALLY_PROVEN")
        self.assertEqual(hit.hit_count, 2)

if __name__ == "__main__":
    unittest.main()
