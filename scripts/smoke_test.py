import asyncio
import os

from infrastructure_diagram_mcp_server.diagrams_tools import generate_diagram


DIAGRAM_CODE = """with Diagram(\"Smoke Test\", show=False):
    ELB(\"lb\") >> EC2(\"web\")
"""


async def main() -> None:
    result = await generate_diagram(
        code=DIAGRAM_CODE,
        filename="smoke_test",
        timeout=60,
        workspace_dir=os.getcwd(),
    )
    print(result.model_dump())
    if result.status != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
