# ALEPH SUPREMACY PLAN — PARTE XI: GRAFO DE CÓDIGO DUAL (SINTÁCTICO AST + SEMÁNTICO LSH)

## 1. Fusión Híbrida de Señales Estructurales y Semánticas
El motor de recuperación de El Aleph (`omega_continual_learner.py`) combina tres señales ortogonales para cada consulta técnica:
1. **Señal Léxica Exacta (Okapi BM25, peso 0.48):** Captura identificadores exactos de funciones, códigos de regla (`REG-xxx`), banderas de compilador y nombres de herramientas MCP.
2. **Señal Topológica de Grafo (Personalized PageRank $\alpha = 0.15$, peso 0.35):** Propaga masa de relevancia a través de las 4.742 entidades técnicas compartidas entre los 9 shards de la Bitácora.
3. **Señal Semántica Densa (Signed Random Projection N-Gram LSH $D=64$, peso 0.12 + Prior Fisher EWC 0.05):** Captura similitud morfológica y conceptual incluso ante variaciones de redacción entre español e inglés.
