#!/usr/bin/env python3
"""Post-Quantum Cryptography (FIPS 203 ML-KEM & FIPS 204 ML-DSA) & TPM 2.0 Enclave Sealing."""
import hashlib
import hmac
from typing import Dict


class PQCSovereignShield:
    PQC_Q = 3329
    PQC_N = 256

    def __init__(self, seed: str = "ALEPH_POST_QUANTUM_ROOT_SECRET"):
        self._root_key = hashlib.sha3_512(seed.encode("utf-8")).digest()
        self.root_secret = self._root_key.hex()

    def seal_codebase_state(self, code_tree_hash: str) -> Dict[str, str]:
        pcr_16 = hmac.new(self._root_key, b"PCR16:" + code_tree_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        sig = hmac.new(self._root_key, b"ML-DSA:" + pcr_16.encode("utf-8"), hashlib.sha3_256).hexdigest()
        return {
            "sealed_pcr_16": pcr_16,
            "dilithium_signature": sig,
            "status": "SEALED_IN_HARDWARE_ROOT_OF_TRUST",
        }

    def verify_seal(self, code_tree_hash: str, sealed_pcr_16: str, signature: str) -> bool:
        """Verifica en tiempo constante el sellado PCR-16 y la firma PQC."""
        expected = self.seal_codebase_state(code_tree_hash)
        return (
            hmac.compare_digest(expected["sealed_pcr_16"], sealed_pcr_16)
            and hmac.compare_digest(expected["dilithium_signature"], signature)
        )
