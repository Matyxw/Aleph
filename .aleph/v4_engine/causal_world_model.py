#!/usr/bin/env python3
"""Causal World Model Engine (S-JEPA & Pearl Structural Causal Models do(X))."""
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class ProgramNode:
    node_id: str
    node_type: str
    symbol_name: str = ""


@dataclass(frozen=True)
class CausalEdge:
    source_id: str
    target_id: str
    relation: str = "depends_on"
    weight: float = 1.0


class UnifiedProgramGraph:
    def __init__(self, name: str = "main"):
        self.name = name
        self.nodes: Dict[str, ProgramNode] = {}
        self.children: Dict[str, Set[str]] = {}
        self.parents: Dict[str, Set[str]] = {}
        self.edges: List[CausalEdge] = []

    def add_node(self, node: ProgramNode) -> None:
        self.nodes[node.node_id] = node
        self.children.setdefault(node.node_id, set())
        self.parents.setdefault(node.node_id, set())

    def add_edge(self, source_id: str, target_id: str, relation: str = "depends_on", weight: float = 1.0) -> None:
        if source_id not in self.nodes:
            self.add_node(ProgramNode(node_id=source_id, node_type="symbol", symbol_name=source_id))
        if target_id not in self.nodes:
            self.add_node(ProgramNode(node_id=target_id, node_type="symbol", symbol_name=target_id))
        self.children[source_id].add(target_id)
        self.parents[target_id].add(source_id)
        self.edges.append(CausalEdge(source_id=source_id, target_id=target_id, relation=relation, weight=weight))

    def topological_impact(self, root_id: str) -> Set[str]:
        """Calcula el conjunto alcanzable desde `root_id` tolerando grafos con ciclos."""
        if root_id not in self.nodes and root_id not in self.children:
            return set()
        visited: Set[str] = {root_id}
        queue: deque[str] = deque([root_id])
        while queue:
            cur = queue.popleft()
            for nxt in self.children.get(cur, ()):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return visited

    def interventional_do(self, node_id: str) -> float:
        """Operador Pearl do(X=node_id): corta padres entrantes e informa el peso causal del subgrafo afectado."""
        for p in list(self.parents.get(node_id, ())):
            self.children.get(p, set()).discard(node_id)
        self.parents[node_id] = set()
        self.edges = [e for e in self.edges if e.target_id != node_id]
        impacted = self.topological_impact(node_id)
        return self.compute_causal_weight(len(impacted), max(1, len(self.nodes)))

    def compute_causal_weight(self, affected_count: int, total_nodes: int) -> float:
        safe_total = max(1, total_nodes)
        return float(max(0, affected_count)) / float(safe_total)
