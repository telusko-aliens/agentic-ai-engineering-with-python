import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call
from langchain_core.tools import tool

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""

    return f"{order_id.upper()}: packed, ships tomorrow"


@tool
def delivery_estimate(pin_code: str) -> str:
    """Estimate delivery days for an Indian pin code."""

    return "2 days" if pin_code.startswith("4") else "5 days"


@tool
def start_refund(order_id: str, reason: str) -> str:
    """Start a refund for an order."""

    return f"Refund started for {order_id.upper()}, reason: {reason}"


@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order that has not shipped yet."""

    return f"{order_id.upper()} cancelled"

DELIVERY_TOOLS = [
    order_status,
    delivery_estimate
]

MONEY_TOOLS = [
    order_status,
    start_refund,
    cancel_order
]

MONEY_WORDS = (
    "refund",
    "cancel",
    "money",
    "return"
)

def latest_question(messages):
    """
    Get the customer's most recent message.

    We don't simply use messages[-1].

    During an agent run, the last message could be:
        - a tool result
        - the model's response
        - another internal message

    We specifically want the latest message written
    by the human/customer.
    """

    for message in reversed(messages):

        if type(message).__name__ == "HumanMessage":
            return str(message.content).lower()

    return ""


# dynamic tool selection middle ware --> @wrap_model_call
@wrap_model_call
def pick_tools(request, handler):

    # Get the customer's latest question.
    question = latest_question(request.messages)

    # -----------------------------------------------------
    # CHOOSE TOOLS BASED ON THE QUESTION
    # -----------------------------------------------------

    if any(word in question for word in MONEY_WORDS):

        # Money/refund-related question.
        #
        # Give the model only the money-related tools
        # for THIS model call.
        request = request.override(
            tools=MONEY_TOOLS
        )

    else:

        # Normal delivery/order question.
        #
        # Give the model only the delivery-related tools.
        request = request.override(
            tools=DELIVERY_TOOLS
        )
    print(
        "   offered:",
        [t.name for t in request.tools]
    )
    return handler(request)



agent = create_agent(
    model="gpt-4o-mini",

    tools=[
        order_status,
        delivery_estimate,
        start_refund,
        cancel_order
           ],
    middleware=[pick_tools],
    system_prompt="You are a support agent. Use the tools, never guess.",
)

# helper funcation to ask question

def ask(question):

    print("Q:", question)

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    print("A:", result["messages"][-1].content)
    print("-" * 70)



ask("Where is my order ORD-1002?")
ask("I want a refund for ORD-1002, it is too late for me.")
ask("what is the status of ORD-1002 and initiate refund if it is not shipped today")

    



