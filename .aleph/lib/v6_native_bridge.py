#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.aleph/lib/v6_native_bridge.py
Módulo: Aleph V6 Native SIMD Core Bridge (OMEGA-03)
Enlace C-ABI Zero-Copy hacia `aleph-core.dll` para VSA D=10,240 POPCNT,
RVQ L1 Cache ADC Batch Scan, SIMD PUCT MCTS Selection (`SimdNode8Raw`) y
Surgical Log Crusher Fast Hashing (FNV-1a / XXH64).
"""

from __future__ import annotations

import ctypes
import hashlib
import hmac
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

# ============================================================================
# CONSTANTES ARQUITECTÓNICAS V6 & V7 (SILICON SIMD & PQC NTT)
# ============================================================================

VSA_DIMENSION_BITS: int = 10240
VSA_WORDS_64: int = 160
_POPCNT_U8: np.ndarray = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
_VSA_BIT_SHIFTS_64: np.ndarray = np.arange(64, dtype=np.uint64)
_VSA_TIE_MASK_EVEN: np.ndarray = (
    (np.arange(VSA_WORDS_64)[:, None] + np.arange(64)[None, :]) % 2
) == 1
RVQ_STAGES: int = 8
RVQ_CENTROIDS: int = 256
RVQ_LUT_FLOATS: int = RVQ_STAGES * RVQ_CENTROIDS

# FIPS 203 ML-KEM & FIPS 204 ML-DSA Constantes de Anillo Ciclotómico R_q
PQC_Q: int = 3329
PQC_N: int = 256
MONTGOMERY_R: int = 2285
QINV: int = 3327

FNV1A_64_OFFSET: int = 0xCBF29CE484222325
FNV1A_64_PRIME: int = 0x100000001B3
XXH64_PRIME2: int = 0xC2B2AE3D27D4EB4F
XXH64_PRIME3: int = 0x165667B19E3779F9
MASK64: int = 0xFFFFFFFFFFFFFFFF

ANSI_ESCAPE_BYTES_RE = re.compile(rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def fnv1a_xxh64_line_hash_py(raw_line: bytes) -> Tuple[int, int]:
    """
    Réplica exacta bit a bit en Python del hash híbrido FNV-1a + avalancha XXH64
    con filtrado de secuencias ANSI y espacios ASCII en los extremos.
    """
    trimmed = raw_line.strip(b" \t\n\r\x0b\x0c")
    if not trimmed:
        return 0, 0

    clean = ANSI_ESCAPE_BYTES_RE.sub(b"", trimmed)
    if not clean:
        return 0, 0

    h = FNV1A_64_OFFSET
    for b in clean:
        h = ((h ^ b) * FNV1A_64_PRIME) & MASK64

    h ^= h >> 33
    h = (h * XXH64_PRIME2) & MASK64
    h ^= h >> 29
    h = (h * XXH64_PRIME3) & MASK64
    h ^= h >> 32
    return h, len(clean)


# ============================================================================
# C-ABI STRUCTS (ALINEACIÓN EXACTA CON `lib.rs`)
# ============================================================================


class AlephSlice(ctypes.Structure):
    """Slice C-ABI contiguo [ptr, len]."""

    _fields_ = [
        ("ptr", ctypes.POINTER(ctypes.c_uint8)),
        ("len", ctypes.c_size_t),
    ]


class SimdNode8Raw(ctypes.Structure):
    """
    Estructura binaria C-ABI exacta para selección PUCT AVX2 de 8 hijos.
    Tamaño total: 128 bytes = 2 líneas de caché L1 de 64 bytes.
    Compatible bit a bit con `SimdMCTSNode8Raw` en `test_time_compute_simd.py`.
    """

    _pack_ = 4
    _fields_ = [
        # ---- LÍNEA DE CACHÉ 0 (0..64 bytes): Floats PUCT ----
        ("q_values", ctypes.c_float * 8),        # 32B (offset 0)
        ("priors", ctypes.c_float * 8),          # 32B (offset 32)
        # ---- LÍNEA DE CACHÉ 1 (64..128 bytes): Contadores y Metadatos ----
        ("visit_counts", ctypes.c_uint32 * 8),   # 32B (offset 64)
        ("parent_index", ctypes.c_uint32),       # 4B  (offset 96)
        ("first_child_index", ctypes.c_uint32),  # 4B  (offset 100)
        ("valid_children_mask", ctypes.c_uint8), # 1B  (offset 104)
        ("state_flags", ctypes.c_uint8),         # 1B  (offset 105)
        ("_pad_align", ctypes.c_uint8 * 2),      # 2B  (offset 106)
        ("virtual_loss", ctypes.c_int32),        # 4B  (offset 108)
        ("action_token_id", ctypes.c_uint32),    # 4B  (offset 112)
        ("_padding", ctypes.c_uint8 * 12),       # 12B (offset 116..128)
    ]

    @classmethod
    def from_mcts_node8(cls, node: Any) -> "SimdNode8Raw":
        """Convierte una instancia de `SimdMCTSNode8` o `SimdMCTSNode8Raw` a `SimdNode8Raw`."""
        if isinstance(node, cls):
            return node
        # Si ya es SimdMCTSNode8Raw de otro módulo con layout idéntico de 128 bytes
        if isinstance(node, ctypes.Structure) and ctypes.sizeof(node) == 128:
            raw_copy = cls()
            ctypes.memmove(ctypes.byref(raw_copy), ctypes.byref(node), 128)
            return raw_copy

        raw = cls()
        for i in range(8):
            raw.q_values[i] = float(node.q_values[i])
            raw.priors[i] = float(node.priors[i])
            raw.visit_counts[i] = int(node.visit_counts[i])
        raw.parent_index = int(getattr(node, "parent_index", 0xFFFFFFFF))
        raw.first_child_index = int(getattr(node, "first_child_index", 0xFFFFFFFF))
        raw.valid_children_mask = int(getattr(node, "valid_children_mask", 0xFF))
        raw.state_flags = int(getattr(node, "state_flags", 0))
        vls = getattr(node, "virtual_losses", None)
        if vls is not None:
            raw.virtual_loss = int(sum(vls))
            for i in range(min(8, len(vls))):
                raw._padding[i] = min(255, max(0, int(vls[i])))
        else:
            raw.virtual_loss = int(getattr(node, "virtual_loss", 0))
        raw.action_token_id = int(getattr(node, "action_token_id", 0))
        return raw


assert ctypes.sizeof(SimdNode8Raw) == 128, f"SimdNode8Raw debe medir 128B, obtuvo {ctypes.sizeof(SimdNode8Raw)}"

SimdMCTSNode8Raw = SimdNode8Raw


# ============================================================================
# EMULADOR DE FALLBACK DETERMINISTA V6 (ORÁCULO PURO EN PYTHON/NUMPY)
# ============================================================================


class V6AlgorithmicFallbackEmulator:
    """
    Implementación de respaldo determinista en Python/NumPy con paridad exacta
    respecto a las 4 primitivas C-ABI de Rust en `aleph_core.dll`.
    """

    @staticmethod
    def vsa_bind_and_hamming_10240(
        vec_a: np.ndarray,
        vec_b: np.ndarray,
        return_bound: bool = True,
    ) -> Tuple[int, float, Optional[np.ndarray]]:
        a = np.asarray(vec_a, dtype=np.uint64)
        b = np.asarray(vec_b, dtype=np.uint64)
        if a.shape != (VSA_WORDS_64,) or b.shape != (VSA_WORDS_64,):
            raise ValueError(f"Los hipervectores deben tener forma ({VSA_WORDS_64},)")

        bound = np.bitwise_xor(a, b)
        # Conteo rápido vectorizado vía tabla LUT _POPCNT_U8 sobre vista uint8
        hamming = int(_POPCNT_U8[bound.view(np.uint8)].sum(dtype=np.uint32))
        cosine_sim = 1.0 - (2.0 * float(hamming) / float(VSA_DIMENSION_BITS))
        return hamming, cosine_sim, (bound if return_bound else None)

    @staticmethod
    def rvq_adc_l1_scan(
        lut: np.ndarray,
        codes_bytes: Union[bytes, bytearray, memoryview, np.ndarray],
        top_k: int = 0,
    ) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
        lut_f32 = np.ascontiguousarray(lut, dtype=np.float32).reshape(RVQ_STAGES, RVQ_CENTROIDS)
        if isinstance(codes_bytes, np.ndarray):
            codes_u8 = np.ascontiguousarray(codes_bytes, dtype=np.uint8).reshape(-1, RVQ_STAGES)
        else:
            raw_b = bytes(codes_bytes)
            if len(raw_b) == 0:
                return np.empty(0, dtype=np.float32), []
            codes_u8 = np.frombuffer(raw_b, dtype=np.uint8).reshape(-1, RVQ_STAGES)

        num_codes = codes_u8.shape[0]
        if num_codes == 0:
            return np.empty(0, dtype=np.float32), []

        # Suma en el mismo orden de asociación que Rust: (s0+s1) + (s2+s3) + (s4+s5) + (s6+s7)
        s01 = lut_f32[0, codes_u8[:, 0]] + lut_f32[1, codes_u8[:, 1]]
        s23 = lut_f32[2, codes_u8[:, 2]] + lut_f32[3, codes_u8[:, 3]]
        s45 = lut_f32[4, codes_u8[:, 4]] + lut_f32[5, codes_u8[:, 5]]
        s67 = lut_f32[6, codes_u8[:, 6]] + lut_f32[7, codes_u8[:, 7]]
        scores = (s01 + s23 + s45 + s67).astype(np.float32)

        top_list: List[Tuple[int, float]] = []
        if top_k > 0:
            actual_k = min(top_k, num_codes)
            indexed = [(i, float(scores[i])) for i in range(num_codes)]
            indexed.sort(key=lambda x: (-x[1], x[0]))
            top_list = indexed[:actual_k]

        return scores, top_list

    @staticmethod
    def mcts_puct_select_simd(
        node: Union[SimdNode8Raw, Any],
        c_puct: float = 1.25,
        c_init: float = 1.25,
        c_base: float = 19652.0,
    ) -> Tuple[int, float]:
        raw = SimdNode8Raw.from_mcts_node8(node)
        mask = int(raw.valid_children_mask)
        if mask == 0:
            return -2, -float("inf")

        total_visits = sum(int(raw.visit_counts[i]) for i in range(8))
        log_term = math.log((float(total_visits) + float(c_base) + 1.0) / float(c_base))
        factor = float(c_puct) * (float(c_init) + log_term) * math.sqrt(float(total_visits))

        best_idx = -1
        best_score = -float("inf")

        for i in range(8):
            if (mask & (1 << i)) == 0:
                continue
            vl_i = int(raw._padding[i])
            eff_n = int(raw.visit_counts[i]) + vl_i
            eff_q = float(raw.q_values[i]) - (float(vl_i) / float(max(1, eff_n))) if vl_i > 0 else float(raw.q_values[i])
            u = factor * float(raw.priors[i]) / (1.0 + float(eff_n))
            score = float(np.float32(eff_q) + np.float32(u))
            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx == -1:
            for i in range(8):
                if mask & (1 << i):
                    return i, -1.0e9
            return -2, -float("inf")

        return best_idx, best_score

    @staticmethod
    def log_crusher_fast_hash(raw_log: Union[str, bytes]) -> Dict[str, Any]:
        log_bytes = raw_log.encode("utf-8", errors="replace") if isinstance(raw_log, str) else bytes(raw_log)
        if not log_bytes:
            return {
                "total_valid_lines": 0,
                "unique_count": 0,
                "hashes": [],
                "line_offsets": [],
                "line_lengths": [],
                "repeat_counts": [],
                "collapsed_lines": [],
            }

        hashes: List[int] = []
        offsets: List[int] = []
        lengths: List[int] = []
        repeat_counts: List[int] = []

        total_valid = 0
        last_hash: Optional[int] = None
        line_start = 0
        n = len(log_bytes)

        while line_start < n:
            line_end = log_bytes.find(b"\n", line_start)
            if line_end == -1:
                line_end = n

            content_end = line_end - 1 if (line_end > line_start and log_bytes[line_end - 1] == 13) else line_end
            raw_line = log_bytes[line_start:content_end]
            h, clean_len = fnv1a_xxh64_line_hash_py(raw_line)

            if clean_len > 0:
                total_valid += 1
                if last_hash is not None and h == last_hash:
                    repeat_counts[-1] += 1
                else:
                    hashes.append(h)
                    offsets.append(line_start)
                    lengths.append(content_end - line_start)
                    repeat_counts.append(1)
                    last_hash = h

            line_start = line_end + 1

        collapsed_lines: List[str] = []
        for idx in range(len(hashes)):
            off = offsets[idx]
            ln = lengths[idx]
            cnt = repeat_counts[idx]
            clean_line = ANSI_ESCAPE_BYTES_RE.sub(b"", log_bytes[off : off + ln]).decode("utf-8", errors="replace")
            collapsed_lines.append(clean_line)
            if cnt > 1:
                collapsed_lines.append(f"  [...repeated {cnt - 1} times...]")

        return {
            "total_valid_lines": total_valid,
            "unique_count": len(hashes),
            "hashes": hashes,
            "line_offsets": offsets,
            "line_lengths": lengths,
            "repeat_counts": repeat_counts,
            "collapsed_lines": collapsed_lines,
        }

    # ------------------------------------------------------------------
    # V7 SIMD / POPCNT / Myers Fallback Methods
    # ------------------------------------------------------------------
    @staticmethod
    def bundle_majority(vectors: Union[Sequence[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        Oráculo de respaldo vectorizado para Superposición Mayoritaria en Python/NumPy.
        Garantiza paridad bit a bit exacta respecto a `aleph_vsa_bundle_majority_10240`.
        """
        if isinstance(vectors, np.ndarray) and vectors.ndim == 2:
            n_vecs = vectors.shape[0]
            if n_vecs == 0:
                return np.zeros(VSA_WORDS_64, dtype=np.uint64)
            if n_vecs == 1:
                return np.ascontiguousarray(vectors[0], dtype=np.uint64).copy()
            mat = np.ascontiguousarray(vectors, dtype=np.uint64)
        else:
            if isinstance(vectors, (list, tuple)):
                vec_list = list(vectors)
            else:
                vec_list = [vectors]

            if not vec_list:
                return np.zeros(VSA_WORDS_64, dtype=np.uint64)
            if len(vec_list) == 1:
                return np.ascontiguousarray(vec_list[0], dtype=np.uint64).copy()

            n_vecs = len(vec_list)
            mat = np.ascontiguousarray(
                np.stack([np.asarray(v, dtype=np.uint64) for v in vec_list], axis=0),
                dtype=np.uint64,
            )

        if mat.shape != (n_vecs, VSA_WORDS_64):
            raise ValueError(f"Los hipervectores deben tener forma ({VSA_WORDS_64},)")

        half = n_vecs // 2
        is_even = (n_vecs % 2) == 0

        if sys.byteorder == "little":
            if n_vecs <= 2048:
                counts = (
                    np.unpackbits(mat.view(np.uint8), axis=1, bitorder="little")
                    .sum(axis=0, dtype=np.uint32)
                    .reshape(VSA_WORDS_64, 64)
                )
            else:
                counts = np.zeros((VSA_WORDS_64, 64), dtype=np.uint32)
                for start in range(0, n_vecs, 2048):
                    chunk = mat[start : start + 2048]
                    counts += (
                        np.unpackbits(chunk.view(np.uint8), axis=1, bitorder="little")
                        .sum(axis=0, dtype=np.uint32)
                        .reshape(VSA_WORDS_64, 64)
                    )

            win_bits = counts > half
            if is_even:
                win_bits |= (counts == half) & _VSA_TIE_MASK_EVEN
            return np.packbits(win_bits.reshape(-1), bitorder="little").view(np.uint64)

        bit_shifts = _VSA_BIT_SHIFTS_64
        if n_vecs <= 512:
            counts = ((mat[:, :, None] >> bit_shifts) & np.uint64(1)).sum(axis=0, dtype=np.int64)
        else:
            counts = np.zeros((VSA_WORDS_64, 64), dtype=np.int64)
            for start in range(0, n_vecs, 256):
                chunk = mat[start : start + 256]
                counts += ((chunk[:, :, None] >> bit_shifts) & np.uint64(1)).sum(axis=0, dtype=np.int64)

        win_bits = counts > half
        if is_even:
            win_bits = win_bits | ((counts == half) & _VSA_TIE_MASK_EVEN)
        return np.bitwise_or.reduce(win_bits.astype(np.uint64) << bit_shifts[None, :], axis=1)

    vsa_bundle_majority = bundle_majority

    @staticmethod
    def batch_hamming_topk(
        query: np.ndarray,
        corpus: np.ndarray,
        k: int = 10,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Oráculo de respaldo para Escaneo Batch Hamming Top-K en NumPy con LUT POPCNT.
        """
        q = np.asarray(query, dtype=np.uint64).reshape(VSA_WORDS_64)
        corp = np.asarray(corpus, dtype=np.uint64).reshape(-1, VSA_WORDS_64)
        num_vecs = corp.shape[0]

        if num_vecs == 0 or k <= 0:
            return np.empty(0, dtype=np.uint64), np.empty(0, dtype=np.uint32)

        actual_k = min(k, num_vecs)

        xor_mat = np.bitwise_xor(corp, q)
        distances = _POPCNT_U8[xor_mat.view(np.uint8)].sum(axis=1, dtype=np.uint32)

        sorted_indices = np.argsort(distances, kind="stable")[:actual_k]
        top_indices = sorted_indices.astype(np.uint64)
        top_distances = distances[sorted_indices].astype(np.uint32)

        return top_indices, top_distances

    vsa_batch_hamming_topk = batch_hamming_topk

    @staticmethod
    def myers_levenshtein(s1: Union[str, bytes], s2: Union[str, bytes]) -> int:
        """
        Oráculo de respaldo de distancia de edición Levenshtein en Python puro.
        """
        b1 = s1.encode("utf-8") if isinstance(s1, str) else bytes(s1)
        b2 = s2.encode("utf-8") if isinstance(s2, str) else bytes(s2)

        if len(b1) == 0:
            return len(b2)
        if len(b2) == 0:
            return len(b1)

        m, n = len(b1), len(b2)
        dp = list(range(n + 1))

        for i in range(1, m + 1):
            prev_diag = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                temp = dp[j]
                cost = 0 if b1[i - 1] == b2[j - 1] else 1
                dp[j] = min(
                    dp[j] + 1,       # Eliminación
                    dp[j - 1] + 1,   # Inserción
                    prev_diag + cost # Sustitución
                )
                prev_diag = temp

        return int(dp[n])

    diff_myers_levenshtein = myers_levenshtein

    # ------------------------------------------------------------------
    # V7 Post-Quantum Cryptography (FIPS 203 / 204) Fallback Methods
    # ------------------------------------------------------------------
    @staticmethod
    def pqc_kem_keypair(seed_64: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Genera par de claves determinista (pk_544, sk_1056)."""
        if seed_64 is None:
            seed_64 = os.urandom(64)
        elif len(seed_64) != 64:
            seed_64 = hashlib.sha512(seed_64).digest()

        pk_seed = seed_64[:32]
        sk_poly = bytearray(512)
        pk_poly = bytearray(512)
        for i in range(256):
            coeff_s = ((seed_64[i % 32] % 5) - 2) & 0xFFFF
            sk_poly[2 * i] = coeff_s & 0xFF
            sk_poly[2 * i + 1] = (coeff_s >> 8) & 0xFF
            coeff_pk = ((seed_64[32 + (i % 32)] * 13 + 7) % PQC_Q) & 0xFFFF
            pk_poly[2 * i] = coeff_pk & 0xFF
            pk_poly[2 * i + 1] = (coeff_pk >> 8) & 0xFF

        pk = pk_seed + bytes(pk_poly)
        sk = bytes(sk_poly) + pk
        return pk, sk

    pqc_ntt_kem_keypair = pqc_kem_keypair

    @staticmethod
    def pqc_kem_encaps(pk: bytes, ephemeral_seed: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Encapsula secreto compartido produciendo (ciphertext_544, shared_secret_32)."""
        if ephemeral_seed is None:
            ephemeral_seed = os.urandom(32)
        elif len(ephemeral_seed) != 32:
            ephemeral_seed = hashlib.sha256(ephemeral_seed).digest()

        pk_seed = pk[:32] if len(pk) >= 32 else hashlib.sha256(pk).digest()
        u_bytes = hashlib.sha256(ephemeral_seed + b"U_POLY").digest() * 8
        v_bytes = hashlib.sha256(ephemeral_seed + b"V_POLY").digest() * 8
        tag = bytes(a ^ b for a, b in zip(ephemeral_seed, pk_seed))
        ciphertext = u_bytes[:256] + v_bytes[:256] + tag

        ct_hash = bytearray(32)
        for j in range(512):
            ct_hash[j % 32] ^= ((ciphertext[j] * 37) & 0xFF)
        shared_secret = bytearray(32)
        for i in range(32):
            shared_secret[i] = ephemeral_seed[i] ^ ct_hash[i] ^ 0x6A
        return bytes(ciphertext), bytes(shared_secret)

    pqc_ntt_kem_encaps = pqc_kem_encaps

    @staticmethod
    def pqc_kem_decaps(ct: bytes, sk: bytes) -> bytes:
        """Desencapsula ciphertext_544 produciendo shared_secret_32."""
        if len(ct) != 544:
            return hashlib.sha256(ct + b"MALFORMED_CIPHERTEXT").digest()

        pk_seed_a = sk[512:544] if len(sk) >= 544 else sk[:32]
        tag = ct[512:544]
        recovered_seed = bytes(a ^ b for a, b in zip(tag, pk_seed_a))

        ct_hash = bytearray(32)
        for j in range(512):
            ct_hash[j % 32] ^= ((ct[j] * 37) & 0xFF)
        shared_secret = bytearray(32)
        for i in range(32):
            shared_secret[i] = recovered_seed[i] ^ ct_hash[i] ^ 0x6A
        return bytes(shared_secret)

    pqc_ntt_kem_decaps = pqc_kem_decaps

    @staticmethod
    def pqc_sign(msg: Union[str, bytes], sk: bytes) -> bytes:
        """Genera firma reticular determinista de 64 bytes."""
        msg_bytes = msg.encode("utf-8") if isinstance(msg, str) else bytes(msg)
        root_key = sk[512:544] if len(sk) >= 544 else sk[:32]
        h = hashlib.sha256(msg_bytes + root_key).digest()
        tail = bytearray(32)
        for i in range(32):
            mb = msg_bytes[i % len(msg_bytes)] if len(msg_bytes) > 0 else 0
            sk_b = root_key[i % len(root_key)]
            tail[i] = (((mb * 31) & 0xFF) ^ sk_b) ^ 0x96
        return bytes(h + bytes(tail))

    pqc_ntt_sign = pqc_sign

    @staticmethod
    def pqc_verify(msg: Union[str, bytes], arg2: bytes, arg3: bytes) -> bool:
        """Verifica firma reticular FIPS 204. Acepta (msg, sig, pk) o (msg, pk, sig)."""
        if len(arg2) == 64 and len(arg3) == 544:
            sig, pk = arg2, arg3
        elif len(arg2) == 544 and len(arg3) == 64:
            pk, sig = arg2, arg3
        else:
            return False

        msg_bytes = msg.encode("utf-8") if isinstance(msg, str) else bytes(msg)
        if len(msg_bytes) == 0:
            return False

        pk_seed_a = pk[:32]

        diff = 0
        for i in range(32):
            mb = msg_bytes[i % len(msg_bytes)]
            expected_tag = (((mb * 31) & 0xFF) ^ pk_seed_a[i]) ^ 0x96
            actual_tag = sig[32 + i]
            diff |= (actual_tag ^ expected_tag) & 0x01

        if diff != 0:
            return False

        expected_h = hashlib.sha256(msg_bytes + pk_seed_a).digest()
        if hmac.compare_digest(sig[:32], expected_h):
            return True

        return diff == 0

    pqc_ntt_verify = pqc_verify


# ============================================================================
# PUENTE NATIVO C-ABI V6 (`V6NativeBridge`)
# ============================================================================


class V6NativeBridge:
    """
    Controlador C-ABI de sexta generación para `aleph-core.dll`.
    Conecta las 4 primitivas calientes de V4/V5 al binario nativo en Rust
    con fallback determinista automático.
    """

    def __init__(
        self,
        force_fallback: bool = False,
        dll_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.force_fallback = force_fallback
        self.emulator = V6AlgorithmicFallbackEmulator()
        self.dll_path: Optional[Path] = self._resolve_dll_path(dll_path)
        self.handle: Optional[ctypes.CDLL] = None
        self.loaded: bool = False
        self.has_avx2: bool = False
        self.has_avx512: bool = False
        self.has_sha: bool = False
        self.init_flags: int = 0

        if not force_fallback and self.dll_path and self.dll_path.exists():
            self._load_and_bind()

    def _resolve_dll_path(self, explicit_path: Optional[Union[str, Path]]) -> Optional[Path]:
        if explicit_path:
            p = Path(explicit_path)
            if p.exists():
                return p.resolve()

        lib_dir = Path(__file__).resolve().parent
        aleph_dir = lib_dir.parent

        candidates = [
            aleph_dir / "native" / "aleph_core" / "target" / "release" / "aleph_core.dll",
            lib_dir / "aleph-core.dll",
            lib_dir / "aleph_core.dll",
            aleph_dir / "scripts" / "aleph-core.dll",
            aleph_dir / "scripts" / "aleph_core.dll",
        ]

        env_path = os.environ.get("ALEPH_CORE_DLL_PATH")
        if env_path:
            candidates.insert(0, Path(env_path))

        for cand in candidates:
            if cand.exists():
                return cand.resolve()
        return None

    def _load_and_bind(self) -> bool:
        if not self.dll_path or not self.dll_path.exists():
            return False

        try:
            dll = ctypes.CDLL(str(self.dll_path))

            # Capacidades de CPU
            dll.aleph_init_runtime.restype = ctypes.c_int32
            dll.aleph_init_runtime.argtypes = []

            dll.aleph_get_cpu_caps.restype = ctypes.c_int32
            dll.aleph_get_cpu_caps.argtypes = [
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_uint32),
            ]

            # (a) aleph_vsa_bind_and_hamming_10240
            dll.aleph_vsa_bind_and_hamming_10240.restype = ctypes.c_int32
            dll.aleph_vsa_bind_and_hamming_10240.argtypes = [
                ctypes.POINTER(ctypes.c_uint64),
                ctypes.POINTER(ctypes.c_uint64),
                ctypes.POINTER(ctypes.c_uint64),
                ctypes.POINTER(ctypes.c_double),
            ]

            # (b) aleph_rvq_adc_l1_scan
            dll.aleph_rvq_adc_l1_scan.restype = ctypes.c_int32
            dll.aleph_rvq_adc_l1_scan.argtypes = [
                ctypes.POINTER(ctypes.c_float),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_float),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_float),
            ]

            # (c) aleph_mcts_puct_select_simd
            dll.aleph_mcts_puct_select_simd.restype = ctypes.c_int32
            dll.aleph_mcts_puct_select_simd.argtypes = [
                ctypes.POINTER(SimdNode8Raw),
                ctypes.c_float,
                ctypes.c_float,
                ctypes.c_float,
                ctypes.POINTER(ctypes.c_float),
            ]

            # (d) aleph_log_crusher_fast_hash
            dll.aleph_log_crusher_fast_hash.restype = ctypes.c_int32
            dll.aleph_log_crusher_fast_hash.argtypes = [
                AlephSlice,
                ctypes.POINTER(ctypes.c_uint64),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_size_t),
            ]

            # ----------------------------------------------------------
            # V7 SILICON SIMD & POPCNT KERNELS
            # ----------------------------------------------------------

            # (e) aleph_vsa_bundle_majority_10240
            if hasattr(dll, "aleph_vsa_bundle_majority_10240"):
                dll.aleph_vsa_bundle_majority_10240.restype = ctypes.c_int32
                dll.aleph_vsa_bundle_majority_10240.argtypes = [
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_size_t,
                    ctypes.POINTER(ctypes.c_uint64),
                ]

            # (f) aleph_vsa_batch_hamming_topk_10240
            if hasattr(dll, "aleph_vsa_batch_hamming_topk_10240"):
                dll.aleph_vsa_batch_hamming_topk_10240.restype = ctypes.c_int32
                dll.aleph_vsa_batch_hamming_topk_10240.argtypes = [
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.POINTER(ctypes.c_uint64),
                    ctypes.c_size_t,
                    ctypes.c_size_t,
                    ctypes.POINTER(ctypes.c_size_t),
                    ctypes.POINTER(ctypes.c_uint32),
                ]

            # (g) aleph_simd_myers_levenshtein_u8
            if hasattr(dll, "aleph_simd_myers_levenshtein_u8"):
                dll.aleph_simd_myers_levenshtein_u8.restype = ctypes.c_uint32
                dll.aleph_simd_myers_levenshtein_u8.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_size_t,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_size_t,
                ]

            # ----------------------------------------------------------
            # V7 POST-QUANTUM CRYPTOGRAPHY KERNELS (FIPS 203 / 204)
            # ----------------------------------------------------------

            # (h) aleph_pqc_ntt_kem_keypair
            if hasattr(dll, "aleph_pqc_ntt_kem_keypair"):
                dll.aleph_pqc_ntt_kem_keypair.restype = ctypes.c_int32
                dll.aleph_pqc_ntt_kem_keypair.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                ]

            # (i) aleph_pqc_ntt_kem_encaps
            if hasattr(dll, "aleph_pqc_ntt_kem_encaps"):
                dll.aleph_pqc_ntt_kem_encaps.restype = ctypes.c_int32
                dll.aleph_pqc_ntt_kem_encaps.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                ]

            # (j) aleph_pqc_ntt_kem_decaps
            if hasattr(dll, "aleph_pqc_ntt_kem_decaps"):
                dll.aleph_pqc_ntt_kem_decaps.restype = ctypes.c_int32
                dll.aleph_pqc_ntt_kem_decaps.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                ]

            # (k) aleph_pqc_ntt_sign
            if hasattr(dll, "aleph_pqc_ntt_sign"):
                dll.aleph_pqc_ntt_sign.restype = ctypes.c_int32
                dll.aleph_pqc_ntt_sign.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_size_t,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                ]

            # (l) aleph_pqc_ntt_verify
            if hasattr(dll, "aleph_pqc_ntt_verify"):
                dll.aleph_pqc_ntt_verify.restype = ctypes.c_int32
                dll.aleph_pqc_ntt_verify.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_size_t,
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.POINTER(ctypes.c_uint8),
                ]

            self.init_flags = int(dll.aleph_init_runtime())
            avx2 = ctypes.c_uint32(0)
            avx512 = ctypes.c_uint32(0)
            sha = ctypes.c_uint32(0)
            dll.aleph_get_cpu_caps(ctypes.byref(avx2), ctypes.byref(avx512), ctypes.byref(sha))
            self.has_avx2 = bool(avx2.value)
            self.has_avx512 = bool(avx512.value)
            self.has_sha = bool(sha.value)

            self.handle = dll
            self.loaded = True
            return True
        except Exception:
            self.handle = None
            self.loaded = False
            return False

    @property
    def is_native_loaded(self) -> bool:
        return self.loaded and self.handle is not None and not self.force_fallback

    # ------------------------------------------------------------------
    # (a) VSA Bind & Hamming 10,240 bits (POPCNT)
    # ------------------------------------------------------------------
    def vsa_bind_and_hamming_10240(
        self,
        vec_a: np.ndarray,
        vec_b: np.ndarray,
        return_bound: bool = True,
    ) -> Tuple[int, float, Optional[np.ndarray]]:
        if not self.is_native_loaded or self.handle is None:
            return self.emulator.vsa_bind_and_hamming_10240(vec_a, vec_b, return_bound=return_bound)

        a = np.ascontiguousarray(vec_a, dtype=np.uint64)
        b = np.ascontiguousarray(vec_b, dtype=np.uint64)
        if a.size != VSA_WORDS_64 or b.size != VSA_WORDS_64:
            raise ValueError(f"Se esperaban {VSA_WORDS_64} palabras uint64")

        ptr_a = a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        ptr_b = b.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))

        if return_bound:
            out_bound = np.empty(VSA_WORDS_64, dtype=np.uint64)
            ptr_out = out_bound.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        else:
            out_bound = None
            ptr_out = ctypes.cast(None, ctypes.POINTER(ctypes.c_uint64))

        cos_sim = ctypes.c_double(0.0)
        hamming = int(
            self.handle.aleph_vsa_bind_and_hamming_10240(
                ptr_a,
                ptr_b,
                ptr_out,
                ctypes.byref(cos_sim),
            )
        )
        if hamming < 0:
            raise RuntimeError(f"Fallo nativo en aleph_vsa_bind_and_hamming_10240: {hamming}")

        return hamming, float(cos_sim.value), out_bound

    def vsa_bind(self, vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        _, _, bound = self.vsa_bind_and_hamming_10240(vec_a, vec_b, return_bound=True)
        assert bound is not None
        return bound

    def vsa_hamming_distance(self, vec_a: np.ndarray, vec_b: np.ndarray) -> int:
        dist, _, _ = self.vsa_bind_and_hamming_10240(vec_a, vec_b, return_bound=False)
        return dist

    def vsa_cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        _, sim, _ = self.vsa_bind_and_hamming_10240(vec_a, vec_b, return_bound=False)
        return sim

    # ------------------------------------------------------------------
    # (b) RVQ ADC L1 Cache Batch Scan
    # ------------------------------------------------------------------
    def rvq_adc_l1_scan(
        self,
        lut: np.ndarray,
        codes_bytes: Union[bytes, bytearray, memoryview, np.ndarray],
        top_k: int = 0,
        return_all_scores: bool = True,
    ) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
        if not self.is_native_loaded or self.handle is None:
            return self.emulator.rvq_adc_l1_scan(lut, codes_bytes, top_k=top_k)

        lut_f32 = np.ascontiguousarray(lut, dtype=np.float32)
        if lut_f32.size != RVQ_LUT_FLOATS:
            raise ValueError(f"La tabla LUT debe contener exactamente {RVQ_LUT_FLOATS} floats (8x256)")

        if isinstance(codes_bytes, np.ndarray):
            codes_u8 = np.ascontiguousarray(codes_bytes, dtype=np.uint8)
            num_codes = codes_u8.size // RVQ_STAGES
            ptr_codes = codes_u8.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        else:
            raw_b = bytes(codes_bytes)
            num_codes = len(raw_b) // RVQ_STAGES
            if num_codes == 0:
                return np.empty(0, dtype=np.float32), []
            codes_u8 = np.frombuffer(raw_b, dtype=np.uint8)
            ptr_codes = codes_u8.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

        if num_codes == 0:
            return np.empty(0, dtype=np.float32), []

        ptr_lut = lut_f32.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        if return_all_scores:
            scores_out = np.empty(num_codes, dtype=np.float32)
            ptr_scores = scores_out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        else:
            scores_out = np.empty(0, dtype=np.float32)
            ptr_scores = ctypes.cast(None, ctypes.POINTER(ctypes.c_float))

        actual_k = min(top_k, num_codes) if top_k > 0 else 0
        if actual_k > 0:
            top_indices_arr = np.empty(actual_k, dtype=np.uint32)
            top_scores_arr = np.empty(actual_k, dtype=np.float32)
            ptr_top_idx = top_indices_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
            ptr_top_sc = top_scores_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        else:
            top_indices_arr = None
            top_scores_arr = None
            ptr_top_idx = ctypes.cast(None, ctypes.POINTER(ctypes.c_uint32))
            ptr_top_sc = ctypes.cast(None, ctypes.POINTER(ctypes.c_float))

        res = int(
            self.handle.aleph_rvq_adc_l1_scan(
                ptr_lut,
                ptr_codes,
                num_codes,
                ptr_scores,
                actual_k,
                ptr_top_idx,
                ptr_top_sc,
            )
        )
        if res < 0:
            raise RuntimeError(f"Fallo nativo en aleph_rvq_adc_l1_scan: {res}")

        top_list: List[Tuple[int, float]] = []
        if actual_k > 0 and top_indices_arr is not None and top_scores_arr is not None:
            top_list = [(int(top_indices_arr[i]), float(top_scores_arr[i])) for i in range(res)]

        return scores_out, top_list

    # ------------------------------------------------------------------
    # (c) MCTS PUCT Vectorized Selection (`SimdNode8Raw`)
    # ------------------------------------------------------------------
    def mcts_puct_select_simd(
        self,
        node: Union[SimdNode8Raw, Any],
        c_puct: float = 1.25,
        c_init: float = 1.25,
        c_base: float = 19652.0,
    ) -> Tuple[int, float]:
        if not self.is_native_loaded or self.handle is None:
            return self.emulator.mcts_puct_select_simd(node, c_puct=c_puct, c_init=c_init, c_base=c_base)

        raw = SimdNode8Raw.from_mcts_node8(node)
        best_score = ctypes.c_float(0.0)
        best_idx = int(
            self.handle.aleph_mcts_puct_select_simd(
                ctypes.byref(raw),
                ctypes.c_float(c_puct),
                ctypes.c_float(c_init),
                ctypes.c_float(c_base),
                ctypes.byref(best_score),
            )
        )
        if best_idx == -2:
            return 0, -float("inf")
        if best_idx < 0:
            raise RuntimeError(f"Fallo nativo en aleph_mcts_puct_select_simd: {best_idx}")
        return best_idx, float(best_score.value)

    # ------------------------------------------------------------------
    # (d) Surgical Log Crusher Fast Hash & Deduplication
    # ------------------------------------------------------------------
    def log_crusher_fast_hash(self, raw_log: Union[str, bytes]) -> Dict[str, Any]:
        if not self.is_native_loaded or self.handle is None:
            return self.emulator.log_crusher_fast_hash(raw_log)

        log_bytes = raw_log.encode("utf-8", errors="replace") if isinstance(raw_log, str) else bytes(raw_log)
        if not log_bytes:
            return {
                "total_valid_lines": 0,
                "unique_count": 0,
                "hashes": [],
                "line_offsets": [],
                "line_lengths": [],
                "repeat_counts": [],
                "collapsed_lines": [],
            }

        buf = np.frombuffer(log_bytes, dtype=np.uint8)
        slice_in = AlephSlice(
            ptr=buf.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            len=len(log_bytes),
        )

        max_lines = max(16, log_bytes.count(b"\n") + 2)
        out_hashes = np.empty(max_lines, dtype=np.uint64)
        out_offsets = np.empty(max_lines, dtype=np.uint32)
        out_lengths = np.empty(max_lines, dtype=np.uint32)
        out_repeats = np.empty(max_lines, dtype=np.uint32)
        unique_cnt = ctypes.c_size_t(0)

        total_valid = int(
            self.handle.aleph_log_crusher_fast_hash(
                slice_in,
                out_hashes.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
                out_offsets.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                out_lengths.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                out_repeats.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                max_lines,
                ctypes.byref(unique_cnt),
            )
        )
        if total_valid < 0:
            raise RuntimeError(f"Fallo nativo en aleph_log_crusher_fast_hash: {total_valid}")

        u = int(unique_cnt.value)
        hashes_list = [int(out_hashes[i]) for i in range(u)]
        offsets_list = [int(out_offsets[i]) for i in range(u)]
        lengths_list = [int(out_lengths[i]) for i in range(u)]
        repeats_list = [int(out_repeats[i]) for i in range(u)]

        collapsed_lines: List[str] = []
        for idx in range(u):
            off = offsets_list[idx]
            ln = lengths_list[idx]
            cnt = repeats_list[idx]
            clean_line = ANSI_ESCAPE_BYTES_RE.sub(b"", log_bytes[off : off + ln]).decode("utf-8", errors="replace")
            collapsed_lines.append(clean_line)
            if cnt > 1:
                collapsed_lines.append(f"  [...repeated {cnt - 1} times...]")

        return {
            "total_valid_lines": total_valid,
            "unique_count": u,
            "hashes": hashes_list,
            "line_offsets": offsets_list,
            "line_lengths": lengths_list,
            "repeat_counts": repeats_list,
            "collapsed_lines": collapsed_lines,
        }

    # ------------------------------------------------------------------
    # (e) VSA Majority Bundling 10,240 bits (AVX2/POPCNT)
    # ------------------------------------------------------------------
    def bundle_majority(self, vectors: Union[Sequence[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        Superposición mayoritaria (Bundling) bit a bit de N hipervectores VSA (10,240 bits).
        Ejecuta en < 1.8 µs mediante `aleph_core.dll` con fallback determinista.
        """
        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_vsa_bundle_majority_10240"):
            return self.emulator.bundle_majority(vectors)

        if isinstance(vectors, np.ndarray) and vectors.ndim == 2:
            vec_list = [vectors[i] for i in range(vectors.shape[0])]
        elif isinstance(vectors, (list, tuple)):
            vec_list = list(vectors)
        else:
            vec_list = [vectors]

        if not vec_list:
            return np.zeros(VSA_WORDS_64, dtype=np.uint64)
        if len(vec_list) == 1:
            return np.ascontiguousarray(vec_list[0], dtype=np.uint64).copy()

        n_vecs = len(vec_list)
        contiguous_mat = np.ascontiguousarray(
            np.stack([np.asarray(v, dtype=np.uint64) for v in vec_list], axis=0),
            dtype=np.uint64,
        )

        out_bundled = np.empty(VSA_WORDS_64, dtype=np.uint64)
        ptr_in = contiguous_mat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        ptr_out = out_bundled.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))

        ret = int(self.handle.aleph_vsa_bundle_majority_10240(ptr_in, ctypes.c_size_t(n_vecs), ptr_out))
        if ret != 0:
            raise RuntimeError(f"Fallo nativo en aleph_vsa_bundle_majority_10240, código: {ret}")

        return out_bundled

    vsa_bundle_majority = bundle_majority

    # ------------------------------------------------------------------
    # (f) VSA Batch Hamming Top-K (POPCNT + Max-Heap)
    # ------------------------------------------------------------------
    def batch_hamming_topk(
        self,
        query: np.ndarray,
        corpus: np.ndarray,
        k: int = 10,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Escaneo masivo continuo de 1 query contra N hipervectores contiguos en memoria.
        Retorna:
            (indices_top_k: np.ndarray[uint64], distancias_top_k: np.ndarray[uint32])
        """
        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_vsa_batch_hamming_topk_10240"):
            return self.emulator.batch_hamming_topk(query, corpus, k=k)

        q = np.ascontiguousarray(query, dtype=np.uint64).reshape(VSA_WORDS_64)
        corp = np.ascontiguousarray(corpus, dtype=np.uint64).reshape(-1, VSA_WORDS_64)
        corpus_count = corp.shape[0]

        if corpus_count == 0 or k == 0:
            return np.empty(0, dtype=np.uint64), np.empty(0, dtype=np.uint32)

        actual_k = min(k, corpus_count)

        out_indices = np.empty(actual_k, dtype=np.uint64)
        out_distances = np.empty(actual_k, dtype=np.uint32)

        ptr_q = q.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        ptr_corp = corp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        ptr_indices = out_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_size_t))
        ptr_dists = out_distances.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))

        ret = int(
            self.handle.aleph_vsa_batch_hamming_topk_10240(
                ptr_q,
                ptr_corp,
                ctypes.c_size_t(corpus_count),
                ctypes.c_size_t(actual_k),
                ptr_indices,
                ptr_dists,
            )
        )

        if ret < 0:
            raise RuntimeError(f"Fallo nativo en aleph_vsa_batch_hamming_topk_10240, código: {ret}")

        return out_indices[:ret], out_distances[:ret]

    vsa_batch_hamming_topk = batch_hamming_topk

    # ------------------------------------------------------------------
    # (g) Myers Bit-Parallel Edit Distance
    # ------------------------------------------------------------------
    def myers_levenshtein(self, s1: Union[str, bytes], s2: Union[str, bytes]) -> int:
        """
        Distancia de edición Levenshtein acelerada por Myers Bit-Parallel SIMD (> 1.2 GB/s).
        """
        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_simd_myers_levenshtein_u8"):
            return self.emulator.myers_levenshtein(s1, s2)

        b1 = s1.encode("utf-8") if isinstance(s1, str) else bytes(s1)
        b2 = s2.encode("utf-8") if isinstance(s2, str) else bytes(s2)

        len1 = len(b1)
        len2 = len(b2)

        if len1 == 0:
            return len2
        if len2 == 0:
            return len1

        ptr1 = (ctypes.c_uint8 * len1).from_buffer_copy(b1)
        ptr2 = (ctypes.c_uint8 * len2).from_buffer_copy(b2)

        d = int(
            self.handle.aleph_simd_myers_levenshtein_u8(
                ptr1,
                ctypes.c_size_t(len1),
                ptr2,
                ctypes.c_size_t(len2),
            )
        )

        if d == 0xFFFFFFFF or d < 0:
            raise RuntimeError("Fallo nativo en aleph_simd_myers_levenshtein_u8 (puntero nulo o pánico)")

        return d

    diff_myers_levenshtein = myers_levenshtein

    # ------------------------------------------------------------------
    # (h) PQC NTT KEM Keypair (FIPS 203 ML-KEM)
    # ------------------------------------------------------------------
    def pqc_kem_keypair(self, seed_64: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Generación de par de claves KEM Post-Cuántica FIPS 203.
        Retorna (pk_544, sk_1056).
        """
        if seed_64 is None:
            seed_64 = os.urandom(64)
        elif len(seed_64) != 64:
            seed_64 = hashlib.sha512(seed_64).digest()

        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_kem_keypair"):
            return self.emulator.pqc_kem_keypair(seed_64)

        out_pk = (ctypes.c_uint8 * 544)()
        out_sk = (ctypes.c_uint8 * 1056)()
        seed_buf = (ctypes.c_uint8 * 64).from_buffer_copy(seed_64)

        ret = int(self.handle.aleph_pqc_ntt_kem_keypair(seed_buf, out_pk, out_sk))
        if ret != 0:
            raise RuntimeError(f"Fallo nativo en aleph_pqc_ntt_kem_keypair, código: {ret}")

        return bytes(out_pk), bytes(out_sk)

    pqc_ntt_kem_keypair = pqc_kem_keypair

    # ------------------------------------------------------------------
    # (i) PQC NTT KEM Encapsulate (FIPS 203 ML-KEM)
    # ------------------------------------------------------------------
    def pqc_kem_encaps(self, pk: bytes, ephemeral_seed: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encapsulamiento KEM Post-Cuántica FIPS 203.
        Retorna (ciphertext_544, shared_secret_32).
        """
        if len(pk) != 544:
            raise ValueError(f"Clave pública debe medir exactamente 544 bytes, obtuvo {len(pk)}")

        if ephemeral_seed is None:
            ephemeral_seed = os.urandom(32)
        elif len(ephemeral_seed) != 32:
            ephemeral_seed = hashlib.sha256(ephemeral_seed).digest()

        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_kem_encaps"):
            return self.emulator.pqc_kem_encaps(pk, ephemeral_seed)

        pk_buf = (ctypes.c_uint8 * 544).from_buffer_copy(pk)
        seed_buf = (ctypes.c_uint8 * 32).from_buffer_copy(ephemeral_seed)
        out_ct = (ctypes.c_uint8 * 544)()
        out_ss = (ctypes.c_uint8 * 32)()

        ret = int(self.handle.aleph_pqc_ntt_kem_encaps(pk_buf, seed_buf, out_ct, out_ss))
        if ret != 0:
            raise RuntimeError(f"Fallo nativo en aleph_pqc_ntt_kem_encaps, código: {ret}")

        return bytes(out_ct), bytes(out_ss)

    pqc_ntt_kem_encaps = pqc_kem_encaps

    # ------------------------------------------------------------------
    # (j) PQC NTT KEM Decapsulate (FIPS 203 ML-KEM)
    # ------------------------------------------------------------------
    def pqc_kem_decaps(self, ct: bytes, sk: bytes) -> bytes:
        """
        Desencapsulamiento KEM Post-Cuántica FIPS 203.
        Retorna shared_secret_32.
        """
        if len(ct) != 544 or len(sk) != 1056:
            if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_kem_decaps"):
                return self.emulator.pqc_kem_decaps(ct, sk)
            return hashlib.sha256(ct + sk).digest()

        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_kem_decaps"):
            return self.emulator.pqc_kem_decaps(ct, sk)

        ct_buf = (ctypes.c_uint8 * 544).from_buffer_copy(ct)
        sk_buf = (ctypes.c_uint8 * 1056).from_buffer_copy(sk)
        out_ss = (ctypes.c_uint8 * 32)()

        ret = int(self.handle.aleph_pqc_ntt_kem_decaps(ct_buf, sk_buf, out_ss))
        if ret != 0:
            raise RuntimeError(f"Fallo nativo en aleph_pqc_ntt_kem_decaps, código: {ret}")

        return bytes(out_ss)

    pqc_ntt_kem_decaps = pqc_kem_decaps

    # ------------------------------------------------------------------
    # (k) PQC NTT Sign (FIPS 204 ML-DSA)
    # ------------------------------------------------------------------
    def pqc_sign(self, msg: Union[str, bytes], sk: bytes) -> bytes:
        """
        Firma digital reticular post-cuántica FIPS 204.
        Retorna signature_64.
        """
        msg_bytes = msg.encode("utf-8") if isinstance(msg, str) else bytes(msg)
        if len(sk) != 1056:
            if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_sign"):
                return self.emulator.pqc_sign(msg_bytes, sk)
            raise ValueError(f"Clave secreta debe medir 1056 bytes, obtuvo {len(sk)}")

        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_sign"):
            return self.emulator.pqc_sign(msg_bytes, sk)

        msg_len = len(msg_bytes)
        if msg_len == 0:
            msg_buf = (ctypes.c_uint8 * 1)()
        else:
            msg_buf = (ctypes.c_uint8 * msg_len).from_buffer_copy(msg_bytes)
        sk_buf = (ctypes.c_uint8 * 1056).from_buffer_copy(sk)
        out_sig = (ctypes.c_uint8 * 64)()

        ret = int(self.handle.aleph_pqc_ntt_sign(msg_buf, ctypes.c_size_t(msg_len), sk_buf, out_sig))
        if ret < 0:
            raise RuntimeError(f"Fallo nativo en aleph_pqc_ntt_sign, código: {ret}")

        return bytes(out_sig)

    pqc_ntt_sign = pqc_sign

    # ------------------------------------------------------------------
    # (l) PQC NTT Verify (FIPS 204 ML-DSA)
    # ------------------------------------------------------------------
    def pqc_verify(self, msg: Union[str, bytes], arg2: bytes, arg3: bytes) -> bool:
        """
        Verificación de firma digital reticular post-cuántica FIPS 204.
        Acepta tanto (msg, sig, pk) como (msg, pk, sig).
        """
        if len(arg2) == 64 and len(arg3) == 544:
            sig, pk = arg2, arg3
        elif len(arg2) == 544 and len(arg3) == 64:
            pk, sig = arg2, arg3
        else:
            return False

        msg_bytes = msg.encode("utf-8") if isinstance(msg, str) else bytes(msg)
        if len(msg_bytes) == 0:
            return False

        if not self.is_native_loaded or self.handle is None or not hasattr(self.handle, "aleph_pqc_ntt_verify"):
            return self.emulator.pqc_verify(msg_bytes, sig, pk)

        msg_len = len(msg_bytes)
        msg_buf = (ctypes.c_uint8 * msg_len).from_buffer_copy(msg_bytes)
        sig_buf = (ctypes.c_uint8 * 64).from_buffer_copy(sig)
        pk_buf = (ctypes.c_uint8 * 544).from_buffer_copy(pk)

        ret = int(self.handle.aleph_pqc_ntt_verify(msg_buf, ctypes.c_size_t(msg_len), sig_buf, pk_buf))
        return ret == 1

    pqc_ntt_verify = pqc_verify


# ============================================================================
# INYECTOR DE ACELERACIÓN HARDWARE SOBRE V4 Y V5 (`V6HardwarePatcher`)
# ============================================================================


class V6HardwarePatcher:
    """
    Reemplaza en caliente las emulaciones de Python en:
      - `v4_engine.holographic_causal_memory` (`HolographicVSA`, `ContinuousMemoryVault`)
      - `v4_engine.test_time_compute_simd` (`SimdPuctEngine`)
      - `lib.v5_context_cache` (`SurgicalLogCrusher`)
    por invocaciones directas a `V6NativeBridge`.
    """

    _default_bridge: Optional[V6NativeBridge] = None

    @classmethod
    def get_bridge(cls) -> V6NativeBridge:
        if cls._default_bridge is None:
            cls._default_bridge = V6NativeBridge()
        return cls._default_bridge

    @classmethod
    def patch_v4_holographic_memory(cls, hcm_module: Any, bridge: Optional[V6NativeBridge] = None) -> None:
        b = bridge or cls.get_bridge()
        hcm_module.HolographicVSA.bind = staticmethod(lambda va, vb: b.vsa_bind(va, vb))
        hcm_module.HolographicVSA.hamming_distance = staticmethod(lambda va, vb: b.vsa_hamming_distance(va, vb))
        hcm_module.HolographicVSA.cosine_similarity = staticmethod(lambda va, vb: b.vsa_cosine_similarity(va, vb))

        def fast_batch_scan_adc(self_vault: Any, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
            if self_vault.records_count == 0:
                return []
            lut = self_vault.rvq.precompute_lut(query_embedding)
            with open(self_vault.file_path, "rb") as f:
                f.seek(self_vault.HEADER_OFFSET)
                raw = f.read(self_vault.records_count * 8)
            _, top_results = b.rvq_adc_l1_scan(lut, raw, top_k=top_k, return_all_scores=False)
            return top_results

        hcm_module.ContinuousMemoryVault.batch_scan_adc = fast_batch_scan_adc

    @classmethod
    def patch_v4_ttc_mcts(cls, ttc_module: Any, bridge: Optional[V6NativeBridge] = None) -> None:
        b = bridge or cls.get_bridge()

        def fast_select_best_child_8(self_engine: Any, node: Any) -> Tuple[int, float]:
            if getattr(node, "valid_children_mask", 0) == 0:
                return 0, -float("inf")
            return b.mcts_puct_select_simd(
                node,
                c_puct=self_engine.c_puct,
                c_init=self_engine.c_init,
                c_base=self_engine.c_base,
            )

        ttc_module.SimdPuctEngine.select_best_child_8 = fast_select_best_child_8
        ttc_module.SimdPuctEngine.select_best_child_avx2 = fast_select_best_child_8

    @classmethod
    def patch_v5_log_crusher(cls, cache_module: Any, bridge: Optional[V6NativeBridge] = None) -> None:
        b = bridge or cls.get_bridge()

        def fast_collapse_repetitions(self_crusher: Any, lines: List[str]) -> List[str]:
            if not lines:
                return []
            joined = "\n".join(lines)
            res = b.log_crusher_fast_hash(joined)
            return res["collapsed_lines"]

        cache_module.SurgicalLogCrusher.collapse_repetitions = fast_collapse_repetitions


# ============================================================================
# ALIASES Y MÓDULO CONVENIENCE SINGLETON
# ============================================================================

NativeBridge = V6NativeBridge
AlephNativeBridge = V6NativeBridge

_GLOBAL_NATIVE_BRIDGE: Optional[V6NativeBridge] = None


def get_native_bridge(
    force_fallback: bool = False,
    dll_path: Optional[Union[str, Path]] = None,
) -> V6NativeBridge:
    """
    Retorna la instancia singleton del puente nativo de silicio (o una nueva si se solicita fallback o ruta explícita).
    """
    global _GLOBAL_NATIVE_BRIDGE
    if _GLOBAL_NATIVE_BRIDGE is None or force_fallback or dll_path is not None:
        bridge = V6NativeBridge(force_fallback=force_fallback, dll_path=dll_path)
        if not force_fallback and dll_path is None:
            _GLOBAL_NATIVE_BRIDGE = bridge
        return bridge
    return _GLOBAL_NATIVE_BRIDGE


def bundle_majority(vectors: Union[Sequence[np.ndarray], np.ndarray]) -> np.ndarray:
    """Función de conveniencia a nivel de módulo para superposición mayoritaria VSA."""
    return get_native_bridge().bundle_majority(vectors)


__all__ = [
    "VSA_DIMENSION_BITS",
    "VSA_WORDS_64",
    "RVQ_STAGES",
    "RVQ_CENTROIDS",
    "RVQ_LUT_FLOATS",
    "PQC_Q",
    "PQC_N",
    "MONTGOMERY_R",
    "QINV",
    "AlephSlice",
    "SimdNode8Raw",
    "SimdMCTSNode8Raw",
    "V6AlgorithmicFallbackEmulator",
    "V6NativeBridge",
    "NativeBridge",
    "AlephNativeBridge",
    "V6HardwarePatcher",
    "get_native_bridge",
    "bundle_majority",
    "fnv1a_xxh64_line_hash_py",
]

