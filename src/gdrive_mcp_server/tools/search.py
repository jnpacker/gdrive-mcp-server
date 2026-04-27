from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def search_files(query: str, creds: Credentials) -> list[dict]:
    """Search Google Drive for files matching a name or content pattern.

    Args:
        query: Google Drive query string (e.g. "name contains 'report'").
        creds: Authenticated Google OAuth2 credentials.

    Returns:
        List of file metadata dicts with id, name, mimeType, modifiedTime, parents.
    """
    service = build("drive", "v3", credentials=creds)
    results = []
    page_token = None

    while True:
        response = service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents)",
            pageToken=page_token,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        ).execute()
        results.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return results
