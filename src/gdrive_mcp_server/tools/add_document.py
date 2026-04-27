from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload


def _escape_q(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _find_available_name(service, folder_id: str, name: str) -> str:
    def exists(candidate: str) -> bool:
        q = f"'{_escape_q(folder_id)}' in parents and trashed = false and name = '{_escape_q(candidate)}'"
        return bool(service.files().list(q=q, fields="files(id)", includeItemsFromAllDrives=True, supportsAllDrives=True).execute().get("files"))

    if not exists(name):
        return name

    stem, _, ext = name.rpartition(".")
    base = name if not stem else stem
    suffix = f".{ext}" if stem else ""

    counter = 1
    while True:
        candidate = f"{base}_{counter}{suffix}"
        if not exists(candidate):
            return candidate
        counter += 1


def add_document_to_folder(folder_id: str, name: str, content: str, creds: Credentials) -> dict:
    """Upload a plain-text document to a Google Drive folder.

    If a file with the same name already exists in the folder, an incrementing
    numeric suffix (_1, _2, …) is appended to avoid overwriting.

    Args:
        folder_id: The Google Drive folder ID to upload into.
        name: Desired file name.
        content: Plain-text content to upload.
        creds: Authenticated Google OAuth2 credentials.

    Returns:
        Created file metadata dict with id, name, mimeType, parents, webViewLink.
    """
    service = build("drive", "v3", credentials=creds)
    available_name = _find_available_name(service, folder_id, name)

    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    return service.files().create(
        body={"name": available_name, "parents": [folder_id]},
        media_body=media,
        fields="id, name, mimeType, parents, webViewLink",
        supportsAllDrives=True,
    ).execute()
