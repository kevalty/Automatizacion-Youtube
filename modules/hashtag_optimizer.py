"""
Genera hashtags optimizados para cada video basándose en el tema del guión.
Máximo 12 hashtags (YouTube penaliza si son demasiados).
"""
import random

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

HASHTAGS_GENERICOS = [
    "#datoscuriosos", "#sabíasque", "#viral", "#fyp",
    "#teorias", "#enigmas", "#secretos", "#paranormal",
    "#inexplicable", "#nocreerasesto", "#impactante",
]


def generar_hashtags(tags_guion, max_hashtags=12):
    """
    Recibe los tags del guión, busca coincidencias en el banco,
    combina con los default y retorna string de hashtags.
    """
    resultado = set(HASHTAG_BANK["default"])

    for tag in tags_guion:
        tag_lower = tag.lower()
        for key, hashtags in HASHTAG_BANK.items():
            if key in tag_lower or tag_lower in key:
                resultado.update(hashtags[:3])

    # Agregar hashtags genéricos rotatorios
    resultado.update(random.sample(HASHTAGS_GENERICOS, min(3, len(HASHTAGS_GENERICOS))))

    return " ".join(list(resultado)[:max_hashtags])
