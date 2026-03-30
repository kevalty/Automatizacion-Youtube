# Efectos de Sonido (SFX)

Coloca aquí los siguientes archivos .mp3 (recortados a 1-3 segundos máximo):

| Archivo | Descripción | Uso en el video |
|---|---|---|
| `whisper.mp3` | Susurro misterioso | Pausas "..." del guión |
| `static.mp3` | Estática de TV/radio | Pausas "..." del guión |
| `heartbeat.mp3` | Latido de corazón | Pausas "..." del guión |
| `deep_drone.mp3` | Drone grave/ominoso | Apertura y cierre |
| `reverse_cymbal.mp3` | Platillo reversa | Apertura (transición) |

## Dónde descargarlos gratis

### Pixabay Sound Effects (sin registro)
Buscar en: https://pixabay.com/sound-effects/
- `whisper`: buscar "whisper mystery" o "dark whisper"
- `static`: buscar "radio static" o "tv noise"
- `heartbeat`: buscar "heartbeat" o "heart beat slow"
- `deep_drone`: buscar "dark drone" o "horror ambience"
- `reverse_cymbal`: buscar "reverse cymbal" o "impact reverse"

### Freesound.org (requiere cuenta gratuita)
Buscar en: https://freesound.org/
- Términos: "dark ambient", "suspense hit", "horror sting"

## Recortar a 1-3 segundos con ffmpeg

```bash
ffmpeg -i original.mp3 -ss 0 -t 2 -q:a 0 whisper.mp3
```

## Nota
Sin SFX el sistema funciona igual — simplemente omite ese track.
El campo `sfx.activo: false` en config.yaml desactiva los SFX por completo.
