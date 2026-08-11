# MVP: Clipping automático para prédicas (nicho: iglesias hispanohablantes)
Pipeline mínimo que convierte un vídeo largo (sermón/prédica) en clips verticales
con subtítulos, listos para TikTok/Reels/Shorts.

## Cómo funciona (`pipeline.py`)
1. **`transcribe.py`** — transcribe el vídeo localmente con `faster-whisper` (gratis, sin API de pago). Descarga el modelo la primera vez que se ejecuta.
2. **`detect_highlights.py`** — **100% GRATIS, sin API de pago.** Usa reglas heurísticas (palabras clave típicas de una prédica, signos de exclamación/interrogación, duración ideal del fragmento) para elegir los 3-5 mejores momentos. Es menos preciso que una IA, pero sirve perfectamente para validar el negocio sin gastar nada.
3. **`cut_clips.py`** — recorta cada fragmento con `ffmpeg`, lo reencuadra a formato vertical 9:16 y quema los subtítulos.

**Ya probado y funcionando en este entorno de punta a punta**, sin ninguna clave de API: detección heurística de momentos + recorte + reencuadre + subtítulos quemados (ver `output/` con un vídeo de prueba real).

### Cuando tengas presupuesto: `detect_highlights_ia.py`
Está incluido y listo un segundo módulo, `detect_highlights_ia.py`, que hace lo mismo pero usando la API de Claude para una selección mucho más precisa (entiende contexto, no solo palabras clave). Cuesta céntimos por vídeo. Para activarlo:
1. En `pipeline.py`, cambia `from detect_highlights import detect_highlights` por `from detect_highlights_ia import detect_highlights`.
2. `export ANTHROPIC_API_KEY=sk-ant-tu-clave`

## Cómo probarlo tú
```bash
pip install -r requirements.txt
python3 pipeline.py ruta/a/tu_sermon.mp4 output/
```

La primera ejecución descarga el modelo de Whisper (`small`, ~500MB); tarda un poco más esa vez. No hace falta ninguna clave de API para esta versión gratuita.

## Qué falta para convertirlo en el SaaS
- **Interfaz web** (subida de vídeo o enlace de YouTube, previsualización de clips, descarga) — encaja con tu stack de React + Vercel.
- **Cola de procesamiento** (los vídeos de 40-60 min tardan varios minutos en transcribirse y recortarse): mover el procesamiento pesado a un worker/servidor en vez de una función serverless con límite de tiempo.
- **Autenticación y planes de suscripción** (Stripe).
- **Mejora del reencuadre**: ahora mismo el crop es centrado fijo; para un resultado más profesional habría que detectar y seguir al orador (face-tracking), como hacen los competidores.
- **Validación con iglesias reales**: antes de invertir en la web completa, probar el pipeline con 5-10 sermones reales y mostrar los clips a un par de iglesias para confirmar que el criterio de selección de la IA acierta.

## Estructura de archivos
```
transcribe.py              # transcripción local (faster-whisper)
detect_highlights.py       # selección de momentos GRATIS (reglas heurísticas)
detect_highlights_ia.py    # selección de momentos con IA (API de Claude, cuando haya presupuesto)
cut_clips.py                # recorte + subtítulos + reencuadre (ffmpeg)
pipeline.py                 # orquesta los tres pasos
requirements.txt
```
