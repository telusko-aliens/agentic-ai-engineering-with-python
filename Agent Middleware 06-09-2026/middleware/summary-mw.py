
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

load_dotenv()

# This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[],
    system_prompt="You are a support agent for an online store.",
    middleware=[
        SummarizationMiddleware(
            model="openai:gpt-4o-mini",
            trigger=("messages", 6),# trigger the sumamrization after 5 messages
            keep=("messages", 2)  # after summarizing keep latest 2 messsages and before older that summarise

        )
     
    ],
)
conversation = [
    "Hi, my name is Asha and my customer id is C-9087.",

    "I ordered a mechanical keyboard last week, order ORD-1002.",

    "My pin code is 560034, in Bengaluru.",

    "I also have an older order, ORD-1001, a wireless mouse.",

    "The keyboard is a gift, so the date matters to me.",

    "Tell me everything you remember about me and my orders.",
]

messages = []

for question in conversation:

    messages.append({"role": "user", "content": question})

    result = agent.invoke({"messages": messages})

    messages = result["messages"]

    print("Customer:", question)

    print(
        "Agent   :",
        result["messages"][-1].content[:160]
    )


    # how many messages currently remain in history
    print("\n========== COMPLETE MESSAGE LIST ==========")

    for i, message in enumerate(messages):

        print(f"\n[{i}] {type(message).__name__}")
        print("Content:", message.content)

    print("\n============================================")

    print(
        f"   history now holds {len(messages)} messages"
    )

    print("-" * 70)

