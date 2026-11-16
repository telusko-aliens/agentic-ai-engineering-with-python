from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class PostState(BaseModel):
    title: str = ''
    version: int = 1
    status: str = ''

def editor_review(state: PostState) -> Command[Literal['publish', 'rewrite', '__end__']]:
    print(f'--- editor_review: version {state.version} ---')

    reply = interrupt(f"'{state.title}' version {state.version}: publish / changes / reject? ")

    if reply == 'publish':
        return Command(goto='publish')
    if reply == 'changes':
        return Command(goto='rewrite')
    return Command(update={'status': 'rejected'}, goto=END)

def rewrite(state: PostState):
    print('--- rewrite ---')
    return {'version': state.version + 1}

def publish(state: PostState):
    print('--- publish ---')
    return {'status': f'published version {state.version}'}

graph = StateGraph(PostState)
graph.add_node('editor_review', editor_review)
graph.add_node('rewrite', rewrite)
graph.add_node('publish', publish)

graph.add_edge(START, 'editor_review')
graph.add_edge('rewrite', 'editor_review')
graph.add_edge('publish', END)

workflow = graph.compile(checkpointer=InMemorySaver())

post_1 = {'configurable': {'thread_id': 'post-1'}}

result = workflow.invoke({'title': 'Learning LangGraph'}, post_1)

while '__interrupt__' in result:
    reply = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=reply), post_1)

print(f"status: {result['status']}")

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('37_command_goto_resume.png', 'wb') as f:
    f.write(png)