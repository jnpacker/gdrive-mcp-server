from unittest.mock import MagicMock, patch

import pytest

from gdrive_mcp_server.tools.export import GOOGLE_DOC_MIME, export_file_as_markdown


@pytest.fixture
def mock_creds():
    return MagicMock()


def _make_service(mime_type: str, export_content: bytes):
    service = MagicMock()
    service.files.return_value.get.return_value.execute.return_value = {"mimeType": mime_type}


    def fake_next_chunk():
        return None, True

    downloader = MagicMock()
    downloader.next_chunk.side_effect = fake_next_chunk

    import io

    io.BytesIO(export_content)

    class FakeDownloader:
        def __init__(self, buf, req):
            buf.write(export_content)
            buf.seek(0)
            self._done = False

        def next_chunk(self):
            if not self._done:
                self._done = True
                return None, True
            return None, True

    return service, FakeDownloader


@patch("gdrive_mcp_server.tools.export.MediaIoBaseDownload")
@patch("gdrive_mcp_server.tools.export.build")
def test_google_doc_exported_as_markdown(mock_build, mock_downloader, mock_creds):
    service = MagicMock()
    service.files.return_value.get.return_value.execute.return_value = {"mimeType": GOOGLE_DOC_MIME}
    mock_build.return_value = service

    content = b"# Hello\n\nThis is markdown."

    def fake_init(buf, req):
        buf.write(content)
        return MagicMock(next_chunk=MagicMock(return_value=(None, True)))

    mock_downloader.side_effect = fake_init

    result = export_file_as_markdown("doc-id-123", mock_creds)

    service.files.return_value.export_media.assert_called_once_with(
        fileId="doc-id-123", mimeType="text/markdown"
    )
    assert result == content.decode("utf-8")


@patch("gdrive_mcp_server.tools.export.MediaIoBaseDownload")
@patch("gdrive_mcp_server.tools.export.build")
def test_non_doc_falls_back_to_plain_text(mock_build, mock_downloader, mock_creds):
    service = MagicMock()
    service.files.return_value.get.return_value.execute.return_value = {
        "mimeType": "application/vnd.google-apps.spreadsheet"
    }
    mock_build.return_value = service

    content = b"col1,col2"

    def fake_init(buf, req):
        buf.write(content)
        return MagicMock(next_chunk=MagicMock(return_value=(None, True)))

    mock_downloader.side_effect = fake_init

    result = export_file_as_markdown("sheet-id-456", mock_creds)

    service.files.return_value.export_media.assert_called_once_with(
        fileId="sheet-id-456", mimeType="text/plain"
    )
    assert result == content.decode("utf-8")


@patch("gdrive_mcp_server.tools.export.MediaIoBaseDownload")
@patch("gdrive_mcp_server.tools.export.build")
def test_regular_file_uses_get_media(mock_build, mock_downloader, mock_creds):
    service = MagicMock()
    service.files.return_value.get.return_value.execute.return_value = {
        "mimeType": "text/plain"
    }
    mock_build.return_value = service

    content = b"plain file content"

    def fake_init(buf, req):
        buf.write(content)
        return MagicMock(next_chunk=MagicMock(return_value=(None, True)))

    mock_downloader.side_effect = fake_init

    result = export_file_as_markdown("file-id-789", mock_creds)

    service.files.return_value.get_media.assert_called_once_with(fileId="file-id-789")
    assert result == content.decode("utf-8")
