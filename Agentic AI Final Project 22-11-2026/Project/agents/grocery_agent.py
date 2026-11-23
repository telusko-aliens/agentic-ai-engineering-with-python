from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool

from core.config import model
from agents.memory import UserContext

# what you will learn:
# - the grocery list is long-term memory too: it is saved in the Postgres store, so it survives restarts
# - agent isolation: the list is saved under ('users', user_id, 'grocery'), and the user_id comes from
#   the context, so riya's agent can only ever touch riya's list
# - this agent mixes tools: get_price from the MCP server + its own list tools


def grocery_namespace(user_id: str) -> tuple:
    return ('users', user_id, 'grocery')


@tool
async def add_to_grocery_list(item: str, runtime: ToolRuntime[UserContext]) -> str:
    """Add one item to the user's grocery list."""
    user_id = runtime.context.user_id
    print(f'      --- add_to_grocery_list({item}) for {user_id} ---')
    await runtime.store.aput(grocery_namespace(user_id), item.lower(), {'item': item})
    return f'added {item}'


@tool
async def show_grocery_list(runtime: ToolRuntime[UserContext]) -> str:
    """Show everything on the user's grocery list."""
    user_id = runtime.context.user_id
    print(f'      --- show_grocery_list() for {user_id} ---')
    items = await runtime.store.asearch(grocery_namespace(user_id), limit=100)
    if not items:
        return 'the grocery list is empty'
    return '\n'.join(f'- {item.value["item"]}' for item in items)


@tool
async def clear_grocery_list(runtime: ToolRuntime[UserContext]) -> str:
    """Remove everything from the user's grocery list."""
    user_id = runtime.context.user_id
    print(f'      --- clear_grocery_list() for {user_id} ---')
    items = await runtime.store.asearch(grocery_namespace(user_id), limit=100)
    for item in items:
        await runtime.store.adelete(grocery_namespace(user_id), item.key)
    return 'the grocery list is now empty'


def build_grocery_agent(mcp_tools_by_name, store):
    return create_agent(
        model=model,
        tools=[mcp_tools_by_name['get_price'], add_to_grocery_list, show_grocery_list, clear_grocery_list],
        system_prompt=(
            'You manage the user\'s grocery list. Add items one by one with add_to_grocery_list. '
            'Skip pantry basics like salt, oil, water and spices. '
            'When asked about cost, use get_price for each item. The user buys one pack of each item, '
            'so the total is simply the sum of the pack prices, in rupees.'
        ),
        context_schema=UserContext,
        store=store,
        name='grocery_agent',
    )
