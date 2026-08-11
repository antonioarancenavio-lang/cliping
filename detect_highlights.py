"""
Detecta los mejores momentos de una transcripción SIN usar ninguna API de pago.
Usa reglas heurísticas pensadas para prédicas/sermones: palabras clave de
impacto, signos de exclamación/interrogación, duración ideal del fragmento
y agrupación de segmentos consecutivos en un clip coherente.

Cuando tengas presupuesto, sustituye este módulo por detect_highlights_ia.py
(usa la API de Claude) para una selección más precisa.
"""
import re

# Palabras y expresiones típicas de un momento "fuerte" o citable en una prédica.
# Ajusta esta lista según el tono real de los sermones que proceses.
PALABRAS_CLAVE = [
    "nunca", "jamás", "siempre", "dios", "fe", "milagro", "esperanza",
    "amor", "perdón", "victoria", "libertad", "salvación", "gracia",
    "levántate", "levantate", "recuerda", "hoy", "ahora", "no estás solo",
    "no están solos", "amén", "gloria", "poder", "verdad", "promesa",
]

MIN_CLIP_DURATION = 15
MAX_CLIP_DURATION = 75
MAX_GAP_BETWEEN_SEGMENTS = 3.0  # segundos; si hay más hueco, no se agrupan


def _score_segment(text: str) -> float:
    text_lower = text.lower()
    score = 0.0

    for palabra in PALABRAS_CLAVE:
        if palabra in text_lower:
            score += 2.0

    score += text.count("!") * 1.5
    score += text.count("?") * 1.0

    # Frases cortas y contundentes puntúan más que párrafos largos y dispersos.
    palabra_count = len(text.split())
    if 5 <= palabra_count <= 25:
        score += 1.0

    return score


def _group_into_candidates(segments: list) -> list:
    """Agrupa segmentos consecutivos (sin huecos grandes) en bloques candidatos a clip."""
    groups = []
    current = []

    for seg in segments:
        if current and (seg["start"] - current[-1]["end"]) > MAX_GAP_BETWEEN_SEGMENTS:
            groups.append(current)
            current = []
        current.append(seg)

    if current:
        groups.append(current)

    return groups


def _best_window(group: list) -> dict:
    """Dentro de un grupo, busca la subventana con mejor puntuación y duración válida."""
    best = None
    best_score = -1.0

    n = len(group)
    for i in range(n):
        acc_score = 0.0
        for j in range(i, n):
            acc_score += _score_segment(group[j]["text"])
            duration = group[j]["end"] - group[i]["start"]

            if duration < MIN_CLIP_DURATION:
                continue
            if duration > MAX_CLIP_DURATION:
                break

            # Normalizamos un poco por duración para no premiar solo clips larguísimos.
            normalized = acc_score / (1 + duration / 60)
            if normalized > best_score:
                best_score = normalized
                best = {
                    "start": group[i]["start"],
                    "end": group[j]["end"],
                    "text": " ".join(s["text"] for s in group[i:j + 1]),
                    "score": acc_score,
                }

    return best


def _make_title(text: str) -> str:
    """Genera un título corto a partir de la primera frase del clip."""
    clean = re.split(r"[.!?]", text.strip())[0]
    words = clean.split()
    return " ".join(words[:8]) if words else "Clip"


def detect_highlights(segments: list, max_clips: int = 5) -> list:
    """
    Versión sin IA de pago: agrupa la transcripción en bloques, puntúa cada
    posible ventana por palabras clave/puntuación/duración, y devuelve los
    mejores `max_clips` candidatos, ordenados por aparición en el vídeo.
    """
    groups = _group_into_candidates(segments)

    candidates = []
    for group in groups:
        best = _best_window(group)
        if best:
            candidates.append(best)

    # Nos quedamos con los de mayor puntuación...
    candidates.sort(key=lambda c: c["score"], reverse=True)
    top = candidates[:max_clips]
    # ...pero los devolvemos en orden cronológico, como en el vídeo original.
    top.sort(key=lambda c: c["start"])

    return [
        {
            "start": c["start"],
            "end": c["end"],
            "title": _make_title(c["text"]),
            "reason": f"Puntuación heurística: {round(c['score'], 1)} (palabras clave, énfasis, duración)",
        }
        for c in top
    ]


if __name__ == "__main__":
    import sys, json

    with open(sys.argv[1], encoding="utf-8") as f:
        segments = json.load(f)
    clips = detect_highlights(segments)
    print(json.dumps(clips, ensure_ascii=False, indent=2))
