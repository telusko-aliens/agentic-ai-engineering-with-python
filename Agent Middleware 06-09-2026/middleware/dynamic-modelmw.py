import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

load_dotenv()

# This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")


CHEAP = init_chat_model("openai:gpt-4o-mini")
STRONG = init_chat_model("openai:gpt-4o")

HARD_WORDS = (
    "hard",
    "difficult",
    "complex",
    "complicated",
    "challenging",
    "compare",
    "explain why",
    "analyze",
    "risk",
    "legal"
)

@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""

    return f"{order_id.upper()}: packed, ships tomorrow"


def latest_question(messages):
    """
    Get the customer's most recent message.

    We don't simply use messages[-1] because the last message
    might be a tool result or another agent message.

    We specifically want the latest human message.
    """

    for message in reversed(messages):

        if type(message).__name__ == "HumanMessage":
            return str(message.content).lower()

    return ""

@wrap_model_call
def route_model(request, handler):

    # Get the latest customer question.
    question = latest_question(request.messages)

    hard = (
        any(word in question for word in HARD_WORDS)
        or len(question) > 180
    )
    chosen = STRONG if hard else CHEAP

    print(f"   routed to {chosen.model_name}")

    return handler(
        request.override(model=chosen)
    )

agent = create_agent(
    model=CHEAP,
    tools=[order_status],
    system_prompt="You are a support agent for an online store.",
    middleware=[route_model],
)

def ask(question):

    print("Q:", question[:70])

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    print(
        "A:",
        result["messages"][-1].content[:200]
    )

    print("-" * 70)

ask("Where is my order ORD-1002?")
ask(
    "Compare buying a mechanical keyboard now against "
    "waiting for the sale, and explain why."
)

