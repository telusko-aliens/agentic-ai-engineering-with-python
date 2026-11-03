from typing import Annotated, Literal
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    print(f'--- add_numbers called with {a}, {b} ---')
    return a + b

@tool
def send_email(to: str, message: str) -> str:
    """Send an email to someone."""
    print('--- send_email started ---')
    decision = interrupt(f'Send email to {to} saying "{message}"? (yes/no): ', response_schema=Literal['yes', 'no'])
    if decision != 'yes':
        return 'The human cancelled this email.'
    print(f'--- email sent to {to} ---')
    return f'Email sent to {to}.'

tools = [add_numbers, send_email]
model_with_tools = model.bind_tools(tools, parallel_tool_calls=False)

class ChatState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages] = []

def call_model(state: ChatState):
    print('--- call_model started ---')
    response = model_with_tools.invoke(state.messages)
    return {'messages': [response]}

def say_hi(state: ChatState):
    print('--- say_hi started ---')
    return {'messages': [HumanMessage('This is sparta')]}

graph = StateGraph(ChatState)
graph.add_node('call_model', call_model)
graph.add_node('say_hi', say_hi)
graph.add_node('tools', ToolNode(tools))

graph.add_edge(START, 'call_model')
graph.add_conditional_edges(
    'call_model',
    tools_condition,
    {'tools': 'tools', '__end__': 'say_hi'},
)
graph.add_edge('tools', 'call_model')

workflow = graph.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': '1'}}

question = 'Add 12 and 8, then email the result to rahul@example.com.'
result = workflow.invoke({'messages': [HumanMessage(question)]}, config)

while '__interrupt__' in result:
    reply = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=reply), config)

print(result['messages'][-1].content)

png = workflow.get_graph().draw_mermaid_png()
with open('19_tools_hitl.png', 'wb') as f:
    f.write(png)