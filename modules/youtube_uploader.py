"""
Sube el video como YouTube Short usando Google API con OAuth 2.0.
El video se detecta como Short automáticamente si:
- Es vertical (9:16)
- Dura menos de 60 segundos
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET = "credentials/youtube_client_secret.json"
TOKEN_PICKLE = "credentials/youtube_token.pickle"


def obtener_credenciales():
    """Obtiene o refresca las credenciales OAuth de YouTube."""
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def subir_short(video_path, titulo, descripcion, tags, categoria_id="22", privacidad="public"):
    """
    Sube un video como YouTube Short.
    Retorna el ID del video subido.
    """
    creds = obtener_credenciales()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": titulo,
            "description": descripcion,
            "tags": tags,
            "categoryId": categoria_id,
        },
        "status": {
            "privacyStatus": privacidad,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response["id"]
