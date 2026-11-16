# MÓDULO 01: ORQUESTADOR DE CICLO DE VIDA (LIFECYCLE ORCHESTRATOR)

## 1. Pipeline Contractual SOP (`Architect -> Coder -> Tester -> Reviewer`)
El ciclo de vida de cada tarea de ingeniería en El Aleph se rige por paquetes formales inmutables (`v5_blackboard_squads.py` y `aleph_core/engine.py`):
1. **Fase 1 — Architect (`ArchitectureContractPacket`):** Descompone el requerimiento en precondiciones `@requires`, poscondiciones `@ensures`, invariantes de estado y presupuesto de complejidad temporal/espacial.
2. **Fase 2 — Tester Red (`TddRedPacket`):** Sintetiza la suite de pruebas deterministas y casos de frontera antes de permitir la escritura de código de producción.
3. **Fase 3 — Coder Green (`CoderGreenPacket`):** Implementa la solución mínima verificada por AST y el demostrador SMT (`Z3VerificationEngine`), generando un diff unificado limpio.
4. **Fase 4 — Reviewer & Security Gate (`AdversarialReviewPacket`, `SecurityAuditPacket`):** Audita equivalencia relacional (`RelationalEquivalenceProver`), ausencia de flujo Taint (`ASTIFDSDataflowTaintGate`) y sellado criptográfico en la Bitácora.
