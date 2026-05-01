# Diagram MCP Server (Windows) – Quick Start

## 1) Prereqs

- Graphviz installed (provides `dot.exe`).
  - Recommended: `winget install -e --id Graphviz.Graphviz`
  - Default install path is usually `C:\Program Files\Graphviz\bin\dot.exe`

## 2) Create a dedicated venv for this project

From the repo tasks/scripts, you can use the included `diagram-mcp-server/.venv`.
If you want to recreate it manually:

- `python -m venv .venv`
- `.venv\Scripts\python.exe -m pip install -e .`

## 3) Run the MCP server (stdio)

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run-mcp.ps1`

This runs the MCP server over stdio (intended for MCP clients like Claude Desktop/Cursor/VS Code MCP support).

## 4) Smoke test diagram generation

- `.\.venv\Scripts\python.exe .\scripts\smoke_test.py`

On success it writes output under `generated-diagrams/` in your current working directory.

## Optional: Mermaid input support

This MCP server primarily generates diagrams from the Python `diagrams` DSL.
If you want to paste Mermaid code and render it to a PNG, use the MCP tool `render_mermaid`.

Prereq (local rendering): install Mermaid CLI (`mmdc`):

- Install Node.js
- Run: `npm i -g @mermaid-js/mermaid-cli`

Then your MCP client can call `render_mermaid(mermaid=..., workspace_dir=...)` and you’ll get back a PNG.

## Optional: enable .drawio export

This project can optionally generate a `.drawio` file via the `graphviz2drawio` extra:

- `.venv\Scripts\python.exe -m pip install -e ".[drawio]"`

Note: on Windows, `graphviz2drawio` may pull `pygraphviz`, which can require Microsoft C++ Build Tools and may not have wheels for all Python versions.
