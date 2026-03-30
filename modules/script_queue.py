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
