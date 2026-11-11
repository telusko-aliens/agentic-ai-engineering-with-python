from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

# ---------- approval subgraph ----------
class ApprovalState(BaseModel):
    amount: int = 0
    decision: str = ''


def ask_manager(state: ApprovalState):
    print('--- subgraph: ask_manager started ---')
    decision = interrupt(f'Approve the expense of Rs {state.amount}? (yes/no): ')
    return {'decision': decision}


approval_graph = StateGraph(ApprovalState)
approval_graph.add_node('ask_manager', ask_manager)

approval_graph.add_edge(START, 'ask_manager')
approval_graph.add_edge('ask_manager', END)

approval_subgraph = approval_graph.compile()

# ---------- parent graph ----------
class ExpenseState(BaseModel):
    claim_amount: int = 0
    manager_decision: str = ''
    message: str = ''


def process_expense(state: ExpenseState):
    print('--- parent: process_expense started ---')
    result = approval_subgraph.invoke({'amount': state.claim_amount})
    return {'manager_decision': result['decision']}

def notify_employee(state: ExpenseState):
    print('--- parent: notify_employee ---')
    if state.manager_decision == 'yes':
        return {'message': f'Your expense of Rs {state.claim_amount} is approved'}
    return {'message': f'Your expense of Rs {state.claim_amount} is rejected'}


graph = StateGraph(ExpenseState)
graph.add_node('process_expense', process_expense)
graph.add_node('notify_employee', notify_employee)

graph.add_edge(START, 'process_expense')
graph.add_edge('process_expense', 'notify_employee')
graph.add_edge('notify_employee', END)

workflow = graph.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': 'expense-1'}}

result = workflow.invoke({'claim_amount': 5000}, config)

while '__interrupt__' in result:
    reply = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=reply), config)

print(result['message'])


png = workflow.get_graph().draw_mermaid_png()
with open('29_subgraph_with_hitl.png', 'wb') as f:
    f.write(png)
