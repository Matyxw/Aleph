#!/usr/bin/env python3
"""Holographic Causal Memory (HCM) & Vector Symbolic Architectures (VSA D=10,240 bits)."""
import hashlib
import re
from typing import Dict, List, Tuple


class HolographicCausalMemoryEngine:
    DIMENSION_BITS = 10240
    _FULL_MASK = (1 << DIMENSION_BITS) - 1

    def __init__(self):
        self.episodes: Dict[str, str] = {}
        self.vectors: Dict[str, int] = {}
        self.records: Dict[str, Dict[str, str]] = {}

    @classmethod
    def project_binary_hv(cls, text: str) -> int:
        """Proyecta texto en un hipervector binario de 10,240 bits mediante bundling mayoritario."""
        tokens = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_:\-]{2,}", text.lower())
        if not tokens:
            tokens = [text.strip().lower() or "empty"]
        n_words = cls.DIMENSION_BITS // 64
        if len(tokens) == 1:
            seed = hashlib.sha256(tokens[0].encode("utf-8")).digest()
            hv = 0
            for idx in range(n_words):
                blk = hashlib.sha256(seed + idx.to_bytes(2, "big")).digest()[:8]
                hv = (hv << 64) | int.from_bytes(blk, "big")
            return hv

        accum = [0] * cls.DIMENSION_BITS
        for tok in tokens:
            tok_hv = cls.project_binary_hv(tok)
            for bit_pos in range(cls.DIMENSION_BITS):
                accum[bit_pos] += 1 if ((tok_hv >> bit_pos) & 1) else -1
        result = 0
        for bit_pos, score in enumerate(accum):
            if score >= 0:
                result |= (1 << bit_pos)
        return result

    @classmethod
    def similarity(cls, hv_a: int, hv_b: int) -> float:
        """Similitud normalizada de Hamming [-1.0, 1.0] entre dos hipervectores de 10,240 bits."""
        diff_bits = (hv_a ^ hv_b).bit_count()
        return round(1.0 - (2.0 * diff_bits) / float(cls.DIMENSION_BITS), 4)

    def store_causal_episode(self, episode_id: str, cause_str: str, effect_str: str, fix_str: str) -> str:
        payload = f"{episode_id}:{cause_str}->{effect_str}=>{fix_str}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.episodes[episode_id] = digest
        self.records[episode_id] = {"cause": cause_str, "effect": effect_str, "fix": fix_str}
        self.vectors[episode_id] = self.project_binary_hv(f"{cause_str} {effect_str} {fix_str}")
        return digest

    def query_similar(self, cue: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Recupera los `top_k` episodios causales más cercanos al hipervector de consulta."""
        if not self.vectors:
            return []
        q_hv = self.project_binary_hv(cue)
        scored = [(ep_id, self.similarity(q_hv, vec)) for ep_id, vec in self.vectors.items()]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[: max(1, top_k)]
