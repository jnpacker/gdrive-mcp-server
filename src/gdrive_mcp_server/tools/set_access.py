from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

REDHAT_DOMAIN = "redhat.com"

ROLE_MAP = {
    "edit": "writer",
    "comment": "commenter",
    "read": "reader",
}


def set_general_access(file_id: str, access: str, creds: Credentials) -> dict:
    """Set a Drive file's General access to the Red Hat Workspace domain.

    Creates a domain-wide permission on the file for redhat.com, granting the
    requested access level to anyone in the organization.

    Args:
        file_id: The Google Drive file ID to update.
        access: Desired access level, one of "Edit", "Comment", or "Read"
            (case-insensitive).
        creds: Authenticated Google OAuth2 credentials.

    Returns:
        Created permission metadata dict with id, type, role, domain.

    Raises:
        ValueError: If access is not one of the supported values.
    """
    role = ROLE_MAP.get(access.lower())
    if role is None:
        valid = ", ".join(sorted(ROLE_MAP, key=str.lower))
        raise ValueError(f"Invalid access '{access}'; must be one of: {valid}")

    service = build("drive", "v3", credentials=creds)
    return service.permissions().create(
        fileId=file_id,
        body={"type": "domain", "domain": REDHAT_DOMAIN, "role": role},
        fields="id, type, role, domain",
        supportsAllDrives=True,
    ).execute()
