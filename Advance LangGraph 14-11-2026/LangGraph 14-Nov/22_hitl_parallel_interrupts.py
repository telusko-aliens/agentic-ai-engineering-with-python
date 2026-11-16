from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class PurchaseState(BaseModel):
    manager_reply: str = ''
    finance_reply: str = ''
    result: str = ''

def ask_manager(state: PurchaseState):
    print('--- ask_manager started ---')
    return {'manager_reply': interrupt('Manager, approve this purchase? (yes/no): ')}

def ask_finance(state: PurchaseState):
    print('--- ask_finance started ---')
    return {'finance_reply': interrupt('Finance, approve this purchase? (yes/no): ')}

def decide(state: PurchaseState):
    print('--- decide started ---')
    if state.manager_reply == 'yes' and state.finance_reply == 'yes':
        return {'result': 'Purchase approved'}
    return {'result': 'Purchase rejected'}

graph = StateGraph(PurchaseState)
graph.add_node('ask_manager', ask_manager)
graph.add_node('ask_finance', ask_finance)
graph.add_node('decide', decide)

graph.add_edge(START, 'ask_manager')
graph.add_edge(START, 'ask_finance')
graph.add_edge('ask_manager', 'decide')
graph.add_edge('ask_finance', 'decide')
graph.add_edge('decide', END)

workflow = graph.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': 'purchase-1'}}

result = workflow.invoke({}, config)

replies = {}
pending = result['__interrupt__']
for item in pending:
    replies[item.id] = input(item.value)

result = workflow.invoke(Command(resume=replies), config)
print(result['result'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('22_hitl_parallel_interrupts.png', 'wb') as f:
    f.write(png)