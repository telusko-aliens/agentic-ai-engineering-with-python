from langchain.agents import create_agent

from core.config import model

# what you will learn:
# - this agent's tool comes from the MCP server (get_nutrition), not from a Python function in this project
# - agent isolation: it gets ONLY the get_nutrition tool, even though the MCP server also offers get_price


def build_nutrition_agent(mcp_tools_by_name):
    return create_agent(
        model=model,
        tools=[mcp_tools_by_name['get_nutrition']],
        system_prompt=(
            'You are the nutrition expert. Use get_nutrition for every main ingredient, never guess numbers. '
            'Estimate sensible gram amounts for the servings asked, add up the totals and give a short summary.'
        ),
        name='nutrition_agent',
    )
