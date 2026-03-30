"""
Lee el .vtt generado por edge-tts y agrupa palabras en bloques de N palabras.
Retorna lista de bloques con texto, inicio y fin en segundos.
"""
import re


def _vtt_time_to_seconds(t):
    """Convierte '00:00:01.500' a 1.5 (float)."""
    parts = t.strip().split(":")
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s


def parsear_vtt(vtt_path):
    """
    Parsea el VTT de edge-tts.
    Retorna lista de: [{"texto": "palabra", "inicio": 1.2, "fin": 1.8}, ...]
    """
    palabras = []
    try:
        with open(vtt_path, encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        return []

    # Formato edge-tts VTT:
    # 00:00:00.500 --> 00:00:01.200
    # palabra
    bloques = re.split(r"\n\n+", contenido.strip())
    for bloque in bloques:
        lineas = [l.strip() for l in bloque.strip().splitlines() if l.strip()]
        for i, linea in enumerate(lineas):
            if "-->" in linea:
                tiempos = linea.split("-->")
                if len(tiempos) == 2:
                    inicio = _vtt_time_to_seconds(tiempos[0])
                    fin = _vtt_time_to_seconds(tiempos[1])
                    # La siguiente línea es el texto
                    if i + 1 < len(lineas):
                        texto = lineas[i + 1]
                        if texto and texto != "WEBVTT":
                            palabras.append({"texto": texto, "inicio": inicio, "fin": fin})

    return palabras


def generar_subtitulos(vtt_path, palabras_por_bloque=3):
    """
    Agrupa las palabras del VTT en bloques de N palabras.
    Retorna: [{"texto": "tres palabras aquí", "inicio": 2.5, "fin": 3.8, "palabras": [...]}, ...]
    """
    palabras = parsear_vtt(vtt_path)
    if not palabras:
        return []

    bloques = []
    for i in range(0, len(palabras), palabras_por_bloque):
        grupo = palabras[i:i + palabras_por_bloque]
        bloque = {
            "texto": " ".join(p["texto"] for p in grupo),
            "inicio": grupo[0]["inicio"],
            "fin": grupo[-1]["fin"],
            "palabras": grupo,
        }
        bloques.append(bloque)

    return bloques
