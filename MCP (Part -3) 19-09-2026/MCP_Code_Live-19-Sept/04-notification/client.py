import asyncio
import sys
from pathlib import Path

from langchain_mcp_adapters.callbacks import Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient

SERVER_PATH = Path(__file__).parent / "server.py"  # started by the client (stdio)
SERVER_URL = "http://127.0.0.1:8001/mcp"  # already running (HTTP)

async def on_log(params, context):
    print(f"LOG     : [{context.server_name} / {context.tool_name}]", params.data["msg"])

async def on_progress(progress, total, message, context):
    print(f"PROGRESS: [{context.server_name} / {context.tool_name}] {progress:.0f} / {total:.0f} - {message}")


async def main():

    client = MultiServerMCPClient(
        {
            "stdio_server": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER_PATH)],
                "env": {"FASTMCP_LOG_LEVEL": "WARNING"},  # hides the server's own logs
            },
            "http_server": {
                "transport": "streamable_http",
                "url": SERVER_URL,
            },
        },
        callbacks=Callbacks(on_logging_message=on_log, on_progress=on_progress),
    )

    for server_name in ["stdio_server", "http_server"]:
        print(f"\n--- Calling do_work on {server_name} ---")

        tools = await client.get_tools(server_name=server_name)
        tools_by_name = {tool.name: tool for tool in tools}
        tool = tools_by_name["do_work"]

        result = await tool.ainvoke({})

        tool_output = result[0]["text"]
        print("RESULT  :", tool_output)


if __name__ == "__main__":
    asyncio.run(main())
