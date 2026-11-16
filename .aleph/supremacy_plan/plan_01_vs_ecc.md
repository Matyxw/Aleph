# ALEPH SUPREMACY PLAN — PARTE I: INGESTA TIPADA DE SKILLS Y COMPUERTA DE SEGURIDAD

## 1. Validación Estructural y Criptográfica de Skills (`v5_skill_security.py` & `v5_skills_router.py`)
1. **Esquema Estricto (`.aleph/schemas/skill_schema.json`):** Toda skill debe declarar `id`, `name`, `version`, `entrypoint` y `permissions` bajo validación JSON Schema / Pydantic.
2. **Escaneo de Seguridad Pre-Carga (`v5_skill_security.py`):** Inspección estática de patrones de exfiltración, ejecución de subprocesos no autorizados y rutas fuera del sandbox antes de admitir una skill en el índice.
3. **Enrutamiento Híbrido Sub-Milisegundo (`v7_mmap_skill_router.py`):** Indexación en memoria compartida `mmap` combinada con filtrado léxico BM25 y activación por intención.
