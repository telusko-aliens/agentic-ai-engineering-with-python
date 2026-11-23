from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_mcp_adapters.client import MultiServerMCPClient

from core.config import MCP_URL, model
from agents.grocery_agent import build_grocery_agent
from agents.memory import UserContext, add_user_preferences, save_preference, trim_history
from agents.nutrition_agent import build_nutrition_agent
from agents.recipe_agent import recipe_agent

# what you will learn:
# - multi-agent supervisor: the Head Chef talks to the user and hands work to 3 specialist agents
# - each specialist is wrapped as a tool, like in the supervisor lesson
# - agent isolation: a specialist only gets the request text, NOT the chat history,
#   and only the tools it needs. The user_id is passed down as context.
# - the Head Chef has short-term memory (checkpointer), long-term memory (store),
#   and message trimming (middleware)

mcp_client = MultiServerMCPClient({
    'kitchen_tools': {
        'transport': 'streamable_http',
        'url': MCP_URL,
    }
})


async def build_head_chef(store, checkpointer):
    # ---------- tools from the MCP server ----------
    mcp_tools = await mcp_client.get_tools()
    mcp_tools_by_name = {mcp_tool.name: mcp_tool for mcp_tool in mcp_tools}
    print(f'MCP tools loaded: {list(mcp_tools_by_name)}')

    # ---------- the specialists ----------
    nutrition_agent = build_nutrition_agent(mcp_tools_by_name)
    grocery_agent = build_grocery_agent(mcp_tools_by_name, store)

    # ---------- wrap each specialist as a tool for the Head Chef ----------
    @tool
    async def ask_recipe_agent(request: str) -> str:
        """Ask the recipe expert to find recipes. Include the meal, the user's diet and allergies."""
        print(f'  >>> head chef -> recipe_agent: {request}')
        result = await recipe_agent.ainvoke({'messages': [('user', request)]})
        return result['messages'][-1].content

    @tool
    async def ask_nutrition_agent(request: str) -> str:
        """Ask the nutrition expert for calories, protein, carbs and fat. Include the dish, its ingredients and servings."""
        print(f'  >>> head chef -> nutrition_agent: {request}')
        result = await nutrition_agent.ainvoke({'messages': [('user', request)]})
        return result['messages'][-1].content

    @tool
    async def ask_grocery_agent(request: str, runtime: ToolRuntime[UserContext]) -> str:
        """Ask the grocery expert to add items to, show or clear the user's grocery list, or estimate the cost."""
        print(f'  >>> head chef -> grocery_agent: {request}')
        # pass the SAME user context down, so the grocery agent works on this user's list only
        result = await grocery_agent.ainvoke({'messages': [('user', request)]}, context=runtime.context)
        return result['messages'][-1].content

    # ---------- the Head Chef (supervisor) ----------
    # no system_prompt here: add_user_preferences builds it fresh before every model call
    head_chef = create_agent(
        model=model,
        tools=[ask_recipe_agent, ask_nutrition_agent, ask_grocery_agent, save_preference],
        middleware=[add_user_preferences, trim_history],
        context_schema=UserContext,
        checkpointer=checkpointer,  # short-term memory: chat history per thread_id, in Postgres
        store=store,                # long-term memory: preferences + grocery lists per user, in Postgres
        name='head_chef',
    )
    return head_chef
