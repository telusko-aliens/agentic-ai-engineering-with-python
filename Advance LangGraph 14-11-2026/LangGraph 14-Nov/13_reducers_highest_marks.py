from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# custom reducer function
def keep_highest(current: int, new: int) -> int:
    print(f'--current: {current} | --new: {new}')
    return max(current, new)

class MarksState(BaseModel):
    highest_marks: Annotated[int, keep_highest]

def maths_marks(state: MarksState):
    print('--maths_marks called--')
    return {'highest_marks': 98}

def science_marks(state: MarksState):
    print('--science_marks called--')
    return {'highest_marks': 97}

def english_marks(state: MarksState):
    print('--english_marks called--')
    return {'highest_marks': 99}

graph = StateGraph(MarksState)
graph.add_node('maths_marks', maths_marks)
graph.add_node('science_marks', science_marks)
graph.add_node('english_marks', english_marks)

graph.add_edge(START, 'maths_marks')
graph.add_edge(START, 'science_marks')
graph.add_edge(START, 'english_marks')

workflow = graph.compile()
final_state = workflow.invoke({})
print(final_state['highest_marks'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('13_reducers_highest_marks.png', 'wb') as f:
    f.write(png)