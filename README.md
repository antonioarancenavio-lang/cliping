# Vigilia — web de clipping de prédicas

## Por qué te daba 404

Ese error venía de Vercel intentando servir una URL sin nada desplegado detrás.
Es importante entender esto para no repetirlo: **el pipeline de clipping
(transcripción con Whisper + recorte con ffmpeg) no puede correr en Vercel**,
porque:
- Las funciones serverless de Vercel tienen un límite de tiempo de ejecución corto; procesar un vídeo de 40 minutos tarda varios minutos.
- No tienen `ffmpeg` instalado por defecto.
- No guardan archivos entre peticiones (sistema de archivos efímero).

Por eso este proyecto se divide en **dos partes que se despliegan en sitios distintos**:

```
clipping-web/       -> Vercel (la página, estática, siempre gratis)
clipping-backend/   -> Railway / Render / un VPS (procesa los vídeos)
```

## 1. La web (`clipping-web/`) → Vercel

Es un único `index.html` sin build ni dependencias — cero configuración.

```bash
cd clipping-web
git init && git add . && git commit -m "web de Vigilia"
git branch -M main
git remote add origin https://github.com/tu-usuario/vigilia-web.git
git push -u origin main
```

Luego en [vercel.com](https://vercel.com) → **Add New Project** → importa ese repo.
Como es HTML estático, Vercel lo detecta solo, sin "Framework Preset" que configurar.
Con esto ya no te dará más 404: la web se sirve sola, aunque el backend
todavía no exista (el formulario simplemente avisa de que falta conectarlo,
en vez de fallar en silencio).

## 2. El backend (`clipping-backend/`) → Railway o Render

Este es el que necesita quedarse encendido y con ffmpeg disponible.
**Railway** es la opción más simple para empezar (tiene un plan gratuito con
horas limitadas al mes, suficiente para validar):

```bash
cd clipping-backend
git init && git add . && git commit -m "backend de Vigilia"
git branch -M main
git remote add origin https://github.com/tu-usuario/vigilia-backend.git
git push -u origin main
```

En Railway: **New Project → Deploy from GitHub repo** → selecciona este repo.
Railway detecta Python solo. Define el comando de arranque:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
Y añade un `nixpacks.toml` (incluido) para que instale `ffmpeg` en el contenedor.

## 3. Conectar la web con el backend

Una vez el backend esté desplegado, tendrás una URL tipo
`https://vigilia-backend-production.up.railway.app`.

Añade esta línea justo antes del `</body>` de `index.html`, con tu URL real:
```html
<script>window.VIGILIA_BACKEND_URL = "https://tu-backend.up.railway.app";</script>
```

Sube ese cambio a GitHub y Vercel redespliega solo.

## Ya probado en este entorno
- El backend arranca y `/health` responde correctamente.
- `/process` recibe el vídeo, ejecuta el pipeline completo y devuelve error
  controlado (no un crash) cuando algo falla — probado con un vídeo real.
- La descarga del modelo de Whisper falla aquí porque este entorno de
  pruebas bloquea `huggingface.co`; en Railway/Render no tendrás esa
  restricción y descargará el modelo la primera vez sin problema.

## Nota sobre el coste
El backend en Railway/Render tiene un coste pequeño una vez superes el plan
gratuito (procesar vídeo consume CPU un rato). La detección de momentos sigue
usando la versión gratuita (`detect_highlights.py`, sin API) por defecto,
tal como quedó configurado — nada de esto requiere `ANTHROPIC_API_KEY`
todavía.
