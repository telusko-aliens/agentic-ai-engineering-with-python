from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Data Provider Application
# mb which is consumer per month and per session
# for monthly, we need add all the session usage mb
# for every session, it should start counting from 0

class MonthlyState(BaseModel):
    mb: int = 0
    report: str = ''
    # private field: never sent back to the parent
    total_mb: int = 0

def add_to_month(state: MonthlyState):
    total_mb = state.total_mb + state.mb
    return {
        'total_mb': total_mb,
        'report': f'{total_mb} MB this month'
    }

monthly_graph = StateGraph(MonthlyState)
monthly_graph.add_node('add_to_month', add_to_month)

monthly_graph.add_edge(START, 'add_to_month')
monthly_graph.add_edge('add_to_month', END)
monthly_subgraph = monthly_graph.compile(checkpointer=True)

class SessionState(BaseModel):
    mb: int = 0
    report: str = ''
    # private field: never sent back to the parent
    session_mb: int = 0

def add_to_session(state: SessionState):
    session_mb = state.session_mb + state.mb
    return {
        'session_mb': session_mb,
        'report': f'{session_mb} MB this session'
    }

session_graph = StateGraph(SessionState)
session_graph.add_node('add_to_session', add_to_session)
session_graph.add_edge(START, 'add_to_session')
session_graph.add_edge('add_to_session', END)
session_subgraph = session_graph.compile()

class PhoneState(BaseModel):
    used_mb: int = 0
    monthly_report: str = ''
    session_report: str = ''


def check_month(state: PhoneState):
    result = monthly_subgraph.invoke({'mb': state.used_mb})
    return {'monthly_report': result['report']}

def check_session(state: PhoneState):
    result = session_subgraph.invoke({'mb': state.used_mb})
    return {'session_report': result['report']}

graph = StateGraph(PhoneState)
graph.add_node('check_month', check_month)
graph.add_node('check_session', check_session)

graph.add_edge(START, 'check_month')
graph.add_edge('check_month', 'check_session')
graph.add_edge('check_session', END)

workflow = graph.compile(checkpointer=InMemorySaver())

phone_1 = {'configurable': {'thread_id': 'phone-1'}}
phone_2 = {'configurable': {'thread_id': 'phone-2'}}

result = workflow.invoke({'used_mb': 200}, phone_1)
print(f"phone-1: {result['monthly_report']} | {result['session_report']}")

result = workflow.invoke({'used_mb': 300}, phone_1)
print(f"phone-1: {result['monthly_report']} | {result['session_report']}")

result = workflow.invoke({'used_mb': 300}, phone_1)
print(f"phone-2: {result['monthly_report']} | {result['session_report']}")
