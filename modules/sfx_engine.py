"""
Genera lista de efectos de sonido para insertar en el video.
Analiza pausas "..." en el texto y coloca SFX estratégicamente.
"""
import os
import re
import random
import logging


SFX_APERTURA = ["deep_drone.mp3", "reverse_cymbal.mp3"]
SFX_PAUSA = ["whisper.mp3", "static.mp3", "heartbeat.mp3"]
SFX_CIERRE = ["deep_drone.mp3"]


def _tiempos_pausas(texto_narrado, duracion_audio, palabras_por_segundo=2.5):
    """
    Estima el segundo aproximado de cada "..." en el texto.
    Retorna lista de segundos donde hay pausa.
    """
    pausas = []
    palabras = texto_narrado.split()
    total_palabras = len(palabras)
    if total_palabras == 0:
        return []

    segundos_por_palabra = duracion_audio / total_palabras if duracion_audio else 1 / palabras_por_segundo

    pos = 0
    for i, palabra in enumerate(palabras):
        if "..." in palabra:
            segundo_estimado = i * segundos_por_palabra
            pausas.append(round(segundo_estimado, 1))

    return pausas


def _sfx_disponibles(carpeta, nombres):
    """Retorna los SFX que existen físicamente en la carpeta."""
    disponibles = []
    for nombre in nombres:
        path = os.path.join(carpeta, nombre)
        if os.path.exists(path):
            disponibles.append(path)
    return disponibles


def generar_sfx(texto_narrado, audio_path, config_sfx):
    """
    Genera lista de efectos de sonido con sus tiempos de inserción.
    Retorna: [{"archivo": "path/sfx.mp3", "segundo": 1.5, "volumen": 0.15}, ...]
    """
    if not config_sfx.get("activo", True):
        return []

    carpeta = config_sfx.get("carpeta", "assets/sfx/")
    volumen = config_sfx.get("volumen", 0.15)
    sfx_lista = []

    # Obtener duración del audio
    duracion = 55.0  # default
    try:
        from moviepy.editor import AudioFileClip
        with AudioFileClip(audio_path) as clip:
            duracion = clip.duration
    except Exception:
        pass

    # 1. SFX de apertura (segundo 0-2)
    apertura = _sfx_disponibles(carpeta, SFX_APERTURA)
    if apertura:
        sfx_lista.append({
            "archivo": random.choice(apertura),
            "segundo": 0.5,
            "volumen": volumen * 0.8,
        })

    # 2. SFX en pausas "..." (probabilidad 40%)
    pausas = _tiempos_pausas(texto_narrado, duracion)
    sfx_pausa = _sfx_disponibles(carpeta, SFX_PAUSA)
    if sfx_pausa:
        for segundo in pausas:
            if random.random() < 0.40 and segundo > 3 and segundo < duracion - 4:
                sfx_lista.append({
                    "archivo": random.choice(sfx_pausa),
                    "segundo": round(segundo, 1),
                    "volumen": volumen,
                })

    # 3. SFX de cierre (últimos 3 seg)
    cierre = _sfx_disponibles(carpeta, SFX_CIERRE)
    if cierre:
        sfx_lista.append({
            "archivo": random.choice(cierre),
            "segundo": max(0, round(duracion - 3, 1)),
            "volumen": volumen * 0.6,
        })

    logging.info(f"  SFX generados: {len(sfx_lista)} efectos")
    return sfx_lista
