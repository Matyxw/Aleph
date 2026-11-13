#!/usr/bin/env python3
"""Agent Execution Protocol (AEP) Binary Standard (<8.5us IPC)."""
from enum import IntEnum

class AEPMessageType(IntEnum):
    HEARTBEAT = 1
    EXEC_REQUEST = 2
    EXEC_RESPONSE = 3
    CAPABILITY_GRANT = 4
    ZK_PROOF_ATTEST = 5
