from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command

class LeaveState(BaseModel):
    days: int = 0
    decision: str = ''

def ask_manager(state: LeaveState):
    print('--- ask_manager started ---')
    decision = interrupt(f'Approve {state.days} days of leave? (yes/no): ')
    return {'decision': decision}

def notify_employee(state: LeaveState):
    print(f'--- notify_employee: manager replied {state.decision} ---')
    return {}

graph = StateGraph(LeaveState)
graph.add_node('ask_manager', ask_manager)
graph.add_node('notify_employee', notify_employee)

graph.add_edge(START, 'ask_manager')
graph.add_edge('ask_manager', 'notify_employee')
graph.add_edge('notify_employee', END)

config = {'configurable': {'thread_id': 'leave-1'}}

# this is going to save the things
with SqliteSaver.from_conn_string('20_hitl_checkpoints.db') as checkpointer:
    workflow = graph.compile(checkpointer=checkpointer)
    workflow.invoke({'days': 3}, config)
    print('Paused and saved to the file')

with SqliteSaver.from_conn_string('20_hitl_checkpoints.db') as checkpointer:
    workflow = graph.compile(checkpointer=checkpointer)
    response = workflow.get_state(config)
    print(response)
    question = workflow.get_state(config).tasks[0].interrupts[0].value
    reply = input(question)
    workflow.invoke(Command(resume=reply), config)

png = workflow.get_graph().draw_mermaid_png()
with open('20_hitl_checkpoints.png', 'wb') as f:
    f.write(png)