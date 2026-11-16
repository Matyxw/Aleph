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

        # Idempotencia: re-verificar un claim ya VERIFIED conserva su estado y hash
        hash_before = verified.proof_hash
        verified_again = VerificationGate.verify(verified, lambda _: False)
        self.assertEqual(verified_again.status, EpistemicStatus.VERIFIED)
        self.assertEqual(verified_again.proof_hash, hash_before)

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

    def test_gate_refutes_on_verifier_exception_and_serializes_to_dict(self):
        claim = EpistemicClaim(
            claim_id="c_003",
            description="Exception raising verifier",
            payload={"x": 0}
        )
        def bad_verifier(p):
            if not isinstance(p, dict) or p.get("x", 0) == 0:
                raise ZeroDivisionError("Simulated division by zero in verifier")
            return True
        refuted = VerificationGate.verify(claim, bad_verifier)
        self.assertEqual(refuted.status, EpistemicStatus.REFUTED)
        self.assertIn("exception", refuted.proof_output.lower())
        d = refuted.to_dict()
        self.assertEqual(d["claim_id"], "c_003")
        self.assertEqual(d["status"], "REFUTED")

    def test_verify_formal_proves_safe_function_and_refutes_buggy_function(self):
        safe_code = (
            '@requires("y != 0")\n'
            'def safe_div(x: int, y: int) -> int:\n'
            '    return x // y\n'
        )
        claim_safe = EpistemicClaim(claim_id="c_formal_ok", description="Safe division", payload={})
        res_safe = VerificationGate.verify_formal(claim_safe, source_code=safe_code)
        self.assertEqual(res_safe.status, EpistemicStatus.FORMALLY_PROVEN)
        self.assertIsNotNone(res_safe.proof_hash)

        buggy_code = (
            'def unsafe_div(x: int, y: int) -> int:\n'
            '    return x // y\n'
        )
        claim_buggy = EpistemicClaim(claim_id="c_formal_bad", description="Unsafe division", payload={})
        res_buggy = VerificationGate.verify_formal(claim_buggy, source_code=buggy_code)
        self.assertEqual(res_buggy.status, EpistemicStatus.REFUTED)
        self.assertEqual(res_buggy.metadata.get("defect_type"), "ZERO_DIVISION")


if __name__ == "__main__":
    unittest.main()
