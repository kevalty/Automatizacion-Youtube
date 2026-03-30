"""
Módulo central. Ensambla audio, imágenes, subtítulos y SFX en un Short de máx 58 segundos.
Usa moviepy para el ensamblado.
"""
import os
import logging
import numpy as np
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip,
    concatenate_videoclips,
)
from moviepy.audio.AudioClip import AudioArrayClip
from PIL import Image, ImageDraw, ImageFont


def _crear_clip_imagen(path, duracion, zoom_factor=1.12, zoom_in=True):
    """Crea un ImageClip con efecto Ken Burns."""
    clip = ImageClip(path, duration=duracion)
    target_w, target_h = 1080, 1920
    if clip.w != target_w or clip.h != target_h:
        clip = clip.resize((target_w, target_h))

    def make_frame(t):
        progress = t / duracion if duracion > 0 else 0
        if zoom_in:
            scale = 1.0 + (zoom_factor - 1.0) * progress
        else:
            scale = zoom_factor - (zoom_factor - 1.0) * progress
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        new_w = int(target_w * scale)
        new_h = int(target_h * scale)
        img_scaled = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img_cropped = img_scaled.crop((left, top, left + target_w, top + target_h))
        return np.array(img_cropped)

    return clip.fl(lambda gf, t: make_frame(t))


