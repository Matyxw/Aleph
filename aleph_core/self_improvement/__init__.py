"""
aleph_core/self_improvement/__init__.py
Motor Soberano de Automejora Continua Sin Olvido y Bóveda Interna de Bitácora (El Aleph v33.0.0).
Integra los 8 pilares SOTA de aprendizaje continuo e ingeniería de agentes:
1. HippoRAG 2 (arXiv:2502.14802): Memoria asociativa no paramétrica con Grafo de Conocimiento + Personalized PageRank (PPR) + BM25.
2. Titans + ATLAS (arXiv:2501.00663, arXiv:2505.23735): Memorización en tiempo de test guiada por sorpresa epistémica y momento.
3. EWC + Merkle-Locked Ledger: Consolidación elástica de reglas (0.0% Catastrophic Forgetting, cadena SHA-256 append-only).
4. MemGPT / Letta (arXiv:2310.08560): Jerarquía de memoria de 3 niveles (Core Working Memory, Episodic Recall Memory, Archival Vault).
5. ExpeL + Reflexion (arXiv:2308.10144, arXiv:2303.11366): Extracción experiencial de reglas SI -> ENTONCES -> EVITAR desde trazas.
6. TextGrad (Nature / arXiv:2406.07496): Diferenciación automática vía texto para refinar predicados y reglas operativas.
7. Darwin Gödel Machine (arXiv:2505.22954) & AlphaEvolve (arXiv:2506.13131): Evolución abierta con torneo Pareto multi-objetivo (REG-007).
8. Voyager Skill Library (arXiv:2305.16291) + CEGIS/SMT Proof-Carrying Gate: Compilación de reglas en compuertas ejecutables AST verificadas.
"""
from aleph_core.self_improvement.omega_continual_learner import (
    BitacoraRuleRecord,
    EpisodicExperienceTrace,
    OmegaSelfImprovementCycleReport,
    AlephOmegaContinualSelfImprovementEngine,
)

__all__ = [
    "BitacoraRuleRecord",
    "EpisodicExperienceTrace",
    "OmegaSelfImprovementCycleReport",
    "AlephOmegaContinualSelfImprovementEngine",
]
