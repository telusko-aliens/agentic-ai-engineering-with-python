import time
import operator
from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

SPECS = {
    'pixel 9': '6.3" OLED, Tensor G4, 12GB RAM, 4700mAh, ₹79,999',
    'iphone 16': '6.1" OLED, A18, 8GB RAM, 3561mAh, ₹79,900',
    'galaxy s24': '6.2" AMOLED, Exynos 2400, 8GB RAM, 4000mAh, ₹74,999',
    'oneplus 13': '6.8" AMOLED, Snapdragon 8 Elite, 12GB RAM, 6000mAh, ₹69,999',
}
REVIEWS = {
    'pixel 9': 'Best camera software, 7 years of updates, gets warm when gaming.',
    'iphone 16': 'Smooth and reliable, great video, slow 25W charging.',
    'galaxy s24': 'Compact, bright screen, battery only average.',
    'oneplus 13': 'Huge battery, very fast 100W charging, camera a step behind.',
}

@tool
def get_specs(phone: str) -> str:
    """Get the specs and price of a phone."""
    print(f'      --- get_specs({phone}) ---')
    time.sleep(1)   # pretend this is a slow website
    return SPECS.get(phone.lower(), 'no data')

@tool
def get_reviews(phone: str) -> str:
    """Get a summary of user reviews for a phone."""
    print(f'      --- get_reviews({phone}) ---')
    time.sleep(1)
    return REVIEWS.get(phone.lower(), 'no data')

research_agent = create_agent(
    model=model,
    tools=[get_specs, get_reviews],
    system_prompt='You research ONE phone. Use both tools, then write a 3-line summary: specs, price, pros and cons.',
)


class State(TypedDict):
    request: str
    phones: list[str]
    research: Annotated[list[str], operator.add]   # every worker ADDS its result to this list
    final_answer: str

class WorkerInput(TypedDict):
    phone: str

class Plan(BaseModel):
    phones: list[str]

def orchestrator(state: State):
    plan = model.with_structured_output(Plan).invoke(
        f'List the phone names the user wants to compare, in lowercase.\nRequest: {state["request"]}'
    )
    print(f'[orchestrator] {len(plan.phones)} workers needed: {plan.phones}')
    return {'phones': plan.phones}


def assign_workers(state: State):
    return [Send('worker', {'phone': phone}) for phone in state['phones']]

def worker(worker_input: WorkerInput):
    phone = worker_input['phone']
    print(f'  [worker] started: {phone}')
    result = research_agent.invoke({'messages': [('user', f'Research the {phone}.')]})
    print(f'  [worker] finished: {phone}')
    return {'research': [f'## {phone}\n{result["messages"][-1].content}']}

def writer(state: State):
    all_research = '\n\n'.join(state['research'])
    reply = model.invoke(
        f'User request: {state["request"]}\n\nResearch from the team:\n{all_research}\n\n'
        'Write a short comparison and give a clear recommendation.'
    )
    return {'final_answer': reply.content}


builder = StateGraph(State)
builder.add_node('orchestrator', orchestrator)
builder.add_node('worker', worker)
builder.add_node('writer', writer)

builder.add_edge(START, 'orchestrator')
builder.add_conditional_edges('orchestrator', assign_workers, ['worker'])
builder.add_edge('worker', 'writer')     # writer waits until ALL workers are done
builder.add_edge('writer', END)
graph = builder.compile()

start = time.time()
result = graph.invoke({'request': 'Compare Pixel 9, iPhone 16 and OnePlus 13. I care about battery and camera.'})
print(f'\ntime taken: {time.time() - start:.1f} seconds (workers ran in parallel)')

print('\n========== final answer ==========')
print(result['final_answer'])

with open('20_orchestrator_workers.png', 'wb') as f:
    f.write(graph.get_graph().draw_mermaid_png())
