import re
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMatch, PIIMiddleware, PIIDetectionError

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

def indian_phone(text: str) -> list[PIIMatch]:
    """Find 10 digit Indian mobile numbers, with or without the country code."""
    matches = []
    for found in re.finditer(r"(?:\+91[\s-]?)?[6-9]\d{9}", text):  # +91-88  , +91 88  
        matches.append(PIIMatch(type="phone", value=found.group(), start=found.start(), end=found.end()))
    return matches


agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[],
    system_prompt="You are a support agent. Confirm what the customer told you in one line.",
    middleware=[
        PIIMiddleware("email", strategy="redact"),
        PIIMiddleware("credit_card", strategy="mask"),
        PIIMiddleware("phone", detector=indian_phone, strategy="redact"),
    ],
)
message = (
    "Hi, I am Asha. Mail me at asha.k@example.com or call 9876543210. "
    "I paid with card 4111 1111 1111 1111."
)
result =agent.invoke(
    {
        "messages": [
    {
        "role": "user", 
        "content": message
        }
    ]
    })
print("What customer typed:")
print(" ", message)
print()

print("What the model received:")
print(" ", result["messages"][0].content)
print()

print("Answer:")
print(" ", result["messages"][-1].content)

print()
strict =create_agent(
    model="openai:gpt-4o-mini",
    tools=[],
    system_prompt="You are a support agent. Confirm what the customer told you in one line.",
    middleware=[
     
        PIIMiddleware("credit_card", strategy="block")

    ],
)
try:
    strict.invoke({"messages": [{"role": "user", "content": "my card is 4111 1111 1111 1111"}]})
except PIIDetectionError:
    print("Blocked, ask the customer never to send card numbers in chat.")
