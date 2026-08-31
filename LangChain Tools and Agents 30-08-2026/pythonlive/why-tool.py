import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

print("Q1: What is the time right now in Mumbai")

print(model.invoke("What is the time right now in Mumbai").content)
print("-" * 60)

print("Q2: What is 98765 multiplied by 43210?")
print(model.invoke("What is 98765 multiplied by 43210?").content)

print("The python calc :",98765 * 43210 )
