import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.agents.middleware.types import AgentMiddleware, AgentState
from langchain_core.tools import tool

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

# {
#    "messages": [....]
#     "tool_uses": 1
#     "refund_started": True
# }

class SupportState(AgentState):
    """The usual messages, plus two keys of our own."""

    tool_uses: int  # how many tools calls have happened so far
    refund_started: bool  # True once start_refund has been called

@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""
    return f"{order_id.upper()}: packed, ships tomorrow"



@tool
def delivery_estimate(pin_code: str) -> str:
    """Estimate delivery days for an Indian pin code."""
    return "5 days"


@tool
def start_refund(order_id: str, reason: str) -> str:
    """Start a refund for an order."""
    return f"Refund started for {order_id.upper()}, reason: {reason}"

#Middleware

class TrackWork(AgentMiddleware):
    """Counts tool calls and notices when a refund has been started."""

    state_schema = SupportState  # tell langchain that my state is like SupportState 

    # model after -->  tool execution

    def after_model(self, state, runtime):
        last = state["messages"][-1]
        calls = getattr(last, "tool_calls", []) or []
        if not calls:
            return None

        update = {"tool_uses": state.get("tool_uses", 0) + len(calls)}
        if any(call["name"] == "start_refund" for call in calls):
            update["refund_started"] = True

        print(f"   [state] tool_uses={update['tool_uses']} refund_started={update.get('refund_started', state.get('refund_started', False))}")
        return update

@dynamic_prompt
def prompt_with_budget(request):
    used = request.state.get("tool_uses", 0)

    prompt = "You are a support agent. Look things up with the tools, never guess."
    if used >= 3:
        prompt += " You have already used three tools, answer now with what you have."
    return prompt

agent = create_agent(
    model="gpt-4o-mini",
    tools=[order_status, delivery_estimate, start_refund],
    middleware=[TrackWork(), prompt_with_budget],
   
)

result = agent.invoke(
    {
    "messages": [{
        "role": "user",
        "content": "Where is ORD-1002, when does it reach pin 560034, and refund it because it is too late.",
    }],
    "tool_uses": 0,
    "refund_started": False,
}

)
print()
print("Answer:", result["messages"][-1].content)
print()
print("tool_uses      :", result["tool_uses"])
print("refund_started :", result["refund_started"])
if result["refund_started"]:
    print("Refund has been started,notify the finance team and support team")



