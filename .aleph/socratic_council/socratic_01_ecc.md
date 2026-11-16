# Dictamen Socrático 01: El Aleph vs Colecciones de Prompts Estáticos (ECC)

## 1. Limitación de las Colecciones de Reglas en Texto Plano
Las colecciones masivas de prompts y reglas estáticas sufren de dos patologías fundamentales:
1. **Saturación de Ventana de Contexto:** Inyectar cientos de reglas irrelevantes degrada la atención del modelo y consume decenas de miles de tokens por turno.
2. **Ausencia de Compuerta Ejecutable:** Un archivo Markdown no puede impedir por sí mismo que un agente escriba `transition: all`, `VACUUM FULL` o una división por cero.

## 2. Solución Arquitectónica en El Aleph
- **Recuperación Selectiva HippoRAG 2 PPR:** En cada turno se recuperan únicamente las $k$ reglas relevantes mediante BM25 + Embeddings LSH + Personalized PageRank sobre las 4.742 entidades del grafo.
- **Compuertas AST/SMT Ejecutables:** Cada regla crítica está respaldada por un verificador programático en `aleph_core/verification/` y `.aleph/hooks/`.
