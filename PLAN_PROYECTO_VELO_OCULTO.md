# 🔮 VELO OCULTO — Automatización de YouTube Shorts

## INSTRUCCIONES PARA CLAUDE CODE

**Lee este archivo completo antes de escribir una sola línea de código.**
Construye TODO el proyecto de una sola pasada siguiendo el orden de implementación del final.
No preguntes, no pidas confirmación. Solo construye.

---

## Descripción

Sistema en Python que genera YouTube Shorts automáticamente para el canal "Velo Oculto" (teorías conspirativas). Lee guiones pre-escritos de un JSON, genera audio, descarga imágenes, agrega subtítulos estilo TikTok, efectos de sonido ambientales y música de fondo, ensambla el video y lo sube a YouTube como Short. Publica 3 videos diarios (8am, 12pm, 5pm hora Ecuador UTC-5).

**Solo YouTube.** Facebook se hará en otro proyecto.

---

## Arquitectura

```
velo-oculto/
├── .env                            # API keys (Pexels + YouTube OAuth path)
├── .gitignore                      # Ignorar .env, credentials/, output/, __pycache__
├── config.yaml                     # Configuración general
├── main.py                         # Genera y sube 1 video
├── scheduler.py                    # Corre 24/7, ejecuta main.py en horarios
├── modules/
│   ├── __init__.py
│   ├── script_queue.py             # Cola: toma siguiente guión, marca usado
│   ├── tts_engine.py               # edge-tts → audio + timestamps
│   ├── image_fetcher.py            # Pexels API → imágenes verticales
│   ├── subtitle_generator.py       # VTT → bloques de 3 palabras
│   ├── sfx_engine.py               # Efectos de sonido ambientales
│   ├── hashtag_optimizer.py        # Genera hashtags optimizados por tema
│   ├── video_assembler.py          # Ensambla todo → .mp4 final
│   └── youtube_uploader.py         # Sube como YouTube Short
├── data/
│   ├── guionesVeloOculto.json      # ← Guiones pre-escritos por el usuario (120+)
│   └── historial.json              # Registro de guiones usados (se crea solo)
├── assets/
│   ├── fonts/
│   │   └── Montserrat-Bold.ttf     # Descargar de Google Fonts
│   ├── music/                      # 5-10 tracks de dark ambient (Pixabay Music)
│   │   └── README.md               # Instrucciones de dónde descargar
│   └── sfx/                        # Efectos de sonido
│       ├── whisper.mp3             # Susurro misterioso
│       ├── static.mp3              # Estática de TV/radio
│       ├── heartbeat.mp3           # Latido de corazón
│       ├── deep_drone.mp3          # Drone grave/ominoso
│       ├── reverse_cymbal.mp3      # Platillo reversa (para transiciones)
│       └── README.md               # Instrucciones de dónde descargar gratis
├── output/
│   ├── videos/                     # Videos generados
│   └── audio/                      # Audio narrado
├── logs/
│   └── velo_oculto.log
├── credentials/
│   ├── youtube_client_secret.json  # OAuth de Google Cloud (usuario lo descarga)
│   └── youtube_token.pickle        # Se genera automático en primera ejecución
├── requirements.txt
├── setup.sh                        # Instala todo
└── README.md                       # Instrucciones de uso
```

---

## .env (API Keys)

```env
# PEXELS (gratis) → https://www.pexels.com/api/
PEXELS_API_KEY=XXXXXXXXXX

# YOUTUBE → No va key aquí, usa OAuth con archivo JSON
# El archivo va en: credentials/youtube_client_secret.json
```

Solo dos cosas. Pexels en el .env, YouTube con su JSON aparte.

---

## .gitignore

```
.env
credentials/
output/
logs/
__pycache__/
*.pickle
*.pyc
data/historial.json
```

---

## config.yaml

