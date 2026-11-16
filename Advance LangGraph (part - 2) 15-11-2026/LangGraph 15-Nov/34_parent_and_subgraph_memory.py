import operator
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class RewardsState(BaseModel):
    nights: int = 0
    reward_message: str = ''
    # private field: the parent state does not have it
    points: int = 0

def add_points(state: RewardsState):
    points = state.points + state.nights * 100
    return {'points': points, 'reward_message': f'{points} points'}

rewards_graph = StateGraph(RewardsState)
rewards_graph.add_node('add_points', add_points)

rewards_graph.add_edge(START, 'add_points')
rewards_graph.add_edge('add_points', END)
rewards_subgraph = rewards_graph.compile(checkpointer=True)

class StayState(BaseModel):
    # shared fields: the same names in both states, so they pass to the subgraph and back
    nights: int = 0
    reward_message: str = ''
    # parent-only fields
    city: str = ''
    # operator.add: parent memory, so each new city is added to the saved list
    cities: Annotated[list[str], operator.add] = []

def check_in(state: StayState):
    return {'cities': [state.city]}

graph = StateGraph(StayState)
graph.add_node('check_in', check_in)
graph.add_node('rewards', rewards_subgraph)

graph.add_edge(START, 'check_in')
graph.add_edge('check_in', 'rewards')
graph.add_edge('rewards', END)

workflow = graph.compile(checkpointer=InMemorySaver())

guest_1 = {'configurable': {'thread_id': 'guest-1'}}
guest_2 = {'configurable': {'thread_id': 'guest-2'}}

result = workflow.invoke({'city': 'Goa', 'nights': 2}, guest_1)
print(f"guest-1: cities {result['cities']} | {result['reward_message']}")

result = workflow.invoke({'city': 'Delhi', 'nights': 3}, guest_1)
print(f"guest-1: cities {result['cities']} | {result['reward_message']}")

result = workflow.invoke({'city': 'Jaipur', 'nights': 1}, guest_2)
print(f"guest-2: cities {result['cities']} | {result['reward_message']}")


print(f"guest-1: {workflow.get_state(guest_1).values}")
print(f"guest-2: {workflow.get_state(guest_2).values}")

namespaces = set()
for checkpoint in workflow.checkpointer.list(None):
    thread_id = checkpoint.config['configurable']['thread_id']
    checkpoint_ns = checkpoint.config['configurable']['checkpoint_ns'] #namespace
    namespaces.add((thread_id, checkpoint_ns))

for thread_id, checkpoint_ns in sorted(namespaces):
    print(f"thread_id: {thread_id} | checkpoint_ns: '{checkpoint_ns}'")

rewards_guest_1 = {'configurable': {'thread_id': 'guest-1', 'checkpoint_ns': 'rewards'}}
print(f"rewards_guest_1: {workflow.get_state(rewards_guest_1).values}")

rewards_guest_2 = {'configurable': {'thread_id': 'guest-2', 'checkpoint_ns': 'rewards'}}
print(f"rewards_guest_2: {workflow.get_state(rewards_guest_2).values}")
