import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain_core.tools import tool

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

@dataclass
class Customer:
    """What we know about the person asking, before the model sees anything."""

    name: str
    plan: str
    language: str


@tool
def order_status(order_id: str) -> str:
    """Get the status of an order using its id."""

    return f"{order_id.upper()}: packed, ships tomorrow"

@dynamic_prompt  # moddleware hook# before the model --> create or chnage the system prompt
def support_prompt(request):

    # this will give us that Customer object we passed in when we called agent.invoke()
    # Customer(
    #     name="Alice",
    #     plan="premium",
    #     language="English",
    # )
    customer = request.runtime.context

    lines = [
        f"You are a support agent for an online store. The customer is {customer.name}.",
        "Look up the order before answering, never guess.",
        "Write like a chat reply, no email signature.",
    ]

    if customer.plan == "premium":
        lines.append("This is a premium customer, apologise for any delay and offer a callback.")
    else:
        lines.append("This is a free plan customer, keep the answer to two lines.")

    lines.append(f"Reply in {customer.language}.")

    prompt = " ".join(lines)
    print("[prompt used]", prompt)
    print()
    return prompt

agent = create_agent(
    model="gpt-4o-mini",

    tools=[order_status],
    middleware=[support_prompt],
    context_schema=Customer,
)

question = {
    "messages": [
        {
            "role": "user",
            "content": "Where is my order ORD-1002?"
        }
    ]
}
for customer in [
    Customer(name="Asha", plan="premium", language="English"),
    Customer(name="Ramesh", plan="free", language="Hindi"),
]:


    result = agent.invoke(question, context=customer)
    print(f"To {customer.name} ({customer.plan}):")
    print(result["messages"][-1].content)