```yaml
canal:
  nombre: "Velo Oculto"
  timezone: "America/Guayaquil"

horarios:
  - "08:00"
  - "12:00"
  - "17:00"

video:
  duracion_max: 58                  # Segundos (margen bajo 60 para Shorts)
  resolucion: [1080, 1920]          # 9:16 vertical obligatorio
  fps: 30
  codec_video: "libx264"
  codec_audio: "aac"

tts:
  voz: "es-MX-JorgeNeural"
  velocidad: "-5%"

subtitulos:
  fuente: "assets/fonts/Montserrat-Bold.ttf"
  tamaño: 55
  color: "#FFFFFF"
  color_resaltado: "#FFD700"        # Dorado para palabra actual
  color_borde: "#000000"
  grosor_borde: 4
  palabras_por_bloque: 3
  posicion_y: 0.45                  # Centro-ligeramente arriba (0.0=top, 1.0=bottom)

musica:
  volumen: 0.06
  fade_in: 1.5
  fade_out: 2.5
  carpeta: "assets/music/"

sfx:
  activo: true
  volumen: 0.15
  # El sistema inserta automáticamente:
  # - 1 efecto al inicio (primeros 3 seg) para enganchar
  # - 1-2 efectos durante el video en momentos de pausa ("...")
  # - 1 efecto al cierre
  carpeta: "assets/sfx/"

imagenes:
  duracion_por_imagen: 4
  efecto_zoom: true                 # Ken Burns
  zoom_factor: 1.12                 # Zoom de 1.0 a 1.12
  filtro_oscuro: 0.35
  fallback_keywords:                # Si las del guión no dan resultados
    - "dark mystery"
    - "night sky stars"
    - "abandoned building"
    - "shadow silhouette"
    - "ancient ruins dark"

youtube:
  categoria_id: "22"
  privacidad: "public"
  sufijo_titulo: " #Shorts"
  tags_base:
    - "velo oculto"
    - "teorias conspirativas"
    - "misterios"
    - "shorts"
    - "misterios sin resolver"

guiones:
  archivo: "data/guionesVeloOculto.json"
  historial: "data/historial.json"
```

---

## Formato del JSON de guiones (guionesVeloOculto.json)

El usuario ya tiene este archivo listo. El sistema lo lee tal cual.

```json
{
  "guiones": [
    {
      "id": 1,
      "titulo": "Lo que la NASA borró de sus archivos en 1969",
      "texto_narrado": "¿Te has preguntado... qué fue lo que realmente encontraron en la Luna? Se dice que las transmisiones originales del Apolo 11... tenían 2 minutos que fueron cortados. Algunos exempleados de la NASA afirman... que en esos 2 minutos... los astronautas reportaron estructuras en el horizonte lunar. La NASA jamás confirmó ni negó esto. Lo que sí sabemos... es que las cintas originales fueron convenientemente borradas en 2006. ¿Por qué destruir algo tan histórico? Hay quienes creen que la respuesta... es que no estamos solos. Sígueme para más secretos.",
      "descripcion_youtube": "🔮 ¿Qué borró la NASA del Apolo 11? 🌑 #velooculto #nasa #conspiracion #misterios #shorts",
      "tags": ["nasa", "apolo 11", "luna", "conspiracion", "misterio"],
      "keywords_imagenes": ["nasa apollo", "moon surface", "dark space"]
    },
    {
      "id": 2,
      "titulo": "...",
      "texto_narrado": "...",
      "descripcion_youtube": "...",
      "tags": ["..."],
      "keywords_imagenes": ["..."]
    }
  ]
}
```

**Campos obligatorios por guión:**
- `id` → número secuencial (1, 2, 3...)
- `titulo` → máximo 60 caracteres, clickbait misterioso
- `texto_narrado` → 120-140 palabras, usar "..." para pausas
- `descripcion_youtube` → máx 200 chars, emojis + hashtags
- `tags` → lista de 3-5 tags en español
- `keywords_imagenes` → lista de 2-3 keywords en INGLÉS para Pexels

---

## Módulos — Especificaciones

### modules/script_queue.py

