from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# subgraph
class GradeState(BaseModel):
    marks: int = 0
    grade: str = ''

def calculate_grade(state: GradeState):
    print('--- subgraph: calculate_grade ---')
    return {'grade': 'Pass' if state.marks >= 40 else 'Fail'}

grade_graph = StateGraph(GradeState)
grade_graph.add_node('calculate_grade', calculate_grade)

grade_graph.add_edge(START, 'calculate_grade')
grade_graph.add_edge('calculate_grade', END)

grade_subgraph = grade_graph.compile()

# parent graph

class StudentState(BaseModel):
    student_marks: int = 0
    student_grade: str = ''

def get_grade(state: StudentState):
    print('--- parent: get_grade ---')
    result = grade_subgraph.invoke({'marks': state.student_marks})
    return {'student_grade': result['grade']}

graph = StateGraph(StudentState)
graph.add_node('get_grade', get_grade)

graph.add_edge(START, 'get_grade')
graph.add_edge('get_grade', END)

workflow = graph.compile()
final_state = workflow.invoke({'student_marks': 33})
print(final_state)

png = workflow.get_graph(xray=True).draw_mermaid_png()
with open('27_subgraph_invoke.png', 'wb') as f:
    f.write(png)