import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


def _has_required_scopes(token_file: Path) -> bool:
    """Check whether a saved token file was actually granted all SCOPES.

    ``Credentials.from_authorized_user_file`` accepts an explicit ``scopes``
    argument that *overrides* whatever was really granted, so relying on the
    loaded ``Credentials.scopes`` can't detect a stale, narrower grant. We
    read the file's raw ``scopes`` list instead. A token authorized before a
    new scope was added will fail to refresh with ``invalid_scope`` (Google's
    refresh grant requires all requested scopes to already be authorized), so
    such tokens must go through the full OAuth flow again rather than being
    refreshed.
    """
    try:
        granted = set(json.loads(token_file.read_text()).get("scopes", []))
    except (OSError, ValueError):
        return False
    return set(SCOPES).issubset(granted)


def get_credentials() -> Credentials:
    token_file = Path(os.environ["GOOGLE_TOKEN_FILE"])
    secrets_file = os.environ["GOOGLE_CLIENT_SECRETS_FILE"]

    creds: Credentials | None = None
    if token_file.exists() and _has_required_scopes(token_file):
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())

    return creds
