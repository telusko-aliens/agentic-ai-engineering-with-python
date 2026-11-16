from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer
from langchain.agents import create_agent

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

class TripState(BaseModel):
    interest: str
    destination: str = ''
    itinerary: str = ''

def suggest_destination(state: TripState):
    writer = get_stream_writer()
    writer('step 1/2: picking the best city for you ...')
    response = llm.invoke(
        f'I love {state.interest}. Pick the best city for me from: Paris, London, Tokyo. '
        'Reply with only the city name.'
    )
    return {'destination': response.content}

def plan_itinerary(state: TripState):
    writer = get_stream_writer()
    writer(f'step 2/2: planning your day in {state.destination} ...')
    response = llm.invoke(f'Plan a one-day {state.interest} itinerary for {state.destination} in 3 short bullet points.')
    return {'itinerary': response.content}

graph = StateGraph(TripState)
graph.add_node('suggest_destination', suggest_destination)
graph.add_node('plan_itinerary', plan_itinerary)

graph.add_edge(START, 'suggest_destination')
graph.add_edge('suggest_destination', 'plan_itinerary')
graph.add_edge('plan_itinerary', END)

trip_planner = graph.compile()

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    writer = get_stream_writer()
    writer(f'checking the weather in {city} ...')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

@tool
def plan_trip(interest: str) -> str:
    """Pick a destination and plan a one-day itinerary, based on what the user loves (food, art, history ...)."""
    final_state = trip_planner.invoke({'interest': interest})
    return f"destination: {final_state['destination']}\nitinerary:\n{final_state['itinerary']}"

agent = create_agent(
    model=llm,
    tools=[get_weather, plan_trip],
    system_prompt=(
        'You are a travel assistant. Use the tools for weather and trip plans, never guess. '
        'For a trip, first call plan_trip, then call get_weather for the city it picked. Keep the final answer short.'
    ),
)

question = {'messages': [('user', 'I love art, plan me a day trip and tell me the weather there.')]}

print("\n --- stream_mode='custom' --- \n")

for namespace, message in agent.stream(question, stream_mode='custom', subgraphs=True):
    print(message)

print("\n --- stream_mode='multiple modes' --- \n")
for namespace, mode, chunk in agent.stream(question, stream_mode=['updates', 'custom'], subgraphs=True):
    if mode == 'custom':
        print(f'    progress: {chunk}')
    else:
        for node_name in chunk:
            print(f'node finished: {node_name}')
