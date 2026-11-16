import operator
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# ---------- parent state ----------

class ClassState(BaseModel):
    papers: dict[str, int] = {}
    # reducer: every grade_paper run adds one line, and operator.add joins them all
    grades: Annotated[list[str], operator.add] = []
    report: str = ''

# ---------- state of one Send ----------
class PaperState(BaseModel):
    name: str = ''
    marks: int = 0

def send_papers(state: ClassState):
    print(f'--- send_papers: {len(state.papers)} papers ---')
    return [Send('grade_paper', PaperState(name=name, marks=marks)) for name, marks in state.papers.items()]

def grade_paper(state: PaperState):
    print(f'--- grade_paper: {state.name} ---')
    grade = 'Pass' if state.marks >= 40 else 'Fail'
    return {'grades': [f'{state.name}: {grade}']}

def make_report(state: ClassState):
    print('--- make_report ---')
    passed = sum(1 for grade in state.grades if grade.endswith('Pass'))
    return {'report': f'{passed} of {len(state.grades)} passed'}

graph = StateGraph(ClassState)
graph.add_node('grade_paper', grade_paper)
graph.add_node('make_report', make_report)

graph.add_conditional_edges(START, send_papers, ['grade_paper'])
graph.add_edge('grade_paper', 'make_report')
graph.add_edge('make_report', END)

workflow = graph.compile()

papers = {
    'Maths': 75,
    'English': 35,
    'Chemistry': 60,
    'History': 90,
    'Hindi': 10
}

result = workflow.invoke({'papers': papers})
print(f"grades: {result['grades']}")
print(f"report: {result['report']}\n")

png = workflow.get_graph().draw_mermaid_png()
with open('38_send_map_reduce.png', 'wb') as f:
    f.write(png)
