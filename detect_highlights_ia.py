"""
Detecta los mejores momentos de una transcripción usando la API de Claude.
Pensado para prédicas/sermones: prioriza frases citables, mensajes fuertes,
llamados a la acción y momentos con carga emocional.
"""
import json
import os
import urllib.request

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """Eres un editor experto en repurposing de contenido para iglesias.
Recibes la transcripción de una prédica con marcas de tiempo por segmento.
Tu tarea: identificar los mejores fragmentos para convertir en clips verticales
de redes sociales (TikTok, Reels, Shorts).

Criterios de selección:
- Frases citables o memorables, con carga emocional o inspiradora.
- Momentos con mensaje completo y autocontenido (no cortar una idea a medias).
- Llamados a la acción o reflexiones que enganchen en los primeros 2 segundos.
- Duración ideal por clip: entre 20 y 75 segundos.

Devuelve SOLO un JSON (sin texto adicional, sin markdown) con esta forma exacta:
{"clips": [{"start": <float>, "end": <float>, "title": "<titulo corto para el clip>", "reason": "<por que funciona>"}]}
"""


def detect_highlights(segments: list, max_clips: int = 5) -> list:
    transcript_text = "\n".join(
        f"[{s['start']}s -> {s['end']}s] {s['text']}" for s in segments
    )

    body = {
        "model": MODEL,
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": f"Selecciona hasta {max_clips} clips de esta transcripción:\n\n{transcript_text}",
            }
        ],
    }

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()

    # El modelo puede envolver el JSON en ```json ... ``` a veces; lo limpiamos por seguridad.
    text = text.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(text)
    return parsed["clips"]


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], encoding="utf-8") as f:
        segments = json.load(f)
    clips = detect_highlights(segments)
    print(json.dumps(clips, ensure_ascii=False, indent=2))
