import asyncio

import httpx  # a simple HTTP library, used to call the /token endpoint
from langchain_mcp_adapters.client import MultiServerMCPClient
import time

BASE_URL = "http://127.0.0.1:8004"
TOKEN_URL = f"{BASE_URL}/token"
MCP_URL = f"{BASE_URL}/mcp"

async def get_token(client_id: str, client_secret: str) -> str:
    form = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient() as http:
        response = await http.post(TOKEN_URL, data=form)

    if response.status_code == 401:
        print("get_token -> REJECTED:", response.json()["error"])
        return None

    return response.json()["access_token"]

async def call_tool(token: str | None, tool_name: str, args: dict):
    connection = {
        "transport": "streamable_http",
        "url": MCP_URL
    }

    if token is not None:
        connection["headers"] = {"Authorization": f"Bearer {token}"}
    client = MultiServerMCPClient({"secure": connection})

    try:
        async with client.session("secure") as session:
            result = await session.call_tool(tool_name, args)
            status = "DENIED" if result.isError else "OK"
            print(f"{tool_name} -> {status}:", result.content[0].text)
    except Exception as error:
        # The MCP client wraps failures in an exception group; unwrap it if so.
        real_error = error.exceptions[0] if isinstance(error, BaseExceptionGroup) else error
        print(f"{tool_name} -> REJECTED:", str(real_error).splitlines()[0])


async def main():
    #1. token = None
    await call_tool(token=None, tool_name="greet", args={"name": "Akshay"})

    #2. Reader Token
    reader_token = await get_token(client_id="reader-app", client_secret="reader-secret")
    await call_tool(token=reader_token, tool_name="greet", args={"name": "Akshay"})

    time.sleep(5)

    #3. Out of Scope
    await call_tool(token=reader_token, tool_name="reset_database", args={})

    #4: Using Admin Access token
    admin_token = await get_token(client_id="admin-app", client_secret="admin-secret")
    await call_tool(token=admin_token, tool_name="reset_database", args={})


    #5. If the creds are wrong
    admin_token = await get_token(client_id="admin-app", client_secret="admin-secret1")









if __name__ == "__main__":
    asyncio.run(main())