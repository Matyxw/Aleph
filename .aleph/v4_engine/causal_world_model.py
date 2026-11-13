#!/usr/bin/env python3
"""Causal World Model Engine (S-JEPA & Pearl Structural Causal Models do(X))."""
from dataclasses import dataclass
from typing import Dict, Set

@dataclass
class ProgramNode:
    node_id: str
    node_type: str
    symbol_name: str = ""

class UnifiedProgramGraph:
    def __init__(self, name: str = "main"):
        self.name = name
        self.nodes: Dict[str, ProgramNode] = {}
        self.children: Dict[str, Set[str]] = {}

    def compute_causal_weight(self, affected_count: int, total_nodes: int) -> float:
        safe_total = max(1, total_nodes)
        return float(max(0, affected_count)) / float(safe_total)
