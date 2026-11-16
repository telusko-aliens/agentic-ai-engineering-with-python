import operator
from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class CheckState(BaseModel):
    text: str = ''
    # every parallel node writes one key, and operator.or_ merges the dicts: {a: 1} | {b: 2} = {a: 1, b: 2}
    results: Annotated[dict[str, str], operator.or_] = {}
    report: str = ''

CHECKS = {
    'word_count': lambda text: f'{len(text.split())} words',
    'char_count': lambda text: f'{len(text)} characters',
    'has_numbers': lambda text: 'yes' if any(c.isdigit() for c in text) else 'no',
    'shouting': lambda text: 'yes' if any(word.isupper() and len(word) > 1 for word in text.split()) else 'no',
    'question': lambda text: 'yes' if '?' in text else 'no',
}

def make_check_node(check_name: str):
    check = CHECKS[check_name]

    # the node: writes only its own key, the reducer merges it with the other branches
    def node(state: CheckState):
        result = check(state.text)
        print(f'--- {check_name}: {result} ---')
        return {'results': {check_name: result}}

    return node

def report(state: CheckState):
    print('--- report ---')
    lines = [f'{name}: {value}' for name, value in sorted(state.results.items())]
    return {'report': '\n'.join(lines)}

def build_workflow(check_names: list[str]):
    graph = StateGraph(CheckState)

    graph.add_node('report', report)

    for check_name in check_names:
        graph.add_node(check_name, make_check_node(check_name))
        graph.add_edge(START, check_name)
        graph.add_edge(check_name, 'report')

    graph.add_edge('report', END)

    return graph.compile()

text = 'Is LangGraph FUN? I have built 44 graphs so far'

workflow_1 = build_workflow(['word_count', 'question', 'char_count', 'shouting'])
result = workflow_1.invoke({'text': text})
print(f"report:\n{result['report']}\n")


with open('41_parallel_nodes_workflow_1.png', 'wb') as f:
    f.write(workflow_1.get_graph().draw_mermaid_png())
