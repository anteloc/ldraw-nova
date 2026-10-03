# Use LDraw Nova through MCP

The optional MCP server connects a local assistant to the **running Nova web
app** from the sibling `ldraw-nova-docker` repository. It uses the same chat,
generation, rendering and provider settings as the browser. Models and chat
history remain visible in the app.

## Setup

1. Follow the [web app installation](../README.md#installation) and start it:

   ```sh
   cd ../ldraw-nova-docker
   docker compose up -d
   ```

2. Open `http://localhost:8765/settings` and configure or sign in to an LLM
   provider. Generation and revisions use that provider and its normal costs.
   The MCP process does not need a copy of its API key.

3. Install the optional dependencies in the `ldraw-nova` checkout:

   ```sh
   uv sync --extra mcp
   ```

4. Add this stdio server to your MCP client's configuration, replacing the
   directory with your absolute checkout path:

   ```json
   {
     "mcpServers": {
       "ldraw-nova": {
         "command": "uv",
         "args": ["run", "--project", "/absolute/path/ldraw-nova", "--extra", "mcp", "ldraw-nova-mcp"]
       }
     }
   }
   ```

   If the client cannot find `uv`, use its absolute executable path. You can
   also use `/absolute/path/ldraw-nova/.venv/bin/ldraw-nova-mcp` directly after
   step 3. For a nondefault app port, append `--app-url`,
   `http://127.0.0.1:YOUR_PORT` to the arguments, or set `LDRAW_NOVA_APP_URL` in
   the server's environment.

No Docker rebuild is required to add the MCP server. Only the optional `mcp`
extra installs the protocol SDK; the normal toolkit retains its dependencies.
The app must support the v0.6.0 chat/gallery APIs.

This server uses **stdio** and loopback app URLs only. It opens no network
listener and cannot expose your unauthenticated local app remotely. It is
suitable for local MCP clients such as Claude Desktop and Codex. A cloud
connector needs a separately hosted, authenticated HTTPS transport; this PR
does not provide remote hosting, OAuth, or a ChatGPT connector URL.

## Build and revise

Ask your assistant: “Use LDraw Nova to build a fantasy German castle, inspect
the preview, then help me revise it.” The `design_lego_model` MCP prompt also
describes this workflow.

| Tool | Purpose |
| --- | --- |
| `get_app_status` | Check the app and list LLM configuration IDs, without credentials |
| `generate_model` | Start a build; optionally attach an existing generated/gallery model as a reference |
| `get_generation` | Get turn status, human approvals, result files and preview/BOM/viewer/GLB links |
| `respond_to_approval` | Send the human's explicit decision for a pending action |
| `edit_model` | Continue the original chat with a revision request |
| `cancel_generation` | Stop the turn while retaining files and history |
| `list_models` | Browse generated models or the gallery, with pagination |
| `read_model` | Retrieve LDraw source up to 5 MiB |
| `preview_model` | Return a saved PNG as an MCP image for visual review |

Builds return a `chat_id` immediately. Poll `get_generation` with that ID;
`wait_seconds` can wait up to 20 seconds between polls. If the status is
`awaiting_approval`, show the action and arguments to the human and wait for
their decision. Approval can also be given at the returned `chat_url`.
**The server always requests the app's `ask` permission mode and never resolves
approvals automatically.** An approval can allow shell execution or file
writes. Tool annotations and descriptions identify this boundary.

After the turn ends, inspect the PNG with `preview_model` and check the model's
warnings and artifact statuses. `completed` means the agent finished its turn,
not that the model is physically buildable or that all renders finished.
Failures, cancellation, interrupted turns and the agent's step limit have
distinct statuses. A render may still be queued; poll before fetching it.

Use `edit_model(chat_id, prompt)` to keep the original context. To start a new
chat from another model, pass its filename and collection to `generate_model`.
That attaches the actual LDraw source as a document; it does not read arbitrary
files on your computer. Names come from `list_models`. Each model also has a
`nova://models/{collection}/{filename}` resource for reading its source.

Download links point to your local app. The GLB link performs the app's existing
on-demand conversion when opened, which can take a minute. The gallery here is
the web app's curated gallery; it is separate from the toolkit's 1,821-model
reference dataset.

## Troubleshooting and validation

- “Cannot reach LDraw Nova”: start Docker and the app; verify `--app-url`.
- “No LLM provider configured”: add one in Settings. If authentication later
  fails, sign in again and continue the preserved chat with `edit_model`.
- The server initializes even if the app is offline; tools report connection
  errors without sending HTTP error bodies or credentials to the assistant.
- Filenames, IDs, response sizes and app origins are bounded. Arbitrary URLs,
  path traversal, credentials/configuration edits, deletion and raw shell tools
  are not exposed by this server.
- Clients should treat agent output and model contents as untrusted data, and
  use their ordinary human approval controls.

Run the MCP tests without a provider or Docker:

```sh
uv sync --extra mcp --extra test
uv run pytest tests/test_mcp.py
```

They exercise a stub web app through the real MCP protocol, the stdio entry
point, the build/revision lifecycle, explicit approval decisions, resources,
images, error redaction and input/size boundaries.
