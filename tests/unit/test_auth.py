import json
from unittest.mock import MagicMock, patch

import pytest

from gdrive_mcp_server.auth import SCOPES, get_credentials


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("GOOGLE_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("GOOGLE_CLIENT_SECRETS_FILE", str(tmp_path / "secrets.json"))
    return token_file


def _write_token(token_file, scopes, extra=None):
    data = {
        "refresh_token": "rt",
        "client_id": "cid",
        "client_secret": "csecret",
        "scopes": scopes,
    }
    if extra:
        data.update(extra)
    token_file.write_text(json.dumps(data))


@patch("gdrive_mcp_server.auth.InstalledAppFlow")
def test_runs_full_flow_when_no_token_file(mock_flow_cls, env):
    mock_creds = MagicMock()
    mock_creds.to_json.return_value = "{}"
    mock_flow_cls.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds

    result = get_credentials()

    mock_flow_cls.from_client_secrets_file.assert_called_once()
    assert result is mock_creds
    assert env.exists()


@patch("gdrive_mcp_server.auth.InstalledAppFlow")
def test_runs_full_flow_when_token_missing_new_scope(mock_flow_cls, env):
    # Token was granted before the "drive" scope was added; refreshing it
    # would fail with invalid_scope, so we must not attempt a refresh.
    _write_token(env, scopes=SCOPES[:-1])
    mock_creds = MagicMock()
    mock_creds.to_json.return_value = "{}"
    mock_flow_cls.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds

    result = get_credentials()

    mock_flow_cls.from_client_secrets_file.assert_called_once()
    assert result is mock_creds


@patch("gdrive_mcp_server.auth.InstalledAppFlow")
@patch("gdrive_mcp_server.auth.Credentials")
def test_uses_existing_valid_token_with_all_scopes(mock_creds_cls, mock_flow_cls, env):
    _write_token(env, scopes=SCOPES)
    mock_creds = MagicMock(valid=True)
    mock_creds_cls.from_authorized_user_file.return_value = mock_creds

    result = get_credentials()

    mock_creds_cls.from_authorized_user_file.assert_called_once_with(str(env), SCOPES)
    mock_flow_cls.from_client_secrets_file.assert_not_called()
    mock_creds.refresh.assert_not_called()
    assert result is mock_creds


@patch("gdrive_mcp_server.auth.Request")
@patch("gdrive_mcp_server.auth.InstalledAppFlow")
@patch("gdrive_mcp_server.auth.Credentials")
def test_refreshes_expired_token_that_has_all_scopes(mock_creds_cls, mock_flow_cls, mock_request, env):
    _write_token(env, scopes=SCOPES)
    mock_creds = MagicMock(valid=False, expired=True, refresh_token="rt")
    mock_creds.to_json.return_value = "{}"
    mock_creds_cls.from_authorized_user_file.return_value = mock_creds

    result = get_credentials()

    mock_creds.refresh.assert_called_once()
    mock_flow_cls.from_client_secrets_file.assert_not_called()
    assert result is mock_creds
