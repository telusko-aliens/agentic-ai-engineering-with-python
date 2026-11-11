from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# USING SUBGRAPH AS NODE

# ---------- stamp card subgraph ----------
class CardState(BaseModel):
    customer: str = ''
    card_message: str = ''
    # private field: the parent state does not have it
    stamps: int = 0

def add_stamp(state: CardState):
    stamps = state.stamps + 1
    return {'stamps': stamps, 'card_message': f'{stamps} stamps'}


card_graph = StateGraph(CardState)
card_graph.add_node('add_stamp', add_stamp)

card_graph.add_edge(START, 'add_stamp')
card_graph.add_edge('add_stamp', END)

# The parent graph is going to remember the values of child-subgraph's private fields as well
card_subgraph = card_graph.compile(checkpointer=True)

# ---------- parent graph ----------
class VisitState(BaseModel):
    customer: str = ''
    card_message: str = ''

graph = StateGraph(VisitState)
graph.add_node('stamp_card', card_subgraph)

graph.add_edge(START, 'stamp_card')
graph.add_edge('stamp_card', END)

workflow = graph.compile(checkpointer=InMemorySaver())

for customer in ['customer-1', 'customer-1', 'customer-1', 'customer-2', 'customer-1']:
    config = {'configurable': {'thread_id': customer}}
    result = workflow.invoke({'customer': customer}, config)
    print(f"{customer}: {result['card_message']}")