```python
"""
Cola de guiones. Lee guionesVeloOculto.json, lleva control de cuál toca.
"""
import json
import os
from datetime import datetime

GUIONES_PATH = "data/guionesVeloOculto.json"
HISTORIAL_PATH = "data/historial.json"

def _cargar_historial():
    if not os.path.exists(HISTORIAL_PATH):
        return {"usados": [], "fallidos": []}
    with open(HISTORIAL_PATH) as f:
        return json.load(f)

def _guardar_historial(hist):
    with open(HISTORIAL_PATH, "w") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)

def obtener_siguiente_guion():
    """Retorna el siguiente guión no usado. None si no quedan."""
    with open(GUIONES_PATH) as f:
        data = json.load(f)
    hist = _cargar_historial()
    ids_usados = set(hist["usados"])
    for guion in data["guiones"]:
        if guion["id"] not in ids_usados:
            return guion
    return None  # Se acabaron

def marcar_completado(guion_id):
    hist = _cargar_historial()
    hist["usados"].append(guion_id)
    if guion_id in hist.get("fallidos", []):
        hist["fallidos"].remove(guion_id)
    _guardar_historial(hist)

def marcar_fallido(guion_id):
    hist = _cargar_historial()
    if guion_id not in hist.get("fallidos", []):
        hist["fallidos"].append(guion_id)
    _guardar_historial(hist)

def obtener_estado():
    with open(GUIONES_PATH) as f:
        total = len(json.load(f)["guiones"])
    hist = _cargar_historial()
    usados = len(hist["usados"])
    fallidos = len(hist.get("fallidos", []))
    return {"total": total, "usados": usados, "pendientes": total - usados, "fallidos": fallidos}

def regenerar_fallidos():
    hist = _cargar_historial()
    for fid in hist.get("fallidos", []):
        if fid in hist["usados"]:
            hist["usados"].remove(fid)
    hist["fallidos"] = []
    _guardar_historial(hist)
```

### modules/tts_engine.py

Usa edge-tts (100% gratis, sin API key). Genera audio .mp3 + archivo .vtt con timestamps por palabra.

```python
import edge_tts
import asyncio

async def generar_audio(texto, output_path, voz="es-MX-JorgeNeural", velocidad="-5%"):
    communicate = edge_tts.Communicate(texto, voz, rate=velocidad)
    submaker = edge_tts.SubMaker()
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
    vtt_path = output_path.replace(".mp3", ".vtt")
    with open(vtt_path, "w") as f:
        f.write(submaker.generate_subs())
    return output_path, vtt_path
```

### modules/image_fetcher.py

Descarga imágenes verticales de Pexels. API key del .env.

Lógica:
1. Recibe lista de keywords del guión (en inglés)
2. Para cada keyword: `GET https://api.pexels.com/v1/search?query={kw}&orientation=portrait&per_page=10&size=large`
3. Header: `Authorization: {PEXELS_API_KEY}`
4. Descarga las imágenes más relevantes
5. Si no hay suficientes, usa `fallback_keywords` del config
6. Necesita ~14 imágenes (58 seg ÷ 4 seg/imagen)
7. Redimensiona a 1080x1920 con PIL (crop al centro si no es 9:16)
8. Aplica overlay negro al 35% de opacidad
9. Guarda en una carpeta temporal y retorna lista de paths
10. IMPORTANTE: cachear imágenes por keyword para no repetir llamadas a la API

### modules/subtitle_generator.py

Lee el .vtt de edge-tts y agrupa en bloques de 3 palabras.

Retorna: `[{"texto": "tres palabras aquí", "inicio": 2.5, "fin": 3.8}, ...]`

Parsear el VTT manualmente (el formato es simple):
```
00:00:00.500 --> 00:00:01.200
palabra
```

Agrupar cada 3 palabras, usando el inicio de la primera y el fin de la última como tiempos del bloque.

### modules/sfx_engine.py

Agrega efectos de sonido ambientales al video automáticamente.

Lógica:
1. Analiza el `texto_narrado` buscando pausas marcadas con "..."
2. Elige puntos de inserción:
   - Segundo 0-2: un efecto de "apertura" (deep_drone o reverse_cymbal)
   - En cada "..." del guión: probabilidad del 40% de insertar un efecto (whisper, static, heartbeat)
   - Últimos 3 segundos: efecto de cierre (deep_drone con fade out)
3. Selecciona efectos aleatorios de `assets/sfx/`
4. Retorna lista de: `[{"archivo": "whisper.mp3", "segundo": 15.5, "volumen": 0.15}, ...]`
5. El video_assembler los mezcla en el audio final

