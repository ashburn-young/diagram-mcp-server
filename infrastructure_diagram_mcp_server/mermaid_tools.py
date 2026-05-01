"""Mermaid diagram rendering tools.

This MCP server primarily renders diagrams from the Python `diagrams` DSL.
This module adds *optional* support for Mermaid input by calling a local Mermaid CLI.

We intentionally do not call any external web service for rendering, to avoid leaking
potentially sensitive architecture diagrams.
"""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
import uuid
from typing import Optional

from infrastructure_diagram_mcp_server.models import DiagramGenerateResponse


def _resolve_output_path(filename: Optional[str], workspace_dir: Optional[str]) -> tuple[str, str]:
    if filename is None:
        filename = f'mermaid_{uuid.uuid4().hex[:8]}'

    if os.path.isabs(filename):
        output_path = filename[:-4] if filename.endswith('.png') else filename
        output_dir = os.path.dirname(output_path) or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        return output_dir, output_path

    simple_filename = os.path.basename(filename)
    if simple_filename.endswith('.png'):
        simple_filename = simple_filename[:-4]

    if workspace_dir and os.path.isdir(workspace_dir) and os.access(workspace_dir, os.W_OK):
        output_dir = os.path.join(workspace_dir, 'generated-diagrams')
    else:
        import tempfile

        output_dir = os.path.join(tempfile.gettempdir(), 'generated-diagrams')

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, simple_filename)
    return output_dir, output_path


def _find_mermaid_renderer() -> tuple[list[str], str] | tuple[None, str]:
    """Find a local Mermaid renderer command.

    Preference order:
    1) `mmdc` if available on PATH (installed via `npm i -g @mermaid-js/mermaid-cli`)

    Returns:
        (cmd_prefix, kind) or (None, message)
    """

    # 1) PATH
    mmdc = shutil.which('mmdc')
    if mmdc:
        return [mmdc], 'mmdc'

    # 2) Common Windows npm global bin: %APPDATA%\npm\mmdc.(cmd|ps1)
    appdata = os.environ.get('APPDATA')
    if appdata:
        npm_bin = os.path.join(appdata, 'npm')
        for candidate in ('mmdc.cmd', 'mmdc.ps1', 'mmdc'):
            candidate_path = os.path.join(npm_bin, candidate)
            if os.path.exists(candidate_path):
                return [candidate_path], 'mmdc'

    return None, (
        "Mermaid rendering requires the Mermaid CLI (mmdc). "
        "Install Node.js, then run: `npm i -g @mermaid-js/mermaid-cli`, "
        "and ensure `mmdc` is on PATH (or available under %APPDATA%\\npm)."
    )


async def render_mermaid(
    mermaid: str,
    filename: Optional[str] = None,
    timeout: int = 90,
    workspace_dir: Optional[str] = None,
) -> DiagramGenerateResponse:
    """Render Mermaid code to a PNG diagram.

    This is optional functionality and requires `mmdc` to be installed locally.

    Args:
        mermaid: Mermaid source code (e.g. `graph TD; A-->B`)
        filename: Output filename (without extension). If not provided, a random name is used.
        timeout: Timeout seconds for rendering.
        workspace_dir: Directory used to place `generated-diagrams/`.

    Returns:
        DiagramGenerateResponse: Base64 PNG plus saved file path.
    """

    if not mermaid or not mermaid.strip():
        return DiagramGenerateResponse(status='error', message='Mermaid code is empty.')

    output_dir, output_path = _resolve_output_path(filename, workspace_dir)

    cmd_prefix, kind_or_message = _find_mermaid_renderer()
    if cmd_prefix is None:
        return DiagramGenerateResponse(status='error', message=kind_or_message)

    # Write input to a temp .mmd file in the output directory.
    # Keeping it local makes debugging easier (users can open it).
    input_path = os.path.join(output_dir, f'{os.path.basename(output_path)}.mmd')
    png_path = f'{output_path}.png'

    try:
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(mermaid)

        # mmdc args:
        # -i input, -o output, -b background.
        # NOTE: We avoid `--puppeteerConfigFile` etc. Keep defaults.
        cmd = [
            *cmd_prefix,
            '-i',
            input_path,
            '-o',
            png_path,
            '-b',
            'transparent',
        ]

        subprocess.run(
            cmd,
            cwd=output_dir,
            timeout=timeout,
            check=True,
            capture_output=True,
            text=True,
        )

        if not os.path.exists(png_path):
            return DiagramGenerateResponse(
                status='error',
                message='Mermaid renderer (mmdc) did not produce an output file.',
            )

        with open(png_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')

        return DiagramGenerateResponse(
            status='success',
            path=png_path,
            message=f'Mermaid diagram rendered successfully at {png_path}',
            image_data=image_data,
            mime_type='image/png',
            drawio_path=None,
        )

    except subprocess.TimeoutExpired:
        return DiagramGenerateResponse(
            status='error', message=f'Mermaid rendering timed out after {timeout} seconds.'
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or '').strip()
        stdout = (e.stdout or '').strip()
        detail = stderr or stdout or 'Unknown error'
        return DiagramGenerateResponse(
            status='error',
            message=f'Error rendering Mermaid via {kind_or_message}: {detail}',
        )
    except Exception as e:
        return DiagramGenerateResponse(status='error', message=f'Error rendering Mermaid: {e}')
