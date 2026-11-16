# Dictamen Socrático 03: El Aleph vs Entornos Propietarios Acoplados a Nube (Cursor)

## 1. Soberanía Operativa y Portabilidad Multi-Cliente MCP
El Aleph opera como un servidor y biblioteca estándar bajo el protocolo **Model Context Protocol (MCP JSON-RPC 2.0)** y CLI autónomo (`aleph_cli.py`), compatible simultáneamente con Google Antigravity, Gemini CLI, Claude Code y entornos locales sin dependencia de servicios propietarios externos.

## 2. Aislamiento de Worktrees y Gobernanza de Enjambre (`swarm_governor_50.py`)
- **Worktrees Efímeros (`RamWorktreeManager`):** Aprovisionamiento en `< 40 ms` con limpieza automática de agentes inactivos.
- **Coordinación Multi-Raft con Fencing Tokens (`MultiRaftShardCoordinator`):** Rechazo determinista de escrituras con época obsoleta (`ERR_FENCING_TOKEN_STALE`).
- **Detección Incremental de Deadlocks (`IncrementalDeadlockDetector`):** Prevención de ciclos con algoritmo de Tarjan (`< 0.45 ms`) y política preventiva *Wound-Wait*.
