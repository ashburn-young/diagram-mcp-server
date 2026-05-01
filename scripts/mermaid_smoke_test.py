import asyncio
import os

from infrastructure_diagram_mcp_server.mermaid_tools import render_mermaid


MERMAID = """graph TD
  A[Client] --> B[Server]
  B --> C[(Database)]
"""


async def main() -> None:
    result = await render_mermaid(
        mermaid=MERMAID,
        filename="mermaid_smoke",
        timeout=60,
        workspace_dir=os.getcwd(),
    )
    print(result.model_dump())
    if result.status != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
