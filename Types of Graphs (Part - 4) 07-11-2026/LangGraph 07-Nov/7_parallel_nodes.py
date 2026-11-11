from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class GuideState(BaseModel):
    city: str
    places: str = ''
    food: str = ''
    budget: str = ''
    guide: str = ''

def find_places(state: GuideState):
    print("find places called")
    response = model.invoke(f'List 3 must-see places in {state.city}, one line each.')
    return {'places': response.content}

def find_food(state: GuideState):
    print("find food called")
    response = model.invoke(f'List 3 local dishes to try in {state.city}, one line each.')
    return {'food': response.content}

def estimate_budget(state: GuideState):
    print("estimate budget called")
    response = model.invoke(f'Estimate a daily budget in USD for a backpacker in {state.city}, in 2 lines.')
    return {'budget': response.content}

def make_guide(state: GuideState):
    guide = f'PLACES:\n{state.places}\n\nFOOD:\n{state.food}\n\nBUDGET:\n{state.budget}'
    return {'guide': guide}

graph = StateGraph(GuideState)
graph.add_node('find_places', find_places)
graph.add_node('find_food', find_food)
graph.add_node('estimate_budget', estimate_budget)
graph.add_node('make_guide', make_guide)

graph.add_edge(START, 'find_places')
graph.add_edge(START, 'find_food')
graph.add_edge(START, 'estimate_budget')
graph.add_edge('find_places', 'make_guide')
graph.add_edge('find_food', 'make_guide')
graph.add_edge('estimate_budget', 'make_guide')
graph.add_edge('make_guide', END)

workflow = graph.compile()

final_state = workflow.invoke({'city': 'Jaipur'})
print(final_state['guide'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('7_parallel_nodes.png', 'wb') as f:
    f.write(png)
