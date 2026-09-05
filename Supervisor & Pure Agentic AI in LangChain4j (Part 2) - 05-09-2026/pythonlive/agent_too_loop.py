import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# create_agent is going to manage the tool-calling loop for us.
from langchain.agents import create_agent

from langchain_core.tools import tool


load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")
@tool
def current_time(city: str) -> str:
    """Get the current time in a city."""

    zones = {
        "mumbai": "Asia/Kolkata",
        "london": "Europe/London",
        "new york": "America/New_York"
    }

    zone = zones.get(city.lower())

    if zone is None:
        return f"I do not know the timezone for {city}."

    return datetime.now(
        ZoneInfo(zone)
    ).strftime("%d %B %Y, %I:%M %p")


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the exact result."""

    return a * b

#creating agent with required info for agent

agent = create_agent(
   model="openai:gpt-4o-mini", 
   tools=[
        current_time,
        multiply
   ],
   system_prompt=(
        "You are a helpful assistant. "
        "Use the tools when they fit." 
   ),

)

# asking that agent a question
result = agent.invoke({

    "messages": [
        {
            "role": "user",
            "content": (
                "What time is it in Mumbai, "
                "and what is 98765 times 43210?"
            )
        }
    ]
    

    }
)
print("Final Answer")
print(result["messages"][-1].content)


print()

print("What happened along the way:")

for message in result["messages"]:

    # Get the type of message.
    #
    # For example:
    #
    # HumanMessage
    # AIMessage
    # ToolMessage
    #
    kind = type(message).__name__
    if getattr(message, "tool_calls", None):

        # Yes!
        #
        # The LLM requested one or more tools.
        #
        # We print the names of those tools.

        print(
            f"  {kind}: asked for "
            f"{[c['name'] for c in message.tool_calls]}"
        )


    else:

        print(
            f"  {kind}: "
            f"{str(message.content)[:70]}"
        )