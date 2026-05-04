from unittest.mock import MagicMock, patch

import pytest

from gdrive_mcp_server.tools.search import search_files


@pytest.fixture
def mock_creds():
    return MagicMock()


def _make_service(pages):
    """Build a mock Drive service that returns `pages` sequentially from files().list()."""
    service = MagicMock()
    execute_mock = MagicMock(side_effect=pages)
    service.files.return_value.list.return_value.execute = execute_mock
    return service


@patch("gdrive_mcp_server.tools.search.build")
def test_returns_files_from_single_page(mock_build, mock_creds):
    files = [{"id": "1", "name": "report.docx", "mimeType": "application/vnd.google-apps.document"}]
    service = _make_service([{"files": files, "nextPageToken": None}])
    mock_build.return_value = service

    result = search_files("name contains 'report'", mock_creds)

    assert result == files


@patch("gdrive_mcp_server.tools.search.build")
def test_passes_query_to_drive_api(mock_build, mock_creds):
    service = _make_service([{"files": [], "nextPageToken": None}])
    mock_build.return_value = service

    search_files("fullText contains 'budget'", mock_creds)

    service.files.return_value.list.assert_called_once_with(
        q="fullText contains 'budget'",
        spaces="drive",
        fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents)",
        pageToken=None,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    )


@patch("gdrive_mcp_server.tools.search.build")
def test_paginates_through_all_pages(mock_build, mock_creds):
    page1 = {"files": [{"id": "1", "name": "a.doc"}], "nextPageToken": "tok1"}
    page2 = {"files": [{"id": "2", "name": "b.doc"}], "nextPageToken": None}
    service = _make_service([page1, page2])
    mock_build.return_value = service

    result = search_files("name contains 'doc'", mock_creds)

    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


@patch("gdrive_mcp_server.tools.search.build")
def test_returns_empty_list_when_no_results(mock_build, mock_creds):
    service = _make_service([{"files": [], "nextPageToken": None}])
    mock_build.return_value = service

    result = search_files("name = 'nonexistent'", mock_creds)

    assert result == []
