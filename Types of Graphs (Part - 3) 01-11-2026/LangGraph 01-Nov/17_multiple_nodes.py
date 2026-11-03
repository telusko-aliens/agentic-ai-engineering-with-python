from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class AskState(BaseModel):
    question: str
    decision: str = ''
    style: str = ''
    answer: str = ''

def confirm_question(state: AskState):
    print('--- confirm_question started ---')
    decision = interrupt(f'Send "{state.question}" to the model? (yes/no): ', response_schema=Literal['yes', 'no'])
    return {'decision': decision}

def choose_style(state: AskState):
    print('--- choose_style started ---')
    style = interrupt('Which answer style? (short/detailed): ', response_schema=Literal['short', 'detailed'])
    return {'style': style}

def generate_answer(state: AskState):
    print('--- generate_answer started ---')
    response = model.invoke(f'{state.question} Give a {state.style} answer.')
    return {'answer': response.content}

def cancel(state: AskState):
    print('--- cancel started ---')
    return {'answer': 'Cancelled by human.'}

def route_decision(state: AskState):
    if state.decision == 'yes':
        return 'choose_style'
    return 'cancel'

graph = StateGraph(AskState)
graph.add_node('confirm_question', confirm_question)
graph.add_node('choose_style', choose_style)
graph.add_node('generate_answer', generate_answer)
graph.add_node('cancel', cancel)

graph.add_edge(START, 'confirm_question')
graph.add_conditional_edges('confirm_question', route_decision, ['choose_style', 'cancel'])
graph.add_edge('choose_style', 'generate_answer')
graph.add_edge('generate_answer', END)
graph.add_edge('cancel', END)

workflow = graph.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': '1'}}

question = input('Ask anything: ')
result = workflow.invoke({'question': question}, config)

while '__interrupt__' in result:
    reply = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=reply), config)

print(result['answer'])

png = workflow.get_graph().draw_mermaid_png()
with open('17_multiple_nodes.png', 'wb') as f:
    f.write(png)
