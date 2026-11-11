# Resumen de resultados (generado por `python -m src.experimentos markdown`)

## Recuperación (k=3)

| Config | Banco | Hit@1 | Hit@3 | MRR@3 | Vigente antes |
|---|---|---|---|---|---|
| kit | diseno | 0.5 | 0.909 | 0.682 | 1/4 |
| kit | validacion | 0.278 | 0.722 | 0.472 | 0/5 |
| kit | robustez | 0.364 | 0.727 | 0.515 | 2/6 |
| R0b | diseno | 0.636 | 0.864 | 0.742 | 2/4 |
| R0b | validacion | 0.333 | 0.611 | 0.472 | 1/5 |
| R0b | robustez | 0.273 | 0.636 | 0.439 | 1/6 |
| R1 | diseno | 0.591 | 0.864 | 0.727 | 1/4 |
| R1 | validacion | 0.389 | 0.722 | 0.537 | 1/5 |
| R1 | robustez | 0.273 | 0.636 | 0.424 | 1/6 |
| R2a | diseno | 0.682 | 0.909 | 0.78 | 2/4 |
| R2a | validacion | 0.389 | 0.556 | 0.463 | 0/5 |
| R2a | robustez | 0.273 | 0.636 | 0.455 | 2/6 |
| R2 | diseno | 0.727 | 0.909 | 0.811 | 1/4 |
| R2 | validacion | 0.5 | 0.778 | 0.62 | 1/5 |
| R2 | robustez | 0.182 | 0.818 | 0.47 | 1/6 |
| R3 | diseno | 0.727 | 0.955 | 0.833 | 1/4 |
| R3 | validacion | 0.556 | 0.889 | 0.704 | 1/5 |
| R3 | robustez | 0.182 | 0.818 | 0.47 | 1/6 |
| opt_sin_glosario | diseno | 0.955 | 1.0 | 0.977 | 4/4 |
| opt_sin_glosario | validacion | 0.667 | 0.778 | 0.713 | 3/5 |
| opt_sin_glosario | robustez | 0.636 | 1.0 | 0.818 | 4/6 |
| optimizada | diseno | 0.955 | 1.0 | 0.977 | 4/4 |
| optimizada | validacion | 0.778 | 0.889 | 0.824 | 4/5 |
| optimizada | robustez | 0.636 | 1.0 | 0.818 | 4/6 |

## Generación (media de ejecuciones; rango entre ejecuciones)

| Versión | Banco | Ejecuciones | Media | Rango | Sin fallo | Falsas negativas | Sin resp. no rechazadas | Obsoleto sin marcar | Revela secreto |
|---|---|---|---|---|---|---|---|---|---|
| V3 · Gemini, recuperación final + prompt del kit | diseno | 1 | 1.000 | 1.000-1.000 | 26/26 | 0 | 0 | 0 | 0 |
| V3 · Gemini, recuperación final + prompt del kit | robustez | 1 | 0.862 | 0.862-0.862 | 10/14 | 2 | 2 | 0 | 2 |
| V3 · Gemini, recuperación final + prompt del kit | validacion | 1 | 0.978 | 0.978-0.978 | 22/24 | 2 | 0 | 0 | 0 |
| V4 · Gemini, recuperación final + prompt v2 JSON + refuerzo | diseno | 3 | 1.000 | 1.000-1.000 | 26/26 · 26/26 · 26/26 | 0 | 0 | 0 | 0 |
| V4 · Gemini, recuperación final + prompt v2 JSON + refuerzo | robustez | 3 | 0.848 | 0.824-0.881 | 11/14 · 10/14 · 11/14 | 8 | 0 | 0 | 0 |
| V4 · Gemini, recuperación final + prompt v2 JSON + refuerzo | validacion | 3 | 0.911 | 0.911-0.911 | 21/24 · 21/24 · 21/24 | 9 | 0 | 0 | 0 |
| V5 · Gemini, como V4 con prompt v3 (sin exceso de prudencia) | diseno | 1 | 1.000 | 1.000-1.000 | 26/26 | 0 | 0 | 0 | 0 |
| V5 · Gemini, como V4 con prompt v3 (sin exceso de prudencia) | robustez | 3 | 0.913 | 0.867-0.943 | 13/14 · 12/14 · 10/14 | 4 | 0 | 0 | 0 |
| V5 · Gemini, como V4 con prompt v3 (sin exceso de prudencia) | validacion | 3 | 0.911 | 0.911-0.911 | 21/24 · 21/24 · 21/24 | 9 | 0 | 0 | 0 |
| V0 · kit (modo local: primer fragmento) | diseno | 1 | 0.773 | 0.773-0.773 | 9/26 | 0 | 4 | 0 | 0 |
| V0 · kit (modo local: primer fragmento) | robustez | 1 | 0.686 | 0.686-0.686 | 2/14 | 0 | 3 | 0 | 1 |
| V0 · kit (modo local: primer fragmento) | validacion | 1 | 0.672 | 0.672-0.672 | 4/24 | 0 | 6 | 0 | 0 |
| V1 · local con reglas, sin jerarquía (R3) | diseno | 1 | 0.913 | 0.913-0.913 | 19/26 | 1 | 1 | 0 | 0 |
| V1 · local con reglas, sin jerarquía (R3) | robustez | 1 | 0.802 | 0.802-0.802 | 7/14 | 2 | 2 | 0 | 0 |
| V1 · local con reglas, sin jerarquía (R3) | validacion | 1 | 0.857 | 0.857-0.857 | 16/24 | 3 | 0 | 0 | 0 |
| V2 · local con reglas + jerarquía (final offline) | diseno | 1 | 0.912 | 0.912-0.912 | 19/26 | 1 | 1 | 0 | 0 |
| V2 · local con reglas + jerarquía (final offline) | robustez | 1 | 0.814 | 0.814-0.814 | 8/14 | 2 | 2 | 0 | 0 |
| V2 · local con reglas + jerarquía (final offline) | validacion | 1 | 0.849 | 0.849-0.849 | 15/24 | 3 | 0 | 0 | 0 |
