from dotenv import load_dotenv
import sys
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

server_params = {
    "FirstMCPServer": {
        "command": sys.executable,
        "args": [str(Path(__file__).parent / "my_mcp_server.py")],
        "transport": "stdio",
    }
}

async def main():
    mcp_server = MultiServerMCPClient(server_params)
    tools = await mcp_server.get_tools()

    print(tools)

    llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

    history = [
        HumanMessage(content="Add 4 and 5"),
    ]

    response = llm.invoke(history)
    history.append(response)

    toolcall = response.tool_calls[0]
    tool = next(t for t in tools if t.name == toolcall["name"])
    result = await tool.ainvoke(toolcall["args"])
    print(result[0]['text'])
    history.append(ToolMessage(content=result[0]['text'], tool_call_id=toolcall["id"]))

    response = await llm.ainvoke(history)
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())