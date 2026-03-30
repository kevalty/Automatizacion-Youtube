# 🔮 Velo Oculto — Automatización YouTube Shorts

Sistema de automatización para generar y publicar YouTube Shorts del canal **Velo Oculto** (teorías conspirativas). Publica 3 videos diarios (8am, 12pm, 5pm hora Ecuador).

## Requisitos

- Python 3.9+
- ffmpeg instalado en el sistema
- API key de Pexels (gratis)
- Credenciales OAuth de YouTube (Google Cloud Console)

## Instalación rápida

```bash
# Linux/Mac
bash setup.sh

# Windows (manual)
pip install -r requirements.txt
```

## Configuración inicial

### 1. API key de Pexels
Regístrate gratis en https://www.pexels.com/api/ y copia tu key en `.env`:
```
PEXELS_API_KEY=tu_key_aqui
```

### 2. Credenciales de YouTube
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto → habilita "YouTube Data API v3"
3. Crea credenciales → OAuth 2.0 → Desktop App
4. Descarga el JSON y guárdalo como `credentials/youtube_client_secret.json`

En la primera ejecución se abrirá el navegador para autorizar. El token se guarda en `credentials/youtube_token.pickle` para futuras ejecuciones.

### 3. Guiones
El archivo `data/guionesVeloOculto.json` contiene los guiones pre-escritos. Ver el plan del proyecto para el formato exacto.

### 4. Fuente Montserrat Bold
Descarga desde https://fonts.google.com/specimen/Montserrat y coloca `Montserrat-Bold.ttf` en `assets/fonts/`.

### 5. Assets opcionales (pero recomendados)
- **Música**: Ver `assets/music/README.md`
- **SFX**: Ver `assets/sfx/README.md`

## Uso

### Generar y subir 1 video ahora
```bash
python main.py
```

### Activar publicación automática 3x/día
```bash
python scheduler.py
```

El scheduler corre indefinidamente. Usa `screen` o `tmux` en servidor para mantenerlo activo:
```bash
screen -S velooculto
python scheduler.py
# Ctrl+A, D para detachar
```

### Ver estado de la cola
```python
from modules.script_queue import obtener_estado, regenerar_fallidos
print(obtener_estado())
regenerar_fallidos()  # Reintenta los que fallaron
```

## Estructura de archivos

```
├── main.py              → Genera y sube 1 video
├── scheduler.py         → Automatización 3x/día
├── config.yaml          → Toda la configuración
├── .env                 → API keys (no en git)
├── modules/             → Módulos del sistema
├── data/
│   ├── guionesVeloOculto.json   → Tus guiones
│   └── historial.json           → Registro de usados (auto)
├── assets/
│   ├── fonts/           → Montserrat-Bold.ttf
│   ├── music/           → Tracks de fondo
│   └── sfx/             → Efectos de sonido
├── output/
│   ├── videos/          → Videos generados
│   └── audio/           → Narración generada
├── logs/                → Logs del sistema
└── credentials/         → OAuth YouTube (no en git)
```

## Flujo de generación

1. Lee el siguiente guión no usado de `data/guionesVeloOculto.json`
2. Genera narración con edge-tts (voz es-MX-JorgeNeural)
3. Descarga imágenes verticales de Pexels según keywords del guión
4. Parsea timestamps VTT → bloques de 3 palabras para subtítulos
5. Calcula puntos de inserción de SFX (inicio, pausas "...", cierre)
6. Ensambla: imágenes con Ken Burns + narración + música + SFX + subtítulos
7. Sube como YouTube Short (9:16, < 60s = detectado automáticamente como Short)
8. Marca guión como completado en historial

## Problemas comunes

**"PEXELS_API_KEY no está configurada"** → Verifica tu `.env`

**"No se puede abrir la fuente"** → Descarga `Montserrat-Bold.ttf` en `assets/fonts/`

**El video tarda mucho** → Normal. Un Short de ~55s tarda 3-15 min según hardware.

**Error de YouTube OAuth** → Borra `credentials/youtube_token.pickle` y vuelve a ejecutar.

**"No quedan guiones"** → Agrega más entradas a `data/guionesVeloOculto.json`.
