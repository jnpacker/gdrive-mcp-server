from unittest.mock import MagicMock, patch

import pytest

from gdrive_mcp_server.tools.set_access import REDHAT_DOMAIN, set_general_access


@pytest.fixture
def mock_creds():
    return MagicMock()


def _make_service(created_permission: dict):
    service = MagicMock()
    service.permissions.return_value.create.return_value.execute.return_value = created_permission
    return service


@pytest.mark.parametrize(
    "access, expected_role",
    [
        ("Edit", "writer"),
        ("Comment", "commenter"),
        ("Read", "reader"),
        ("edit", "writer"),
        ("COMMENT", "commenter"),
        ("rEaD", "reader"),
    ],
)
@patch("gdrive_mcp_server.tools.set_access.build")
def test_maps_access_to_role(mock_build, access, expected_role, mock_creds):
    created = {"id": "perm-1", "type": "domain", "role": expected_role, "domain": REDHAT_DOMAIN}
    service = _make_service(created)
    mock_build.return_value = service

    result = set_general_access("file-123", access, mock_creds)

    call_kwargs = service.permissions.return_value.create.call_args.kwargs
    assert call_kwargs["fileId"] == "file-123"
    assert call_kwargs["body"] == {"type": "domain", "domain": REDHAT_DOMAIN, "role": expected_role}
    assert call_kwargs["supportsAllDrives"] is True
    assert result == created


@patch("gdrive_mcp_server.tools.set_access.build")
def test_invalid_access_raises_value_error(mock_build, mock_creds):
    with pytest.raises(ValueError, match="Invalid access"):
        set_general_access("file-123", "Owner", mock_creds)

    mock_build.assert_not_called()
