import unittest
import tempfile
from pathlib import Path
from aleph_core.engine import AlephEngine
from aleph_core.verification.semantic_patch import SemanticPatchEngine, SemanticPatchResult

class TestSemanticPatchEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_patch.db"
        self.engine = AlephEngine(engine_id="test_engine_patch", db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_semantic_patch_accepts_proven_safe_replacement(self):
        original_code = """
def calculate_ratio(a: int, b: int) -> int:
    return a * 2

def helper():
    return 1
"""
        safe_replacement = """
@requires("b != 0")
def calculate_ratio(a: int, b: int) -> int:
    return a // b
"""
        target_file = Path(self.temp_dir.name) / "service.py"
        target_file.write_text(original_code, encoding="utf-8")

        res = self.engine.apply_verified_semantic_patch(
            original_source=original_code,
            target_function_name="calculate_ratio",
            replacement_function_source=safe_replacement,
            target_file_path=target_file
        )
        self.assertTrue(res.success)
        self.assertTrue(res.formal_proof_passed)
        self.assertEqual(res.proof_status, "PROVEN_SAFE")
        self.assertIn("-    return a * 2", res.diff_unified)
        self.assertIn("+    return a // b", res.diff_unified)
        self.assertTrue(target_file.exists())
        self.assertIn("def helper():", target_file.read_text(encoding="utf-8"))

    def test_semantic_patch_rejects_buggy_regression(self):
        original_code = """
def divide_items(a: int, b: int) -> int:
    return a
"""
        buggy_replacement = """
def divide_items(a: int, b: int) -> int:
    return a // b
"""
        res = self.engine.apply_verified_semantic_patch(
            original_source=original_code,
            target_function_name="divide_items",
            replacement_function_source=buggy_replacement
        )
        self.assertFalse(res.success)
        self.assertFalse(res.formal_proof_passed)
        self.assertEqual(res.proof_status, "DEFECT_FOUND")
        self.assertIn("ZERO_DIVISION", res.error)

if __name__ == "__main__":
    unittest.main()
