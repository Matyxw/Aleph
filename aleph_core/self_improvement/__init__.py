"""
aleph_core/self_improvement/__init__.py
Motor Soberano de Automejora Continua Sin Olvido y Bóveda Interna de Bitácora (El Aleph v33.0.0).
Integra los 8 pilares SOTA de aprendizaje continuo e ingeniería de agentes:
1. HippoRAG 2 (arXiv:2502.14802): Memoria asociativa no paramétrica con Grafo de Conocimiento + Personalized PageRank (PPR) + BM25 + LSH Semántico.
2. Titans + ATLAS (arXiv:2501.00663, arXiv:2505.23735): Matriz de Memoria Asociativa Paramétrica en Tiempo de Test con Regla Delta y Momento.
3. EWC + Merkle-Locked Ledger + Top-K Retention: Diagonal Empírica de Información de Fisher F_ii, cadena SHA-256 append-only y medición real de retención Top-K.
4. MemGPT / Letta (arXiv:2310.08560): Jerarquía de memoria de 3 niveles (Core Working Memory, Episodic Recall Memory, Archival Vault).
5. ExpeL + Reflexion (arXiv:2308.10144, arXiv:2303.11366): Destilación autónoma de reglas SI -> ENTONCES -> EVITAR desde trazas AST.
6. TextGrad (Nature / arXiv:2406.07496): Crítica diferencial simbólica sobre diagnósticos AST/SMT y entropía de recuperación.
7. Darwin Gödel Machine (arXiv:2505.22954) & AlphaEvolve (arXiv:2506.13131): Evolución abierta con torneo Pareto ejecutado en vivo.
8. Voyager Skill Library (arXiv:2305.16291) + AST IFDS Taint Gate: Compilación y ejecución estéril de reglas en compuertas AST verificadas.
"""
from aleph_core.self_improvement.omega_continual_learner import (
    ASTIFDSDataflowTaintGate,
    BitacoraRuleRecord,
    EpisodicExperienceTrace,
    MemGPTTieredMemoryPager,
    OmegaSelfImprovementCycleReport,
    TitansAssociativeMemoryMatrix,
    AlephOmegaContinualSelfImprovementEngine,
)

__all__ = [
    "ASTIFDSDataflowTaintGate",
    "BitacoraRuleRecord",
    "EpisodicExperienceTrace",
    "MemGPTTieredMemoryPager",
    "OmegaSelfImprovementCycleReport",
    "TitansAssociativeMemoryMatrix",
    "AlephOmegaContinualSelfImprovementEngine",
]