**Dónde descargar los SFX gratis (poner en assets/sfx/README.md):**
- https://pixabay.com/sound-effects/ (buscar: whisper, static, heartbeat, drone, horror ambience)
- https://freesound.org/ (crear cuenta gratis, buscar: dark ambient, suspense hit, reverse cymbal)
- Descargar como .mp3, recortar a 1-3 segundos máximo con cualquier editor o ffmpeg

### modules/hashtag_optimizer.py

Genera hashtags optimizados para cada video basándose en el tema.

```python
# Banco de hashtags organizados por categoría/keyword
HASHTAG_BANK = {
    "default": ["#velooculto", "#misterios", "#conspiracion", "#shorts", "#misteriossinresolver"],
    "nasa": ["#nasa", "#espacio", "#ovnis", "#universo"],
    "illuminati": ["#illuminati", "#sociedadsecreta", "#nuevoordenmundial"],
    "gobierno": ["#gobiernosecreto", "#encubrimiento", "#documentossecretos"],
    "historia": ["#historiaoscura", "#historiaprohibida", "#losquenocuentan"],
    "ciencia": ["#cienciaoculta", "#experimentosecreto", "#proyectoclasificado"],
    "desapariciones": ["#desaparicionesmisteriosas", "#casossinresolver", "#misterio"],
    "egipto": ["#piramides", "#egipto", "#antiguosecreto", "#faraones"],
    "tecnologia": ["#tecnologiaoculta", "#haarp", "#controlmental"],
    "apocalipsis": ["#fintiempos", "#profecias", "#predicciones"],
}

def generar_hashtags(tags_guion, max_hashtags=12):
    """
    Recibe los tags del guión, busca coincidencias en el banco,
    combina con los default y retorna string de hashtags.
    Máximo 12 hashtags (YouTube penaliza si son demasiados).
    """
    resultado = set(HASHTAG_BANK["default"])
    for tag in tags_guion:
        tag_lower = tag.lower()
        for key, hashtags in HASHTAG_BANK.items():
            if key in tag_lower or tag_lower in key:
                resultado.update(hashtags[:3])
    # Agregar hashtags genéricos del nicho que rotan
    genericos = ["#datoscuriosos", "#sabíasque", "#viral", "#fyp",
                 "#teorias", "#enigmas", "#secretos", "#paranormal",
                 "#inexplicable", "#nocreerasesto", "#impactante"]
    import random
    resultado.update(random.sample(genericos, min(3, len(genericos))))
    return " ".join(list(resultado)[:max_hashtags])
```

El hashtag_optimizer se llama desde main.py y el resultado se agrega a la descripcion_youtube antes de subir.

### modules/video_assembler.py

El módulo central. Ensambla todo en un Short de máx 58 segundos.

**Pasos detallados:**

1. **Cargar audio narrado** con moviepy/AudioFileClip → medir duración
2. **Verificar** que la duración sea ≤ 58 seg. Si es mayor, loggear warning.
3. **Crear clips de imagen:**
   - Para cada imagen: ImageClip con duración de 4 seg
   - Resize a 1080x1920 (crop center si la relación no es 9:16)
   - Aplicar efecto Ken Burns: zoom progresivo de 1.0x a 1.12x
     (usar moviepy resize con una función lambda que depende del tiempo)
   - Alternar dirección del zoom (unos zoom-in, otros zoom-out) para variedad
4. **Concatenar** todos los clips de imagen en secuencia
5. **Audio track 1:** narración (volumen 1.0)
6. **Audio track 2:** música de fondo
   - Elegir archivo aleatorio de `assets/music/`
   - Volumen 0.06
   - Fade in 1.5 seg, fade out 2.5 seg
   - Loop si el track es más corto que el video
   - Recortar si es más largo
7. **Audio track 3:** efectos de sonido
   - Leer la lista del sfx_engine
   - Insertar cada SFX en el segundo indicado
   - Volumen 0.15
