# ALEPH SUPREMACY PLAN — PARTE II: PAGERANK AST ESPECTRAL Y PARCHEO DIFERENCIAL

## 1. Navegación de Repositorio Basada en Grafo de Símbolos AST
A diferencia de la selección heurística de archivos por nombre, el módulo de análisis de repositorio construye el grafo dirigido de definiciones y referencias de símbolos en el AST y calcula centralidad mediante **Personalized PageRank (PPR)** y aproximación polinomial de Chebyshev.

## 2. Desacoplamiento Estricto `Coder != Tester`
El agente o módulo que propone una mutación (`SemanticPatchEngine`) está separado estructuralmente del oráculo de verificación (`Z3VerificationEngine` y `PropertyBasedFallback`), impidiendo que un parche debilite los tests para forzar su aprobación.
