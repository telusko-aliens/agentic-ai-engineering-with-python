from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class TextState(BaseModel):
    text: str = ''

CLEANING_STEPS = {
    'strip_spaces': lambda text: text.strip(),
    'lowercase': lambda text: text.lower(),
    'remove_dots': lambda text: text.replace('.', ''),
    'single_spaces': lambda text: ' '.join(text.split()),
}

def make_node(step_name: str):
    clean = CLEANING_STEPS[step_name]

    def node(state: TextState):
        new_text = clean(state.text)
        print(f'--- {step_name}: {new_text!r} ---')
        return {'text': new_text}

    return node

def build_workflow(step_names: list[str]):
    graph = StateGraph(TextState)

    for step_name in step_names:
        graph.add_node(step_name, make_node(step_name))

    previous = START
    for step_name in step_names:
        graph.add_edge(previous, step_name)
        previous = step_name
    graph.add_edge(previous, END)

    return graph.compile()

text = '   Hello.   LangGraph   IS   Fun.  '

workflow_1 = build_workflow(['strip_spaces', 'lowercase'])
result = workflow_1.invoke({'text': text})
print(f"result: {result['text']!r}\n")

with open('40_workflow_1.png', 'wb') as f:
    f.write(workflow_1.get_graph().draw_mermaid_png())


workflow_2 = build_workflow(['remove_dots', 'single_spaces', 'lowercase', 'strip_spaces'])
result = workflow_2.invoke({'text': text})
print(f"result: {result['text']!r}")

with open('40_workflow_2.png', 'wb') as f:
    f.write(workflow_2.get_graph().draw_mermaid_png())