8. **Mezclar** los 3 tracks de audio con CompositeAudioClip
9. **Renderizar subtítulos:**
   - Para cada bloque de 3 palabras:
     - Crear TextClip con Montserrat Bold tamaño 55
     - Color blanco, borde negro grueso (stroke)
     - Posición: centrado horizontal, 45% desde arriba
     - La palabra que se está diciendo en ese momento va en dorado (#FFD700)
   - Usar CompositeVideoClip para superponer textos sobre el video
10. **Agregar transiciones suaves** entre imágenes:
    - Crossfade de 0.3 segundos entre cada imagen
11. **Exportar** como .mp4:
    - codec: libx264, audio_codec: aac
    - fps: 30
    - preset: "medium" (balance velocidad/calidad)
    - bitrate: "4M" (buena calidad para Shorts)
12. **Verificar** archivo final: duración < 60s, resolución 1080x1920

**Nota sobre rendimiento:** Un Short de 55 seg tarda ~3-8 minutos en renderizar dependiendo del hardware. Generar con 30 min de anticipación al horario de publicación.

### modules/youtube_uploader.py

Sube el video como YouTube Short.

```python
"""
Usa google-api-python-client con OAuth 2.0.
El video se detecta como Short automáticamente si:
- Es vertical (9:16)
- Dura menos de 60 segundos
El #Shorts en el título ayuda pero no es estrictamente necesario.
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET = "credentials/youtube_client_secret.json"
TOKEN_PICKLE = "credentials/youtube_token.pickle"

def obtener_credenciales():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, "wb") as f:
            pickle.dump(creds, f)
    return creds

def subir_short(video_path, titulo, descripcion, tags, categoria_id="22", privacidad="public"):
    creds = obtener_credenciales()
    youtube = build("youtube", "v3", credentials=creds)
    
    body = {
        "snippet": {
            "title": titulo,
            "description": descripcion,
            "tags": tags,
            "categoryId": categoria_id,
        },
        "status": {
            "privacyStatus": privacidad,
            "selfDeclaredMadeForKids": False,
        },
    }
    
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response["id"]
```

---

## main.py (Orquestador)

```python
import asyncio
import yaml
import logging
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from modules.script_queue import obtener_siguiente_guion, marcar_completado, marcar_fallido, obtener_estado
from modules.tts_engine import generar_audio
from modules.image_fetcher import descargar_imagenes
from modules.subtitle_generator import generar_subtitulos
from modules.sfx_engine import generar_sfx
from modules.hashtag_optimizer import generar_hashtags
from modules.video_assembler import ensamblar_video
from modules.youtube_uploader import subir_short

load_dotenv()
logging.basicConfig(
    filename="logs/velo_oculto.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# También mostrar en consola
logging.getLogger().addHandler(logging.StreamHandler())

async def generar_y_subir():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Estado de la cola
    estado = obtener_estado()
    logging.info(f"Cola: {estado['pendientes']} pendientes, {estado['usados']} usados de {estado['total']}")
    if estado["pendientes"] <= 10:
        logging.warning(f"⚠️ ¡Solo quedan {estado['pendientes']} guiones! Agrega más a guionesVeloOculto.json")
    
    # 1. Siguiente guión
    guion = obtener_siguiente_guion()
    if not guion:
        logging.critical("❌ No quedan guiones. Agrega más al JSON.")
        return
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info(f"▶ Guión #{guion['id']}: {guion['titulo']}")
    
    try:
        # 2. Audio
        audio_path = f"output/audio/{ts}.mp3"
        audio_path, vtt_path = await generar_audio(
            guion["texto_narrado"], audio_path,
            config["tts"]["voz"], config["tts"]["velocidad"]
        )
        logging.info(f"  Audio: {audio_path}")
        
        # 3. Imágenes
        num_imgs = config["video"]["duracion_max"] // config["imagenes"]["duracion_por_imagen"] + 1
        imagenes = descargar_imagenes(
            guion["keywords_imagenes"],
            num_imgs,
            config["imagenes"].get("fallback_keywords", [])
        )
        logging.info(f"  Imágenes: {len(imagenes)}")
        
        # 4. Subtítulos
        subtitulos = generar_subtitulos(vtt_path, config["subtitulos"]["palabras_por_bloque"])
        
        # 5. Efectos de sonido
        sfx_lista = generar_sfx(guion["texto_narrado"], audio_path, config["sfx"])
        logging.info(f"  SFX: {len(sfx_lista)} efectos")
        
        # 6. Hashtags optimizados
        hashtags = generar_hashtags(guion["tags"])
        
        # 7. Ensamblar video
        video_path = f"output/videos/{ts}.mp4"
        musica_dir = config["musica"]["carpeta"]
        musica_files = [f for f in os.listdir(musica_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]
        musica_path = os.path.join(musica_dir, random.choice(musica_files)) if musica_files else None
        
        video_path = ensamblar_video(
            audio_path=audio_path,
            imagenes=imagenes,
            subtitulos=subtitulos,
            sfx_lista=sfx_lista,
            musica_path=musica_path,
            config=config,
            output_path=video_path
        )
        logging.info(f"  Video: {video_path}")
        
        # 8. Subir a YouTube
        titulo_yt = guion["titulo"]
        if not titulo_yt.endswith("#Shorts"):
            titulo_yt += config["youtube"]["sufijo_titulo"]
        
        desc_completa = guion["descripcion_youtube"] + "\n\n" + hashtags
        all_tags = config["youtube"]["tags_base"] + guion["tags"]
        
        yt_id = subir_short(
            video_path, titulo_yt, desc_completa, all_tags,
            config["youtube"]["categoria_id"],
            config["youtube"]["privacidad"]
        )
        logging.info(f"  ✅ YouTube Short: https://youtube.com/shorts/{yt_id}")
        
        # 9. Marcar completado
        marcar_completado(guion["id"])
        
    except Exception as e:
        logging.error(f"  ❌ Error: {e}", exc_info=True)
        marcar_fallido(guion["id"])

if __name__ == "__main__":
    asyncio.run(generar_y_subir())
```

---

## scheduler.py

```python
import schedule
import time
import asyncio
import logging
from main import generar_y_subir

logging.basicConfig(
    filename="logs/velo_oculto.log", level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())

def run():
    asyncio.run(generar_y_subir())

schedule.every().day.at("08:00").do(run)
schedule.every().day.at("12:00").do(run)
schedule.every().day.at("17:00").do(run)

logging.info("🔮 Velo Oculto Scheduler iniciado")
logging.info("   Horarios: 08:00 | 12:00 | 17:00 (UTC-5)")

while True:
    schedule.run_pending()
    time.sleep(30)
```

---

## requirements.txt

```
edge-tts>=6.1.0
moviepy>=1.0.3
Pillow>=10.0.0
pyyaml>=6.0
requests>=2.31.0
python-dotenv>=1.0.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
schedule>=1.2.0
numpy>=1.24.0
```

---

## setup.sh

```bash
#!/bin/bash
set -e
echo "🔮 Configurando Velo Oculto..."
sudo apt update && sudo apt install -y ffmpeg
pip install -r requirements.txt
mkdir -p data output/videos output/audio assets/fonts assets/music assets/sfx logs credentials
# Descargar fuente Montserrat Bold
if [ ! -f "assets/fonts/Montserrat-Bold.ttf" ]; then
    echo "Descargando Montserrat Bold..."
    wget -q -O /tmp/montserrat.zip "https://fonts.google.com/download?family=Montserrat" 2>/dev/null || \
    echo "⚠️ No se pudo descargar Montserrat. Descárgala manualmente de https://fonts.google.com/specimen/Montserrat"
    if [ -f /tmp/montserrat.zip ]; then
        unzip -q -o /tmp/montserrat.zip -d /tmp/montserrat/
        cp /tmp/montserrat/static/Montserrat-Bold.ttf assets/fonts/
        rm -rf /tmp/montserrat /tmp/montserrat.zip
    fi
fi
echo ""
echo "✅ Instalación completa. Próximos pasos:"
echo "1. Pon tu API key de Pexels en .env"
echo "2. Pon tu youtube_client_secret.json en credentials/"
echo "3. Pon tus guiones en data/guionesVeloOculto.json"
echo "4. Descarga música de fondo en assets/music/ (pixabay.com/music → busca 'dark ambient')"
echo "5. Descarga efectos de sonido en assets/sfx/ (pixabay.com/sound-effects)"
echo "6. Prueba: python main.py"
echo "7. Activa: python scheduler.py"
```

---

## GitHub — Repositorio automático

### Configuración inicial (una sola vez):

```bash
# En la raíz del proyecto:
git init
git add .
git commit -m "🔮 Velo Oculto - sistema de automatización"

# Crear repo en GitHub (necesitas GitHub CLI o hacerlo manual):
# Opción A: GitHub CLI
gh repo create velo-oculto --private --source=. --push

# Opción B: Manual
# 1. Ve a github.com → New repository → nombre: velo-oculto → Private
# 2. Copia la URL del repo
git remote add origin https://github.com/TU_USUARIO/velo-oculto.git
git push -u origin main
```

### Auto-push después de cada video exitoso:

Agregar al final de main.py, después de `marcar_completado()`:

```python
# Auto-push a GitHub (solo historial, no videos)
import subprocess
try:
    subprocess.run(["git", "add", "data/historial.json", "logs/"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"📹 Video #{guion['id']}: {guion['titulo'][:40]}"], 
                   check=True, capture_output=True)
    subprocess.run(["git", "push"], check=True, capture_output=True)
    logging.info("  📤 Push a GitHub completado")
except Exception as e:
    logging.warning(f"  ⚠️ Git push falló: {e}")  # No es crítico
```

NOTA: Solo hace push del historial y logs, NO de los videos (son muy pesados y están en .gitignore).

---

## Dónde correr el sistema 24/7 — Recomendación

### Opción 1: Oracle Cloud Free Tier (RECOMENDADA — GRATIS PARA SIEMPRE)

Oracle ofrece una VPS gratis permanente con estas specs:
- **1 CPU, 1 GB RAM** (suficiente para generar Shorts)
- **Ubuntu 22.04**
- **Gratis para siempre** (no es trial, es "Always Free")

Cómo configurar:
1. Ve a https://cloud.oracle.com → crear cuenta (pide tarjeta pero NO cobra)
2. Compute → Create Instance → Shape: VM.Standard.E2.1.Micro (free)
3. OS: Ubuntu 22.04 → Create
4. Conéctate por SSH: `ssh ubuntu@IP_DE_TU_SERVIDOR`
5. Clona tu repo: `git clone https://github.com/TU_USUARIO/velo-oculto.git`
6. Ejecuta `setup.sh`
7. Configura .env y credentials
8. Configura crontab:
   ```bash
   crontab -e
   # Agregar (ajustar ruta):
   0 8 * * * cd /home/ubuntu/velo-oculto && /usr/bin/python3 main.py >> logs/cron.log 2>&1
   0 12 * * * cd /home/ubuntu/velo-oculto && /usr/bin/python3 main.py >> logs/cron.log 2>&1
   0 17 * * * cd /home/ubuntu/velo-oculto && /usr/bin/python3 main.py >> logs/cron.log 2>&1
   ```

**NOTA:** Con 1 GB de RAM el renderizado será lento (~10-15 min por video) pero funciona. Si quieres más rápido, Oracle también tiene instancias ARM con 4 CPU y 24 GB RAM gratis (VM.Standard.A1.Flex).

### Opción 2: Tu computadora personal
- Ventaja: más rápido, ya tienes todo instalado
- Desventaja: debe estar encendida 24/7

### Opción 3: Raspberry Pi
- Funciona pero es MUY lento para video rendering (~20-30 min por Short)

---

## 📈 ESTRATEGIAS DE CRECIMIENTO PARA YOUTUBE

Estas estrategias están incorporadas en el sistema o se aplican manualmente:

### 1. Los primeros 3 segundos son TODO
- El gancho del guión DEBE ser una pregunta impactante o dato que obligue a quedarse
- El SFX de apertura (deep_drone o reverse_cymbal) ayuda a captar atención auditiva
- Buenos ejemplos de gancho: "¿Sabías que...?", "Esto que voy a contarte fue censurado en...", "Hay un lugar donde nadie puede entrar..."

### 2. Títulos clickbait (pero no engañosos)
- Patrones que funcionan:
  - "Lo que [ENTIDAD] NO quiere que sepas sobre..."
  - "El secreto más oscuro de [TEMA]"
  - "[NÚMERO] cosas que te ocultan sobre..."
  - "¿Por qué nadie habla de [TEMA]?"
  - "Esto fue censurado en [AÑO]..."
- NUNCA prometas algo que el video no cumple (YouTube penaliza clickbait engañoso)

### 3. Subtítulos SIEMPRE
- El 85% de videos en redes se ven sin sonido
- Subtítulos grandes (55px), centrados, 3 palabras a la vez
- Palabra actual en dorado → guía al ojo → retiene al viewer

### 4. Consistencia = crecimiento
- 3 videos diarios es excelente
- Publicar SIEMPRE a la misma hora crea hábito en la audiencia
- YouTube premia la consistencia en el algoritmo

### 5. Hashtags optimizados (ya automatizado)
- Máximo 12 hashtags por video
- Mezcla de hashtags grandes (#shorts #misterios) y de nicho (#velooculto #teorias)
- El sistema ya genera esto automáticamente con hashtag_optimizer.py

### 6. Engagement hooks al final
- Todos los guiones deben terminar con CTA: "Sígueme para más secretos"
- Variaciones: "Dale like si quieres la parte 2", "Comenta cuál misterio quieres que investigue"

### 7. Series y partes
- Crear guiones que sean "Parte 1", "Parte 2", etc.
- Ejemplo: "Los experimentos del MK Ultra - Parte 1" → incentiva a seguir y ver más
- Agregar al JSON guiones con títulos secuenciales

### 8. Trending topics
- Cada mes, buscar qué temas de misterio/conspiración están trending
- Generar 5-10 guiones sobre esos temas y agregarlos al JSON
- YouTube prioriza contenido sobre temas en tendencia

### 9. Thumbnails (para la sección Shorts del canal)
- Aunque Shorts no muestran thumbnail clásico, el primer frame importa
- El primer frame del video debe ser visualmente impactante
- Considerar agregar texto grande en el primer frame

### 10. Monetización — Ruta realista
- **Requisitos:** 1,000 suscriptores + 10 millones de vistas en Shorts (últimos 90 días)
- **Ingresos Shorts:** $0.01-0.06 por cada 1,000 vistas (es bajo comparado con videos largos)
- **Estrategia fase 2:** Una vez tengas audiencia, crear videos largos (8-15 min) sobre los mismos temas → esos pagan 10-50x más por vista con ads
- **Afiliados:** Enlazar a libros sobre conspiraciones en Amazon (comisión por venta)
- **Merch:** Una vez tengas 5K+ subs, vender merch de "Velo Oculto"

---

## Orden de implementación para Claude Code

**IMPORTANTE:** Construir TODO en este orden, sin pausas, sin preguntas.

1. `mkdir -p` toda la estructura de carpetas
2. Crear `.env`, `.gitignore`, `config.yaml`, `requirements.txt`, `setup.sh`
3. Crear `modules/__init__.py`
4. Crear `modules/script_queue.py` (copiar código de arriba, ya está completo)
5. Crear `modules/tts_engine.py` (copiar código de arriba)
6. Crear `modules/image_fetcher.py` (implementar completo)
7. Crear `modules/subtitle_generator.py` (implementar completo)
8. Crear `modules/sfx_engine.py` (implementar completo)
9. Crear `modules/hashtag_optimizer.py` (copiar código de arriba, ya está completo)
10. Crear `modules/video_assembler.py` (implementar completo — el más complejo)
11. Crear `modules/youtube_uploader.py` (copiar código de arriba, ya está completo)
12. Crear `main.py` (copiar código de arriba, agregar git push)
13. Crear `scheduler.py` (copiar código de arriba)
14. Crear `README.md` con instrucciones de uso
15. Crear `assets/sfx/README.md` con links de descarga de SFX
16. Crear `assets/music/README.md` con links de descarga de música
17. Inicializar git repo: `git init && git add . && git commit -m "🔮 Init"`

**NO instalar dependencias ni ejecutar nada.** El usuario hará eso después.
