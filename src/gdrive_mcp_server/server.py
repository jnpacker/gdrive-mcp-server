from mcp.server.fastmcp import FastMCP

from .auth import get_credentials
from .tools.add_document import add_document_to_folder as _add_document
from .tools.export import export_file_as_markdown as _export
from .tools.search import search_files as _search
from .tools.set_access import set_general_access as _set_general_access

mcp = FastMCP("gdrive-mcp-server")

_creds = None


def _get_creds():
    global _creds
    if _creds is None or not _creds.valid:
        _creds = get_credentials()
    return _creds


@mcp.tool()
def search_files(query: str) -> list[dict]:
    """Search Google Drive for files matching a name or content pattern."""
    return _search(query, _get_creds())


@mcp.tool()
def export_file_as_markdown(file_id: str) -> str:
    """Export a Google Drive file as Markdown (Google Docs) or plain text."""
    return _export(file_id, _get_creds())


@mcp.tool()
def add_document_to_folder(folder_id: str, name: str, content: str) -> dict:
    """Add a document to a Drive folder; appends _N suffix on name collision."""
    return _add_document(folder_id, name, content, _get_creds())


@mcp.tool()
def set_general_access(file_id: str, access: str) -> dict:
    """Set a file's General access to the Red Hat domain (redhat.com).

    access must be one of: Edit, Comment, Read.
    """
    return _set_general_access(file_id, access, _get_creds())


def main():
    mcp.run()


if __name__ == "__main__":
    main()
