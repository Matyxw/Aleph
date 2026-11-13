import unittest
from aleph_core.state.epistemic import EpistemicClaim, EpistemicStatus, VerificationGate

class TestEpistemicVerification(unittest.TestCase):
    def test_gate_verifies_correctly(self):
        claim = EpistemicClaim(
            claim_id="c_001",
            description="Test calculation",
            payload={"result": 42}
        )
        self.assertEqual(claim.status, EpistemicStatus.INFERRED)
        self.assertIsNone(claim.proof_hash)
        verifier = lambda p: p.get("result") == 42
        verified = VerificationGate.verify(claim, verifier, proof_context="42 matches expectation")
        self.assertEqual(verified.status, EpistemicStatus.VERIFIED)
        self.assertIsNotNone(verified.proof_hash)
        self.assertIn("matches expectation", verified.proof_output)

    def test_gate_refutes_failed_predicate(self):
        claim = EpistemicClaim(
            claim_id="c_002",
            description="Flawed assertion",
            payload={"result": 99}
        )
        verifier = lambda p: p.get("result") == 100
        verified = VerificationGate.verify(claim, verifier)
        self.assertEqual(verified.status, EpistemicStatus.REFUTED)
        self.assertIsNone(verified.proof_hash)

if __name__ == "__main__":
    unittest.main()
