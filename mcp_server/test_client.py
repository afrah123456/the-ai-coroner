import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"],
        env=dict(os.environ)
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("✅ Available MCP tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            print("\n🔬 Running full autopsy via MCP...\n")

            # Call the autopsy tool
            result = await session.call_tool(
                "run_full_autopsy",
                arguments={"project_name": "ai-coroner-demo"}
            )

            # Print raw result
            print(f"Raw result content: {result.content}")

            if result.content:
                for item in result.content:
                    if hasattr(item, 'text'):
                        print(f"\n✅ Response:\n{item.text[:500]}")
                    elif hasattr(item, 'data'):
                        print(f"\n✅ Data:\n{item.data}")
                    else:
                        print(f"\n✅ Item: {item}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())