import io

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
GOOGLE_WORKSPACE_PREFIX = "application/vnd.google-apps."


def export_file_as_markdown(file_id: str, creds: Credentials) -> str:
    """Export a Google Drive file to Markdown (Google Docs) or plain text (others).

    Google Docs are exported as Markdown. Other Google Workspace files (Sheets,
    Slides, etc.) fall back to plain text. Regular files are downloaded directly.

    Args:
        file_id: The Google Drive file ID to export.
        creds: Authenticated Google OAuth2 credentials.

    Returns:
        File content as a string.
    """
    service = build("drive", "v3", credentials=creds)
    mime = service.files().get(fileId=file_id, fields="mimeType", supportsAllDrives=True).execute().get("mimeType", "")

    buf = io.BytesIO()

    if mime == GOOGLE_DOC_MIME:
        request = service.files().export_media(fileId=file_id, mimeType="text/markdown")
    elif mime.startswith(GOOGLE_WORKSPACE_PREFIX):
        request = service.files().export_media(fileId=file_id, mimeType="text/plain")
    else:
        request = service.files().get_media(fileId=file_id)

    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    return buf.getvalue().decode("utf-8")
