from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from typing import Literal

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class AskState(BaseModel):
    question: str
    answer: str = ''

def answer_question(state: AskState):
    print('--- answer_question called ---')
    decision = interrupt(f'Send "{state.question}" to the model? (yes/no): ')

    if decision != 'yes':
        return {'answer': 'Cancelled by human.'}

    style = interrupt('Which answer style? (short/detailed): ', response_schema=Literal['short', 'detailed'])

    response = model.invoke(f'{state.question}, give response in {style} format.')
    return {'answer': response.content}

graph = StateGraph(AskState)
graph.add_node('answer_question', answer_question)

graph.add_edge(START, 'answer_question')
graph.add_edge('answer_question', END)

config = {'configurable': {'thread_id': '1'}}

workflow = graph.compile(checkpointer=InMemorySaver())
question = input('Ask anything: ')
result = workflow.invoke({'question': question}, config)

while '__interrupt__' in result:
    decision = input(result['__interrupt__'][0].value)
    result = workflow.invoke(Command(resume=decision), config)
    print(result)

print(f'Final Answer: {result['answer']}')

png = workflow.get_graph().draw_mermaid_png()
with open('16_hitl_single_node.png', 'wb') as f:
    f.write(png)