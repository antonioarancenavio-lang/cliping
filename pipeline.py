"""
Pipeline completo: vídeo largo -> clips verticales con subtítulos, listos para publicar.

Por defecto usa detect_highlights.py (reglas heurísticas, 100% gratis, sin API).
Cuando tengas presupuesto, cambia el import de abajo por detect_highlights_ia.py
para que la selección de momentos la haga la API de Claude.

Uso:
    python3 pipeline.py sermon.mp4 output/
"""
import json
import os
import sys

from transcribe import transcribe
from detect_highlights import detect_highlights
from cut_clips import cut_clip


def run_pipeline(video_path: str, output_dir: str, max_clips: int = 5):
    print("1/3 Transcribiendo...")
    segments = transcribe(video_path)
    with open(os.path.join(output_dir, "transcript.json"), "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print("2/3 Detectando los mejores momentos...")
    clips = detect_highlights(segments, max_clips=max_clips)
    with open(os.path.join(output_dir, "clips.json"), "w", encoding="utf-8") as f:
        json.dump(clips, f, ensure_ascii=False, indent=2)

    print(f"3/3 Generando {len(clips)} clips...")
    generated = []
    for clip in clips:
        path = cut_clip(video_path, segments, clip, output_dir)
        generated.append(path)
        print(f"  -> {path}")

    return generated


if __name__ == "__main__":
    video_path, output_dir = sys.argv[1], sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    run_pipeline(video_path, output_dir)