def _render_subtitulo_frame(texto, config_sub, target_w=1080, target_h=1920):
    """Renderiza el frame de subtítulo con PIL. Devuelve array numpy RGBA."""
    img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fuente_path = config_sub.get("fuente", "assets/fonts/Montserrat-Bold.ttf")
    tamanio = config_sub.get("tamaño", 55)
    color_texto = config_sub.get("color", "#FFFFFF")
    color_borde = config_sub.get("color_borde", "#000000")
    grosor_borde = config_sub.get("grosor_borde", 4)
    posicion_y_ratio = config_sub.get("posicion_y", 0.45)

    try:
        font = ImageFont.truetype(fuente_path, tamanio)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (target_w - text_w) // 2
    y = int(target_h * posicion_y_ratio) - text_h // 2

    borde_hex = color_borde.lstrip("#")
    borde_color = tuple(int(borde_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    for dx in range(-grosor_borde, grosor_borde + 1):
        for dy in range(-grosor_borde, grosor_borde + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto, font=font, fill=borde_color)

    texto_hex = color_texto.lstrip("#")
    texto_color = tuple(int(texto_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    draw.text((x, y), texto, font=font, fill=texto_color)

    return np.array(img)


def _crear_clips_subtitulos(subtitulos, config_sub, duracion_total):
    """Crea clips de subtítulos usando PIL."""
    clips = []
    for bloque in subtitulos:
        inicio = bloque["inicio"]
        fin = min(bloque["fin"] + 0.1, duracion_total)
        duracion = fin - inicio
        if duracion <= 0:
            continue
        frame = _render_subtitulo_frame(bloque["texto"], config_sub)
        clip = ImageClip(frame, ismask=False, duration=duracion).set_start(inicio)
        clips.append(clip)
    return clips


def _loop_audio(audio_clip, duracion_objetivo):
    """Hace loop de un clip de audio hasta alcanzar la duración objetivo."""
    from moviepy.editor import concatenate_audioclips
    if audio_clip.duration >= duracion_objetivo:
        return audio_clip.subclip(0, duracion_objetivo)
    repeticiones = int(duracion_objetivo / audio_clip.duration) + 1
    return concatenate_audioclips([audio_clip] * repeticiones).subclip(0, duracion_objetivo)


def _crear_sfx_track(sfx_lista, duracion_total, sample_rate=44100):
    """Crea track de audio con los SFX insertados en sus tiempos."""
    if not sfx_lista:
        return None
    samples = int(duracion_total * sample_rate)
    audio_array = np.zeros((samples, 2), dtype=np.float32)

    for sfx in sfx_lista:
        try:
            sfx_clip = AudioFileClip(sfx["archivo"])
            sfx_samples = sfx_clip.to_soundarray(fps=sample_rate)
            volumen = sfx.get("volumen", 0.15)
            sfx_samples = sfx_samples * volumen
            start = int(sfx["segundo"] * sample_rate)
            end = min(start + len(sfx_samples), samples)
            length = end - start
            if sfx_samples.ndim == 1:
                sfx_samples = np.column_stack([sfx_samples, sfx_samples])
            if length > 0 and start < samples:
                audio_array[start:end] += sfx_samples[:length]
            sfx_clip.close()
        except Exception as e:
            logging.warning(f"  SFX error ({sfx['archivo']}): {e}")

    max_val = np.abs(audio_array).max()
    if max_val > 1.0:
        audio_array = audio_array / max_val
    return AudioArrayClip(audio_array, fps=sample_rate)


def ensamblar_video(audio_path, imagenes, subtitulos, sfx_lista, musica_path, config, output_path):
    """Ensambla el video final completo. Retorna el path del video exportado."""
    cfg_video = config["video"]
    cfg_sub = config["subtitulos"]
    cfg_musica = config["musica"]
    cfg_img = config["imagenes"]

    fps = cfg_video.get("fps", 30)
    duracion_max = cfg_video.get("duracion_max", 58)

    narr_clip = AudioFileClip(audio_path)
    duracion_audio = narr_clip.duration
    logging.info(f"  Duración audio: {duracion_audio:.1f}s")
    if duracion_audio > duracion_max:
        logging.warning(f"  Audio ({duracion_audio:.1f}s) supera {duracion_max}s")

    duracion_video = min(duracion_audio, duracion_max)
    duracion_img = cfg_img.get("duracion_por_imagen", 4)
    zoom_factor = cfg_img.get("zoom_factor", 1.12)

    clips_img = []
    for i, img_path in enumerate(imagenes):
        zoom_in = (i % 2 == 0)
        try:
            clip = _crear_clip_imagen(img_path, duracion_img, zoom_factor, zoom_in)
            clips_img.append(clip)
        except Exception as e:
            logging.warning(f"  Error en imagen {img_path}: {e}")

    if not clips_img:
        raise RuntimeError("No hay clips de imagen para ensamblar.")

    video_base = concatenate_videoclips(clips_img, method="compose")
    video_base = video_base.subclip(0, min(duracion_video, video_base.duration))
    video_base = video_base.set_fps(fps)

    narr_audio = narr_clip.subclip(0, min(duracion_video, narr_clip.duration)).volumex(1.0)
    audio_tracks = [narr_audio]

    if musica_path and os.path.exists(musica_path):
        try:
            musica_clip = AudioFileClip(musica_path)
            musica_clip = _loop_audio(musica_clip, duracion_video)
            musica_clip = musica_clip.volumex(cfg_musica.get("volumen", 0.06))
            musica_clip = musica_clip.audio_fadein(cfg_musica.get("fade_in", 1.5))
            musica_clip = musica_clip.audio_fadeout(cfg_musica.get("fade_out", 2.5))
            audio_tracks.append(musica_clip)
            logging.info(f"  Música: {os.path.basename(musica_path)}")
        except Exception as e:
            logging.warning(f"  Música error: {e}")

    sfx_track = _crear_sfx_track(sfx_lista, duracion_video)
    if sfx_track:
        audio_tracks.append(sfx_track)

    audio_final = CompositeAudioClip(audio_tracks) if len(audio_tracks) > 1 else audio_tracks[0]
    video_con_audio = video_base.set_audio(audio_final)

    clips_sub = _crear_clips_subtitulos(subtitulos, cfg_sub, duracion_video)
    if clips_sub:
        video_final = CompositeVideoClip([video_con_audio] + clips_sub, size=(1080, 1920))
        video_final = video_final.set_audio(audio_final)
    else:
        video_final = video_con_audio

    video_final = video_final.set_duration(duracion_video)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logging.info(f"  Exportando → {output_path}")
    video_final.write_videofile(
        output_path,
        fps=fps,
        codec=cfg_video.get("codec_video", "libx264"),
        audio_codec=cfg_video.get("codec_audio", "aac"),
        preset="medium",
        bitrate="4M",
        threads=4,
        logger=None,
    )

    narr_clip.close()
    video_final.close()

    from moviepy.editor import VideoFileClip
    with VideoFileClip(output_path) as check:
        logging.info(f"  Video final: {check.duration:.1f}s {check.size}")
        if check.duration > 60:
            logging.warning(f"  Video supera 60s ({check.duration:.1f}s)")

    return output_path
