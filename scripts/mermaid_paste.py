r"""Paste Mermaid on stdin and render to PNG.

Usage:
    .\.venv\Scripts\python.exe .\scripts\mermaid_paste.py --name my_diagram

Input:
    - Paste Mermaid content to stdin
    - End input with Ctrl+Z then Enter (Windows)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from infrastructure_diagram_mcp_server.mermaid_tools import render_mermaid


def _read_stdin_all() -> str:
    # On Windows, users end stdin with Ctrl+Z then Enter.
    return sys.stdin.read()


async def _main_async() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='mermaid_input', help='Output base name (no extension)')
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()

    mermaid = _read_stdin_all()
    result = await render_mermaid(
        mermaid=mermaid,
        filename=args.name,
        timeout=args.timeout,
        workspace_dir=os.getcwd(),
    )

    print(result.model_dump())
    return 0 if result.status == 'success' else 1


def main() -> None:
    raise SystemExit(asyncio.run(_main_async()))


if __name__ == '__main__':
    main()
