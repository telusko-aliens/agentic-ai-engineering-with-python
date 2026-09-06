import sys
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

@tool
def book_seat(name: str, seat: str) -> str:
    """Book a seat in the class for a person."""
    return f"Seat {seat} booked for {name}."

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[book_seat],
    system_prompt="You help learners book a seat in the LangChain class.",
    checkpointer=InMemorySaver(),  # this tell agent to store conversation after each step
)

def ask(question, thread_id):
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    print(f"[{thread_id}] Q: {question}")
    print(f"[{thread_id}] A: {result['messages'][-1].content}")
    print()
ask("My name is vinay kumar gurram", thread_id="vinay")


ask("Book me a seat A12.", thread_id="vinay")

ask("What is my name and what seat did i book", thread_id="vinay")

ask("What is my name and what seat did i book", thread_id="nimish")

