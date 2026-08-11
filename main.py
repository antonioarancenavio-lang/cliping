"""
Backend mínimo que expone el pipeline de clipping como una API.

Este servicio NO va en Vercel: necesita ffmpeg instalado, descarga un modelo
de Whisper y procesar un vídeo tarda varios minutos — todo eso excede lo que
una función serverless de Vercel puede hacer (por eso el 404: la web estaba
desplegada pero no había ningún backend real detrás para procesar nada).

Despliega esto en un sitio con proceso persistente: Railway, Render o un VPS.
La web (index.html) le apunta a través de VIGILIA_BACKEND_URL.
"""
import os
import shutil
import tempfile
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pipeline import run_pipeline

app = FastAPI(title="Vigilia — clipping de prédicas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción, limita esto al dominio de tu web
    allow_methods=["*"],
    allow_headers=["*"],
)

JOBS_DIR = os.path.join(tempfile.gettempdir(), "vigilia-jobs")
os.makedirs(JOBS_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=JOBS_DIR), name="files")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
async def process(file: UploadFile = File(None), url: str = Form(None)):
    if not file and not url:
        return {"error": "Sube un archivo o pasa una URL."}

    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    if file:
        video_path = os.path.join(job_dir, file.filename)
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    else:
        # Descargar desde YouTube/Facebook requiere yt-dlp; se añade cuando
        # se active este flujo (no incluido en el MVP para mantenerlo simple).
        return {"error": "La subida por enlace todavía no está implementada. Sube el archivo directamente."}

    try:
        clip_paths = run_pipeline(video_path, job_dir)
    except Exception as exc:
        return {"error": f"Fallo procesando el vídeo: {exc}"}

    clip_urls = [f"/files/{job_id}/{os.path.basename(p)}" for p in clip_paths]
    return {
        "message": f"{len(clip_paths)} clips generados.",
        "job_id": job_id,
        "clips": clip_urls,
    }
