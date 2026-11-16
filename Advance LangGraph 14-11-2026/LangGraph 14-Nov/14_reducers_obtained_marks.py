from typing import Annotated
import operator
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

def add_obtained_marks(total: int, marks: int) -> int:
    return total + marks


class MarksState(BaseModel):
    total_marks: Annotated[int, operator.add]
    total_obtained_marks: Annotated[int, add_obtained_marks]

    @property
    def percentage(self) -> float:
        return self.total_obtained_marks / self.total_marks * 100

def maths_marks(state: MarksState):
    return {'total_marks': 100, 'total_obtained_marks': 85}

def science_marks(state: MarksState):
    return {'total_marks': 100, 'total_obtained_marks': 90}

def english_marks(state: MarksState):
    return {'total_marks': 50, 'total_obtained_marks': 39}

graph = StateGraph(MarksState)
graph.add_node('maths_marks', maths_marks)
graph.add_node('science_marks', science_marks)
graph.add_node('english_marks', english_marks)

graph.add_edge(START, 'maths_marks')
graph.add_edge(START, 'science_marks')
graph.add_edge(START, 'english_marks')

workflow = graph.compile()
final_state = workflow.invoke({})

print(f"Total marks: {final_state['total_marks']}")
print(f"Total obtained marks: {final_state['total_obtained_marks']}")

marks = MarksState(**final_state)
print(f'Percentage: {marks.percentage}')


# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('14_reducers_obtained_marks.png', 'wb') as f:
    f.write(png)

# Create a new node to calculate percentage.
# 