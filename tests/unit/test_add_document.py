from unittest.mock import MagicMock, patch

import pytest

from gdrive_mcp_server.tools.add_document import add_document_to_folder


@pytest.fixture
def mock_creds():
    return MagicMock()


def _make_service(existing_names: list[str], created_file: dict):
    service = MagicMock()

    def list_execute(*args, **kwargs):
        q: str = service.files.return_value.list.call_args.kwargs.get("q", "")
        for name in existing_names:
            escaped = name.replace("'", "\\'")
            if f"name = '{escaped}'" in q:
                return {"files": [{"id": "existing"}]}
        return {"files": []}

    service.files.return_value.list.return_value.execute.side_effect = list_execute
    service.files.return_value.create.return_value.execute.return_value = created_file
    return service


@patch("gdrive_mcp_server.tools.add_document.MediaInMemoryUpload")
@patch("gdrive_mcp_server.tools.add_document.build")
def test_creates_file_with_given_name_when_no_collision(mock_build, mock_media, mock_creds):
    created = {"id": "new-id", "name": "notes.txt"}
    service = _make_service(existing_names=[], created_file=created)
    mock_build.return_value = service

    result = add_document_to_folder("folder-123", "notes.txt", "hello", mock_creds)

    service.files.return_value.create.assert_called_once()
    call_kwargs = service.files.return_value.create.call_args.kwargs
    assert call_kwargs["body"]["name"] == "notes.txt"
    assert call_kwargs["body"]["parents"] == ["folder-123"]
    assert result == created


@patch("gdrive_mcp_server.tools.add_document.MediaInMemoryUpload")
@patch("gdrive_mcp_server.tools.add_document.build")
def test_appends_suffix_on_collision(mock_build, mock_media, mock_creds):
    created = {"id": "new-id", "name": "notes_1.txt"}
    service = _make_service(existing_names=["notes.txt"], created_file=created)
    mock_build.return_value = service

    add_document_to_folder("folder-123", "notes.txt", "hello", mock_creds)

    call_kwargs = service.files.return_value.create.call_args.kwargs
    assert call_kwargs["body"]["name"] == "notes_1.txt"


@patch("gdrive_mcp_server.tools.add_document.MediaInMemoryUpload")
@patch("gdrive_mcp_server.tools.add_document.build")
def test_increments_suffix_until_available(mock_build, mock_media, mock_creds):
    created = {"id": "new-id", "name": "notes_2.txt"}
    service = _make_service(existing_names=["notes.txt", "notes_1.txt"], created_file=created)
    mock_build.return_value = service

    add_document_to_folder("folder-123", "notes.txt", "hello", mock_creds)

    call_kwargs = service.files.return_value.create.call_args.kwargs
    assert call_kwargs["body"]["name"] == "notes_2.txt"


@patch("gdrive_mcp_server.tools.add_document.MediaInMemoryUpload")
@patch("gdrive_mcp_server.tools.add_document.build")
def test_uploads_content_as_utf8(mock_build, mock_media, mock_creds):
    service = _make_service(existing_names=[], created_file={"id": "x", "name": "doc.txt"})
    mock_build.return_value = service

    add_document_to_folder("folder-123", "doc.txt", "héllo wörld", mock_creds)

    mock_media.assert_called_once_with("héllo wörld".encode("utf-8"), mimetype="text/plain")
