"""
Scheduler 24/7. Ejecuta la generación de videos en horarios fijos.
Horarios: 08:00 | 12:00 | 17:00 (hora Ecuador, UTC-5)
Uso: python scheduler.py
"""
import schedule
import time
import asyncio
import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/velo_oculto.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler())


def run():
    """Ejecuta la generación y subida de un video."""
    from main import generar_y_subir
    asyncio.run(generar_y_subir())


schedule.every().day.at("08:00").do(run)
schedule.every().day.at("12:00").do(run)
schedule.every().day.at("17:00").do(run)

logging.info("🔮 Velo Oculto Scheduler iniciado")
logging.info("   Horarios: 08:00 | 12:00 | 17:00 (UTC-5 / hora Ecuador)")
logging.info("   Ctrl+C para detener")

while True:
    schedule.run_pending()
    time.sleep(30)
