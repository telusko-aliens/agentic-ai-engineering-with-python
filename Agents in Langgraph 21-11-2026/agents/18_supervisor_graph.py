from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, SystemMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, MessagesState, START, END


load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class State(MessagesState):
    next: str            # who (which agent) the supervisor picked

@tool
def search_flights(from_city: str, to_city: str) -> str:
    """Search flights between two cities."""
    print(f'      --- search_flights({from_city}, {to_city}) ---')
    return 'AI-143: ₹52,000 | AF-226: ₹61,000'

flight_agent = create_agent(
    model=model,
    tools=[search_flights],
    system_prompt=(
        'You are the flight expert in a travel team. Reply ONLY with the flight result from your tool. '
        'Never talk about hotels or total cost, other team members handle that.'
    ),
)

def flight_node(state: State):
    result = flight_agent.invoke({'messages': state['messages']})   # sees the WHOLE shared conversation
    answer = result['messages'][-1].content
    return {'messages': [AIMessage(content=answer, name='flight_agent')]}


@tool
def search_hotels(city: str, max_price_per_night: int) -> str:
    """Search hotels in a city under a price per night (in ₹)."""
    print(f'      --- search_hotels({city}, {max_price_per_night}) ---')
    return 'Hotel Lumiere: ₹7,500/night | Seine View Inn: ₹9,000/night'

hotel_agent = create_agent(
    model=model,
    tools=[search_hotels],
    system_prompt=(
        'You are the hotel expert in a travel team. Reply ONLY with the hotel result from your tool. '
        'Never talk about flights or total cost, other team members handle that.'
    ),
)

def hotel_node(state: State):
    result = hotel_agent.invoke({'messages': state['messages']})
    answer = result['messages'][-1].content
    return {'messages': [AIMessage(content=answer, name='hotel_agent')]}

class Route(BaseModel):
    next: Literal['flight_agent', 'hotel_agent', 'FINISH']

supervisor_model = model.with_structured_output(Route)

SUPERVISOR_PROMPT = SystemMessage(
    'You are a supervisor managing a travel team: flight_agent and hotel_agent. '
    'Read the conversation and pick who should work next. '
    'Do not pick an agent whose part is already answered. '
    'When every part of the user request is answered, pick FINISH.'
)

def supervisor_node(state: State):
    route = supervisor_model.invoke([SUPERVISOR_PROMPT] + state['messages'])
    print(f'  [supervisor] next -> {route.next}')
    return {'next': route.next}

def final_answer_node(state: State):
    reply = model.invoke(
        [SystemMessage('Combine the team answers into one short final reply for the user, with the total cost.')]
        + state['messages']
    )
    return {'messages': [reply]}

builder = StateGraph(State)
builder.add_node('supervisor', supervisor_node)
builder.add_node('flight_agent', flight_node)
builder.add_node('hotel_agent', hotel_node)
builder.add_node('final_answer', final_answer_node)

builder.add_edge(START, 'supervisor')

builder.add_conditional_edges(
    'supervisor',
    lambda state: state['next'],
    {'flight_agent': 'flight_agent', 'hotel_agent': 'hotel_agent', 'FINISH': 'final_answer'},
)
builder.add_edge('flight_agent', 'supervisor')
builder.add_edge('hotel_agent', 'supervisor')
builder.add_edge('final_answer', END)

graph = builder.compile()

question = {'messages': [('user',
    'I am going from Delhi to Paris for 3 nights. Find the cheapest flight and a hotel under ₹10,000 per night, '
    'and tell me the total cost.')]}

result = graph.invoke(question)

for message in result['messages']:
    print(f'{message.name or message.type}: {message.content}\n')


with open('18_supervisor_graph.png', 'wb') as f:
    f.write(graph.get_graph().draw_mermaid_png())