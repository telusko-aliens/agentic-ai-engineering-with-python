import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    after_model,
    before_model,
    wrap_model_call,
    wrap_tool_call,
)

from langchain_core.tools import tool

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""

    return f"{order_id.upper()}: packed, ships tomorrow"


# ---------------------------------------------------------
# BEFORE MODEL
# ---------------------------------------------------------
# runs before the model is called

@before_model
def show_before(state, runtime):

    print(
        f"[before_model] "
        f"{len(state['messages'])} message(s) going to the model"
    )

    # None means:
    # "I am not changing the state."
    return None


# ---------------------------------------------------------
# WRAP MODEL CALL
# ---------------------------------------------------------
# around the model call 

@wrap_model_call
def time_the_model(request, handler):

    # We can inspect the request before sending it to
    # the model.
    print(
        f"[wrap_model_call] "
        f"tools offered: {[t.name for t in request.tools]}"
    )
    response = handler(request)
    print("[wrap_model_call] model has replied")

    # Return the model response so the agent can continue.
    return response



# ---------------------------------------------------------
# AFTER MODEL
# ---------------------------------------------------------
#runs immediately after the model responds

@after_model
def show_after(state, runtime):

    # Get the latest message produced by the model.
    last = state["messages"][-1]

    # Check whether the model requested any tools.
    asked = [
        call["name"]
        for call in getattr(last, "tool_calls", []) or []
    ]

    print(
        f"[after_model] asked for: "
        f"{asked or 'nothing, this is the final answer'}"
    )

    # We are only observing here.
    return None



# ---------------------------------------------------------
# WRAP TOOL CALL
# ---------------------------------------------------------

# # This middleware sits AROUND every tool execution.

@wrap_tool_call
def show_tool(request, handler):

    # We can see which tool the agent is about to execute
    # and what arguments are being passed to it.
    print(
        f"[wrap_tool_call] "
        f"running {request.tool_call['name']} "
        f"with {request.tool_call['args']}"
    )

    # Continue the execution and actually run the tool.
    result = handler(request)

    # We are back after the tool has completed.
    print("[wrap_tool_call] tool finished")

    # Return the tool result so the agent can continue.
    return result



agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[order_status],
    system_prompt="You are a support agent.",
    middleware=[
        show_before,
        time_the_model,
        show_after,
        show_tool,
    ],

)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Where is my order ORD-1002?"}]
})
print()
print("Answer:", result["messages"][-1].content)


