"""Integration tests against a real Google Drive account.

Requires environment variables:
  GOOGLE_CLIENT_SECRETS_FILE — path to OAuth2 client_secrets.json
  GOOGLE_TOKEN_FILE          — path to token.json (created on first run)
  GDRIVE_TEST_FOLDER_ID      — Drive folder ID to use as sandbox

Run with:
  pytest tests/integration/ -v
"""

import os

import pytest

from gdrive_mcp_server.auth import get_credentials
from gdrive_mcp_server.tools.add_document import add_document_to_folder
from gdrive_mcp_server.tools.export import export_file_as_markdown
from gdrive_mcp_server.tools.search import search_files

pytestmark = pytest.mark.skipif(
    not os.environ.get("GDRIVE_TEST_FOLDER_ID"),
    reason="GDRIVE_TEST_FOLDER_ID not set — skipping integration tests",
)


@pytest.fixture(scope="module")
def creds():
    return get_credentials()


@pytest.fixture(scope="module")
def test_folder_id():
    return os.environ["GDRIVE_TEST_FOLDER_ID"]


def test_round_trip_add_search(creds, test_folder_id):
    created = add_document_to_folder(test_folder_id, "integration-test.txt", "hello world", creds)
    assert created["id"]

    results = search_files(f"name = 'integration-test.txt' and '{test_folder_id}' in parents", creds)
    ids = [f["id"] for f in results]
    assert created["id"] in ids


def test_collision_suffix_appended(creds, test_folder_id):
    first = add_document_to_folder(test_folder_id, "collision-test.txt", "first", creds)
    second = add_document_to_folder(test_folder_id, "collision-test.txt", "second", creds)

    assert first["name"] == "collision-test.txt"
    assert second["name"] == "collision-test_1.txt"
    assert first["id"] != second["id"]


def test_export_returns_string(creds, test_folder_id):
    created = add_document_to_folder(test_folder_id, "export-test.txt", "export content", creds)
    content = export_file_as_markdown(created["id"], creds)
    assert isinstance(content, str)
    assert len(content) > 0
