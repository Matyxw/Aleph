# Síntesis Socrática 02: Epistemología del Software, Teorema de No Free Lunch y Calibrador Epistémico

## 1. Separación Estricta entre Estado Inferido y Estado Demostrado
En `aleph_core/state/epistemic.py`, ninguna salida de un modelo generativo recibe el estatus `VERIFIED` o `FORMALLY_PROVEN` por autodeclaración:
1. **`INFERRED`:** Hipótesis inicial emitida por un agente o heurística, sin respaldo de ejecución ni demostración formal.
2. **`VERIFIED`:** Afirmación validada empíricamente por un predicado ejecutable independiente (`VerificationGate.verify`) con recibo SHA-256.
3. **`FORMALLY_PROVEN`:** Código cuyas metas de verificación ($\text{VCGen}$) fueron demostradas insatisfacibles en su negación ($\neg \Phi \implies \text{UNSAT}$) por `Z3VerificationEngine`.
4. **`REFUTED`:** Afirmación o función refutada por un contraejemplo concreto ($\text{SAT}$) o bloqueada por `AegisShield`, disparando la destilación de una nueva regla preventiva en el Ciclo Demiurgo.
