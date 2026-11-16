"""
ab_eval/__init__.py
Arnés de Evaluación Experimental A/B Controlada con Prueba Exacta de McNemar para El Aleph.
Permite medir empíricamente la mejora de tasa de éxito y consumo de tokens de un agente
con y sin la inyección de reglas de la Bitácora.
"""
from ab_eval.ab_harness import mcnemar_exact_p, run, summarize

__all__ = ["mcnemar_exact_p", "run", "summarize"]
