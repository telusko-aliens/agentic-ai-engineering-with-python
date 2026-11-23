from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

class TripState(BaseModel):
    interest: str
    destination: str = ''
    itinerary: str = ''

def suggest_destination(state: TripState):
    print('    --- graph node: suggest_destination ---')
    response = llm.invoke(
        f'I love {state.interest}. Pick the best city for me from: Paris, London, Tokyo. '
        'Reply with only the city name.'
    )
    return {'destination': response.content}

def plan_itinerary(state: TripState):
    print('    --- graph node: plan_itinerary ---')
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
    print(f'--- tool: get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

@tool
def plan_trip(interest: str) -> str:
    """Pick a destination and plan a one-day itinerary, based on what the user loves (food, art, history ...)."""
    print(f'--- tool: plan_trip({interest}) runs the graph ---')
    final_state = trip_planner.invoke({'interest': interest})
    return f"destination: {final_state['destination']}\nitinerary:\n{final_state['itinerary']}"

agent = create_agent(
    model=llm,
    tools=[get_weather, plan_trip],
    system_prompt='You are a travel assistant. Use the tools for weather and trip plans, never guess.',
)

result = agent.invoke({'messages': [('user', "What's the weather in Paris?")]})
print(result['messages'][-1].content)

result = agent.invoke({'messages': [('user', 'I love street food, plan me a day trip.')]})
print(result['messages'][-1].content)

with open('5_agent_graph_as_tool.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())

with open('5_graph_trip_planner.png', 'wb') as f:
    f.write(trip_planner.get_graph().draw_mermaid_png())

