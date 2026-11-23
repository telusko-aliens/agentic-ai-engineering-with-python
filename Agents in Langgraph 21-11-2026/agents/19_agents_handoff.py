from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')


class State(MessagesState):
    active_agent: str = 'triage_agent'  # which agent is talking to the customer right now

@tool
def transfer_to_billing(runtime: ToolRuntime) -> Command:
    """Transfer the customer to the billing team (payments, invoices, refunds)."""
    print('  >>> handoff -> billing_agent')
    tool_message = ToolMessage(content='Transferred to billing_agent. billing_agent: you now own this chat, help the customer.', tool_call_id=runtime.tool_call_id)
    return Command(
        goto='billing_agent',
        graph=Command.PARENT,
        update={'messages': runtime.state['messages'] + [tool_message], 'active_agent': 'billing_agent'},
    )

@tool
def transfer_to_tech(runtime: ToolRuntime) -> Command:
    """Transfer the customer to the tech support team (internet, router, speed problems)."""
    print('  >>> handoff -> tech_agent')
    tool_message = ToolMessage('Transferred to tech_agent. tech_agent: you now own this chat, help the customer.', tool_call_id=runtime.tool_call_id)
    return Command(
        goto='tech_agent',
        graph=Command.PARENT,
        update={'messages': runtime.state['messages'] + [tool_message], 'active_agent': 'tech_agent'},
    )

@tool
def get_bill(customer_id: str) -> str:
    """Get this month's bill for a customer."""
    print(f'      --- get_bill({customer_id}) ---')
    return 'Plan ₹799 charged on 2 Nov, ₹799 charged again on 3 Nov (duplicate).'

@tool
def refund(customer_id: str, amount: int) -> str:
    """Refund an amount (in ₹) to a customer."""
    print(f'      --- refund({customer_id}, {amount}) ---')
    return f'Refund of ₹{amount} started for {customer_id}. It will reach in 3-5 days.'

@tool
def check_connection(customer_id: str) -> str:
    """Check the internet connection status for a customer."""
    print(f'      --- check_connection({customer_id}) ---')
    return 'Line OK. Router not restarted for 41 days. Speed 8 Mbps on a 100 Mbps plan.'

@tool
def restart_router(customer_id: str) -> str:
    """Restart the customer's router remotely."""
    print(f'      --- restart_router({customer_id}) ---')
    return 'Router restarted. Speed now 96 Mbps.'

triage_agent = create_agent(
    model=model,
    name='triage_agent',      # the name is put on its messages, so agents know who said what
    tools=[transfer_to_billing, transfer_to_tech],
    system_prompt=(
        'You are the reception desk of an internet company. '
        'Transfer billing questions to billing and internet problems to tech.'
    ),
)

billing_agent = create_agent(
    model=model,
    name='billing_agent',
    tools=[get_bill, refund, transfer_to_tech],
    system_prompt=(
        'You are the billing team of an internet company. Help with bills and refunds. '
        'Ask before giving a refund. If the customer has an internet problem, transfer to tech. Keep answers short.'
    ),
)

tech_agent = create_agent(
    model=model,
    name='tech_agent',
    tools=[check_connection, restart_router, transfer_to_billing],
    system_prompt=(
        'You are the tech support team of an internet company. Fix internet problems. '
        'If the customer has a billing question, transfer to billing. Keep answers short.'
    ),
)

def route_to_active_agent(state: State):
    return state.get('active_agent', 'triage_agent')

builder = StateGraph(State)
builder.add_node('triage_agent', triage_agent, destinations=('billing_agent', 'tech_agent'))
builder.add_node('billing_agent', billing_agent, destinations=('tech_agent',))
builder.add_node('tech_agent', tech_agent, destinations=('billing_agent',))

builder.add_conditional_edges(START, route_to_active_agent, ['triage_agent', 'billing_agent', 'tech_agent'])

builder.add_edge('triage_agent', END)
builder.add_edge('billing_agent', END)
builder.add_edge('tech_agent', END)

graph = builder.compile(checkpointer=InMemorySaver())   # memory: remembers messages + active_agent

config = {'configurable': {'thread_id': 'customer-C101'}}

print('\ncustomer: What is the current weather in Tokyo?')
result = graph.invoke({'messages': [('user', 'What is the current bill amount? customer-C101')]}, config)
#print(f"[{result['active_agent']}] {result['messages'][-1].content}")
print(f"[{result.get('active_agent', 'triage_agent')}] {result['messages'][-1].content}")

with open('19_handoffs.png', 'wb') as f:
    f.write(graph.get_graph().draw_mermaid_png())
