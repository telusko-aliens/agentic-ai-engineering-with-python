import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_core.tools import tool

load_dotenv()

# This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

attempts = {"count": 0}

@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""

    # Increase the attempt counter every time the tool runs.
    attempts["count"] += 1

    print(
        f"   attempt {attempts['count']} "
        f"to reach the order service"
    )
    if attempts["count"] < 3:
       raise RuntimeError("order service unavailable")

    return f"{order_id.upper()}: packed, ships tomorrow"

agent = create_agent(
    model="openai:gpt-4o-mini",

    tools=[order_status],

    system_prompt=(
        "You are a support agent. "
        "Look up the order before answering."
    ),
    middleware=[
        ToolRetryMiddleware(
            max_retries=5,
            initial_delay=0.2,
            backoff_factor=1.5
            )

        ],
)
# this is ToolRetryMiddleware builtin middleware so far in our previous example we create our own custom middleware but now we used builting which is from framework



result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Where is my order ORD-1002?"
        }
    ]
})


print()
print("Answer:", result["messages"][-1].content)
print("Total attempts:", attempts["count"])

