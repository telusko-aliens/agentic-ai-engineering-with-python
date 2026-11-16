import operator
from typing import Annotated, Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

# ---------- state -------------
class OrderState(BaseModel):
    amount: int = 0
    notes: Annotated[list[str], operator.add] = []

# --------- sub graph ------------ 

def charge_card(state: OrderState) -> Command[Literal['send_receipt']]:
    print(f'--- subgraph: charge_card Rs {state.amount} ---')
    if state.amount <= 10000:
        return Command(update={'notes': ['payment done']}, goto='send_receipt')
    
    return Command(graph='other_subgraph', update={'notes': ['payment failed']}, goto='cancel_order')

def send_receipt(state: OrderState) -> Command:
    print('--- subgraph: send_receipt ---')
    return Command(graph=Command.PARENT, update={'notes': ['receipt sent']}, goto='ship_order')

payment_graph = StateGraph(OrderState)
payment_graph.add_node('charge_card', charge_card)
payment_graph.add_node('send_receipt', send_receipt)

payment_graph.add_edge(START, 'charge_card')

payment_subgraph = payment_graph.compile()

# --------- parent graph ------------ 
def ship_order(state: OrderState):
    print('--- parent: ship_order ---')
    return {'notes': ['order shipped']}

def cancel_order(state: OrderState):
    print('--- parent: cancel_order ---')
    return {'notes': ['order cancelled']}


graph = StateGraph(OrderState)
graph.add_node('payment', payment_subgraph, destinations=('ship_order', 'cancel_order'))
graph.add_node('ship_order', ship_order)
graph.add_node('cancel_order', cancel_order)

graph.add_edge(START, 'payment')
graph.add_edge('ship_order', END)
graph.add_edge('cancel_order', END)

workflow = graph.compile()

result = workflow.invoke({'amount': 50000})
print(f"notes: {result['notes']}\n")


# mermaid diagram
# xray=True also draws the nodes inside the subgraph
png = workflow.get_graph(xray=True).draw_mermaid_png()
with open('36_command_parent.png', 'wb') as f:
    f.write(png)
