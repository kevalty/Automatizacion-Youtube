"""
Motor TTS usando edge-tts (gratuito, sin API key).
Genera audio .mp3 + archivo .vtt con timestamps por palabra.
"""
import asyncio
import edge_tts


async def generar_audio(texto, output_path, voz="es-MX-JorgeNeural", velocidad="-5%"):
    """
    Genera audio narrado y subtítulos VTT con timestamps.
    Retorna: (audio_path, vtt_path)
    """
    communicate = edge_tts.Communicate(texto, voz, rate=velocidad)
    submaker = edge_tts.SubMaker()

    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub(
                    (chunk["offset"], chunk["duration"]),
                    chunk["text"]
                )

    vtt_path = output_path.replace(".mp3", ".vtt")
    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())

    return output_path, vtt_path


def generar_audio_sync(texto, output_path, voz="es-MX-JorgeNeural", velocidad="-5%"):
    """Versión síncrona para uso fuera de contextos async."""
    return asyncio.run(generar_audio(texto, output_path, voz, velocidad))
