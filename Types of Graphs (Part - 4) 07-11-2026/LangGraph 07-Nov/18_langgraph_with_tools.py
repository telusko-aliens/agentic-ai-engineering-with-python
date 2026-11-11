from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    print(f'--- add_numbers called with {a}, {b} ---')
    return a + b

@tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f'--- multiply_numbers called with {a}, {b} ---')
    return a * b

tools = [add_numbers, multiply_numbers]
model_with_tools = model.bind_tools(tools)

class ChatState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages] = []

def call_model(state: ChatState):
    print('--- call_model started ---')
    response = model_with_tools.invoke(state.messages)
    print(response)
    return {'messages': [response]}

graph = StateGraph(ChatState)
graph.add_node('call_model', call_model)
graph.add_node('tools', ToolNode(tools))

graph.add_edge(START, 'call_model')
graph.add_conditional_edges('call_model', tools_condition)
graph.add_edge('tools', 'call_model')
graph.add_edge('call_model', END)

workflow = graph.compile()

final_state = workflow.invoke({'messages': [HumanMessage('Add 5 and 7 and if the sum is > 12 multiply the two numbers')]})
print(final_state['messages'][-1].content)

png = workflow.get_graph().draw_mermaid_png()
with open('18_langgraph_with_tools.png', 'wb') as f:
    f.write(png)