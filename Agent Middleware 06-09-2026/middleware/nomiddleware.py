import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji in the
# model's reply can crash print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

ORDERS = {
    "ORD-1001": {"item": "Wireless mouse", "status": "shipped", "amount": 1499},
    "ORD-1002": {"item": "Mechanical keyboard", "status": "packed", "amount": 4999},
}


@tool
def order_status(order_id: str) -> str:
    """Get the item, status and amount of an order using its id."""
    order = ORDERS.get(order_id.upper())
    if order is None:
        return f"No order found with id {order_id}."
    return f"{order['item']}, status {order['status']}, amount {order['amount']} rupees"


agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[order_status],
    system_prompt="You are a support agent. Look up the order before answering.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "Where is my order ORD-1002?"}]})

print(result["messages"][-1].content)
