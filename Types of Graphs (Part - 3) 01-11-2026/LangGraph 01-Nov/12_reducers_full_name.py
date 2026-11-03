import operator
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class NameState(BaseModel):
    name: Annotated[str, operator.add] = '' # reducer

def middle_name(state: NameState):
    return {'name': ' Kumar'}

def surname(state: NameState):
    return {'name': ' Agarwal'}

def first_name(state: NameState):
    return {'name': 'Akshay'}

graph = StateGraph(NameState)

graph.add_node('middle_name', middle_name)
graph.add_node('first_name', first_name)
graph.add_node('surname', surname)

graph.add_edge(START, 'middle_name')
graph.add_edge(START, 'first_name')
graph.add_edge(START, 'surname')
graph.add_edge('middle_name', END)
graph.add_edge('first_name', END)
graph.add_edge('surname', END)

workflow = graph.compile()
final_state = workflow.invoke({})
print(final_state['name'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('12_reducers_full_name.png', 'wb') as f:
    f.write(png)