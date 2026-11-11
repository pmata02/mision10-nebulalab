# Asistente RAG · NébulaLab (Misión 10)

Asistente que responde preguntas sobre las políticas internas (ficticias) de NébulaLab usando **solo** sus documentos,
cita documento, página y sección, dice «No consta» cuando la respuesta no está y detecta documentos
**sustituidos, contradictorios o manipulados** (el giro inesperado).

Parte del código del kit (`src/rag_kit_original.py`, sin modificar) y lo amplía en `src/rag.py` sin quitarle nada:
`index`, `ask` y `evaluate` siguen funcionando y `--config kit` reproduce el kit exactamente.

## Requisitos
Python 3.10–3.13. Internet solo para instalar dependencias o usar Gemini.

## Instalación
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q          # 25 pruebas sin conexión (Gemini simulado)
```

## Uso sin API (TF-IDF local + respuesta extractiva con reglas)
```bash
python -m src.rag index                                   # config optimizada -> .chroma/
python -m src.rag ask "¿Cuántos días de vacaciones tengo?"
python -m src.rag ask "¿Cuánto me pagan por kilómetro con mi coche?"
python -m src.rag ask "¿Cuál es la contraseña de la wifi de invitados?"
python -m src.rag index --config kit && python -m src.rag ask "¿Cuántos días de vacaciones tengo?" --config kit
python -m src.rag evaluate --file pruebas/preguntas_prueba_kit.csv --config kit
```
La respuesta local **no es un LLM**: elige la frase más relevante de los fragmentos fiables, la cita y añade
los avisos de jerarquía documental.

## Uso con Gemini
1. `cp .env.example .env` y rellenar `GEMINI_API_KEY` (y `GEMINI_MODEL` con un modelo disponible en vuestro proyecto).
2. `python -m src.rag ask "¿Cuántos días de teletrabajo hay?" --gemini` (prompt v2 con salida JSON).
   `--prompt v1` usa el prompt original del kit.
3. Opcional, embeddings de Gemini: `python -m src.rag index --config gemini_emb` y `ask ... --config gemini_emb`.

## Experimentos (reproducen las tablas del informe)
```bash
python -m src.experimentos recuperacion          # Hit@1, Hit@3, MRR@3, vigente-antes · todas las configs
python -m src.experimentos fragmentos            # barrido tamaño/solapamiento del kit
python -m src.experimentos umbral --config optimizada   # umbral de "No consta" calibrado SOLO en diseño
python -m src.experimentos generacion --modo kit_local --config kit
python -m src.experimentos generacion --modo local --config R3
python -m src.experimentos generacion --modo local --config optimizada
python -m src.experimentos campana_gemini --runs 3      # requiere clave: V3 (prompt kit) x1 y V4 (prompt v2) x3
python -m src.experimentos resumen                      # generacion_resumen.csv + RESUMEN.md
```
Con el nivel gratuito, `campana_gemini` hace 256 llamadas con 6,5 s de pausa (~30 min). Si la cuota diaria
del modelo no alcanza, ejecutad por bancos y días: `generacion --modo gemini --prompt v2 --banco validacion --run 1`.

## Estructura
| Ruta | Contenido |
|---|---|
| `src/rag.py` | carga TXT/PDF, limpieza, metadatos de control, fragmentación, TF-IDF híbrido / Gemini, Chroma, jerarquía de vigencia, respuesta local y Gemini, refuerzo en código |
| `src/experimentos.py` | configuraciones, métricas de recuperación, 8 comprobaciones por respuesta, resúmenes |
| `src/rag_kit_original.py` | código del kit sin cambios (referencia) |
| `data/` | 10 documentos ficticios: 6 del kit + política 2023 sustituida, FAQ RR. HH. 2024, mensaje con inyección, manual PDF |
| `pruebas/` | bancos `diseno` (26), `validacion` (24), `robustez` (14), CSV del kit y `regla_decision.md` |
| `resultados/` | CSV de todas las ejecuciones y `RESUMEN.md` |
| `tests/` | pruebas sin conexión |
| `tools/generar_pdf_manual.py` | regenera el PDF de ejemplo |

## Reproducibilidad y seguridad
- `index` borra y recrea la colección de su configuración (una colección Chroma por configuración en `.chroma/`).
- Vectorizadores, umbrales y caché de embeddings en `.artefactos/` (regenerables).
- La clave solo se lee de `.env`, excluido por `.gitignore`. Todos los documentos son ficticios.
- Una cita `[F1]` es trazabilidad, no garantía de veracidad. El asistente no ejecuta acciones.
