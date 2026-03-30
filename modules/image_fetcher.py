"""
Descarga imágenes verticales de Pexels API.
Redimensiona a 1080x1920, aplica overlay oscuro.
Cachea por keyword para no repetir llamadas.
"""
import os
import hashlib
import requests
import logging
from PIL import Image, ImageDraw
from io import BytesIO

PEXELS_API = "https://api.pexels.com/v1/search"
CACHE_DIR = "output/cache_images"


def _cache_path(keyword, index):
    key = hashlib.md5(f"{keyword}_{index}".encode()).hexdigest()[:10]
    return os.path.join(CACHE_DIR, f"{key}.jpg")


def _procesar_imagen(img_bytes, filtro_oscuro=0.35):
    """Redimensiona a 1080x1920 (crop center) y aplica overlay oscuro."""
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    target_w, target_h = 1080, 1920
    src_ratio = img.width / img.height
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        # Imagen más ancha → recortar lados
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        # Imagen más alta → recortar arriba/abajo
        new_w = target_w
        new_h = int(new_w / src_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    # Overlay oscuro
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * filtro_oscuro)))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    return img


def _buscar_pexels(keyword, api_key, cantidad=10):
    """Busca imágenes en Pexels y retorna lista de URLs."""
    headers = {"Authorization": api_key}
    params = {
        "query": keyword,
        "orientation": "portrait",
        "per_page": cantidad,
        "size": "large",
    }
    try:
        resp = requests.get(PEXELS_API, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        return [p["src"]["large"] for p in photos]
    except Exception as e:
        logging.warning(f"Pexels error para '{keyword}': {e}")
        return []


def descargar_imagenes(keywords, cantidad_necesaria, fallback_keywords=None, filtro_oscuro=0.35):
    """
    Descarga y procesa imágenes para el video.
    Retorna lista de paths a imágenes procesadas en output/cache_images/.
    """
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        raise ValueError("PEXELS_API_KEY no está configurada en .env")

    os.makedirs(CACHE_DIR, exist_ok=True)
    imagenes = []
    todos_keywords = list(keywords) + (fallback_keywords or [])

    for keyword in todos_keywords:
        if len(imagenes) >= cantidad_necesaria:
            break

        urls = _buscar_pexels(keyword, api_key, cantidad=10)
        for i, url in enumerate(urls):
            if len(imagenes) >= cantidad_necesaria:
                break

            cache = _cache_path(keyword, i)
            if os.path.exists(cache):
                imagenes.append(cache)
                continue

            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                img = _procesar_imagen(resp.content, filtro_oscuro)
                img.save(cache, "JPEG", quality=92)
                imagenes.append(cache)
                logging.info(f"  Imagen descargada: {keyword}[{i}] → {cache}")
            except Exception as e:
                logging.warning(f"  Error descargando {url}: {e}")

    if not imagenes:
        raise RuntimeError("No se pudieron descargar imágenes. Verifica PEXELS_API_KEY.")

    # Si hay menos que las necesarias, repetir imágenes cíclicamente
    while len(imagenes) < cantidad_necesaria:
        imagenes += imagenes
    return imagenes[:cantidad_necesaria]
