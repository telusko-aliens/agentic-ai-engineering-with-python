from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.tools import load_mcp_tools

import sys
from pathlib import Path
import asyncio

load_dotenv()

SERVER_PATH = Path(__file__).parent / "server.py"

async def main():
    client = MultiServerMCPClient({
        'cart_server': {
            'transport':'stdio',
            'command': sys.executable,
            "args": [str(SERVER_PATH)]
        }
    })

    async with client.session("cart_server") as session:
        tools = await load_mcp_tools(session)
        tools_by_name = {}
        for tool in tools:
            tools_by_name[tool.name] = tool

        result = await tools_by_name["add_to_cart"].ainvoke({"item": "apple"})
        print(result[0]["text"])
        result = await tools_by_name["add_to_cart"].ainvoke({"item": "banana"})
        print(result[0]["text"])

        result = await tools_by_name["add_to_cart"].ainvoke({"item": "grapes"})
        print(result[0]["text"])

        result = await tools_by_name["show_cart"].ainvoke({})
        print(result[0]["text"])

        result = await tools_by_name["get_session_id"].ainvoke({})
        print(result[0]["text"])

        result = await tools_by_name["show_product_quantity"].ainvoke({})
        print(result[0]["text"])

    


if __name__ == "__main__":
    asyncio.run(main())