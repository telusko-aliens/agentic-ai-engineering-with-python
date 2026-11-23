from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

@tool
def search_flights(from_city: str, to_city: str) -> str:
    """Search flights between two cities."""
    print(f'      --- search_flights({from_city}, {to_city}) ---')
    return 'AI-143: ₹52,000 | AF-226: ₹61,000'

flight_agent = create_agent(
    model=model,
    tools=[search_flights],
    system_prompt='You are a flight expert. Find flights and recommend the cheapest one. Keep answers short.',
)

@tool
def search_hotels(city: str, max_price_per_night: int) -> str:
    """Search hotels in a city under a price per night (in ₹)."""
    print(f'      --- search_hotels({city}, {max_price_per_night}) ---')
    return 'Hotel Lumiere: ₹7,500/night | Seine View Inn: ₹9,000/night'

hotel_agent = create_agent(
    model=model,
    tools=[search_hotels],
    system_prompt='You are a hotel expert. Find hotels within budget and recommend one. Keep answers short.',
)

# wrap these agents in tools

@tool
def ask_flight_agent(request: str) -> str:
    """Ask the flight expert anything about flights. Describe the full request in plain English."""
    print(f'  >>> supervisor -> flight_agent: {request}')
    result = flight_agent.invoke({'messages': [('user', request)]})
    return result['messages'][-1].content

@tool
def ask_hotel_agent(request: str) -> str:
    """Ask the hotel expert anything about hotels. Describe the full request in plain English."""
    print(f'  >>> supervisor -> hotel_agent: {request}')
    result = hotel_agent.invoke({'messages': [('user', request)]})
    return result['messages'][-1].content

supervisor = create_agent(
    model=model,
    tools=[ask_flight_agent, ask_hotel_agent],
    system_prompt=(
        'You are a travel supervisor. You do not search anything yourself. '
        'Send flight questions to the flight agent and hotel questions to the hotel agent, '
        'then combine their answers into one short reply for the user.'
    ),
)

result = supervisor.invoke({'messages': [('user', 'Find me the cheapest flight from Delhi to Paris.')]})
print(result['messages'][-1].content)

result = supervisor.invoke({'messages': [('user', 'Suggest a hotel in Paris under ₹8,000 per night.')]})
print(result['messages'][-1].content)
print()

result = supervisor.invoke({'messages': [('user',
    'I am going from Delhi to Paris for 3 nights. Find the cheapest flight and a hotel under ₹10,000 per night, '
    'and tell me the total cost.')]})
print(result['messages'][-1].content)
