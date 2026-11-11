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

# Parent Graph

class TicketState(BaseModel):
    seats: int = 0
    amount: int = 0
    payment_status: str = ''
    ticket_message: str = ''

def calculate_price(state: TicketState):
    print('--- ticket parent: calculate_price ---')
    return {'amount': state.seats * state.amount}

def send_ticket(state: TicketState):
    print('--- ticket parent: send_ticket ---')
    return {'ticket_message': f'{state.payment_status}, {state.seats} seats booked'}

ticket_graph = StateGraph(TicketState)
ticket_graph.add_node('calculate_price', calculate_price)
ticket_graph.add_node('payment', payment_subgraph)
ticket_graph.add_node('send_ticket', send_ticket)

ticket_graph.add_edge(START, 'calculate_price')
ticket_graph.add_edge('calculate_price', 'payment')
ticket_graph.add_edge('payment', 'send_ticket')
ticket_graph.add_edge('send_ticket', END)

ticket_workflow = ticket_graph.compile()
ticket_result = ticket_workflow.invoke({'seats': 4, 'amount': 2000})

print(ticket_result)

png = ticket_workflow.get_graph(xray=True).draw_mermaid_png()
with open('25_subgraph_ticket.png', 'wb') as f:
    f.write(png)