# MCP Demo

Learning project for the Model Context Protocol (MCP): a small app that serves horse/race data through a Flask API and exposes it via an MCP server, with a client that simulates an LLM driving tool calls.

## Project layout

```
src/mcp_demo/
  server.py          Flask REST API serving horse/race data (default URL is http://127.0.0.1:5000)
  mcp_server.py      MCP server (stdio) exposing 4 tools that proxy to the Flask API
  mcp_client.py      MCP client + chat loop; fake LLM (Model/ModelWrapper) drives tool calls
  model.py           Simulated LLM: Model + Response + Content (Content defined BEFORE Response)
  model_wrapper.py   ModelWrapper around any Model
  horse.py           Horse class + module-level horse instances (UPPER_CASE names)
  race.py            Race class + module-level race instances
  init_data.py       Seeds in-memory dicts used by server.py
  __init__.py        makes src/mcp_demo a regular package
tests/
  conftest.py        anyio asyncio backend fixture; imports mcp_client (bare top-level import)
  test_mcp_tools.py  unit tests: MCP client <-> MCP server <-> Flask API (6 tests)
  mcp_test_basic.py  standalone smoke test (has a broken import; see gotchas)
  decorator_test.py  scratch decorator exploration
.agents/skills/      agent skills: format-horse-data, format-race-data
src/__pycache__/     bytecode cache
```

## Essential commands

Python is managed with **uv**; target version is **3.12** (`.python-version`). Use the venu (`.venv/bin/python`), or `uv run` when trying to run programs. Dependencies are declared in `pyproject.toml` under the `[dependency-groups] dev` group: `flask`, `httpx2`, `mcp[cli]`, `anyio`.

- Before testing or running anything, start the Flask API server (must be running for MCP tools to resolve data):
  ```
  cd src/mcp_demo && uv run server.py
  ```
- Start the MCP server (stdio transport by default):
  ```
  cd src/mcp_demo && uv run mcp_server.py
  ```
- Run the MCP client against a server script:
  ```
  cd src/mcp_demo && uv run mcp_client.py mcp_server.py
  ```
- Run the test suite. Requires `pytest` and `pytest-anyio`:
  ```
  uv run --with pytest --with pytest-anyio pytest tests/
  ```
  or a single file:
  ```
  uv run --with pytest --with pytest-anyio pytest tests/test_mcp_tools.py
  ```

There is no `[tool.pytest]` section in `pyproject.toml`; the async backend is enabled in-test via `pytestmark = pytest.mark.anyio` (test_mcp_tools.py) and a session-scoped `anyio_backend` fixture returning `"asyncio"` (conftest.py). Tests collect successfully under pytest, which resolves the bare `from mcp_client import ...` import in conftest.py.

## Architecture & data flow

1. For now, test data is stored in memory. `init_data.py` builds in-memory dicts of `Horse`/`Race` instances (from `horse.py`/`race.py`) keyed by name.
2. `server.py` (Flask) exposes REST endpoints: `/horse/`, `/horse/<name>`, `/horse/<name>/color`, `/race/`, `/race/<name>`. Returns 404 `{"error": "X not found"}` for unknown names.
3. `mcp_server.py` defines four MCP tools (`get_horse_data`, `get_race_data`, `get_all_horses`, `get_all_races`) that `GET` `http://127.0.0.1:5000/...` via `httpx2`. Runs with `transport="stdio"`.
4. `mcp_client.py` spawns the MCP server as a subprocess (`uv run <abs path to .py>`), connects an MCP `Client` over stdio, lists tools, and runs a chat loop where a fake `Model` decides which tool to call and the client executes it.

## Conventions

- Files/modules: `snake_code`. Classes: `PascalCase`. Module-level data instances: `UPPER_CASE` (e.g. `SYMBOLI_RUDOLF`, `ARIMA_KINEN`).
- All cross-module imports inside `src/mcp_demo/` use the `mcp_demo.` package prefix (e.g. `from mcp_demo.model_wrapper import ModelWrapper`). The project root must be on `sys.path` so `src` resolves as a namespace package and `src.mcp_demo` as a subpackage.
- `src/mcp_demo/__init__.py` exists; `src/` itself has no `__init__.py` (namespace package under Python 3).
- Docstrings on public functions/classes; `logger = logging.getLogger(__name__)` used throughout.
- `DEBUG_FLAG = True` toggles verbose debug printing in `model.py`, `model_wrapper.py`, and `mcp_client.py`.

## Gotchas / non-obvious patterns

- **Tests require the Flask server to be up:** MCP tools proxy to `http://127.0.0.1:5000`, so start `server.py` before running `test_mcp_tools.py` or all the tool calls will fail/return `None`.
- **`mcp_client.server_params` hardcodes the runner as `uv`** and requires a `.py` suffix; it resolves relative server paths against the client file's directory.
- `make_request` in `mcp_server.py` returns `None` on HTTP error; callers should guard for `None` results.
- `uv run` is the standard runner everywhere; do not use `python` directly unless the venv is activated.

## Existing rule files

None found (no `.cursor/rules`, `.cursorrules`, `claude.md`, or prior `AGENTS.md`). Agent skills live under `.agents/skills/` and are unrelated to runtime code.
