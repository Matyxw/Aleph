#!/usr/bin/env python3
"""
.aleph/v4_engine/holographic_causal_memory.py
Holographic Causal Memory (HCM) & Vector Symbolic Architectures (VSA D=10,240 bits).
Implementa:
1. Hipervectores binarios densos de D = 10,240 bits (1,280 bytes) generados determinísticamente con SHAKE-256.
2. Operador de enlace algebraico XOR autoinverso (Binding: A ^ B ^ B == A).
3. Operador de superposición por regla de mayoría bit a bit (Bundling / Superposition).
4. Permutación cíclica de bits para codificación de orden causal (Cause -> Effect => Fix).
5. Búsqueda asociativa por distancia y similitud de Hamming normalizada (Kanerva SDM).
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class CausalEpisodeRecord:
    episode_id: str
    cause_str: str
    effect_str: str
    fix_str: str
    sha256_digest: str
    hypervector_bytes: bytes


class HolographicCausalMemoryEngine:
    DIMENSION_BITS = 10240
    DIMENSION_BYTES = DIMENSION_BITS // 8  # 1,280 bytes

    def __init__(self):
        self.episodes: Dict[str, str] = {}
        self.episode_records: Dict[str, CausalEpisodeRecord] = {}
        self.symbol_codebook: Dict[str, bytes] = {}

    @classmethod
    def encode_symbol_hypervector(cls, symbol: str) -> bytes:
        """Expande determinísticamente cualquier símbolo o texto en un hipervector de 10,240 bits vía SHAKE-256."""
        return hashlib.shake_256(symbol.encode("utf-8")).digest(cls.DIMENSION_BYTES)

    @classmethod
    def bind_xor(cls, hv_a: bytes, hv_b: bytes) -> bytes:
        """
        Operador de enlace VSA XOR (autoinverso: bind_xor(bind_xor(A, B), B) == A).
        Preserva la distancia de Hamming y es ortogonal a sus operandos.
        """
        if len(hv_a) != cls.DIMENSION_BYTES or len(hv_b) != cls.DIMENSION_BYTES:
            raise ValueError(f"Los hipervectores deben medir exactamente {cls.DIMENSION_BYTES} bytes.")
        int_a = int.from_bytes(hv_a, byteorder="big")
        int_b = int.from_bytes(hv_b, byteorder="big")
        return (int_a ^ int_b).to_bytes(cls.DIMENSION_BYTES, byteorder="big")

    @classmethod
    def permute_cyclic(cls, hv: bytes, byte_shift: int = 1) -> bytes:
        """Permutación cíclica por bytes para distinguir roles posicionales (Causa vs Efecto vs Solución)."""
        n = len(hv)
        shift = byte_shift % n
        if shift == 0:
            return hv
        return hv[-shift:] + hv[:-shift]

    @classmethod
    def bundle_majority(cls, hypervectors: List[bytes]) -> bytes:
        """
        Superposición holográfica por regla de mayoría sobre D=10,240 bits.
        Si el número de vectores es par, desempata con un vector pseudoaleatorio determinista.
        """
        if not hypervectors:
            return b"\x00" * cls.DIMENSION_BYTES
        if len(hypervectors) == 1:
            return hypervectors[0]

        vectors = list(hypervectors)
        if len(vectors) % 2 == 0:
            tie_breaker = cls.encode_symbol_hypervector(f"TIE_BREAKER_{len(vectors)}")
            vectors.append(tie_breaker)

        threshold = len(vectors) // 2
        ints = [int.from_bytes(v, byteorder="big") for v in vectors]
        # Conteo paralelo por bytes para máxima velocidad en Python puro
        out_bytes = bytearray(cls.DIMENSION_BYTES)
        for byte_idx in range(cls.DIMENSION_BYTES):
            b_val = 0
            for bit in range(8):
                mask = 1 << bit
                ones = sum(1 for v in vectors if (v[byte_idx] & mask) != 0)
                if ones > threshold:
                    b_val |= mask
            out_bytes[byte_idx] = b_val
        return bytes(out_bytes)

    @classmethod
    def hamming_similarity(cls, hv_a: bytes, hv_b: bytes) -> float:
        """Calcula la similitud de Hamming normalizada en [0.0, 1.0] sobre D=10,240 bits."""
        int_a = int.from_bytes(hv_a, byteorder="big")
        int_b = int.from_bytes(hv_b, byteorder="big")
        xor_diff = (int_a ^ int_b).bit_count()
        return 1.0 - (xor_diff / float(cls.DIMENSION_BITS))

    def _get_role_hv(self, role_name: str) -> bytes:
        if role_name not in self.symbol_codebook:
            self.symbol_codebook[role_name] = self.encode_symbol_hypervector(f"ROLE::{role_name}")
        return self.symbol_codebook[role_name]

    def store_causal_episode(self, episode_id: str, cause_str: str, effect_str: str, fix_str: str) -> str:
        """
        Codifica holográficamente la tripleta causal:
          E = Bundle( ROLE_CAUSE (*) H(cause), Permute(ROLE_EFFECT (*) H(effect), 1), Permute(ROLE_FIX (*) H(fix), 2) )
        y retorna el digest SHA-256 canónico preservando compatibilidad 100%.
        """
        payload = f"{episode_id}:{cause_str}->{effect_str}=>{fix_str}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.episodes[episode_id] = digest

        h_cause = self.bind_xor(self._get_role_hv("CAUSE"), self.encode_symbol_hypervector(cause_str))
        h_effect = self.permute_cyclic(
            self.bind_xor(self._get_role_hv("EFFECT"), self.encode_symbol_hypervector(effect_str)),
            byte_shift=1,
        )
        h_fix = self.permute_cyclic(
            self.bind_xor(self._get_role_hv("FIX"), self.encode_symbol_hypervector(fix_str)),
            byte_shift=2,
        )
        episode_hv = self.bundle_majority([h_cause, h_effect, h_fix])

        self.episode_records[episode_id] = CausalEpisodeRecord(
            episode_id=episode_id,
            cause_str=cause_str,
            effect_str=effect_str,
            fix_str=fix_str,
            sha256_digest=digest,
            hypervector_bytes=episode_hv,
        )
        return digest

    def query_by_cause(self, cause_str: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recupera los episodios causales más resonantes dado un patrón de causa mediante sondaje VSA."""
        if not self.episode_records:
            return []
        probe_hv = self.bind_xor(self._get_role_hv("CAUSE"), self.encode_symbol_hypervector(cause_str))
        scored: List[Tuple[float, CausalEpisodeRecord]] = []
        for rec in self.episode_records.values():
            sim = self.hamming_similarity(probe_hv, rec.hypervector_bytes)
            scored.append((sim, rec))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {
                "episode_id": rec.episode_id,
                "cause": rec.cause_str,
                "effect": rec.effect_str,
                "fix": rec.fix_str,
                "hamming_similarity": round(sim, 6),
                "sha256_digest": rec.sha256_digest,
            }
            for sim, rec in scored[: max(1, top_k)]
        ]
