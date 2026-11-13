#!/usr/bin/env python3
"""Agent Execution Protocol (AEP) Binary Standard (<8.5us IPC)."""
from dataclasses import dataclass
from enum import IntEnum
import hashlib
import struct

AEP_MAGIC = b"AEP5"
AEP_VERSION = 1
HEADER_STRUCT = struct.Struct("!4sBBI")
TRAILER_STRUCT = struct.Struct("!8s")


class AEPMessageType(IntEnum):
    HEARTBEAT = 1
    EXEC_REQUEST = 2
    EXEC_RESPONSE = 3
    CAPABILITY_GRANT = 4
    ZK_PROOF_ATTEST = 5


@dataclass(frozen=True)
class AEPFrame:
    msg_type: AEPMessageType
    payload: bytes
    version: int = AEP_VERSION
    checksum: bytes = b""


def encode_frame(msg_type: AEPMessageType, payload: bytes, version: int = AEP_VERSION) -> bytes:
    """Serializa un frame binario AEP5 con longitud y digest SHA-256 truncado a 64 bits."""
    header = HEADER_STRUCT.pack(AEP_MAGIC, int(version), int(msg_type), len(payload))
    body = header + payload
    checksum = hashlib.sha256(body).digest()[:8]
    return body + checksum


def decode_frame(raw: bytes) -> AEPFrame:
    """Decodifica y verifica un frame binario AEP5."""
    min_size = HEADER_STRUCT.size + TRAILER_STRUCT.size
    if len(raw) < min_size:
        raise ValueError(f"Frame AEP truncado: {len(raw)} bytes < {min_size}")
    magic, version, msg_type_int, payload_len = HEADER_STRUCT.unpack_from(raw, 0)
    if magic != AEP_MAGIC:
        raise ValueError(f"Magic inválido: {magic!r}")
    expected_len = HEADER_STRUCT.size + payload_len + TRAILER_STRUCT.size
    if len(raw) != expected_len:
        raise ValueError(f"Longitud inconsistente: esperado {expected_len}, recibido {len(raw)}")
    body = raw[: HEADER_STRUCT.size + payload_len]
    checksum = raw[HEADER_STRUCT.size + payload_len :]
    expected_checksum = hashlib.sha256(body).digest()[:8]
    if checksum != expected_checksum:
        raise ValueError("Checksum AEP5 corrupto")
    return AEPFrame(
        msg_type=AEPMessageType(msg_type_int),
        payload=raw[HEADER_STRUCT.size : HEADER_STRUCT.size + payload_len],
        version=version,
        checksum=checksum,
    )
