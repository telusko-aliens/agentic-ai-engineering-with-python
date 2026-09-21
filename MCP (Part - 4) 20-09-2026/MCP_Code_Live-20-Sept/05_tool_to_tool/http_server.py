import sys
from pathlib import Path

from fastmcp import Client, FastMCP
from fastmcp.client.transports import PythonStdioTransport

mcp = FastMCP("HTTP Server")

@mcp.tool
def square(n: int) -> int:
    """Return n multiplied by itself."""
    return n * n

@mcp.tool
async def double_then_square(n: int) -> int:
    """Double n, then square it, using the double tool of the stdio server."""
    stdio_server = PythonStdioTransport(Path(__file__).parent / "stdio_server.py", python_cmd=sys.executable)
    async with Client(stdio_server) as stdio:
        doubled = await stdio.call_tool("double", {"n": n})
    return square(doubled.data)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8002)