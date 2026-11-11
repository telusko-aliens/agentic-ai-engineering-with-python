from typing import Annotated
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
def issue_refund(order_id: str, amount: int) -> str:
    """Refund an order. A human reviews it first."""
    print('--- issue_refund started ---')
    reply = interrupt(f'Refund Rs {amount} for {order_id}? Type yes, no, or a new amount: ')

    if reply.isdigit():
        amount = int(reply)
    # reject: anything other than yes or a number means no money moves
    elif reply != 'yes':
        return f'The human rejected the refund for {order_id}.'

    print(f'--- Rs {amount} refunded for {order_id} ---')
    return f'Refund of Rs {amount} issued for {order_id}.'

tools = [issue_refund]
model_with_tools = model.bind_tools(tools)

class ChatState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages] = []

def call_model(state: ChatState):
    print('--- call_model started ---')
    response = model_with_tools.invoke(state.messages)
    return {'messages': [response]}

graph = StateGraph(ChatState)
graph.add_node('call_model', call_model)
graph.add_node('tools', ToolNode(tools))

graph.add_edge(START, 'call_model')
graph.add_conditional_edges('call_model', tools_condition)
graph.add_edge('tools', 'call_model')

workflow = graph.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': 'refund-1'}}

question = 'Refund Rs 2500 for order ORD-1001, then confirm the final amount.'

result = workflow.invoke({'messages': [HumanMessage(question)]}, config)

while '__interrupt__' in result:
    reply = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=reply), config)

print(result['messages'][-1].content)

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('23_hitl_tools.png', 'wb') as f:
    f.write(png)
