# CAPÍTULO 1: Fundamentos Físico-Matemáticos, Espacio de Color OKLCH y Óptica Perceptual APCA v0.98G

## 1.1 Espacio Perceptualmente Uniforme OKLCH y Conversión Matricial Oklab
Todo color en el motor visual de El Aleph (`aleph_token_compiler.py` y `aleph_design_ir.py`) se define en coordenadas cilíndricas perceptuales $\text{OKLCH}(L, C, h)$:
- **Luminosidad Perceptual ($L \in [0.0, 1.0]$):** Invariante anti-halación foveal $L_{\max} \le 0.965$ en superficies claras y $L_{\min} \ge 0.08$ en superficies oscuras.
- **Croma ($C \in [0.0, 0.37]$):** Acotado dinámicamente al gamut sRGB / Display-P3 mediante bisección geométrica (`clip_oklch_to_srgb`).
- **Tono ($h \in [0^\circ, 360^\circ)$):** Ángulo cromático invariante frente a cambios de luminosidad.

## 1.2 Algoritmo de Contraste Perceptual Avanzado (APCA v0.98G)
La luminancia de pantalla $Y_s$ se calcula desde sRGB linealizado:
$$Y = 0.2126729 R_{\text{lin}}^{2.4} + 0.7151522 G_{\text{lin}}^{2.4} + 0.0721750 B_{\text{lin}}^{2.4}$$
Aplicando el umbral de recorte de negro ($Y_{\text{blk}} = 0.022$, exponente $1.414$), la polaridad normal ($Y_{\text{bg}} > Y_{\text{txt}}$) e inversa ($Y_{\text{bg}} < Y_{\text{txt}}$) garantizan $L_c \ge 75$ para texto de cuerpo y $L_c \ge 60$ para titulares $\ge 24\text{px}$.

## 1.3 Ley del Presupuesto de Acento (60-30-10) y Ecuación de Fresnel-Schlick
- **Superficie Dominante (60%):** Neutros de baja saturación ($C \le 0.02$).
- **Estructura Secundaria (30%):** Tarjetas, bordes y contenedores con reflectancia especular $R(\theta) = R_0 + (1 - R_0)(1 - \cos\theta)^5$ ($R_0 = 0.0426$).
- **Acento Primario ($\le 10\%$):** Verificado físicamente en el DOM renderizado por `LivePlaywrightOracle` mediante muestreo matricial $30 \times 20$.
