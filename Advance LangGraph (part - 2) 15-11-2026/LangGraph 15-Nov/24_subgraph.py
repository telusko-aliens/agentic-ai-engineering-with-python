from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# Subgraph
class PaymentState(BaseModel):
    amount: int = 0
    payment_status: str = ''
    # private field
    total_with_fee: int = 0

def add_fee(state: PaymentState):
    print('--- payment subgraph: add_fee ---')
    return {'total_with_fee': state.amount + 20}

def charge_payment(state: PaymentState):
    print('--- payment subgraph: charge_payment ---')
    return {'payment_status': f'Paid Rs {state.total_with_fee}'}

payment_graph = StateGraph(PaymentState)
payment_graph.add_node('add_fee', add_fee)
payment_graph.add_node('charge_payment', charge_payment)

payment_graph.add_edge(START, 'add_fee')
payment_graph.add_edge('add_fee', 'charge_payment')
payment_graph.add_edge('charge_payment', END)

payment_subgraph = payment_graph.compile()

# Parent Graph 1 - OrderState
class OrderState(BaseModel):
    amount: int = 0
    payment_status: str = ''
    delivery_message: str = ''

def ship_order(state: OrderState):
    print('--- order parent: ship_order ---')
    return {'delivery_message': f'{state.payment_status}, order shipped'}

order_graph = StateGraph(OrderState)
order_graph.add_node('payment', payment_subgraph)
order_graph.add_node('ship_order', ship_order)


order_graph.add_edge(START, 'payment')
order_graph.add_edge('payment', 'ship_order')
order_graph.add_edge('ship_order', END)

order_workflow = order_graph.compile()
order_result = order_workflow.invoke({'amount': 100, 'money': 10})
print(order_result)

png = order_workflow.get_graph(xray=True).draw_mermaid_png()
with open('24_order_subgraph.png', 'wb') as f:
    f.write(png)