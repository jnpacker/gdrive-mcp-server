# gdrive-mcp-server

A Python MCP server exposing limited Google Drive capabilities as tools for AI agents.

## Tools

| Tool | Description |
|---|---|
| `search_files` | Search Drive by name or full-text using a Drive query string |
| `export_file_as_markdown` | Export a Google Doc as Markdown, or any other file as plain text |
| `add_document_to_folder` | Upload a plain-text document to a folder; appends `_1`, `_2`, … on name collision |

## Requirements

- Python 3.11+
- A Google Cloud project with the Drive API enabled
- OAuth2 credentials (Desktop app type)

## Setup

### 1. Enable the Google Drive API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services → Library** and enable **Google Drive API**.

### 2. Create OAuth2 credentials

1. Go to **APIs & Services → Credentials**.
2. Click **Create Credentials → OAuth client ID**.
3. Select **Desktop app** as the application type.
4. Download the generated `client_secrets.json` file.

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in the paths:

```sh
cp .env.example .env
```

```sh
# Path to the client_secrets.json downloaded above
GOOGLE_CLIENT_SECRETS_FILE=/path/to/client_secrets.json

# Path where the OAuth2 token will be saved after first login
GOOGLE_TOKEN_FILE=/path/to/token.json
```

Source the file before running:

```sh
source .env   # or: export $(cat .env | xargs)
```

### 4. Install

```sh
pip install -e .
```

### 5. Authenticate

Run the server once directly to trigger the OAuth2 browser flow:

```sh
gdrive-mcp-server
```

A browser window will open asking you to sign in and grant Drive access. After you approve, a `token.json` is saved to `GOOGLE_TOKEN_FILE`. Subsequent runs load the token automatically and refresh it when it expires.

## Running the server

```sh
gdrive-mcp-server
```

Or via the module:

```sh
python3 -m gdrive_mcp_server.server
```

## MCP client configuration

Add the server to your MCP client config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "gdrive-mcp-server",
      "env": {
        "GOOGLE_CLIENT_SECRETS_FILE": "/path/to/client_secrets.json",
        "GOOGLE_TOKEN_FILE": "/path/to/token.json"
      }
    }
  }
}
```

## Running tests

**Unit tests** (no credentials required):

```sh
pip install -e ".[dev]"
python3 -m pytest tests/unit/ -v
```

**Integration tests** (requires real credentials and a sandbox folder):

```sh
export GDRIVE_TEST_FOLDER_ID=<your-drive-folder-id>
python3 -m pytest tests/integration/ -v
```
