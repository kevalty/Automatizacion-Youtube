#!/bin/bash
set -e
echo "🔮 Configurando Velo Oculto..."
sudo apt update && sudo apt install -y ffmpeg
pip install -r requirements.txt
mkdir -p data output/videos output/audio assets/fonts assets/music assets/sfx logs credentials
# Descargar fuente Montserrat Bold
if [ ! -f "assets/fonts/Montserrat-Bold.ttf" ]; then
    echo "Descargando Montserrat Bold..."
    wget -q -O /tmp/montserrat.zip "https://fonts.google.com/download?family=Montserrat" 2>/dev/null || \
    echo "⚠️ No se pudo descargar Montserrat. Descárgala manualmente de https://fonts.google.com/specimen/Montserrat"
    if [ -f /tmp/montserrat.zip ]; then
        unzip -q -o /tmp/montserrat.zip -d /tmp/montserrat/
        cp /tmp/montserrat/static/Montserrat-Bold.ttf assets/fonts/
        rm -rf /tmp/montserrat /tmp/montserrat.zip
    fi
fi
echo ""
echo "✅ Instalación completa. Próximos pasos:"
echo "1. Pon tu API key de Pexels en .env"
echo "2. Pon tu youtube_client_secret.json en credentials/"
echo "3. Pon tus guiones en data/guionesVeloOculto.json"
echo "4. Descarga música de fondo en assets/music/ (pixabay.com/music → busca 'dark ambient')"
echo "5. Descarga efectos de sonido en assets/sfx/ (pixabay.com/sound-effects)"
echo "6. Prueba: python main.py"
echo "7. Activa: python scheduler.py"
