from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import sys
from pathlib import Path
import asyncio

load_dotenv()
async def main():
    
    client = MultiServerMCPClient({
        'greeting': {
            'transport':'streamable_http',
            'url': 'http://127.0.0.1:8000/mcp'
        }
    })

    tools = await client.get_tools() # to get the tools list

    # For LLM
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools=tools)

    messages = [HumanMessage(content="Print Akshay in unique way default times")]

    response = await llm_with_tools.ainvoke(messages)
    #print(response)
    messages.append(AIMessage(content=response.content, tool_calls=response.tool_calls))
  
    tools_by_name = {tool.name: tool for tool in tools}

    result = await tools_by_name["add_to_cart"].ainvoke({"item": "apple"})
    print(result[0]["text"])
    result = await tools_by_name["add_to_cart"].ainvoke({"item": "banana"})
    print(result[0]["text"])
    result = await tools_by_name["show_cart"].ainvoke({})
    print(result[0]["text"])


    for tool_call in response.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = await tool.ainvoke(tool_call['args']) # to call the tool
        tool_output = result[0]['text']
        print(tool_output)

        messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call['id']))

    final_response = await llm_with_tools.ainvoke(messages)
    print(final_response.content)

    


if __name__ == "__main__":
    asyncio.run(main())