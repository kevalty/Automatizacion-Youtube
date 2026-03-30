"""
Orquestador principal. Genera y sube 1 video a YouTube.
Uso: python main.py
"""
import asyncio
import yaml
import logging
import os
import random
import subprocess
from datetime import datetime
from dotenv import load_dotenv

from modules.script_queue import (
    obtener_siguiente_guion, marcar_completado, marcar_fallido, obtener_estado
)
from modules.tts_engine import generar_audio
from modules.image_fetcher import descargar_imagenes
from modules.subtitle_generator import generar_subtitulos
from modules.sfx_engine import generar_sfx
from modules.hashtag_optimizer import generar_hashtags
from modules.video_assembler import ensamblar_video
from modules.youtube_uploader import subir_short

load_dotenv()

os.makedirs("logs", exist_ok=True)
os.makedirs("output/audio", exist_ok=True)
os.makedirs("output/videos", exist_ok=True)

logging.basicConfig(
    filename="logs/velo_oculto.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler())


async def generar_y_subir():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Estado de la cola
    estado = obtener_estado()
    logging.info(
        f"Cola: {estado['pendientes']} pendientes, "
        f"{estado['usados']} usados de {estado['total']}"
    )
    if estado["pendientes"] <= 10:
        logging.warning(
            f"⚠️ ¡Solo quedan {estado['pendientes']} guiones! "
            f"Agrega más a data/guionesVeloOculto.json"
        )

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
            guion["texto_narrado"],
            audio_path,
            config["tts"]["voz"],
            config["tts"]["velocidad"],
        )
        logging.info(f"  Audio: {audio_path}")

        # 3. Imágenes
        num_imgs = config["video"]["duracion_max"] // config["imagenes"]["duracion_por_imagen"] + 1
        imagenes = descargar_imagenes(
            guion["keywords_imagenes"],
            num_imgs,
            config["imagenes"].get("fallback_keywords", []),
            config["imagenes"].get("filtro_oscuro", 0.35),
        )
        logging.info(f"  Imágenes: {len(imagenes)}")

        # 4. Subtítulos
        subtitulos = generar_subtitulos(
            vtt_path,
            config["subtitulos"]["palabras_por_bloque"],
        )

        # 5. Efectos de sonido
        sfx_lista = generar_sfx(guion["texto_narrado"], audio_path, config["sfx"])
        logging.info(f"  SFX: {len(sfx_lista)} efectos")

        # 6. Hashtags optimizados
        hashtags = generar_hashtags(guion["tags"])

        # 7. Ensamblar video
        video_path = f"output/videos/{ts}.mp4"
        musica_dir = config["musica"]["carpeta"]
        musica_files = [
            f for f in os.listdir(musica_dir)
            if f.lower().endswith((".mp3", ".wav", ".ogg"))
        ] if os.path.isdir(musica_dir) else []
        musica_path = (
            os.path.join(musica_dir, random.choice(musica_files))
            if musica_files else None
        )

        video_path = ensamblar_video(
            audio_path=audio_path,
            imagenes=imagenes,
            subtitulos=subtitulos,
            sfx_lista=sfx_lista,
            musica_path=musica_path,
            config=config,
            output_path=video_path,
        )
        logging.info(f"  Video: {video_path}")

        # 8. Subir a YouTube
        titulo_yt = guion["titulo"]
        if not titulo_yt.endswith("#Shorts"):
            titulo_yt += config["youtube"]["sufijo_titulo"]

        desc_completa = guion["descripcion_youtube"] + "\n\n" + hashtags
        all_tags = config["youtube"]["tags_base"] + guion["tags"]

        yt_id = subir_short(
            video_path,
            titulo_yt,
            desc_completa,
            all_tags,
            config["youtube"]["categoria_id"],
            config["youtube"]["privacidad"],
        )
        logging.info(f"  ✅ YouTube Short: https://youtube.com/shorts/{yt_id}")

        # 9. Marcar completado
        marcar_completado(guion["id"])

        # 10. Auto-push a GitHub (solo historial y logs)
        try:
            subprocess.run(
                ["git", "add", "data/historial.json", "logs/"],
                check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m",
                 f"Video #{guion['id']}: {guion['titulo'][:40]}"],
                check=True, capture_output=True
            )
            subprocess.run(["git", "push"], check=True, capture_output=True)
            logging.info("  Commit y push a GitHub completado")
        except Exception as e:
            logging.warning(f"  Git push falló (no crítico): {e}")

    except Exception as e:
        logging.error(f"  ❌ Error: {e}", exc_info=True)
        marcar_fallido(guion["id"])


if __name__ == "__main__":
    asyncio.run(generar_y_subir())
