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

with SqliteSaver.from_conn_string('21_hitl_saved_interrupted_checkpoint.db') as checkpointer:
    workflow = graph.compile(checkpointer=checkpointer)

    saved_state = workflow.get_state(config)

    print(saved_state)

    if saved_state.next:
        # this means we are resuming the program from last interrupt
        question = workflow.get_state(config).tasks[0].interrupts[0].value
        reply = input(question)
        workflow.invoke(Command(resume=reply), config)
    else:
        # we are running this program for the first time, and there is no interrupt
        days = input('How many leave do you want (days)?')
        workflow.invoke({'days': days}, config)
        print('Paused and saved to the file')

png = workflow.get_graph().draw_mermaid_png()
with open('21_hitl_saved_interrupted_checkpoints.png', 'wb') as f:
    f.write(png)