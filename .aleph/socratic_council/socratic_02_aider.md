# Dictamen Socrático 02: El Aleph vs Motores de Edición por Búsqueda/Reemplazo (Aider)

## 1. Fragilidad del Reemplazo Textual por Líneas
Los parches basados únicamente en bloques `SEARCH / REPLACE` textuales o `difflib` fallan cuando cambia la indentación, corrompen árboles sintácticos o introducen regresiones semánticas silenciosas.

## 2. Parcheo Quirúrgico sobre AST con Prueba de Equivalencia Relacional
En `aleph_core/verification/semantic_patch.py` (`SemanticPatchEngine`):
1. El código original y el reemplazo se parsean con `ast.parse()`.
2. El nodo `ast.FunctionDef` objetivo es verificado formalmente con `Z3VerificationEngine` para descartar división por cero, desbordamiento de enteros, acceso fuera de rango o violación de `@ensures`.
3. Opcionalmente se demuestra equivalencia funcional entrada-salida con `RelationalEquivalenceProver`.
4. La escritura en disco se ejecuta atómicamente en dos fases (`StateStore.atomic_write_file` con `os.fsync` y `os.replace`).
