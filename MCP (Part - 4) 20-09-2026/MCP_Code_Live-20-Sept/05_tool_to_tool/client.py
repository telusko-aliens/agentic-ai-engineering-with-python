import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

stdio_server = PythonStdioTransport(Path(__file__).parent /
                                    "stdio_server.py", python_cmd=sys.executable)
http_server = "http://127.0.0.1:8002/mcp"

async def main():
    async with Client(stdio_server) as stdio, Client(http_server) as http:

        result = await stdio.call_tool("add_then_double", {"a": 3, "b": 4})
        print(f'1. {result.data}')

        result = await stdio.call_tool("sum_of_squares", {"a": 3, "b": 4})
        print(f'2. {result.data}')

        result = await http.call_tool("double_then_square", {"n": 3})
        print(f'3. {result.data}')


if __name__ == "__main__":
    asyncio.run(main())