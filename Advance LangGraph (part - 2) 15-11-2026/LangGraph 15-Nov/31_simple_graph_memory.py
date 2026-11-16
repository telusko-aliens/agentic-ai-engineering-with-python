import operator
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class CartState(BaseModel):
    item: str = ''
    cart: Annotated[list[str], operator.add] = []

def add_to_cart(state: CartState):
    return {'cart': [state.item]}

def show_cart(state: CartState):
    print(f'cart: {state.cart}')
    return {}

graph = StateGraph(CartState)
graph.add_node('add_to_cart', add_to_cart)
graph.add_node('show_cart', show_cart)

graph.add_edge(START, 'add_to_cart')
graph.add_edge('add_to_cart', 'show_cart')
graph.add_edge('show_cart', END)

workflow = graph.compile(checkpointer=InMemorySaver())

customer_1 = {'configurable': {'thread_id': 'customer-1'}}
data = {'item': 'milk'}
response = workflow.invoke(data, customer_1)
print(response)

data = {'item': 'bread'}
response = workflow.invoke(data, customer_1)
print(response)

customer_2 = {'configurable': {'thread_id': 'customer-2'}}
data = {'item': 'bread'}
response = workflow.invoke(data, customer_2)
response = workflow.invoke({'item': 'eggs'}, customer_2)
print(response)

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('31_simple_graph_memory.png', 'wb') as f:
    f.write(png)