import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

model=ChatOpenAI(model="gpt-4o-mini")

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the exact result."""
    return a * b

@tool
def word_count(text: str) -> int:
    """Count how many words are in a piece of text."""
    return len(text.split())

model_with_tools=model.bind_tools([
    multiply,
    word_count
])

# response =model_with_tools.invoke("What is 98765 mulitplied by 43210?")
# print("content : ", repr(response.content))
# print("tool calls: ", response.tool_calls)

# chat = model_with_tools.invoke("give me one line on why Python is famous for AI")
# print("content : ", chat.content)
# print("tool calls: ", chat.tool_calls)


reply = model_with_tools.invoke(
    "How many words are in the sentence : "
    "LangChain makes agents simple"
)


# reply = model_with_tools.invoke(
#     "tell me in 1 line about ai "
# )
print(
    "content : ", reply.content
)
print("tool calls: ", reply.tool_calls)

if reply.tool_calls:
   tool_call = reply.tool_calls[0]
   print("REQUESTED TOOL:")
   print(tool_call["name"])

   print("TOOL ARGUMENTS:")
   print(tool_call["args"])

   tools = {
       "multiply": multiply,
       "word_count": word_count
   }

   selected_tool = tools[tool_call["name"]]

   tool_result = selected_tool.invoke(tool_call["args"])

   print("TOOL RESULT:")
   print(tool_result)
else:
    print("No TOOL was requested")
 

